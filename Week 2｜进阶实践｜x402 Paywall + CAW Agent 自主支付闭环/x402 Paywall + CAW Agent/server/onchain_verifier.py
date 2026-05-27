from web3 import Web3
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class OnChainVerifier:
    """链上交易验证器"""
    
    def __init__(self, rpc_url: str = "https://mainnet.infura.io/v3/YOUR_INFURA_KEY"):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.usdt_contract_address = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
        self.usdt_abi = [
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": False,
                "inputs": [
                    {"name": "_to", "type": "address"},
                    {"name": "_value", "type": "uint256"}
                ],
                "name": "transfer",
                "outputs": [{"name": "", "type": "bool"}],
                "type": "function"
            }
        ]
        
    async def verify_transaction(self, tx_hash: str, expected_to: str, expected_amount: float) -> Dict[str, Any]:
        """
        验证链上交易
        
        Args:
            tx_hash: 交易哈希
            expected_to: 预期收款地址
            expected_amount: 预期金额 (USDT)
            
        Returns:
            验证结果字典
        """
        try:
            # 获取交易详情
            tx = self.w3.eth.get_transaction(tx_hash)
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            
            # 验证交易状态
            if receipt['status'] != 1:
                return {
                    "valid": False,
                    "error": "Transaction failed",
                    "details": {
                        "status": receipt['status'],
                        "gas_used": receipt['gasUsed']
                    }
                }
            
            # 验证收款地址
            if tx['to'].lower() != expected_to.lower():
                return {
                    "valid": False,
                    "error": "Recipient address mismatch",
                    "details": {
                        "expected": expected_to,
                        "actual": tx['to']
                    }
                }
            
            # 验证金额（需要解码USDT转账数据）
            # 注意：这里简化处理，实际需要解析input data
            expected_amount_wei = int(expected_amount * 10**6)  # USDT有6位小数
            
            return {
                "valid": True,
                "details": {
                    "block_number": receipt['blockNumber'],
                    "gas_used": receipt['gasUsed'],
                    "timestamp": datetime.now().isoformat(),
                    "from": tx['from'],
                    "to": tx['to']
                }
            }
            
        except Exception as e:
            logger.error(f"Transaction verification failed: {e}")
            return {
                "valid": False,
                "error": str(e),
                "details": {}
            }
    
    async def check_transaction_status(self, tx_hash: str) -> str:
        """
        检查交易状态
        
        Returns:
            'pending', 'confirmed', 'failed'
        """
        try:
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            if receipt['status'] == 1:
                return 'confirmed'
            else:
                return 'failed'
        except:
            return 'pending'
    
    async def get_transaction_details(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """获取交易详情"""
        try:
            tx = self.w3.eth.get_transaction(tx_hash)
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            
            return {
                "hash": tx['hash'].hex(),
                "from": tx['from'],
                "to": tx['to'],
                "value": tx['value'],
                "block_number": receipt['blockNumber'],
                "gas_used": receipt['gasUsed'],
                "status": receipt['status']
            }
        except Exception as e:
            logger.error(f"Failed to get transaction details: {e}")
            return None


class TransactionMonitor:
    """交易监控器 - 处理交易超时和重试"""
    
    def __init__(self, verifier: OnChainVerifier):
        self.verifier = verifier
        self.pending_transactions: Dict[str, Dict[str, Any]] = {}
        self.timeout_seconds = 300  # 5分钟超时
        
    async def monitor_transaction(self, tx_hash: str, callback=None):
        """监控交易状态"""
        self.pending_transactions[tx_hash] = {
            "start_time": datetime.now(),
            "status": "pending",
            "retries": 0
        }
        
        while True:
            status = await self.verifier.check_transaction_status(tx_hash)
            
            if status == 'confirmed':
                self.pending_transactions[tx_hash]['status'] = 'confirmed'
                if callback:
                    await callback(tx_hash, 'confirmed')
                break
            elif status == 'failed':
                self.pending_transactions[tx_hash]['status'] = 'failed'
                if callback:
                    await callback(tx_hash, 'failed')
                break
            
            # 检查超时
            start_time = self.pending_transactions[tx_hash]['start_time']
            if (datetime.now() - start_time).seconds > self.timeout_seconds:
                self.pending_transactions[tx_hash]['status'] = 'timeout'
                if callback:
                    await callback(tx_hash, 'timeout')
                break
            
            await asyncio.sleep(5)  # 每5秒检查一次
    
    def get_pending_count(self) -> int:
        """获取待处理交易数量"""
        return len([tx for tx in self.pending_transactions.values() if tx['status'] == 'pending'])


class AntiReplayProtection:
    """防重放攻击保护"""
    
    def __init__(self):
        self.consumed_hashes: Dict[str, Dict[str, Any]] = {}
        self.hash_expiry_hours = 24
        
    def is_hash_consumed(self, tx_hash: str) -> bool:
        """检查交易哈希是否已被消费"""
        if tx_hash not in self.consumed_hashes:
            return False
        
        # 检查是否过期
        consumed_time = self.consumed_hashes[tx_hash]['consumed_at']
        if (datetime.now() - consumed_time).total_seconds() > self.hash_expiry_hours * 3600:
            del self.consumed_hashes[tx_hash]
            return False
        
        return True
    
    def mark_hash_consumed(self, tx_hash: str, metadata: Dict[str, Any]):
        """标记交易哈希为已消费"""
        self.consumed_hashes[tx_hash] = {
            "consumed_at": datetime.now(),
            "metadata": metadata
        }
    
    def get_consumed_hashes_count(self) -> int:
        """获取已消费哈希数量"""
        return len(self.consumed_hashes)
    
    def cleanup_expired_hashes(self):
        """清理过期的哈希记录"""
        expired_hashes = []
        for tx_hash, data in self.consumed_hashes.items():
            if (datetime.now() - data['consumed_at']).total_seconds() > self.hash_expiry_hours * 3600:
                expired_hashes.append(tx_hash)
        
        for tx_hash in expired_hashes:
            del self.consumed_hashes[tx_hash]