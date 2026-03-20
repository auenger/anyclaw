# 完成检查清单: Special Commands Advanced

## 特性信息

- **ID**: feat-special-commands-advanced
- **名称**: Special Commands Advanced
- **优先级**: 65
- **依赖**: feat-special-commands-core

---

## 实现检查

### T1: 权限系统基础设施
- [ ] `CommandPermission` 数据类定义
- [ ] `PermissionManager` 实现完成
  - [ ] `check_permission(command, user_id)` 方法
  - [ ] 配置加载
  - [ ] 默认规则（所有命令可用）
- [ ] `@require_permission` 装饰器实现
- [ ] `CommandDispatcher` 权限集成

### T2: 上下文压缩命令
- [ ] `CompactCommandHandler` 实现
  - [ ] 基本压缩功能
  - [ ] 自定义指令支持
- [ ] 活跃任务检查
- [ ] 压缩结果格式化

### T3: 模型切换命令
- [ ] `ModelCommandHandler` 实现
  - [ ] 查看当前模型
  - [ ] 模型列表显示
  - [ ] 模型切换
- [ ] 权限检查集成
- [ ] 模型验证
- [ ] 配置更新

### T4: Agent 切换命令
- [ ] `AgentCommandHandler` 实现
  - [ ] 查看当前 Agent
  - [ ] Agent 列表显示
  - [ ] Agent 切换
- [ ] 权限检查集成
- [ ] Agent 验证
- [ ] Agent 切换逻辑

### T5: 会话生命周期命令
- [ ] `SessionCommandHandler` 实现
  - [ ] 子命令解析
  - [ ] 显示当前设置
- [ ] 空闲超时设置
- [ ] 最大存活时间设置
- [ ] Channel 兼容性处理

### T6: 配置模板更新
- [ ] `config.template.toml` 更新
  - [ ] 权限配置段
  - [ ] 管理员配置
- [ ] `Settings` 类更新
  - [ ] CommandsSettings
  - [ ] PermissionSettings

### T7: 测试与文档
- [ ] 权限系统测试
- [ ] 命令处理器测试
- [ ] 集成测试
- [ ] CLAUDE.md 更新

---

## 验收测试

### 权限控制
- [ ] `默认配置` → 所有命令可用
- [ ] `配置 model=admin` → 非管理员无法切换模型
- [ ] `配置 model=[user1]` → 仅 user1 可切换模型
- [ ] `无权限执行命令` → 返回友好错误

### 上下文压缩
- [ ] `输入 /compact` → 压缩上下文
- [ ] `输入 /compact 保留工具结果` → 使用自定义指令压缩
- [ ] `有任务时 /compact` → 先停止再压缩
- [ ] `压缩结果` → 显示 Token 变化

### 模型切换
- [ ] `输入 /model` → 显示当前模型和列表
- [ ] `输入 /model glm-4-plus` → 切换模型
- [ ] `输入 /model invalid` → 返回错误和列表
- [ ] `无权限 /model` → 返回权限错误

### Agent 切换
- [ ] `输入 /agent` → 显示当前 Agent 和列表
- [ ] `输入 /agent coder` → 切换 Agent
- [ ] `输入 /agent invalid` → 返回错误和列表
- [ ] `无权限 /agent` → 返回权限错误

### 会话生命周期
- [ ] `输入 /session` → 显示当前设置
- [ ] `输入 /session idle 24h` → 设置空闲超时
- [ ] `输入 /session idle off` → 禁用空闲超时
- [ ] `输入 /session max-age 7d` → 设置最大存活
- [ ] `CLI 中 /session` → 返回提示

### 边界条件
- [ ] `压缩中再次压缩` → 正确处理
- [ ] `切换到当前模型` → 返回提示
- [ ] `切换到当前 Agent` → 返回提示
- [ ] `配置文件缺失权限段` → 使用默认规则

---

## 代码质量

- [ ] 所有新文件有 docstring
- [ ] 类型注解完整
- [ ] 无 Ruff 警告
- [ ] 测试覆盖率 > 80%

---

## 文档更新

- [ ] CLAUDE.md 添加高级命令说明
- [ ] 添加权限配置说明
- [ ] config.template.toml 更新

---

## 完成标准

- [ ] 所有测试通过 (`poetry run pytest tests/ -v`)
- [ ] 代码检查通过 (`poetry run ruff check anyclaw/`)
- [ ] 功能演示成功
- [ ] 文档已更新
- [ ] feat-special-commands-core 已完成

---

## 签署

- 实现者: ________________
- 审核者: ________________
- 完成日期: ________________
