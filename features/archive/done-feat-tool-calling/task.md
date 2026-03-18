# feat-tool-calling: 任务分解

## 阶段 1: SKILL.md 解析器 (VP1)

### 1.1 定义数据模型
- [ ] 创建 `SkillFrontmatter` Pydantic 模型
- [ ] 创建 `OpenClawMetadata` 嵌套模型
- [ ] 创建 `Skill` 完整模型（包含 frontmatter + content）

### 1.2 实现解析器
- [ ] 创建 `skills/parser.py`
- [ ] 实现 `parse_skill_md(file_path) -> Skill`
- [ ] 实现 YAML frontmatter 提取
- [ ] 实现 Markdown 内容保留

### 1.3 实现依赖检查
- [ ] 实现 `check_bin_dependency(bin_name) -> bool`
- [ ] 实现 `check_env_dependency(env_var) -> bool`
- [ ] 实现 `check_skill_eligibility(skill) -> bool`

### 1.4 实现 Skill Loader 重构
- [ ] 重构 `skills/loader.py` 支持 SKILL.md
- [ ] 实现多目录加载（bundled/managed/workspace）
- [ ] 实现优先级合并逻辑
- [ ] 添加单元测试

---

## 阶段 2: Tool Definition 生成 (VP2)

### 2.1 参数 Schema 推断
- [ ] 创建 `skills/converter.py`
- [ ] 实现 `infer_parameters_from_skill(skill) -> dict`
- [ ] 从 Markdown 命令中推断参数（如 `{location}`）
- [ ] 支持手动定义参数（metadata.openclaw.parameters）

### 2.2 Tool Definition 生成
- [ ] 实现 `skill_to_tool_definition(skill) -> dict`
- [ ] 生成 OpenAI 兼容的 JSON Schema
- [ ] 实现 `skills_to_tools(skills) -> list[dict]`

### 2.3 测试验证
- [ ] 验证生成的 schema 符合 litellm 要求
- [ ] 添加单元测试

---

## 阶段 3: Tool Calling 执行 (VP3)

### 3.1 Tool 执行器
- [ ] 创建 `skills/executor.py`
- [ ] 实现 `ToolExecutor` 类
- [ ] 实现 `execute_tool_call(tool_call) -> str`
- [ ] 实现安全命令执行（subprocess）
- [ ] 实现超时控制
- [ ] 实现输出捕获

### 3.2 集成到 AgentLoop
- [ ] 创建 `agent/tool_loop.py`
- [ ] 修改 `AgentLoop.process()` 支持 tool calling
- [ ] 实现 tool results 添加到 history
- [ ] 实现循环调用直到完成

### 3.3 错误处理
- [ ] 实现命令执行错误捕获
- [ ] 实现有意义的错误消息
- [ ] 实现重试逻辑（可选）

### 3.4 集成测试
- [ ] 测试完整 tool calling 流程
- [ ] 测试错误场景
- [ ] 测试超时场景

---

## 阶段 4: 文档和测试

### 4.1 单元测试
- [ ] `test_skill_parser.py`
- [ ] `test_skill_converter.py`
- [ ] `test_tool_executor.py`
- [ ] `test_tool_loop.py`

### 4.2 集成测试
- [ ] 测试真实 LLM tool calling（mock 或真实 API）
- [ ] 测试多轮 tool calling 对话

### 4.3 文档
- [ ] 更新 CLAUDE.md 添加 tool calling 说明
- [ ] 创建 skills 开发指南
- [ ] 添加使用示例

---

## 依赖关系

```
1.1 → 1.2 → 1.3 → 1.4
                  ↓
2.1 → 2.2 → 2.3
            ↓
3.1 → 3.2 → 3.3 → 3.4
                  ↓
            4.1 → 4.2 → 4.3
```

## 预估工时

| 阶段 | 预估 |
|------|------|
| 阶段 1 | 2-3h |
| 阶段 2 | 1-2h |
| 阶段 3 | 3-4h |
| 阶段 4 | 2-3h |
| **总计** | **8-12h** |
