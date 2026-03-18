# feat-workspace-init: 任务分解

## 阶段 1: Workspace Manager 核心

### 1.1 创建模块结构
- [ ] 创建 `anyclaw/workspace/` 目录
- [ ] 创建 `__init__.py`
- [ ] 创建 `manager.py` 文件

### 1.2 实现 WorkspaceManager
- [ ] 实现 `__init__()` - 初始化路径
- [ ] 实现 `exists()` - 检查存在
- [ ] 实现 `create()` - 创建目录
- [ ] 实现 `_init_git()` - git 初始化
- [ ] 实现 `_create_default_files()` - 创建默认文件
- [ ] 实现 `get_bootstrap_files()` - 获取引导文件

### 1.3 路径解析
- [ ] 实现默认路径解析
- [ ] 实现自定义路径支持
- [ ] 实现 Profile 路径支持
- [ ] 处理环境变量 ANYCLAW_PROFILE

### 1.4 单元测试
- [ ] 测试默认路径
- [ ] 测试自定义路径
- [ ] 测试 Profile 路径
- [ ] 测试目录创建
- [ ] 测试 git 初始化

---

## 阶段 2: 引导文件系统

### 2.1 创建模板
- [ ] 创建 `templates.py`
- [ ] 定义 `BOOTSTRAP_TEMPLATE`
- [ ] 定义 `GITIGNORE_TEMPLATE`
- [ ] 模板可本地化

### 2.2 实现引导加载
- [ ] 创建 `bootstrap.py`
- [ ] 实现 `load_bootstrap()` - 加载引导文件
- [ ] 实现 `check_bootstrap_completed()` - 检查完成状态
- [ ] 实现 `mark_bootstrap_completed()` - 标记完成
- [ ] 实现文件截断逻辑

### 2.3 集成到 AgentLoop
- [ ] 在会话开始时加载引导文件
- [ ] 首次运行仪式执行
- [ ] 引导完成标记

### 2.4 单元测试
- [ ] 测试模板生成
- [ ] 测试引导加载
- [ ] 测试文件截断
- [ ] 测试完成标记

---

## 阶段 3: CLI 命令

### 3.1 workspace 命令
- [ ] 创建 `cli/workspace.py`
- [ ] 实现 `init` 子命令
- [ ] 实现 `status` 子命令
- [ ] 实现 `path` 子命令
- [ ] 实现 `files` 子命令

### 3.2 setup 命令
- [ ] 创建/更新 `setup` 命令
- [ ] 集成 WorkspaceManager
- [ ] 支持自定义路径选项

### 3.3 集成
- [ ] 注册命令到主 CLI
- [ ] 添加单元测试

---

## 阶段 4: 配置扩展

### 4.1 Settings 扩展
- [ ] 添加 `workspace` 配置
- [ ] 添加 `skip_bootstrap` 配置
- [ ] 添加 `bootstrap_max_chars` 配置
- [ ] 更新 `.env.example`

### 4.2 配置持久化
- [ ] 支持配置文件覆盖
- [ ] 环境变量支持
- [ ] 配置验证

---

## 依赖关系

```
1.1 → 1.2 → 1.3 → 1.4
              ↓
2.1 → 2.2 → 2.3 → 2.4
              ↓
3.1 → 3.2 → 3.3
              ↓
        4.1 → 4.2
```

## 预估工时

| 阶段 | 预估 |
|------|------|
| 阶段 1 | 2-3h |
| 阶段 2 | 2-3h |
| 阶段 3 | 1-2h |
| 阶段 4 | 1h |
| **总计** | **6-9h** |

## 关键决策

### Q1: 工作区默认位置？

**选项**：
1. `~/.anyclaw/workspace`
2. `~/.anyclaw/`
3. 项目目录 `.anyclaw/`

**决策**: `~/.anyclaw/workspace`，与 OpenClaw 保持一致。

### Q2: 是否强制 git 初始化？

**选项**：
1. 强制初始化
2. 可选（检测 git 是否可用）
3. 跳过

**决策**: 可选，检测 git 是否可用后决定。

### Q3: 引导完成状态存储位置？

**选项**：
1. 删除 BOOTSTRAP.md
2. 在文件中添加标记
3. 状态目录 `.anyclaw/workspace-state.json`

**决策**: 删除 BOOTSTRAP.md，简单直接。
