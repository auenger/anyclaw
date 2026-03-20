# 完成检查清单：LLM 响应韧性增强

## 验收标准

### 功能验收
- [x] 空响应能够被正确检测
- [x] 空响应触发自动重试（最多配置次数）
- [x] 重试成功后返回有效响应
- [x] 达到最大重试次数时返回友好错误提示
- [x] LiteLLM 重试参数正确配置
- [x] 诊断日志正确输出（DEBUG 级别）

### 测试验收
- [x] 单元测试：空响应检测逻辑
- [x] 单元测试：重试次数限制
- [x] 单元测试：配置项读取
- [x] 单元测试：日志输出格式
- [x] 测试覆盖率 >= 80%

### 代码质量
- [x] 代码通过 ruff 检查
- [x] 代码通过 black 格式化
- [x] 无明显性能影响

## 手动测试步骤

1. 空响应恢复测试
   ```bash
   # 修改代码模拟空响应，验证重试逻辑
   GLM_API_KEY=xxx poetry run python -m anyclaw chat
   # 观察日志中的 "LLM returned empty content" 警告
   ```

2. 诊断日志测试
   ```bash
   ANYCLAW_LOG_LEVEL=debug poetry run python -m anyclaw chat
   # 执行一次对话，观察 [LLM] Response detail 日志
   ```

3. 配置项验证
   ```bash
   poetry run python -m anyclaw config show
   # 检查新增配置项是否显示
   ```

## 完成签名

- [x] 所有验收标准通过
- [x] 测试覆盖率达标（>80%）
- [x] 代码审查通过
- [x] 文档更新完成

完成时间：2026-03-21T01:15:00
完成人：dev-agent
