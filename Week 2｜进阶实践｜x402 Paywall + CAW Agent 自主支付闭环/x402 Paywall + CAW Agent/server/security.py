from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib
import hmac
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """速率限制器"""
    
    def __init__(self, max_requests: int = 100, time_window_seconds: int = 60):
        self.max_requests = max_requests
        self.time_window_seconds = time_window_seconds
        self.requests: Dict[str, List[datetime]] = defaultdict(list)
        
    def is_allowed(self, client_id: str) -> bool:
        """检查客户端是否允许发送请求"""
        now = datetime.now()
        window_start = now - timedelta(seconds=self.time_window_seconds)
        
        # 清理过期记录
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > window_start
        ]
        
        # 检查是否超过限制
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        
        # 记录新请求
        self.requests[client_id].append(now)
        return True
    
    def get_remaining_requests(self, client_id: str) -> int:
        """获取剩余请求数"""
        now = datetime.now()
        window_start = now - timedelta(seconds=self.time_window_seconds)
        
        valid_requests = [
            req_time for req_time in self.requests[client_id]
            if req_time > window_start
        ]
        
        return max(0, self.max_requests - len(valid_requests))


class DoubleSpendPrevention:
    """双花攻击防护"""
    
    def __init__(self):
        self.spent_amounts: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self.daily_limits: Dict[str, float] = {}
        
    def check_double_spend(self, wallet_address: str, amount: float, tx_hash: str) -> bool:
        """
        检查是否存在双花攻击
        
        Returns:
            True if allowed, False if double spend detected
        """
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 检查每日限额
        if wallet_address in self.daily_limits:
            daily_spent = self.spent_amounts[wallet_address].get(today, 0)
            if daily_spent + amount > self.daily_limits[wallet_address]:
                logger.warning(f"Daily limit exceeded for {wallet_address}")
                return False
        
        # 检查交易哈希是否已使用
        if self._is_tx_hash_used(wallet_address, tx_hash):
            logger.warning(f"Transaction hash already used: {tx_hash}")
            return False
        
        return True
    
    def record_spend(self, wallet_address: str, amount: float, tx_hash: str):
        """记录支出"""
        today = datetime.now().strftime("%Y-%m-%d")
        self.spent_amounts[wallet_address][today] += amount
        self._mark_tx_hash_used(wallet_address, tx_hash)
    
    def set_daily_limit(self, wallet_address: str, limit: float):
        """设置每日限额"""
        self.daily_limits[wallet_address] = limit
    
    def _is_tx_hash_used(self, wallet_address: str, tx_hash: str) -> bool:
        """检查交易哈希是否已使用"""
        key = f"{wallet_address}:{tx_hash}"
        return hasattr(self, '_used_hashes') and key in self._used_hashes
    
    def _mark_tx_hash_used(self, wallet_address: str, tx_hash: str):
        """标记交易哈希为已使用"""
        if not hasattr(self, '_used_hashes'):
            self._used_hashes = set()
        key = f"{wallet_address}:{tx_hash}"
        self._used_hashes.add(key)


