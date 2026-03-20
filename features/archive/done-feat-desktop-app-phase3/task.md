# feat-desktop-app-phase3 任务分解

## Phase 3.1: SSE 实时消息流

### 任务列表

- [ ] **T1.1** 实现 SSE 客户端 (`src/lib/sse.ts`)
  - EventSource 封装
  - 自动重连机制
  - 错误处理

- [ ] **T1.2** 创建 useSSE Hook (`src/hooks/useSSE.ts`)
  - 连接管理
  - 消息状态
  - 断开/重连控制

- [ ] **T1.3** 更新 MessageList 组件
  - 流式消息显示
  - 打字动画效果
  - 停止按钮

- [ ] **T1.4** 集成到 ChatWindow
  - 替换现有轮询
  - 优化渲染性能

## Phase 3.2: Settings 页面

### 任务列表

- [ ] **T2.1** 创建 SettingsPage 组件 (`src/components/settings/SettingsPage.tsx`)
  - 页面布局
  - 导航菜单
  - 保存/重置按钮

- [ ] **T2.2** 实现 LLMSettings 组件
  - 模型选择下拉框
  - Temperature 滑块
  - Max Tokens 输入

- [ ] **T2.3** 实现 ProviderSettings 组件
  - API Key 输入 (遮蔽显示)
  - Endpoint 配置
  - 连接测试

- [ ] **T2.4** 创建 useSettings Hook
  - 配置加载
  - 配置保存
  - 状态管理

## Phase 3.3: Skills 管理页面

### 任务列表

- [ ] **T3.1** 创建 SkillsPage 组件 (`src/components/skills/SkillsPage.tsx`)
  - 技能网格布局
  - 搜索框
  - 重载按钮

- [ ] **T3.2** 实现 SkillCard 组件
  - 技能图标/名称
  - 简短描述
  - 状态指示

- [ ] **T3.3** 实现 SkillDetail 组件
  - 详细描述
  - 参数定义
  - 使用示例

- [ ] **T3.4** 集成 API
  - GET /api/skills
  - POST /api/skills/{id}/reload

## Phase 3.4: Tasks 页面

### 任务列表

- [ ] **T4.1** 创建 TasksPage 组件 (`src/components/tasks/TasksPage.tsx`)
  - Tab 切换 (SubAgent / Cron)
  - 刷新按钮
  - 空状态提示

- [ ] **T4.2** 实现 SubAgentList 组件
  - 任务列表
  - 状态显示 (running/completed/failed)
  - 取消按钮

- [ ] **T4.3** 实现 CronList 组件
  - 任务列表
  - 下次执行时间
  - 启用/禁用开关

- [ ] **T4.4** 创建 useTasks Hook
  - 任务加载
  - 实时更新
  - 操作处理

## Phase 3.5: 整合与测试

### 任务列表

- [ ] **T5.1** 更新 App.tsx 路由
  - 添加 Settings 路由
  - 添加 Skills 路由
  - 添加 Tasks 路由

- [ ] **T5.2** 侧边栏导航
  - 添加导航项
  - 图标支持
  - 激活状态

- [ ] **T5.3** 端到端测试
  - 聊天流程
  - 设置保存
  - 技能管理
  - 任务管理

- [ ] **T5.4** 性能优化
  - 懒加载
  - 虚拟列表 (消息)
  - 缓存策略

---

## 预计工时

| 阶段 | 预计工时 |
|------|----------|
| Phase 3.1 SSE | 4h |
| Phase 3.2 Settings | 3h |
| Phase 3.3 Skills | 3h |
| Phase 3.4 Tasks | 3h |
| Phase 3.5 整合 | 2h |
| **总计** | **15h** |
