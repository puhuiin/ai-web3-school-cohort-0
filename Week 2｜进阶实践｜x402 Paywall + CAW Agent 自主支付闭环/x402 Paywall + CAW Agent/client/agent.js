const axios = require('axios');
const { ethers } = require('ethers');
const winston = require('winston');
const cron = require('node-cron');

// 配置日志
const logger = winston.createLogger({
    level: 'info',
    format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json()
    ),
    transports: [
        new winston.transports.File({ filename: 'agent-error.log', level: 'error' }),
        new winston.transports.File({ filename: 'agent.log' }),
        new winston.transports.Console({
            format: winston.format.combine(
                winston.format.colorize(),
                winston.format.simple()
            )
        })
    ]
});

// Cobo CAW 配置
const COBO_CAW_CONFIG = {
    apiKey: process.env.COBO_API_KEY || 'your-cobo-api-key',
    apiSecret: process.env.COBO_API_SECRET || 'your-cobo-api-secret',
    baseUrl: 'https://api.cobo.com/v2',
    walletId: process.env.COBO_WALLET_ID || 'your-wallet-id'
};

// Pact 策略配置
const PACT_CONFIG = {
    max_fee_per_task: 1.0,  // 单次最大支付金额 (USDT)
    daily_budget: 50.0,     // 每日总预算 (USDT)
    allowed_destinations: [
        '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'  // 允许的支付目标地址
    ],
    allowed_chains: [1],    // 允许的链ID (Ethereum Mainnet)
    allowed_tokens: ['USDT'], // 允许的代币
    ttl_hours: 24,          // 策略有效期（小时）
    cooldown_seconds: 5     // 支付冷却时间（秒）
};

// 信誉度追踪器
class ReputationTracker {
    constructor() {
        this.providers = new Map();
    }

    recordSuccess(provider) {
        if (!this.providers.has(provider)) {
            this.providers.set(provider, { successes: 0, failures: 0, lastSuccess: null, lastFailure: null });
        }
        const record = this.providers.get(provider);
        record.successes++;
        record.lastSuccess = new Date();
        logger.info(`Reputation updated for ${provider}: success`);
    }

    recordFailure(provider) {
        if (!this.providers.has(provider)) {
            this.providers.set(provider, { successes: 0, failures: 0, lastSuccess: null, lastFailure: null });
        }
        const record = this.providers.get(provider);
        record.failures++;
        record.lastFailure = new Date();
        logger.warn(`Reputation updated for ${provider}: failure`);
    }

    getReputationScore(provider) {
        if (!this.providers.has(provider)) {
            return 0.5; // 默认中立评分
        }
        const record = this.providers.get(provider);
        const total = record.successes + record.failures;
        if (total === 0) return 0.5;
        return record.successes / total;
    }

    shouldTrustProvider(provider) {
        return this.getReputationScore(provider) > 0.3;
    }
}

// Cobo CAW Pact 管理器
class CoboCawPactManager {
    constructor(config) {
        this.config = config;
        this.dailySpent = 0;
        this.lastPaymentTime = null;
        this.paymentHistory = [];
    }

    async checkPactRules(paymentRequest) {
        const { to, value, token, chainId } = paymentRequest;
        const errors = [];

        // 检查单次支付限额
        if (value > this.config.max_fee_per_task) {
            errors.push(`Payment amount ${value} exceeds max_fee_per_task ${this.config.max_fee_per_task}`);
        }

        // 检查每日预算
        if (this.dailySpent + value > this.config.daily_budget) {
            errors.push(`Daily budget exceeded: ${this.dailySpent} + ${value} > ${this.config.daily_budget}`);
        }

        // 检查目标地址白名单
        if (!this.config.allowed_destinations.includes(to.toLowerCase())) {
            errors.push(`Destination ${to} is not in whitelist`);
        }

        // 检查链ID
        if (!this.config.allowed_chains.includes(chainId)) {
            errors.push(`Chain ID ${chainId} is not allowed`);
        }

        // 检查代币类型
        if (!this.config.allowed_tokens.includes(token)) {
            errors.push(`Token ${token} is not allowed`);
        }

        // 检查冷却时间
        if (this.lastPaymentTime) {
            const timeSinceLastPayment = (Date.now() - this.lastPaymentTime) / 1000;
            if (timeSinceLastPayment < this.config.cooldown_seconds) {
                errors.push(`Cooldown period not met: ${timeSinceLastPayment}s < ${this.config.cooldown_seconds}s`);
            }
        }

        return {
            passed: errors.length === 0,
            errors: errors
        };
    }