class PaymentFraudDetection:
    """支付欺诈检测"""
    
    def __init__(self):
        self.suspicious_patterns: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.blocked_ips: set = set()
        self.blocked_wallets: set = set()
        
    def analyze_payment_pattern(self, client_ip: str, wallet_address: str, amount: float) -> Dict[str, Any]:
        """
        分析支付模式，检测可疑行为
        
        Returns:
            包含风险评分和建议的字典
        """
        risk_score = 0
        reasons = []
        
        # 检查IP是否被封禁
        if client_ip in self.blocked_ips:
            risk_score += 100
            reasons.append("IP address is blocked")
        
        # 检查钱包是否被封禁
        if wallet_address in self.blocked_wallets:
            risk_score += 100
            reasons.append("Wallet address is blocked")
        
        # 检查支付频率
        recent_payments = self._get_recent_payments(client_ip, hours=1)
        if len(recent_payments) > 10:
            risk_score += 30
            reasons.append("High payment frequency")
        
        # 检查金额异常
        if amount > 10:  # 单次支付超过10 USDT
            risk_score += 20
            reasons.append("Large single payment amount")
        
        # 记录支付模式
        self.suspicious_patterns[client_ip].append({
            "timestamp": datetime.now(),
            "amount": amount,
            "wallet": wallet_address
        })
        
        return {
            "risk_score": risk_score,
            "reasons": reasons,
            "is_suspicious": risk_score > 50,
            "recommended_action": self._get_recommended_action(risk_score)
        }
    
    def block_ip(self, ip_address: str):
        """封禁IP地址"""
        self.blocked_ips.add(ip_address)
        logger.info(f"Blocked IP address: {ip_address}")
    
    def block_wallet(self, wallet_address: str):
        """封禁钱包地址"""
        self.blocked_wallets.add(wallet_address)
        logger.info(f"Blocked wallet address: {wallet_address}")
    
    def _get_recent_payments(self, client_ip: str, hours: int = 1) -> List[Dict[str, Any]]:
        """获取最近的支付记录"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            p for p in self.suspicious_patterns.get(client_ip, [])
            if p["timestamp"] > cutoff_time
        ]
    
    def _get_recommended_action(self, risk_score: int) -> str:
        """获取推荐操作"""
        if risk_score >= 80:
            return "block_and_alert"
        elif risk_score >= 50:
            return "require_additional_verification"
        elif risk_score >= 30:
            return "monitor_closely"
        else:
            return "allow"


class NonceManager:
    """Nonce 管理器 - 防止交易重放"""
    
    def __init__(self):
        self.used_nonces: Dict[str, set] = defaultdict(set)
        self.nonce_expiry_hours = 24
        
    def is_nonce_used(self, address: str, nonce: int) -> bool:
        """检查nonce是否已使用"""
        return nonce in self.used_nonces[address]
    
    def mark_nonce_used(self, address: str, nonce: int):
        """标记nonce为已使用"""
        self.used_nonces[address].add(nonce)
    
    def get_next_nonce(self, address: str) -> int:
        """获取下一个可用nonce"""
        if not self.used_nonces[address]:
            return 0
        return max(self.used_nonces[address]) + 1
    
    def cleanup_expired_nonces(self):
        """清理过期的nonce记录"""
        # 简化实现：实际应该根据时间戳清理
        pass


class SecurityAuditLogger:
    """安全审计日志"""
    
    def __init__(self, log_file: str = "security_audit.log"):
        self.logger = logging.getLogger("security_audit")
        self.logger.setLevel(logging.INFO)
        
        # 添加文件处理器
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)
        
    def log_payment_attempt(self, client_ip: str, wallet: str, amount: float, status: str):
        """记录支付尝试"""
        self.logger.info(f"Payment attempt: IP={client_ip}, Wallet={wallet}, Amount={amount}, Status={status}")
    
    def log_fraud_detection(self, client_ip: str, risk_score: int, reasons: List[str]):
        """记录欺诈检测"""
        self.logger.warning(f"Fraud detected: IP={client_ip}, RiskScore={risk_score}, Reasons={reasons}")
    
    def log_replay_attack(self, tx_hash: str, client_ip: str):
        """记录重放攻击"""
        self.logger.error(f"Replay attack detected: TxHash={tx_hash}, IP={client_ip}")
    
    def log_pact_violation(self, wallet: str, violation_type: str, details: str):
        """记录Pact违规"""
        self.logger.error(f"Pact violation: Wallet={wallet}, Type={violation_type}, Details={details}")


class SecurityManager:
    """安全管理器 - 整合所有安全功能"""
    
    def __init__(self):
        self.rate_limiter = RateLimiter(max_requests=100, time_window_seconds=60)
        self.double_spend_prevention = DoubleSpendPrevention()
        self.fraud_detection = PaymentFraudDetection()
        self.nonce_manager = NonceManager()
        self.audit_logger = SecurityAuditLogger()
        
    def validate_payment_request(self, client_ip: str, wallet_address: str, 
                                amount: float, tx_hash: str, nonce: int = 0) -> Dict[str, Any]:
        """
        验证支付请求的安全性
        
        Returns:
            包含验证结果的字典
        """
        errors = []
        
        # 检查速率限制
        if not self.rate_limiter.is_allowed(client_ip):
            errors.append("Rate limit exceeded")
            self.audit_logger.log_fraud_detection(client_ip, 100, ["Rate limit exceeded"])
        
        # 检查双花
        if not self.double_spend_prevention.check_double_spend(wallet_address, amount, tx_hash):
            errors.append("Double spend detected")
            self.audit_logger.log_replay_attack(tx_hash, client_ip)
        
        # 检查欺诈模式
        fraud_analysis = self.fraud_detection.analyze_payment_pattern(client_ip, wallet_address, amount)
        if fraud_analysis["is_suspicious"]:
            errors.append(f"Suspicious pattern: {', '.join(fraud_analysis['reasons'])}")
        
        # 检查nonce
        if nonce > 0 and self.nonce_manager.is_nonce_used(wallet_address, nonce):
            errors.append("Nonce already used")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "risk_score": fraud_analysis["risk_score"],
            "recommended_action": fraud_analysis["recommended_action"]
        }
    
    def record_successful_payment(self, client_ip: str, wallet_address: str, 
                                 amount: float, tx_hash: str, nonce: int = 0):
        """记录成功的支付"""
        self.double_spend_prevention.record_spend(wallet_address, amount, tx_hash)
        if nonce > 0:
            self.nonce_manager.mark_nonce_used(wallet_address, nonce)
        self.audit_logger.log_payment_attempt(client_ip, wallet_address, amount, "success")
    
    def set_wallet_daily_limit(self, wallet_address: str, limit: float):
        """设置钱包每日限额"""
        self.double_spend_prevention.set_daily_limit(wallet_address, limit)