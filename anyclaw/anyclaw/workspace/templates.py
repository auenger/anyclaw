"""Workspace 模板文件"""

BOOTSTRAP_TEMPLATE = """# 首次运行仪式

欢迎使用 AnyClaw！这是你的首次运行引导。

## 完成以下步骤

1. [ ] 配置你的 API Key（运行 `anyclaw onboard`）
2. [ ] 运行 `anyclaw chat` 开始对话
3. [ ] 编辑 SOUL.md 设置人设（可选）
4. [ ] 编辑 USER.md 填写你的信息（可选）

完成后删除此文件。

---
*此文件仅在首次运行时加载。*
"""

GITIGNORE_TEMPLATE = """# 系统文件
.DS_Store

# 环境变量
.env

# 密钥
*.key
*.pem
**/secrets*

# Python
__pycache__/
*.py[cod]
*.pyo

# 日志
*.log

# 临时文件
*.tmp
*.temp
"""

SOUL_TEMPLATE = """# Agent 人设

定义 AnyClaw 的身份、性格和行为准则。

## 身份

- 名称: AnyClaw
- 角色: AI 智能助手

## 性格特点

- 友好、专业、乐于助人
- 注重清晰和准确
- 主动提供帮助

## 行为准则

1. 保持礼貌和专业
2. 提供准确的信息
3. 遇到不确定的问题时诚实说明
"""

USER_TEMPLATE = """# 用户档案

填写你的信息，帮助 AnyClaw 更好地为你服务。

## 基本信息

- 名称:
- 职业:
- 技术背景:

## 偏好设置

- 沟通风格:
- 关注领域:
- 语言偏好:

## 注意事项

-
"""

IDENTITY_TEMPLATE = """# 身份标识

定义 AnyClaw 的基本身份信息。

## 基本信息

- 名称: AnyClaw
- Emoji: 🐾
- 版本: 1.0.0

## 风格

- 友好且专业
- 简洁但完整
- 技术准确

---

*此文件在引导仪式期间创建/更新。*
"""

TOOLS_TEMPLATE = """# 工具说明

关于你的本地工具和约定的说明。此文件不控制工具可用性，仅提供指导。

## 开发环境

- 语言: Python 3.11+
- 包管理: Poetry
- 测试框架: pytest

## 常用命令

```bash
# 运行测试
poetry run pytest tests/

# 格式化代码
poetry run black anyclaw/

# 启动 CLI
poetry run python -m anyclaw chat
```

## 约定

- 异步优先
- 类型注解必需
- 测试覆盖率 > 80%

---

*根据你的项目需要更新此文件。*
"""
