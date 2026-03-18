# feat-context-compression: 任务分解

## 阶段 1: 对话摘要压缩 (VP1)

### 1.1 创建压缩器基础
- [ ] 创建 `agent/compressor.py`
- [ ] 实现 `ConversationCompressor` 类
- [ ] 实现 `compress()` 主方法
- [ ] 实现 `_separate_messages()` 分离消息

### 1.2 实现 LLM 摘要
- [ ] 实现 `_generate_summary()` - 调用 LLM 生成摘要
- [ ] 设计摘要 prompt 模板
- [ ] 实现摘要格式化

### 1.3 实现简单截断
- [ ] 实现 `_truncate()` - 简单截断策略
- [ ] 作为 LLM 失败时的回退

### 1.4 集成到 ConversationHistory
- [ ] 修改 `ConversationHistory` 添加压缩方法
- [ ] 实现自动压缩触发
- [ ] 添加压缩统计

### 1.5 单元测试
- [ ] 测试摘要生成
- [ ] 测试截断策略
- [ ] 测试自动触发
- [ ] 测试回退逻辑

---

## 阶段 2: 滑动窗口策略 (VP2)

### 2.1 创建滑动窗口
- [ ] 创建 `agent/sliding_window.py`
- [ ] 实现 `SlidingWindow` 类
- [ ] 实现 `apply()` 主方法
- [ ] 实现 `_is_protected()` 保护判断

### 2.2 消息保护
- [ ] 实现系统消息保护
- [ ] 实现标记消息保护
- [ ] 实现自定义保护规则

### 2.3 动态窗口
- [ ] 结合 token 限制动态调整窗口
- [ ] 实现窗口大小自适应

### 2.4 单元测试
- [ ] 测试基本滑动窗口
- [ ] 测试消息保护
- [ ] 测试动态调整

---

## 阶段 3: 长对话处理 (VP3)

### 3.1 自动管理
- [ ] 实现自动压缩触发
- [ ] 实现压缩+窗口组合策略
- [ ] 添加用户通知

### 3.2 检查点功能
- [ ] 创建 `agent/checkpoint.py`
- [ ] 实现 `save_checkpoint()`
- [ ] 实现 `load_checkpoint()`
- [ ] 实现 `list_checkpoints()`
- [ ] 实现 `delete_checkpoint()`

### 3.3 导出功能
- [ ] 实现对话摘要导出
- [ ] 支持 Markdown 格式
- [ ] 支持 JSON 格式

### 3.4 单元测试
- [ ] 测试自动管理
- [ ] 测试检查点
- [ ] 测试导出

---

## 阶段 4: CLI 命令

### 4.1 compress 命令
- [ ] 创建 `cli/compress.py`
- [ ] 实现 `compress` 命令
- [ ] 实现 `--preview` 选项
- [ ] 实现 `--strategy` 选项

### 4.2 window 命令
- [ ] 实现 `window set` 子命令
- [ ] 实现 `window apply` 子命令
- [ ] 实现 `window show` 子命令

### 4.3 checkpoint 命令
- [ ] 实现 `checkpoint create` 子命令
- [ ] 实现 `checkpoint list` 子命令
- [ ] 实现 `checkpoint restore` 子命令
- [ ] 实现 `checkpoint delete` 子命令

### 4.4 集成
- [ ] 注册命令到主 CLI
- [ ] 添加单元测试

---

## 阶段 5: 配置和文档

### 5.1 配置扩展
- [ ] 添加压缩相关配置
- [ ] 添加窗口相关配置
- [ ] 更新 `.env.example`

### 5.2 文档
- [ ] 更新 CLAUDE.md
- [ ] 创建上下文管理指南
- [ ] 添加使用示例

---

## 依赖关系

```
feat-token-counter (依赖)
        ↓
1.1 → 1.2 → 1.3 → 1.4 → 1.5
                  ↓
2.1 → 2.2 → 2.3 → 2.4
                  ↓
3.1 → 3.2 → 3.3 → 3.4
                  ↓
4.1 → 4.2 → 4.3 → 4.4
                  ↓
            5.1 → 5.2
```

## 预估工时

| 阶段 | 预估 |
|------|------|
| 阶段 1 | 2-3h |
| 阶段 2 | 1-2h |
| 阶段 3 | 2-3h |
| 阶段 4 | 1-2h |
| 阶段 5 | 1h |
| **总计** | **7-11h** |

## 关键决策

### Q1: 摘要使用哪个模型？

**选项**：
1. 使用当前对话模型
2. 使用单独的小模型（如 gpt-3.5-turbo）
3. 可配置

**决策**: 可配置，默认使用当前模型。

### Q2: 检查点存储位置？

**选项**：
1. `~/.anyclaw/checkpoints/`
2. 工作目录 `checkpoints/`
3. 可配置

**决策**: 默认 `~/.anyclaw/checkpoints/`，可配置。