    async executePayment(paymentRequest) {
        const pactCheck = await this.checkPactRules(paymentRequest);
        
        if (!pactCheck.passed) {
            const error = new Error(`Pact violation: ${pactCheck.errors.join(', ')}`);
            error.code = 'PACT_VIOLATION';
            error.details = pactCheck.errors;
            throw error;
        }

        try {
            // 模拟调用 Cobo CAW API 执行支付
            // 在实际实现中，这里应该调用 Cobo CAW 的 API
            const txHash = await this.simulateCoboCawPayment(paymentRequest);
            
            // 更新每日支出
            this.dailySpent += paymentRequest.value;
            this.lastPaymentTime = Date.now();
            
            // 记录支付历史
            this.paymentHistory.push({
                ...paymentRequest,
                txHash: txHash,
                timestamp: new Date().toISOString()
            });

            logger.info(`Payment executed successfully: ${txHash}`);
            return { txHash: txHash, success: true };
        } catch (error) {
            logger.error(`Payment execution failed: ${error.message}`);
            throw error;
        }
    }

    async simulateCoboCawPayment(paymentRequest) {
        // 模拟 Cobo CAW API 调用
        // 在实际实现中，这里应该：
        // 1. 调用 Cobo CAW API 创建交易
        // 2. CAW 内部验证 Pact 规则
        // 3. CAW 自动签名并广播交易
        // 4. 返回交易哈希
        
        // 模拟网络延迟
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // 生成模拟的交易哈希
        const txHash = '0x' + Array.from({ length: 64 }, () => 
            Math.floor(Math.random() * 16).toString(16)
        ).join('');
        
        return txHash;
    }

    getDailySpent() {
        return this.dailySpent;
    }

    getPaymentHistory() {
        return this.paymentHistory;
    }
}

// 主 Agent 类
class AlphaDataAgent {
    constructor() {
        this.reputationTracker = new ReputationTracker();
        this.pactManager = new CoboCawPactManager(PACT_CONFIG);
        this.apiBaseUrl = process.env.API_BASE_URL || 'http://localhost:8000';
        this.isRunning = false;
        this.alertHandlers = [];
    }

    addAlertHandler(handler) {
        this.alertHandlers.push(handler);
    }

    async sendAlert(message, level = 'info') {
        logger[level](`Alert: ${message}`);
        for (const handler of this.alertHandlers) {
            try {
                await handler(message, level);
            } catch (error) {
                logger.error(`Alert handler failed: ${error.message}`);
            }
        }
    }

