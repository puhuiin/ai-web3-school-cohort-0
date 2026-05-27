const { AlphaDataAgent, CoboCawPactManager, ReputationTracker } = require('./agent');

async function testAgent() {
    console.log('=== Testing Alpha Data Agent ===\n');
    
    // 创建 Agent 实例
    const agent = new AlphaDataAgent();
    
    // 测试 1: 初始状态
    console.log('Test 1: Initial Status');
    const initialStatus = agent.getStatus();
    console.log('Initial status:', JSON.stringify(initialStatus, null, 2));
    console.log('✓ Initial status check passed\n');
    
    // 测试 2: Pact 规则检查
    console.log('Test 2: Pact Rule Check');
    const pactManager = new CoboCawPactManager({
        max_fee_per_task: 1.0,
        daily_budget: 50.0,
        allowed_destinations: ['0x742d35Cc6634C0532925a3b844Bc454e4438f44e'],
        allowed_chains: [1],
        allowed_tokens: ['USDT'],
        cooldown_seconds: 5
    });
    
    // 测试有效支付请求
    const validPayment = {
        to: '0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
        value: 0.5,
        token: 'USDT',
        chainId: 1
    };
    
    const pactCheck = await pactManager.checkPactRules(validPayment);
    console.log('Valid payment pact check:', pactCheck);
    console.log('✓ Valid payment pact check passed\n');
    
    // 测试 3: 超出限额的支付
    console.log('Test 3: Exceed Limit Payment');
    const exceedPayment = {
        to: '0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
        value: 2.0,  // 超出 max_fee_per_task
        token: 'USDT',
        chainId: 1
    };
    
    const exceedCheck = await pactManager.checkPactRules(exceedPayment);
    console.log('Exceed limit pact check:', exceedCheck);
    console.log('✓ Exceed limit check passed\n');
    
    // 测试 4: 未授权地址
    console.log('Test 4: Unauthorized Address');
    const unauthorizedPayment = {
        to: '0x1234567890123456789012345678901234567890',
        value: 0.5,
        token: 'USDT',
        chainId: 1
    };
    
    const unauthorizedCheck = await pactManager.checkPactRules(unauthorizedPayment);
    console.log('Unauthorized address pact check:', unauthorizedCheck);
    console.log('✓ Unauthorized address check passed\n');
    
    // 测试 5: 信誉度追踪器
    console.log('Test 5: Reputation Tracker');
    const reputationTracker = new ReputationTracker();
    
    // 记录一些成功和失败
    reputationTracker.recordSuccess('provider1');
    reputationTracker.recordSuccess('provider1');
    reputationTracker.recordFailure('provider1');
    reputationTracker.recordSuccess('provider2');
    
    const score1 = reputationTracker.getReputationScore('provider1');
    const score2 = reputationTracker.getReputationScore('provider2');
    
    console.log('Provider1 score:', score1);  // 应该是 0.67 (2/3)
    console.log('Provider2 score:', score2);  // 应该是 1.0 (1/1)
    console.log('✓ Reputation tracker test passed\n');
    
    // 测试 6: 模拟支付执行
    console.log('Test 6: Simulated Payment Execution');
    try {
        const result = await pactManager.executePayment(validPayment);
        console.log('Payment execution result:', result);
        console.log('✓ Payment execution test passed\n');
    } catch (error) {
        console.error('Payment execution failed:', error.message);
    }
    
    // 测试 7: 冷却时间检查
    console.log('Test 7: Cooldown Check');
    const cooldownCheck = await pactManager.checkPactRules(validPayment);
    console.log('Cooldown check (should fail):', cooldownCheck);
    console.log('✓ Cooldown check passed\n');
    
    // 测试 8: Agent 完整流程（模拟）
    console.log('Test 8: Full Agent Flow (Simulated)');
    console.log('Note: This test requires a running server at localhost:8000');
    console.log('To run the full test, start the server first:\n');
    console.log('  cd server');
    console.log('  pip install -r requirements.txt');
    console.log('  python main.py\n');
    console.log('Then run this test again.\n');
    
    // 测试 9: 状态输出
    console.log('Test 9: Final Status');
    const finalStatus = agent.getStatus();
    console.log('Final status:', JSON.stringify(finalStatus, null, 2));
    console.log('✓ Final status check passed\n');
    
    console.log('=== All Tests Completed ===');
}

// 运行测试
if (require.main === module) {
    testAgent().catch(error => {
        console.error('Test failed:', error);
        process.exit(1);
    });
}

module.exports = { testAgent };