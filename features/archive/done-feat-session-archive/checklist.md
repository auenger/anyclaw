# 完成检查清单

## 代码实现

### 会话模块
- [x] `anyclaw/session/__init__.py` 已更新（导出新类型）
- [x] `anyclaw/session/records.py` 已创建
- [x] `anyclaw/session/manager.py` 已存在（保持兼容）
- [x] `anyclaw/session/project.py` 已创建
- [x] `anyclaw/session/archive.py` 已创建

### 记录类型
- [x] `SessionRecord` 基类已实现
- [x] `SessionStart` 已实现
- [x] `SessionEnd` 已实现
- [x] `UserMessage` 已实现
- [x] `AssistantMessage` 已实现
- [x] `ToolCall` 已实现
- [x] `ToolResult` 已实现
- [x] `SkillCall` 已实现
- [x] `SkillResult` 已实现
- [x] `Thinking` 已实现
- [x] `ErrorRecord` 已实现

### 会话归档管理器
- [x] `SessionArchiveManager` 类已实现
- [x] Git root 识别已实现
- [x] 项目目录命名已实现
- [x] 按日期归档已实现
- [x] JSONL 追加写入已实现

### Agent 集成
- [x] `AgentLoop` 已集成 SessionArchiveManager
- [x] CLI Channel 已集成（通过 chat 命令）
- [x] 支持 --no-archive 参数禁用归档

### CLI 命令
- [x] `anyclaw session list` 已实现
- [x] `anyclaw session show` 已实现
- [x] `anyclaw session search` 已实现
- [x] `anyclaw session export` 已实现
- [x] `anyclaw session clean` 已实现
- [x] `anyclaw session path` 已实现

## 测试

### 单元测试
- [x] `tests/test_session_records.py` 已创建
- [x] `tests/test_session_archive.py` 已创建
- [x] `tests/test_session_project.py` 已创建

### 测试覆盖
- [x] 记录序列化测试通过
- [x] 会话开始/结束测试通过
- [x] 项目识别测试通过
- [x] Git 项目隔离测试通过
- [x] 非 Git 项目隔离测试通过
- [x] Tool 调用记录测试通过
- [x] Skill 调用记录测试通过
- [x] 新代码测试覆盖率 > 90%

## 功能验证

### 基础功能
- [x] 会话自动保存到 `~/.anyclaw/sessions/`
- [x] JSONL 格式正确（每行一个 JSON）
- [x] 日期目录正确创建

### 项目隔离
- [x] Git 项目按 root 隔离
- [x] 子目录归属同一项目
- [x] 非 Git 项目按 cwd 隔离
- [x] Channel 按类型+ID 隔离

### 记录完整性
- [x] 用户消息正确记录
- [x] 助手消息正确记录
- [x] Tool 调用和结果成对记录
- [x] Skill 调用和结果成对记录
- [x] 时间戳正确

### CLI 命令
- [x] `anyclaw session list` 正常工作
- [x] `anyclaw session show {id}` 正常工作
- [x] `anyclaw session search "关键词"` 正常工作
- [x] `anyclaw session export {id} -o out.md` 正常工作

## 文档

- [x] 代码有详细注释
- [x] CLI 命令有帮助文档
- [x] 记录类型有 docstring

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

- [x] 单次追加写入 < 10ms
- [x] 会话列表加载 < 1s
- [x] 搜索 1000+ 会话 < 3s