    async fetchAlphaData() {
        const apiUrl = `${this.apiBaseUrl}/api/v1/alpha-signals`;
        const provider = 'premium_alpha_provider';
        
        try {
            // 检查提供商信誉度
            if (!this.reputationTracker.shouldTrustProvider(provider)) {
                throw new Error(`Provider ${provider} has low reputation score: ${this.reputationTracker.getReputationScore(provider)}`);
            }

            // 第一步：尝试直接请求
            logger.info(`Requesting alpha data from ${apiUrl}`);
            let response;
            try {
                response = await axios.get(apiUrl);
            } catch (error) {
                if (error.response && error.response.status === 402) {
                    // 第二步：识别 HTTP 402 与 x402 支付条件
                    response = error.response;
                } else {
                    throw error;
                }
            }
            
            // 如果需要支付
            if (response.status === 402) {
                const paymentInfo = response.data.payment_info;
                const amount = paymentInfo.amount;
                const asset = paymentInfo.asset;
                const destination = paymentInfo.destination;
                const chainId = paymentInfo.chain_id;
                
                logger.info(`Detected x402 Paywall: Requires ${amount} ${asset} on Chain ${chainId}`);
                
                // 第三步：请求 Cobo CAW 执行受限支付
                const cawResponse = await this.pactManager.executePayment({
                    to: destination,
                    value: amount,
                    token: asset,
                    chainId: chainId,
                    meta: { 
                        reason: "Purchase alpha-signals API", 
                        timestamp: Date.now(),
                        provider: provider
                    }
                });
                
                const txHash = cawResponse.txHash;
                logger.info(`Pact Check Passed. Transaction signed & broadcasted. Hash: ${txHash}`);
                
                // 第四步：带上链上可审计的收据（Tx Hash）重新请求，获取交付结果
                const finalResponse = await axios.get(apiUrl, {
                    headers: { "X-Payment-Tx-Hash": txHash }
                });
                
                const result = finalResponse.data;
                logger.info("Successfully unlocked data:", result.data);
                
                // 更新提供商信誉度
                this.reputationTracker.recordSuccess(provider);
                
                return result.data;
            }
            
            // 如果不需要支付（可能是免费接口或已付款）
            this.reputationTracker.recordSuccess(provider);
            return response.data.data;
            
        } catch (error) {
            // 更新提供商信誉度
            this.reputationTracker.recordFailure(provider);
            
            if (error.code === 'PACT_VIOLATION') {
                logger.error(`CAW Policy Violation: Payment rejected by Pact guardrails: ${error.message}`);
                await this.sendAlert(`CAW Policy Violation: ${error.details.join(', ')}`, 'error');
            } else {
                logger.error(`Error fetching alpha data: ${error.message}`);
                await this.sendAlert(`Error fetching alpha data: ${error.message}`, 'error');
            }
            
            throw error;
        }
    }

    async start() {
        this.isRunning = true;
        logger.info('Alpha Data Agent started');
        
        // 设置定时任务，每5分钟获取一次数据
        cron.schedule('*/5 * * * *', async () => {
            if (!this.isRunning) return;
            
            try {
                const data = await this.fetchAlphaData();
                logger.info('Scheduled fetch completed:', data);
            } catch (error) {
                logger.error('Scheduled fetch failed:', error.message);
            }
        });
        
        // 初始获取
        try {
            const initialData = await this.fetchAlphaData();
            logger.info('Initial fetch completed:', initialData);
        } catch (error) {
            logger.error('Initial fetch failed:', error.message);
        }
    }

    stop() {
        this.isRunning = false;
        logger.info('Alpha Data Agent stopped');
    }

    getStatus() {
        return {
            isRunning: this.isRunning,
            dailySpent: this.pactManager.getDailySpent(),
            paymentHistory: this.pactManager.getPaymentHistory(),
            reputationScores: Object.fromEntries(
                Array.from(this.reputationTracker.providers.entries()).map(([key, value]) => [
                    key,
                    {
                        score: this.reputationTracker.getReputationScore(key),
                        ...value
                    }
                ])
            )
        };
    }
}

// 主程序
if (require.main === module) {
    const agent = new AlphaDataAgent();
    
    // 添加控制台告警处理器
    agent.addAlertHandler(async (message, level) => {
        console.log(`[${level.toUpperCase()}] Alert: ${message}`);
    });
    
    // 启动 Agent
    agent.start().catch(error => {
        console.error('Failed to start agent:', error);
        process.exit(1);
    });
    
    // 优雅退出
    process.on('SIGINT', () => {
        console.log('Stopping agent...');
        agent.stop();
        process.exit(0);
    });
    
    // 定期输出状态
    setInterval(() => {
        const status = agent.getStatus();
        console.log('Agent Status:', JSON.stringify(status, null, 2));
    }, 30000); // 每30秒输出一次状态
}

module.exports = { AlphaDataAgent, CoboCawPactManager, ReputationTracker };