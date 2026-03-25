# feat-config-form-editor

## 概述

将 Tauri 桌面应用中的配置文件页面从原始 TOML 文本编辑器升级为基于 Schema 的表单式配置界面，提供用户友好的配置编辑体验。

## 背景

当前 `ConfigEditor.tsx` 是一个原始的 TOML 文本编辑器，用户需要直接编辑 TOML 字符串。这种方式存在以下问题：
- 语法错误风险高（拼写错误、格式错误）
- 类型安全无保障（数字字段输入字符串等）
- C 端用户难以接受原始的编辑方式
- 缺乏配置项说明和验证提示

## 用户价值点

### VP1: 配置 Schema 定义

定义完整的配置项数据结构，涵盖所有配置节和字段。

**验收场景**:

```gherkin
Scenario: Schema 包含所有配置节
  Given 配置模板 config.template.toml 存在
  When 定义 configSchema
  Then 应包含 agent、llm、providers、channels、security、memory、compression、streaming、tools、session、commands 等配置节

Scenario: Schema 字段定义完整
  Given 定义 Schema 字段
  Then 每个字段应包含以下属性:
    | 属性 | 说明 |
    | key | 配置键名 (如 "llm.model") |
    | type | 字段类型 (string/number/boolean/enum/array/object) |
    | label | 显示标签 (支持 i18n) |
    | description | 字段描述 (支持 i18n) |
    | default | 默认值 |
    | required | 是否必填 |
    | validation | 验证规则 (min/max/pattern/enum) |
    | group | 所属分组 |
```

### VP2: 动态表单组件生成

根据 Schema 字段类型自动生成对应的 UI 组件。

**验收场景**:

```gherkin
Scenario: 字符串字段生成 Input 组件
  Given 字段类型为 string
  When 渲染表单
  Then 显示 Input 组件
  And 如果有 pattern 验证，显示格式提示

Scenario: 数字字段生成数字输入组件
  Given 字段类型为 number
  When 渲染表单
  Then 显示 type="number" 的 Input 组件
  And 支持 min/max 验证

Scenario: 布尔字段生成 Switch 组件
  Given 字段类型为 boolean
  When 渲染表单
  Then 显示 Switch 组件

Scenario: 枚举字段生成 Select 组件
  Given 字段类型为 enum
  And 可选值为 ["openai", "anthropic", "zai"]
  When 渲染表单
  Then 显示 Select 组件
  And 下拉选项包含所有可选值

Scenario: 数组字段生成多值输入组件
  Given 字段类型为 array
  When 渲染表单
  Then 显示可添加/删除的多值输入组件

Scenario: 敏感字段使用密码输入
  Given 字段标记为 sensitive (如 api_key)
  When 渲染表单
  Then 显示 type="password" 的 Input 组件
```

### VP3: 分组卡片布局

按配置节分组显示，支持折叠和清晰的视觉层次。

**验收场景**:

```gherkin
Scenario: 配置按分组显示
  Given 配置 Schema 定义了多个分组
  When 渲染配置页面
  Then 每个分组显示为一个可折叠的卡片
  And 卡片标题显示分组名称和图标

Scenario: 分组卡片可折叠
  Given 配置页面显示多个分组卡片
  When 点击分组标题
  Then 该分组卡片折叠/展开
  And 折叠状态在会话间保持

Scenario: 分组显示字段数量统计
  Given 分组内有多个配置字段
  When 分组折叠时
  Then 显示该分组已配置字段数量统计
```

### VP4: 表单/高级模式切换

默认表单模式，可切换到原始 TOML 编辑，两种模式数据同步。

**验收场景**:

```gherkin
Scenario: 默认显示表单模式
  Given 用户打开配置页面
  Then 默认显示表单式配置界面
  And 显示"高级模式"切换开关

Scenario: 切换到高级模式
  Given 用户在表单模式
  When 点击"高级模式"开关
  Then 切换到原始 TOML 编辑器
  And TOML 内容与表单数据同步

Scenario: 高级模式编辑后切换回表单模式
  Given 用户在高级模式编辑了 TOML
  And TOML 格式正确
  When 切换回表单模式
  Then 表单自动更新为新的配置值

Scenario: 高级模式格式错误提示
  Given 用户在高级模式编辑了 TOML
  And TOML 格式错误
  When 尝试切换回表单模式或保存
  Then 显示格式错误提示
  And 阻止切换/保存
```

## 技术方案

### 文件结构

```
tauri-app/src/
├── components/settings/
│   ├── ConfigEditor.tsx          # 重构：模式切换容器
│   ├── ConfigFormEditor.tsx      # 新增：表单式编辑器
│   ├── ConfigField.tsx           # 新增：通用字段渲染器
│   └── fields/                   # 新增：字段类型组件
│       ├── StringField.tsx
│       ├── NumberField.tsx
│       ├── BooleanField.tsx
│       ├── EnumField.tsx
│       ├── ArrayField.tsx
│       └── ObjectField.tsx
├── schemas/
│   └── configSchema.ts           # 新增：配置 Schema 定义
├── hooks/
│   └── useConfigForm.ts          # 新增：配置表单状态管理
└── types/
    └── config.ts                 # 新增：配置类型定义
```

### Schema 设计

```typescript
interface ConfigFieldSchema {
  key: string                    // 配置键名
  type: 'string' | 'number' | 'boolean' | 'enum' | 'array' | 'object'
  label: string                  // i18n key
  description?: string           // i18n key
  default?: any
  required?: boolean
  sensitive?: boolean            // 是否为敏感字段（如 API Key）
  validation?: {
    min?: number
    max?: number
    pattern?: string
    enum?: string[]
  }
  group: string                  // 所属分组
  condition?: {                  // 条件显示
    field: string
    value: any
  }
}

interface ConfigGroupSchema {
  id: string
  label: string                  // i18n key
  description?: string           // i18n key
  icon: LucideIcon
  fields: ConfigFieldSchema[]
}
```

### 主要配置分组

| 分组 | ID | 描述 | 字段数 |
|------|-----|------|--------|
| Agent | agent | 智能体基本配置 | 2 |
| LLM | llm | 大语言模型配置 | 5 |
| Providers | providers | API Key 和 Provider 配置 | 动态 |
| Channels | channels | IM 通道配置 | 动态 |
| Security | security | 安全配置 | 10+ |
| Memory | memory | 记忆系统配置 | 4 |
| Compression | compression | 上下文压缩配置 | 4 |
| Streaming | streaming | 流式输出配置 | 2 |
| Tools | tools | 工具系统配置 | 2 |
| Session | session | 会话并发配置 | 1 |

## 依赖

无外部依赖。

## 风险

1. **Schema 维护成本**: 配置模板更新时需要同步更新 Schema
2. **复杂配置项**: 某些配置（如 mcp_servers）结构复杂，可能需要特殊处理
3. **TOML 解析**: 前端需要可靠的 TOML 解析库

## 参考

- 现有实现: `tauri-app/src/components/settings/ConfigEditor.tsx`
- 配置模板: `anyclaw/anyclaw/config/config.template.toml`
- ModelsPanel: `tauri-app/src/components/settings/ModelsPanel.tsx`
