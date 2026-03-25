# feat-config-form-editor 任务分解

## Phase 1: 基础架构 (Day 1)

### Task 1.1: 类型定义和 Schema 结构
- [ ] 创建 `types/config.ts` 定义配置相关类型
- [ ] 定义 `ConfigFieldSchema` 接口
- [ ] 定义 `ConfigGroupSchema` 接口
- [ ] 定义 `ConfigValue` 联合类型

### Task 1.2: 核心 Schema 定义
- [ ] 创建 `schemas/configSchema.ts`
- [ ] 定义 Agent 分组 Schema (2 字段)
- [ ] 定义 LLM 分组 Schema (5 字段)
- [ ] 定义 Security 分组 Schema (10+ 字段)
- [ ] 定义 Memory 分组 Schema (4 字段)
- [ ] 定义 Compression 分组 Schema (4 字段)
- [ ] 定义 Streaming 分组 Schema (2 字段)
- [ ] 定义 Tools 分组 Schema (2 字段)
- [ ] 定义 Session 分组 Schema (1 字段)

### Task 1.3: 安装 TOML 解析库
- [ ] 调研并选择 TOML 解析库 (smol-toml 或 toml)
- [ ] 添加到 package.json
- [ ] 验证解析/序列化功能

## Phase 2: 字段组件 (Day 2)

### Task 2.1: 基础字段组件
- [ ] 创建 `components/settings/fields/StringField.tsx`
- [ ] 创建 `components/settings/fields/NumberField.tsx`
- [ ] 创建 `components/settings/fields/BooleanField.tsx`
- [ ] 添加敏感字段密码显示支持

### Task 2.2: 复杂字段组件
- [ ] 创建 `components/settings/fields/EnumField.tsx` (Select)
- [ ] 创建 `components/settings/fields/ArrayField.tsx` (多值输入)
- [ ] 创建 `components/settings/fields/ObjectField.tsx` (嵌套对象)

### Task 2.3: 通用字段渲染器
- [ ] 创建 `components/settings/ConfigField.tsx`
- [ ] 根据 type 动态渲染对应组件
- [ ] 添加 label、description、验证错误显示
- [ ] 添加条件显示逻辑

## Phase 3: 表单编辑器 (Day 3)

### Task 3.1: 表单状态管理
- [ ] 创建 `hooks/useConfigForm.ts`
- [ ] 实现 TOML → 表单数据解析
- [ ] 实现表单数据 → TOML 序列化
- [ ] 实现表单验证逻辑
- [ ] 实现 dirty 状态追踪

### Task 3.2: 分组卡片组件
- [ ] 创建 `components/settings/ConfigFormEditor.tsx`
- [ ] 实现分组卡片布局
- [ ] 实现折叠/展开功能
- [ ] 实现折叠状态持久化 (localStorage)

### Task 3.3: 表单完整功能
- [ ] 加载配置文件
- [ ] 保存配置文件
- [ ] 重置功能
- [ ] 验证错误提示
- [ ] 保存成功/失败反馈

## Phase 4: 模式切换 (Day 4)

### Task 4.1: 重构 ConfigEditor
- [ ] 添加模式状态 (form/advanced)
- [ ] 添加模式切换开关
- [ ] 整合 ConfigFormEditor 组件
- [ ] 整合原始 TOML 编辑器

### Task 4.2: 模式间数据同步
- [ ] 表单 → TOML 数据同步
- [ ] TOML → 表单数据同步
- [ ] 切换时验证检查
- [ ] 未保存更改提示

## Phase 5: 高级功能 (Day 5)

### Task 5.1: Providers 动态配置
- [ ] 支持 providers.* 分组动态生成
- [ ] 添加/删除 Provider 配置

### Task 5.2: Channels 动态配置
- [ ] 支持 channels.* 分组动态生成
- [ ] 条件显示逻辑 (enabled 字段控制)

### Task 5.3: 国际化支持
- [ ] 添加所有 label/description 的 i18n key
- [ ] 中文翻译
- [ ] 英文翻译

### Task 5.4: 样式优化
- [ ] 响应式布局适配
- [ ] 暗色主题适配
- [ ] 加载状态
- [ ] 错误状态

## 验收标准

- [ ] 所有配置项都有对应的表单 UI
- [ ] 表单验证正确工作
- [ ] 模式切换数据同步正确
- [ ] 折叠状态持久化
- [ ] i18n 完整支持
- [ ] 暗色主题适配

## 预估时间

- Phase 1: 4 小时
- Phase 2: 4 小时
- Phase 3: 4 小时
- Phase 4: 3 小时
- Phase 5: 3 小时

**总计**: 18 小时 (约 3 个工作日)
