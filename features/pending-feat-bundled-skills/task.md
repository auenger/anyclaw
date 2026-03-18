# feat-bundled-skills: 任务分解

## 阶段 1: 准备工作

### 1.1 创建目录结构
- [ ] 创建 `anyclaw/skills/builtin/` 目录
- [ ] 设计 skill 目录命名规范
- [ ] 创建 README 说明文件

### 1.2 等待依赖
- [ ] 等待 `feat-tool-calling` 完成
- [ ] 验证 SKILL.md 解析器可用
- [ ] 验证 Tool Calling 流程可用

---

## 阶段 2: 移植基础 Skills (VP1)

### 2.1 移植 weather skill
- [ ] 从 OpenClaw 复制 `skills/weather/SKILL.md`
- [ ] 验证 frontmatter 格式
- [ ] 测试命令执行
- [ ] 添加测试用例

### 2.2 转换 time skill
- [ ] 分析现有 `skills/builtin/time/skill.py`
- [ ] 转换为 SKILL.md 格式
- [ ] 或保留 Python 执行支持
- [ ] 测试功能

### 2.3 转换 echo skill
- [ ] 分析现有 `skills/builtin/echo/skill.py`
- [ ] 转换为 SKILL.md 格式
- [ ] 测试功能

### 2.4 移植 summarize skill (可选)
- [ ] 从 OpenClaw 复制 `skills/summarize/SKILL.md`
- [ ] 记录依赖要求 (summarize CLI)
- [ ] 测试（如有 CLI）

---

## 阶段 3: 移植开发 Skills (VP2)

### 3.1 移植 github skill
- [ ] 从 OpenClaw 复制 `skills/github/SKILL.md`
- [ ] 验证依赖声明 (gh CLI)
- [ ] 测试命令示例
- [ ] 添加测试用例

### 3.2 移植 gh-issues skill
- [ ] 从 OpenClaw 复制 `skills/gh-issues/SKILL.md`
- [ ] 验证依赖声明
- [ ] 测试命令示例

### 3.3 其他 skills (按需)
- [ ] 评估其他 OpenClaw skills 的价值
- [ ] 选择性移植

---

## 阶段 4: CLI 管理命令 (VP3)

### 4.1 skills list 命令
- [ ] 创建 `anyclaw/cli/skills.py`
- [ ] 实现 `list` 子命令
- [ ] 显示 skill 名称、描述、状态
- [ ] 支持 `--all` 和 `--available` 过滤

### 4.2 skills show 命令
- [ ] 实现 `show` 子命令
- [ ] 显示 skill 详细信息
- [ ] 显示依赖要求
- [ ] 显示使用示例

### 4.3 skills doctor 命令
- [ ] 实现 `doctor` 子命令
- [ ] 检查所有 skills 依赖
- [ ] 报告不可用 skills
- [ ] 提供修复建议

### 4.4 集成到主 CLI
- [ ] 注册 skills 命令组
- [ ] 更新 `--help` 输出
- [ ] 添加单元测试

---

## 阶段 5: 测试和文档

### 5.1 集成测试
- [ ] 测试每个 skill 的 tool calling
- [ ] 测试 CLI 命令
- [ ] 测试依赖检查

### 5.2 文档
- [ ] 更新 CLAUDE.md 添加 skills 使用说明
- [ ] 创建 skills README
- [ ] 添加每个 skill 的使用示例

---

## 依赖关系

```
1.1 → 1.2 (等待 feat-tool-calling)
        ↓
2.1 → 2.2 → 2.3 → 2.4
        ↓
3.1 → 3.2 → 3.3
        ↓
4.1 → 4.2 → 4.3 → 4.4
                    ↓
              5.1 → 5.2
```

## 预估工时

| 阶段 | 预估 |
|------|------|
| 阶段 1 | 0.5h |
| 阶段 2 | 1-2h |
| 阶段 3 | 1-2h |
| 阶段 4 | 2-3h |
| 阶段 5 | 1-2h |
| **总计** | **5.5-9.5h** |

## 依赖说明

**阻塞依赖**: `feat-tool-calling` 必须先完成
- SKILL.md 解析器
- Tool Calling 执行流程
- Tool Definition 生成

**建议**: 在 `feat-tool-calling` 完成后再启动此特性。
