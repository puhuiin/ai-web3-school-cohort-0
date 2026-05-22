DeFi 收益优化助手
1. 这个助手/Workflow 要解决什么问题？
Web3 用户在寻找最佳 DeFi 收益时，面临信息碎片化、操作繁琐以及钓鱼链接泛滥的问题。本助手旨在帮用户自动化搜索、比较收益率（APY），并安全地构建交易步骤，但绝不触碰用户资产。它充当一个“理财顾问和文秘”，而用户保留最终的“签字权”。

2. 工作流概览 (AI vs Web3 工具)
用户输入： 用户的需求、可用资金、所在网络以及风险偏好。

AI 做什么：

调用 API（如 DefiLlama）获取最新 APY 数据。

规划最优资金路径（如：跨链 -> 兑换 -> 质押）。

生成可读的操作草稿和安全的官方前端链接。

（进阶）为支持的钱包构建未签名的交易参数 (Transaction Calldata)。

Web3 工具： 区块链浏览器（如 Etherscan）、DeFi 协议合约（如 Aave, Uniswap）、用户自己的 Web3 钱包（如 MetaMask / Rabby）。

3. 输入和输出示例
用户输入：

“我在 Arbitrum 上有 2000 USDC，想找一个无常损失风险低的地方赚取收益，步骤越少越好。”

AI 输出：

分析结果： 建议将 USDC 存入 Arbitrum 上的 Aave V3。当前存款 APY 为 4.5%，且为单币质押，无无常损失风险。
操作步骤：

授权 (Approve)： 允许 Aave 合约使用你的 USDC。

存款 (Supply)： 将 2000 USDC 存入 Aave。
安全链接： [Aave 官方 Arbitrum 市场链接]
交易参数 (供高级钱包使用)： [生成的待签名 Calldata 字符串，to: Aave Pool Contract...]

4. 人工确认点 (🛑 核心受限边界)
在整个 Workflow 中，以下步骤必须由人工确认，AI 被物理和逻辑隔离，无法代劳：

钱包连接： 决定使用哪个钱包地址进行连接。

Approve 授权签名： 在钱包弹窗中，人工审查并确认授权给 Aave 合约的 USDC 额度（建议按需授权，而非无限授权）。

交易签名广播： 在钱包弹窗中，人工审查 Gas 费、接收方合约地址，并点击“确认”进行私钥签名。

5. 风险和限制
AI 幻觉风险 (合约地址伪造)： AI 可能会因为训练数据的偏差，生成错误的、甚至是黑客部署的仿冒智能合约地址。这需要用户在签名时核对地址。

API 数据滞后导致交易失败： AI 获取的链上状态（如流动性池深度、滑点、Gas 费）可能存在延迟。如果池子已被掏空，AI 生成的交易可能会在链上执行失败（Reverted）。

盲签风险 (Blind Signing)： 尽管 AI 准备了操作说明，如果用户过度依赖 AI，可能在钱包弹窗时不再仔细检查交易参数，从而违背了“人工最后把关”的初衷。

6. 如何验证执行结果
链上验证： 用户将签名后的交易哈希 (TxHash) 输入给 AI，AI 调用 RPC 或浏览器 API 检查交易状态（Success/Fail）。

链下验证： 用户打开 DeBank 或 Zapper 等 Web3 资产看板，查看对应地址下是否成功显示了 Aave 的存款头寸 (aUSDC)。

sequenceDiagram
    participant U as 用户 (User)
    participant A as AI 助手 (Restricted Agent)
    participant W as Web3 钱包 (MetaMask)
    participant C as 链上智能合约

    U->>A: 1. 输入资金量、网络和需求 (例如：Arbitrum 质押 USDC)
    A->>A: 2. 规划策略，获取 APY 数据
    A->>U: 3. 输出策略说明、安全链接及待签名交易参数
    
    Note over U,W: 🛑 人工确认边界：AI 职责结束，人工接管
    
    U->>W: 4. 打开钱包，核对 AI 提供的合约地址和参数
    W->>U: 5. 弹窗请求签名 (Approve & 交易)
    U->>W: 6. 确认并使用私钥签名
    W->>C: 7. 广播交易到区块链
    C-->>U: 8. 返回交易哈希 (TxHash)
    
    U->>A: 9. 提供 TxHash 让 AI 检查
    A->>A: 10. 通过 RPC 查询交易状态
    A->>U: 11. 返回验证结果 (成功/失败) 及后续监控建议
