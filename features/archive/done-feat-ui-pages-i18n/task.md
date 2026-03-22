# feat-ui-pages-i18n: 任务分解

## Phase 1: 国际化基础 (2h)

- [ ] 1.1 创建 i18n 结构
  - [ ] `src/i18n/types.ts` - 类型定义（完整翻译接口）
  - [ ] `src/i18n/zh.ts` - 中文翻译
  - [ ] `src/i18n/en.ts` - 英文翻译
  - [ ] `src/i18n/context.tsx` - I18nContext + useI18n hook
  - [ ] `src/i18n/index.ts` - 导出

- [ ] 1.2 集成到应用
  - [ ] App.tsx 添加 I18nProvider
  - [ ] useSettings 添加语言设置
  - [ ] 持久化语言偏好

## Phase 2: 路由配置 (1h)

- [ ] 2.1 安装依赖
  ```bash
  npm install react-router-dom
  ```

- [ ] 2.2 配置路由
  - [ ] App.tsx 添加 BrowserRouter
  - [ ] 配置路由表 (/, /agents, /cron, /memory, /logs)
  - [ ] 更新侧边栏导航 (NavLink)

## Phase 3: Agents 页面 (3-4h)

- [ ] 3.1 Agent 列表组件
  - [ ] AgentListItem 组件
  - [ ] 创建 Agent 按钮

- [ ] 3.2 Agent 详情面板
  - [ ] 基本配置显示
  - [ ] 技能绑定显示
  - [ ] 操作按钮

- [ ] 3.3 Agent 表单
  - [ ] 创建表单
  - [ ] 编辑表单
  - [ ] 输入验证

- [ ] 3.4 技能市场 (简化版)
  - [ ] MarketplaceCard 组件
  - [ ] 安装对话框

## Phase 4: Tasks 页面重构 (2h)

- [ ] 4.1 更新任务列表
  - [ ] 使用 SidePanel
  - [ ] 状态徽章 (active/paused/completed)
  - [ ] 调度信息显示

- [ ] 4.2 更新任务详情
  - [ ] 使用新的布局
  - [ ] 运行历史（状态、时间、耗时、错误）
  - [ ] 操作按钮（编辑、克隆、暂停、运行、删除）

- [ ] 4.3 更新任务表单
  - [ ] 使用新的 UI 组件
  - [ ] 调度类型选择（interval/cron/once）
  - [ ] i18n 支持

## Phase 5: Memory 页面（完整功能）(3h)

- [ ] 5.1 记忆选择器
  - [ ] SidePanel 组件
  - [ ] Global Memory 选项
  - [ ] Agent Memory 列表

- [ ] 5.2 记忆内容编辑
  - [ ] 工具栏（编辑/保存/取消）
  - [ ] Markdown 编辑器
  - [ ] 只读模式

- [ ] 5.3 右侧面板
  - [ ] 面板开关
  - [ ] Tab 切换（logs/archives/search）

- [ ] 5.4 每日日志
  - [ ] 按日期分组
  - [ ] 展开/收起
  - [ ] 加载日志内容

- [ ] 5.5 对话归档
  - [ ] 归档列表
  - [ ] 展开/收起
  - [ ] 加载归档内容

- [ ] 5.6 搜索功能
  - [ ] 搜索输入
  - [ ] 跨 Agent 搜索
  - [ ] 结果展示

## Phase 6: Logs 页面（完整功能）(3h)

- [ ] 6.1 顶部工具栏
  - [ ] 日期选择器
  - [ ] 分类按钮组
  - [ ] 级别下拉
  - [ ] 搜索框
  - [ ] Live 状态指示器

- [ ] 6.2 日志列表
  - [ ] 终端风格样式
  - [ ] 时间戳 + 级别 + 分类 + 消息
  - [ ] 颜色编码
  - [ ] 展开 JSON 详情

- [ ] 6.3 分页加载
  - [ ] 滚动到顶部加载更早
  - [ ] 保持滚动位置
  - [ ] IntersectionObserver

- [ ] 6.4 SSE 实时更新
  - [ ] useLogSSE hook
  - [ ] 过滤匹配逻辑
  - [ ] 自动滚动到底部

## Phase 7: Settings 对话框（完整功能）(3h)

- [ ] 7.1 对话框框架
  - [ ] SettingsDialog 组件
  - [ ] 左侧标签栏
  - [ ] 右侧内容区

- [ ] 7.2 General 面板
  - [ ] 主题切换（Light/Dark/System）
  - [ ] 语言切换
  - [ ] 服务端口配置（Tauri）

- [ ] 7.3 Models 面板
  - [ ] 活跃模型选择器
  - [ ] 内置模型列表
  - [ ] 自定义模型列表
  - [ ] 添加/编辑对话框
  - [ ] 删除确认

- [ ] 7.4 About 面板
  - [ ] 版本信息
  - [ ] GitHub 链接
  - [ ] 许可证

- [ ] 7.5 Skills 面板集成
  - [ ] 复用 Skills 页面

## Phase 8: 集成测试 (1-2h)

- [ ] 8.1 功能测试
  - [ ] Agent CRUD 测试
  - [ ] Task CRUD 测试
  - [ ] Memory 编辑测试
  - [ ] Logs 过滤测试
  - [ ] Settings 测试
  - [ ] 语言切换测试

- [ ] 8.2 清理
  - [ ] 移除旧组件
  - [ ] 更新导出
  - [ ] TypeScript 检查
  - [ ] ESLint 检查
  - [ ] 构建测试
