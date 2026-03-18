# feat-context-compression: 完成检查清单

## VP1: 对话摘要压缩

### 压缩器基础
- [ ] `ConversationCompressor` 类已实现
- [ ] `compress()` 方法正常工作
- [ ] 消息分离正确

### LLM 摘要
- [ ] `_generate_summary()` 正常工作
- [ ] 摘要 prompt 设计合理
- [ ] 摘要格式正确

### 简单截断
- [ ] `_truncate()` 正常工作
- [ ] 作为回退正常

### 集成
- [ ] `ConversationHistory` 已修改
- [ ] 自动压缩触发正常
- [ ] 压缩统计正确

### 单元测试
- [ ] test_compressor.py 通过
- [ ] 覆盖率 > 80%

---

## VP2: 滑动窗口策略

### 滑动窗口基础
- [ ] `SlidingWindow` 类已实现
- [ ] `apply()` 方法正常工作
- [ ] 窗口大小正确

### 消息保护
- [ ] 系统消息受保护
- [ ] 标记消息受保护
- [ ] 保护规则正确

### 动态窗口
- [ ] 动态调整正常
- [ ] token 限制集成正常

### 单元测试
- [ ] test_sliding_window.py 通过
- [ ] 覆盖率 > 80%

---

## VP3: 长对话处理

### 自动管理
- [ ] 自动压缩触发正常
- [ ] 组合策略正常
- [ ] 用户通知正确

### 检查点功能
- [ ] `save_checkpoint()` 正常
- [ ] `load_checkpoint()` 正常
- [ ] `list_checkpoints()` 正常
- [ ] `delete_checkpoint()` 正常

### 导出功能
- [ ] Markdown 导出正常
- [ ] JSON 导出正常
- [ ] 摘要完整

### 单元测试
- [ ] test_checkpoint.py 通过
- [ ] 覆盖率 > 80%

---

## CLI 命令

### compress 命令
- [ ] `anyclaw compress` 正常
- [ ] `--preview` 选项正常
- [ ] `--strategy` 选项正常

### window 命令
- [ ] `anyclaw window set` 正常
- [ ] `anyclaw window apply` 正常
- [ ] `anyclaw window show` 正常

### checkpoint 命令
- [ ] `anyclaw checkpoint create` 正常
- [ ] `anyclaw checkpoint list` 正常
- [ ] `anyclaw checkpoint restore` 正常
- [ ] `anyclaw checkpoint delete` 正常

### 集成
- [ ] 命令已注册
- [ ] 单元测试通过

---

## 质量标准

### 代码质量
- [ ] 通过 Black 格式化
- [ ] 通过 Ruff 检查
- [ ] 类型注解完整

### 测试
- [ ] 单元测试覆盖率 > 80%
- [ ] 集成测试通过
- [ ] 边界情况有测试

### 文档
- [ ] CLAUDE.md 已更新
- [ ] 上下文管理指南存在

---

## 验收测试

### 手动测试场景

- [ ] **场景 1**: 手动压缩对话
  ```bash
  anyclaw compress --preview
  ```
  预期: 显示压缩预览，列出将被压缩的消息

- [ ] **场景 2**: 自动压缩触发
  ```bash
  # 设置低阈值
  export COMPRESS_THRESHOLD=5
  anyclaw chat
  # 进行 6 轮以上对话
  ```
  预期: 自动触发压缩，显示通知

- [ ] **场景 3**: 滑动窗口
  ```bash
  anyclaw window set 10
  anyclaw window apply
  ```
  预期: 保留最近 10 条消息

- [ ] **场景 4**: 检查点
  ```bash
  anyclaw checkpoint create before-refactor
  # 进行一些对话
  anyclaw checkpoint restore before-refactor
  ```
  预期: 恢复到检查点状态

- [ ] **场景 5**: 导出摘要
  ```bash
  anyclaw export summary --format markdown
  ```
  预期: 生成对话摘要文件

---

## 完成条件

- [ ] 所有 VP1 检查项完成
- [ ] 所有 VP2 检查项完成
- [ ] 所有 VP3 检查项完成
- [ ] CLI 命令完成
- [ ] 所有质量标准满足
- [ ] 所有验收测试通过
- [ ] 代码已提交
