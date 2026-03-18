# feat-workspace-init: 完成检查清单

## VP1: Workspace 目录管理

### 目录创建
- [ ] 默认路径正确 (`~/.anyclaw/workspace`)
- [ ] 目录创建正常
- [ ] 父目录自动创建

### 路径解析
- [ ] 默认路径解析正常
- [ ] 自定义路径正常
- [ ] Profile 路径正常
- [ ] 环境变量 `ANYCLAW_PROFILE` 正常

### Git 初始化
- [ ] 检测 git 可用性
- [ ] git init 正常
- [ ] 跳过已存在的仓库

### 单元测试
- [ ] test_workspace_manager.py 通过
- [ ] 覆盖率 > 80%

---

## VP2: 引导文件系统

### 模板文件
- [ ] BOOTSTRAP.md 模板存在
- [ ] .gitignore 模板存在
- [ ] 模板内容合理

### 文件创建
- [ ] 引导文件创建正常
- [ ] 不覆盖已存在文件
- [ ] 文件权限正确

### 引导加载
- [ ] 加载引导文件正常
- [ ] 文件截断正常
- [ ] 完成标记正常

### AgentLoop 集成
- [ ] 会话开始时加载
- [ ] 首次运行仪式执行
- [ ] 完成后删除 BOOTSTRAP.md

### 单元测试
- [ ] test_bootstrap.py 通过
- [ ] 覆盖率 > 80%

---

## CLI 命令

### workspace 命令
- [ ] `anyclaw workspace init` 正常
- [ ] `anyclaw workspace status` 正常
- [ ] `anyclaw workspace path` 正常
- [ ] `anyclaw workspace files` 正常

### setup 命令
- [ ] `anyclaw setup` 正常
- [ ] `--workspace` 选项正常

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
- [ ] Workspace 使用指南存在

---

## 验收测试

### 手动测试场景

- [ ] **场景 1**: 首次设置
  ```bash
  anyclaw setup
  ```
  预期: 创建 ~/.anyclaw/workspace，包含默认文件

- [ ] **场景 2**: 自定义路径
  ```bash
  anyclaw setup --workspace ~/my-workspace
  ```
  预期: 使用自定义路径

- [ ] **场景 3**: Profile 工作区
  ```bash
  export ANYCLAW_PROFILE=work
  anyclaw workspace path
  ```
  预期: 显示 ~/.anyclaw/workspace-work

- [ ] **场景 4**: 查看状态
  ```bash
  anyclaw workspace status
  ```
  预期: 显示工作区路径、文件列表、git 状态

---

## 完成条件

- [ ] 所有 VP1 检查项完成
- [ ] 所有 VP2 检查项完成
- [ ] CLI 命令完成
- [ ] 所有质量标准满足
- [ ] 所有验收测试通过
- [ ] 代码已提交
