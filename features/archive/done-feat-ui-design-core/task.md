# feat-ui-design-core: 任务分解

## Phase 1: CSS 设计系统 (1-2h) ✅

- [x] 1.1 更新 `src/index.css`
  - [x] 添加 oklch 颜色变量
  - [x] 添加 subtle-border, surface-hover, surface-raised 变量
  - [x] 添加 --ease-soft 过渡曲线
  - [x] 更新暗色主题变量
  - [x] 添加滚动条样式

- [x] 1.2 更新 Tailwind 配置
  - [x] 配置 theme inline 引用 CSS 变量
  - [x] 添加自定义 variant

## Phase 2: UI 组件补充 (2-3h) ✅

- [x] 2.1 安装依赖
  ```bash
  npm install @radix-ui/react-dropdown-menu @radix-ui/react-avatar @radix-ui/react-tooltip zustand tailwind-merge clsx lucide-react react-router-dom @tauri-apps/plugin-opener
  ```

- [x] 2.2 创建组件
  - [x] `src/components/ui/dropdown-menu.tsx`
  - [x] `src/components/ui/avatar.tsx`
  - [x] `src/components/ui/tooltip.tsx`
  - [x] `src/components/ui/spinner.tsx`

## Phase 3: Hooks (1h) ✅

- [x] 3.1 创建 hooks
  - [x] `src/hooks/useSidebar.tsx` - 侧边栏状态管理
  - [x] `src/hooks/usePlatform.tsx` - 平台检测
  - [x] `src/hooks/useDragRegion.ts` - 窗口拖拽区域

## Phase 4: 布局组件 (3-4h) ✅

- [x] 4.1 创建 Shell 组件
  - [x] `src/components/layout/Shell.tsx`
  - [x] PlatformContext 集成
  - [x] 路由嵌套

- [x] 4.2 创建 AppSidebar 组件
  - [x] `src/components/layout/AppSidebar.tsx`
  - [x] 折叠/展开逻辑
  - [x] 导航菜单
  - [x] 用户菜单
  - [x] macOS 适配

- [ ] 4.3 创建 SidePanel 组件 (留待后续)
  - [ ] `src/components/layout/SidePanel.tsx`

- [ ] 4.4 创建 WindowsTitleBar (可选，留待后续)
  - [ ] `src/components/layout/WindowsTitleBar.tsx`

## Phase 5: 状态管理 (1h) ✅

- [x] 5.1 创建 Zustand store
  - [x] `src/stores/app.ts`
  - [x] sidebar 状态
  - [x] theme 状态

## Phase 6: 集成 (1-2h) ✅

- [x] 6.1 更新 App.tsx
  - [x] 使用 Shell 包裹
  - [x] 使用新的 AppSidebar
  - [x] 移除旧的侧边栏代码

- [x] 6.2 测试
  - [x] TypeScript 编译通过
  - [x] Vite 构建成功
  - [ ] 侧边栏折叠/展开 (需要运行时测试)
  - [ ] 主题切换 (需要运行时测试)
  - [ ] 导航功能 (需要运行时测试)
  - [ ] 跨平台测试 (需要运行时测试)
