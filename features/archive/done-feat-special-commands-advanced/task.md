# 任务分解: Special Commands Advanced

## 任务概览

| 任务 ID | 任务描述 | 依赖 | 估算 |
|---------|----------|------|------|
| T1 | 权限系统基础设施 | feat-special-commands-core | 2h |
| T2 | 上下文压缩命令 | T1 | 2h |
| T3 | 模型切换命令 | T1 | 1.5h |
| T4 | Agent 切换命令 | T1 | 1.5h |
| T5 | 会话生命周期命令 | T1 | 1.5h |
| T6 | 配置模板更新 | T1-T5 | 0.5h |
| T7 | 测试与文档 | T1-T6 | 1h |

**总估算**: 10h

---

## T1: 权限系统基础设施

### 目标
为命令系统添加细粒度权限控制。

### 子任务
- [ ] 定义权限数据模型
  ```python
  class CommandPermission:
      command: str
      allowed: Literal["*"] | Literal["admin"] | list[str]
  ```
- [ ] 实现 `PermissionManager` 类
  - `check_permission(command, user_id) -> bool`
  - 从配置加载权限规则
  - 默认规则：所有命令所有人可用
- [ ] 实现 `@require_permission` 装饰器
  - 在 Handler 执行前检查权限
  - 无权限时返回标准错误消息
- [ ] 修改 `CommandDispatcher`
  - 集成 PermissionManager
  - 在分发前检查权限

### 验收标准
- [ ] 默认配置下所有命令可用
- [ ] 配置权限后正确限制访问
- [ ] 无权限时返回友好错误消息

### 关键文件
```
anyclaw/commands/
├── permission.py        # PermissionManager
└── decorators.py        # @require_permission
```

---

## T2: 上下文压缩命令

### 目标
实现 `/compact` 命令，触发上下文压缩。

### 子任务
- [ ] 实现 `CompactCommandHandler`
  - 解析可选的自定义指令
  - 调用 `ConversationHistory.compress()`
  - 格式化压缩结果
- [ ] 处理压缩时的活跃任务
  - 检查是否有正在执行的任务
  - 先停止再压缩
- [ ] 集成现有压缩功能
  - 复用 `feat-context-compression` 的压缩算法

### 验收标准
- [ ] `/compact` 触发压缩
- [ ] `/compact 指令` 使用自定义指令
- [ ] 压缩结果显示 Token 变化
- [ ] 有活跃任务时先停止

### 关键文件
```
anyclaw/commands/handlers/
└── compact.py
```

---

## T3: 模型切换命令

### 目标
实现 `/model` 命令，查看和切换模型。

### 子任务
- [ ] 实现 `ModelCommandHandler`
  - 无参数时返回当前模型和可用列表
  - 有参数时切换模型
- [ ] 添加权限检查
  - 使用 `@require_permission("model")`
- [ ] 模型验证
  - 检查模型名称是否在可用列表中
  - 无效模型返回错误和列表
- [ ] 配置更新
  - 调用 `ConfigManager.set("llm.model", name)`

### 验收标准
- [ ] `/model` 显示当前模型和列表
- [ ] `/model glm-4-plus` 切换模型
- [ ] 无权限时返回错误
- [ ] 无效模型返回提示

### 关键文件
```
anyclaw/commands/handlers/
└── model.py
```

---

## T4: Agent 切换命令

### 目标
实现 `/agent` 命令，查看和切换 Agent。

### 子任务
- [ ] 实现 `AgentCommandHandler`
  - 无参数时返回当前 Agent 和可用列表
  - 有参数时切换 Agent
- [ ] 添加权限检查
  - 使用 `@require_permission("agent")`
- [ ] Agent 验证
  - 检查 Agent 是否存在
  - 不存在时返回错误和列表
- [ ] Agent 切换逻辑
  - 调用 `AgentManager.switch(name)`
  - 加载新人设和配置

### 验收标准
- [ ] `/agent` 显示当前 Agent 和列表
- [ ] `/agent coder` 切换 Agent
- [ ] 无权限时返回错误
- [ ] 不存在的 Agent 返回提示

### 关键文件
```
anyclaw/commands/handlers/
└── agent_cmd.py
```

---

## T5: 会话生命周期命令

### 目标
实现 `/session idle` 和 `/session max-age` 命令。

### 子任务
- [ ] 实现 `SessionCommandHandler`
  - 子命令解析：`idle`, `max-age`
  - 无参数时显示当前设置
- [ ] 实现空闲超时设置
  - `/session idle 24h` 设置超时
  - `/session idle off` 禁用超时
- [ ] 实现最大存活时间设置
  - `/session max-age 7d` 设置最大存活
  - `/session max-age off` 禁用
- [ ] Channel 兼容性
  - CLI 返回提示（主要 IM 使用）
  - Discord/Feishu 正常工作

### 验收标准
- [ ] `/session` 显示当前设置
- [ ] `/session idle 24h` 设置空闲超时
- [ ] `/session max-age 7d` 设置最大存活
- [ ] CLI 中返回友好提示

### 关键文件
```
anyclaw/commands/handlers/
└── session_cmd.py
```

---

## T6: 配置模板更新

### 目标
更新配置模板文件，添加命令权限配置。

### 子任务
- [ ] 更新 `config.template.toml`
  ```toml
  [commands.permissions]
  default = "*"
  compact = "*"
  model = "*"
  agent = "*"
  session = "*"
  ```
- [ ] 更新 `Settings` 类
  - 添加 `CommandsSettings` 嵌套配置
  - 添加 `PermissionSettings` 嵌套配置
- [ ] 添加管理员配置
  ```toml
  [commands]
  admins = []
  ```

### 验收标准
- [ ] 配置模板包含权限设置
- [ ] Settings 类正确解析配置
- [ ] 默认配置所有人可用

### 关键文件
```
anyclaw/config/
├── settings.py
└── config.template.toml
```

---

## T7: 测试与文档

### 目标
编写测试并更新文档。

### 子任务
- [ ] 权限系统测试
  - `test_permission.py`
- [ ] 命令处理器测试
  - `test_compact_cmd.py`
  - `test_model_cmd.py`
  - `test_agent_cmd.py`
  - `test_session_cmd.py`
- [ ] 集成测试
  - 权限控制流程测试
- [ ] 更新 CLAUDE.md
  - 添加高级命令说明
  - 添加权限配置说明

### 验收标准
- [ ] 所有测试通过
- [ ] 测试覆盖率 > 80%
- [ ] 文档已更新

---

## 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 压缩算法集成复杂 | 中 | 复用现有 feat-context-compression |
| 权限配置设计复杂 | 低 | 参考配置模板，保持简单 |
| IM Channel 差异 | 中 | 使用 Channel 抽象层处理差异 |
