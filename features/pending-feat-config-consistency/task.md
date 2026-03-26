# 任务分解

## 任务 1: Python loader.py 添加 CommandsConfig

**文件**: `anyclaw/config/loader.py`

**步骤**:
1. 在 `ToolsConfig` 类后添加 `CommandsPermissionsConfig` 类
2. 添加 `CommandsConfig` 类
3. 在 `Config` 类中添加 `commands` 字段

**代码变更**:
```python
class CommandsPermissionsConfig(BaseModel):
    """命令权限配置"""
    default: str = "*"
    compact: Optional[str] = "*"
    model: Optional[str] = "*"
    agent: Optional[str] = "*"
    session: Optional[str] = "*"


class CommandsConfig(BaseModel):
    """命令配置"""
    admins: List[str] = Field(default_factory=list)
    permissions: Optional[CommandsPermissionsConfig] = None
```

## 任务 2: Tauri 前端添加 channels 配置字段

**文件**: `tauri-app/src/schemas/configSchema.ts`

**步骤**:
1. 添加 `channelsFields` 配置字段数组
2. 在 `configGroups` 中添加 channels 分组

**注意**: channels 配置需要考虑嵌套结构 (cli, feishu, discord)

## 任务 3: Tauri 前端添加 mcp_servers 配置字段

**文件**: `tauri-app/src/schemas/configSchema.ts`

**步骤**:
1. 添加 `mcpServerFields` 配置字段数组
2. 在 `configGroups` 中添加 mcp_servers 分组

**注意**: mcp_servers 是动态字典结构，需要特殊处理

## 任务 4: 添加 i18n 翻译

**文件**: `tauri-app/src/i18n/locales/zh-CN.json` 和 `en-US.json`

**步骤**:
1. 添加 channels 相关翻译键值对
2. 添加 mcp_servers 相关翻译键值对
3. 添加 commands 相关翻译键值对（如果前端需要展示）

## 任务 5: 测试验证

**步骤**:
1. 测试 Python 配置加载（包含 commands section）
2. 测试 Tauri 表单编辑 channels 配置
3. 测试 Tauri 表单编辑 mcp_servers 配置
4. 测试 sidecar 启动（使用修复后的配置）
