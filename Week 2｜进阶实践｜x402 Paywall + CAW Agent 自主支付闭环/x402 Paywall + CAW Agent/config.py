import os
from typing import Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class ServerConfig:
    """服务器配置"""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
@dataclass
class PaymentConfig:
    """支付配置"""
    price_per_call_usdt: float = 0.5
    paywall_address: str = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
    chain_id: int = 1
    token_contract: str = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
    token_symbol: str = "USDT"
    token_decimals: int = 6

@dataclass
class CoboCawConfig:
    """Cobo CAW 配置"""
    api_key: str = os.getenv("COBO_API_KEY", "")
    api_secret: str = os.getenv("COBO_API_SECRET", "")
    wallet_id: str = os.getenv("COBO_WALLET_ID", "")
    base_url: str = "https://api.cobo.com/v2"

@dataclass
class PactConfig:
    """Pact 策略配置"""
    max_fee_per_task: float = 1.0
    daily_budget: float = 50.0
    allowed_destinations: list = None
    allowed_chains: list = None
    allowed_tokens: list = None
    ttl_hours: int = 24
    cooldown_seconds: int = 5
    
    def __post_init__(self):
        if self.allowed_destinations is None:
            self.allowed_destinations = ["0x742d35Cc6634C0532925a3b844Bc454e4438f44e"]
        if self.allowed_chains is None:
            self.allowed_chains = [1]
        if self.allowed_tokens is None:
            self.allowed_tokens = ["USDT"]

@dataclass
class SecurityConfig:
    """安全配置"""
    rate_limit_max_requests: int = 100
    rate_limit_time_window: int = 60
    anti_replay_expiry_hours: int = 24
    max_daily_spending: float = 100.0
    enable_fraud_detection: bool = True

@dataclass
class BlockchainConfig:
    """区块链配置"""
    rpc_url: str = os.getenv("ETH_RPC_URL", "https://mainnet.infura.io/v3/YOUR_KEY")
    network_id: int = 1
    gas_limit: int = 200000
    gas_price_gwei: int = 20

class AppConfig:
    """应用配置"""
    
    def __init__(self):
        self.server = ServerConfig()
        self.payment = PaymentConfig()
        self.cobo_caw = CoboCawConfig()
        self.pact = PactConfig()
        self.security = SecurityConfig()
        self.blockchain = BlockchainConfig()
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "server": {
                "host": self.server.host,
                "port": self.server.port,
                "debug": self.server.debug
            },
            "payment": {
                "price_per_call_usdt": self.payment.price_per_call_usdt,
                "paywall_address": self.payment.paywall_address,
                "chain_id": self.payment.chain_id,
                "token_contract": self.payment.token_contract,
                "token_symbol": self.payment.token_symbol,
                "token_decimals": self.payment.token_decimals
            },
            "pact": {
                "max_fee_per_task": self.pact.max_fee_per_task,
                "daily_budget": self.pact.daily_budget,
                "allowed_destinations": self.pact.allowed_destinations,
                "allowed_chains": self.pact.allowed_chains,
                "allowed_tokens": self.pact.allowed_tokens,
                "ttl_hours": self.pact.ttl_hours,
                "cooldown_seconds": self.pact.cooldown_seconds
            },
            "security": {
                "rate_limit_max_requests": self.security.rate_limit_max_requests,
                "rate_limit_time_window": self.security.rate_limit_time_window,
                "anti_replay_expiry_hours": self.security.anti_replay_expiry_hours,
                "max_daily_spending": self.security.max_daily_spending,
                "enable_fraud_detection": self.security.enable_fraud_detection
            }
        }

# 全局配置实例
config = AppConfig()