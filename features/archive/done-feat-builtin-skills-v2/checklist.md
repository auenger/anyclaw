# 完成检查清单：内置技能扩展 V2

## 实现检查

### code_exec 技能
- [ ] 创建 `anyclaw/skills/builtin/code_exec/skill.py`
- [ ] 支持 Python 代码执行
- [ ] 支持 JavaScript (Node.js) 代码执行
- [ ] 支持 Bash 命令执行
- [ ] 实现超时控制
- [ ] 错误处理和友好提示

### process 技能
- [ ] 创建 `anyclaw/skills/builtin/process/skill.py`
- [ ] 实现 start 动作（启动后台进程）
- [ ] 实现 status 动作（查询状态）
- [ ] 实现 log 动作（获取输出）
- [ ] 实现 kill 动作（终止进程）
- [ ] 实现 list 动作（列出进程）
- [ ] session_id 生成和管理

### text 技能
- [ ] 创建 `anyclaw/skills/builtin/text/skill.py`
- [ ] 实现 stats 动作（统计信息）
- [ ] 实现 extract 动作（正则提取）
- [ ] 实现 replace 动作（搜索替换）
- [ ] 实现 format 动作（格式转换）

### system 技能
- [ ] 创建 `anyclaw/skills/builtin/system/skill.py`
- [ ] 实现 info 动作（系统信息）
- [ ] 实现 env 动作（环境变量）
- [ ] 实现 which 动作（命令检查）
- [ ] 敏感环境变量过滤

### data 技能
- [ ] 创建 `anyclaw/skills/builtin/data/skill.py`
- [ ] 实现 parse 动作（解析数据）
- [ ] 实现 query 动作（JSONPath 查询）
- [ ] 实现 convert 动作（格式转换）
- [ ] 实现 validate 动作（Schema 验证）

## 测试检查

- [ ] 创建 `tests/test_skills_extended.py`
- [ ] code_exec 测试通过
- [ ] process 测试通过
- [ ] text 测试通过
- [ ] system 测试通过
- [ ] data 测试通过
- [ ] 所有现有测试仍然通过

## 文档检查

- [ ] 更新 CLAUDE.md 技能列表
- [ ] 代码注释清晰
- [ ] 技能文档字符串完整

## 质量检查

- [ ] 代码格式化（black）
- [ ] 代码检查通过（ruff）
- [ ] 类型提示完整
- [ ] 无硬编码敏感信息

## 验收检查

- [ ] 可以执行 Python 代码并获取结果
- [ ] 可以执行 JavaScript 代码并获取结果
- [ ] 可以启动和管理后台进程
- [ ] 可以处理文本（统计、提取、替换）
- [ ] 可以获取系统信息
- [ ] 可以处理 JSON/YAML 数据
