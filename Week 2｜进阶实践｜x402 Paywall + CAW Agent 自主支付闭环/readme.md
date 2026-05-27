# 📁 项目结构
##x402 Paywall + CAW Agent/
### ├── server/                    # 服务端 (Python/FastAPI)
### │   ├── main.py               # x402 Paywall 主服务
### │   ├── onchain_verifier.py   # 链上交易验证器
### │   ├── security.py           # 安全防护模块
### │   └── requirements.txt      # Python 依赖
### ├── client/                    # 消费端 (Node.js)
### │   ├── agent.js              # AI Agent 核心逻辑
### │   ├── package.json          # Node.js 依赖
### │   └── test.js               # 测试脚本
### ├── config.py                  # 全局配置
### ├── .env.example              # 环境变量模板
### └── start_server.py           # 服务器启动脚本
## 🚀 核心功能实现
### 1. 服务端 x402 Paywall (server/main.py)
- HTTP 402 响应 ：自动返回支付元数据（金额、代币、目标地址、链ID）
- 交易验证 ：验证链上支付凭证
- 防重放攻击 ：标记已消费的交易哈希
- API 文档 ：访问 http://localhost:8000/docs 查看
### 2. 消费端 Agent (client/agent.js)
- Cobo CAW Pact 管理器 ：执行受限支付
  - 单次支付限额检查
  - 每日预算控制
  - 目标地址白名单
  - 冷却时间机制
- 信誉度追踪器 ：监控数据提供商可靠性
- 定时任务 ：每5分钟自动获取数据
### 3. 安全防护 (server/security.py)
- 速率限制 ：防止 API 滥用
- 双花攻击防护 ：检测重复支付
- 欺诈检测 ：分析支付模式
- Nonce 管理 ：防止交易重放
- 审计日志 ：记录所有安全事件
### 4. 链上验证 (server/onchain_verifier.py)
- 交易状态监控 ：实时跟踪交易确认
- 超时处理 ：自动处理 Pending 状态交易
- 防重放保护 ：清理过期哈希记录
## 📋 启动步骤
### 1. 启动服务器
### 2. 启动 Agent
### 3. 运行测试
```
cd client
npm test
```
## 🔐 Pact 策略配置
在 config.py 或 .env 中配置：

- max_fee_per_task ：单次最大支付金额 (默认 1.0 USDT)
- daily_budget ：每日总预算 (默认 50.0 USDT)
- allowed_destinations ：允许的支付目标地址白名单
- cooldown_seconds ：支付冷却时间 (默认 5 秒)
## ⚠️ 生产环境注意事项
1. 替换模拟验证 ： onchain_verifier.py 中的 verify_onchain_settlement 需要接入真实的区块链节点 API
2. 配置 Cobo CAW ：填入真实的 API Key 和钱包 ID
3. 启用 HTTPS ：生产环境必须使用 HTTPS
4. 数据库持久化 ：将消费记录和信誉度存储到数据库
5. 监控告警 ：集成 Slack/Telegram 告警
