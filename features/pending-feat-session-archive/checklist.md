# 完成检查清单

## 代码实现

### 会话模块
- [ ] `anyclaw/session/__init__.py` 已创建
- [ ] `anyclaw/session/records.py` 已创建
- [ ] `anyclaw/session/manager.py` 已创建
- [ ] `anyclaw/session/project.py` 已创建

### 记录类型
- [ ] `SessionRecord` 基类已实现
- [ ] `SessionStart` 已实现
- [ ] `SessionEnd` 已实现
- [ ] `UserMessage` 已实现
- [ ] `AssistantMessage` 已实现
- [ ] `ToolCall` 已实现
- [ ] `ToolResult` 已实现
- [ ] `SkillCall` 已实现
- [ ] `SkillResult` 已实现
- [ ] `Thinking` 已实现
- [ ] `ErrorRecord` 已实现

### 会话管理器
- [ ] `SessionManager` 类已实现
- [ ] Git root 识别已实现
- [ ] 项目目录命名已实现
- [ ] 按日期归档已实现
- [ ] JSONL 追加写入已实现

### Agent 集成
- [ ] `ConversationHistory` 已改造
- [ ] `AgentLoop` 已集成记录
- [ ] CLI Channel 已集成
- [ ] IM Channel 已集成（如有）

### CLI 命令
- [ ] `anyclaw session list` 已实现
- [ ] `anyclaw session show` 已实现
- [ ] `anyclaw session search` 已实现
- [ ] `anyclaw session export` 已实现
- [ ] `anyclaw session clean` 已实现

## 测试

### 单元测试
- [ ] `tests/test_session_records.py` 已创建
- [ ] `tests/test_session_manager.py` 已创建
- [ ] `tests/test_session_project.py` 已创建
- [ ] `tests/test_session_integration.py` 已创建

### 测试覆盖
- [ ] 记录序列化测试通过
- [ ] 会话开始/结束测试通过
- [ ] 项目识别测试通过
- [ ] Git 项目隔离测试通过
- [ ] 非 Git 项目隔离测试通过
- [ ] Tool 调用记录测试通过
- [ ] Skill 调用记录测试通过
- [ ] 测试覆盖率 > 80%

## 功能验证

### 基础功能
- [ ] 会话自动保存到 `~/.anyclaw/sessions/`
- [ ] JSONL 格式正确（每行一个 JSON）
- [ ] 日期目录正确创建

### 项目隔离
- [ ] Git 项目按 root 隔离
- [ ] 子目录归属同一项目
- [ ] 非 Git 项目按 cwd 隔离
- [ ] Channel 按类型+ID 隔离

### 记录完整性
- [ ] 用户消息正确记录
- [ ] 助手消息正确记录
- [ ] Tool 调用和结果成对记录
- [ ] Skill 调用和结果成对记录
- [ ] 时间戳正确

### CLI 命令
- [ ] `anyclaw session list` 正常工作
- [ ] `anyclaw session show {id}` 正常工作
- [ ] `anyclaw session search "关键词"` 正常工作
- [ ] `anyclaw session export {id} -o out.md` 正常工作

## 文档

- [ ] 代码有详细注释
- [ ] CLI 命令有帮助文档
- [ ] 记录类型有 docstring

## 验收命令

```bash
# 运行所有测试
cd anyclaw && poetry run pytest tests/test_session*.py -v

# 验证会话文件创建
ls ~/.anyclaw/sessions/cli/

# 验证 CLI 命令
poetry run anyclaw session list
poetry run anyclaw session show {session-id}
poetry run anyclaw session search "test"
```

## 性能检查

- [ ] 单次追加写入 < 10ms
- [ ] 会话列表加载 < 1s
- [ ] 搜索 1000+ 会话 < 3s
