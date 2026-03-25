# feat-agents-ui: 任务分解

## 阶段 1: API Hook

### Task 1.1: 创建 useAgents hook
- [ ] 创建 `src/hooks/useAgents.ts`
- [ ] 定义 Agent 接口
- [ ] 实现 fetchAgents()
- [ ] 实现 createAgent()
- [ ] 实现 updateAgent()
- [ ] 实现 deleteAgent()
- [ ] 实现 activateAgent()
- [ ] 实现 deactivateAgent()

## 阶段 2: 组件开发

### Task 2.1: AgentList 组件
- [ ] 创建 `src/components/agents/AgentList.tsx`
- [ ] 接收 agents 数组
- [ ] 接收 selectedId 和 onSelect
- [ ] 显示 emoji + name
- [ ] 高亮选中项

### Task 2.2: AgentDetail 组件
- [ ] 创建 `src/components/agents/AgentDetail.tsx`
- [ ] 显示完整 agent 信息
- [ ] 编辑/删除按钮
- [ ] 激活/禁用按钮

### Task 2.3: CreateAgentDialog 组件
- [ ] 创建 `src/components/agents/CreateAgentDialog.tsx`
- [ ] 名称输入框（必填）
- [ ] Emoji 选择器（使用 EmojiPicker 或简化版）
- [ ] Creature 下拉选择
- [ ] Vibe 下拉选择
- [ ] Workspace 可选输入
- [ ] 提交处理

### Task 2.4: EditAgentDialog 组件
- [ ] 创建 `src/components/agents/EditAgentDialog.tsx`
- [ ] 预填当前值
- [ ] 提交更新

### Task 2.5: 改造 Agents 页面
- [ ] 移除 mock 数据
- [ ] 使用 useAgents hook
- [ ] 集成新组件
- [ ] 添加加载状态
- [ ] 添加错误处理

## 阶段 3: i18n 与样式

### Task 3.1: 添加翻译
- [ ] 更新 `i18n/locales/zh.json`
- [ ] 更新 `i18n/locales/en.json`

### Task 3.2: 样式优化
- [ ] 确保暗色主题兼容
- [ ] 响应式布局
- [ ] 加载动画

## 预计工作量

- 阶段 1: 30 分钟
- 阶段 2: 1.5 小时
- 阶段 3: 30 分钟
- **总计**: 约 2.5 小时
