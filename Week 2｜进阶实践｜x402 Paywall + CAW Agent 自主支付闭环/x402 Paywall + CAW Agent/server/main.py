from fastapi import FastAPI, Request, Response, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
import time
import hashlib
from datetime import datetime, timedelta

app = FastAPI(title="x402 Paywall Server", description="AI Alpha因子数据API服务")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置常量
PRICE_PER_CALL_USDT = 0.5
PAYWALL_ADDRESS = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
CHAIN_ID = 1  # Ethereum Mainnet
TOKEN_CONTRACT = "0xdAC17F958D2ee523a2206206994597C13D831ec7"  # USDT Contract

# 模拟数据库：已消费的交易哈希
consumed_tx_hashes: Dict[str, Dict[str, Any]] = {}

# 模拟数据库：API调用记录
api_call_records: Dict[str, Dict[str, Any]] = {}

class PaymentVerification(BaseModel):
    tx_hash: str
    amount: float
    asset: str
    destination: str
    chain_id: int

class AlphaSignal(BaseModel):
    btc_sentiment: str
    alpha_score: float
    timestamp: str
    confidence: float
    source: str

@app.get("/api/v1/alpha-signals")
async def get_alpha_signals(request: Request, response: Response):
    """获取Alpha信号数据 - 需要x402支付"""
    
    # 检查请求头中是否包含链上支付凭证
    tx_hash = request.headers.get("X-Payment-Tx-Hash")
    
    if not tx_hash:
        # 未付款，构建标准x402响应
        response.status_code = status.HTTP_402_PAYMENT_REQUIRED
        response.headers["X-x402-Amount"] = str(PRICE_PER_CALL_USDT)
        response.headers["X-x402-Asset"] = "USDT"
        response.headers["X-x402-Destination"] = PAYWALL_ADDRESS
        response.headers["X-x402-Chain-ID"] = str(CHAIN_ID)
        response.headers["X-x402-Token-Contract"] = TOKEN_CONTRACT
        response.headers["X-x402-Description"] = "Premium Alpha Signal Data Access"
        response.headers["X-x402-Expires"] = (datetime.now() + timedelta(minutes=5)).isoformat()
        
        return {
            "error": "Payment Required",
            "message": "Please settle via x402 infrastructure.",
            "payment_info": {
                "amount": PRICE_PER_CALL_USDT,
                "asset": "USDT",
                "destination": PAYWALL_ADDRESS,
                "chain_id": CHAIN_ID,
                "token_contract": TOKEN_CONTRACT
            }
        }
    
    # 检查交易哈希是否已被消费（防重放攻击）
    if tx_hash in consumed_tx_hashes:
        raise HTTPException(
            status_code=409,
            detail="Transaction hash already consumed. Replay attack detected."
        )
    
    # 验证链上结算记录
    is_valid = await verify_onchain_settlement(tx_hash, PAYWALL_ADDRESS, PRICE_PER_CALL_USDT)
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail="Invalid payment. Transaction verification failed."
        )
    
    # 标记交易哈希为已消费
    consumed_tx_hashes[tx_hash] = {
        "consumed_at": datetime.now().isoformat(),
        "amount": PRICE_PER_CALL_USDT,
        "client_ip": request.client.host if request.client else "unknown"
    }
    
    # 记录API调用
    call_id = hashlib.sha256(f"{tx_hash}{time.time()}".encode()).hexdigest()[:16]
    api_call_records[call_id] = {
        "tx_hash": tx_hash,
        "timestamp": datetime.now().isoformat(),
        "client_ip": request.client.host if request.client else "unknown"
    }
    
    # 验证通过，交付核心数据
    return {
        "status": "success",
        "call_id": call_id,
        "data": {
            "BTC_sentiment": "bullish",
            "alpha_score": 0.89,
            "timestamp": datetime.now().isoformat(),
            "confidence": 0.92,
            "source": "premium_alpha_provider",
            "factors": {
                "whale_accumulation": 0.85,
                "social_sentiment": 0.78,
                "on_chain_activity": 0.91,
                "technical_indicators": 0.87
            }
        }
    }

@app.post("/api/v1/verify-payment")
async def verify_payment(payment: PaymentVerification):
    """手动验证支付（用于调试）"""
    is_valid = await verify_onchain_settlement(
        payment.tx_hash, 
        payment.destination, 
        payment.amount
    )
    
    if is_valid:
        return {"status": "verified", "message": "Payment is valid"}
    else:
        raise HTTPException(status_code=400, detail="Payment verification failed")

@app.get("/api/v1/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "consumed_hashes_count": len(consumed_tx_hashes),
        "api_calls_count": len(api_call_records)
    }

@app.get("/api/v1/stats")
async def get_stats():
    """获取统计信息"""
    return {
        "total_consumed_hashes": len(consumed_tx_hashes),
        "total_api_calls": len(api_call_records),
        "consumed_hashes": list(consumed_tx_hashes.keys())[-10:],  # 最后10个
        "recent_calls": list(api_call_records.values())[-5:]  # 最后5个调用
    }

async def verify_onchain_settlement(tx_hash: str, expected_destination: str, expected_amount: float) -> bool:
    """
    验证链上结算记录
    在实际生产环境中，这里应该调用区块链节点API验证交易
    """
    # 模拟验证逻辑
    # 1. 检查交易哈希格式
    if not tx_hash.startswith("0x") or len(tx_hash) != 66:
        return False
    
    # 2. 模拟调用区块链API验证交易详情
    # 在实际实现中，这里应该：
    # - 连接到以太坊节点
    # - 获取交易详情
    # - 验证收款地址
    # - 验证金额
    # - 验证交易状态为成功
    
    # 模拟验证通过（实际需要真实的链上验证）
    return True

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)