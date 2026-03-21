# feat-ui-design-core: UI 设计系统 + 布局组件

## 概述

复刻 youclaw 的 UI 设计系统和布局组件，建立统一的视觉语言和交互模式。

## 价值点

### 1. CSS 设计系统

**参考**: `reference/youclaw/web/src/index.css`

- oklch 颜色空间（更准确的色彩感知）
- 自定义 CSS 变量
  - `--background`, `--foreground`, `--card`, `--primary`...
  - `--subtle-border`, `--surface-hover`, `--surface-raised`
  - `--ease-soft`: 平滑过渡曲线
- 暗色/亮色主题变量
- 自定义滚动条样式

### 2. 布局组件

**参考**: `reference/youclaw/web/src/components/layout/`

- **Shell**: 主外壳
  - PlatformContext 提供平台信息
  - ChatProvider 聊天上下文
  - SettingsDialog 设置对话框

- **AppSidebar**: 可折叠侧边栏
  - 折叠宽度: 52px，展开宽度: 220px
  - 导航菜单 (Chat, Agents, Tasks, Memory, Logs)
  - 底部用户菜单 (DropdownMenu)
  - macOS traffic light 间距
  - 平滑折叠动画

- **SidePanel**: 左侧面板
  - 标题栏 + 操作按钮
  - 滚动内容区
  - 用于会话列表、Agent 列表等

### 3. UI 组件库补充

**参考**: `reference/youclaw/web/src/components/ui/`

需要补充的组件：
- `dropdown-menu.tsx` - 下拉菜单
- `dialog.tsx` - 对话框
- `avatar.tsx` - 头像
- `tooltip.tsx` - 提示
- `hover-card.tsx` - 悬浮卡片
- `command.tsx` - 命令面板 (cmdk)
- `progress.tsx` - 进度条
- `spinner.tsx` - 加载动画

## 验收标准

```gherkin
Feature: UI 设计系统 + 布局组件

  Scenario: 侧边栏折叠展开
    Given 用户已打开应用
    When 用户点击折叠按钮
    Then 侧边栏在 200ms 内平滑折叠至 52px
    And 导航图标保持可见
    And 文字标签淡出隐藏
    When 用户再次点击
    Then 侧边栏平滑展开至 220px
    And 文字标签淡入显示

  Scenario: 主题切换
    Given 应用当前为亮色主题
    When 用户切换为暗色主题
    Then 所有 CSS 变量在 200ms 内过渡
    And 背景色变为深色
    And 文字颜色变为浅色
    And 滚动条颜色更新

  Scenario: 导航菜单
    Given 用户在聊天页面
    When 用户点击侧边栏 "Agents" 菜单项
    Then 导航到 Agents 页面
    And 菜单项高亮显示

  Scenario: 用户菜单
    Given 用户已登录
    When 用户点击底部用户头像
    Then 弹出下拉菜单
    And 显示用户信息
    And 显示设置、GitHub、关于选项

  Scenario: macOS 平台适配
    Given 应用运行在 macOS
    Then 侧边栏顶部有 44px 的 traffic light 间距
    And 该区域可拖动窗口
```

## 技术实现

### CSS 变量迁移

```css
/* 亮色主题 */
:root {
  --background: oklch(0.985 0 0);
  --foreground: oklch(0.15 0 0);
  --primary: oklch(0.5 0.2 25);
  --subtle-border: oklch(0 0 0 / 0.06);
  --surface-hover: oklch(0 0 0 / 0.03);
  --surface-raised: oklch(0.97 0 0);
  --ease-soft: cubic-bezier(0.4, 0, 0.2, 1);
}

/* 暗色主题 */
.dark {
  --background: oklch(0.13 0 0);
  --foreground: oklch(0.93 0 0);
  --primary: oklch(0.55 0.2 25);
  /* ... */
}
```

### 侧边栏组件结构

```tsx
<aside className={cn(
  "shrink-0 flex flex-col overflow-hidden",
  "bg-muted/30 border-r border-[var(--subtle-border)]",
  "transition-[width] duration-200 ease-[var(--ease-soft)]",
  isCollapsed ? "w-[52px]" : "w-[220px]"
)}>
  {/* macOS traffic light spacing */}
  {isMac && <div className="h-11 shrink-0" {...drag} />}

  {/* Top action bar */}
  <div className="flex items-center h-[52px] shrink-0 px-2">
    {/* Logo + Title / Collapse button */}
  </div>

  {/* Page navigation */}
  <nav className="space-y-0.5 px-1.5">
    {navItems.map(item => <NavLink />)}
  </nav>

  {/* Spacer - draggable */}
  <div className="flex-1" {...drag} />

  {/* Bottom user menu */}
  <div className="border-t py-2 px-1.5">
    <DropdownMenu>{/* User avatar + menu */}</DropdownMenu>
  </div>
</aside>
```

## 文件清单

### 需要修改

- `src/index.css` - CSS 变量和主题
- `src/App.tsx` - 布局结构
- `src/lib/utils.ts` - cn() 工具函数

### 需要创建

- `src/components/layout/Shell.tsx`
- `src/components/layout/AppSidebar.tsx`
- `src/components/layout/SidePanel.tsx`
- `src/components/layout/WindowsTitleBar.tsx`
- `src/hooks/useSidebar.tsx`
- `src/hooks/usePlatform.tsx`
- `src/hooks/useDragRegion.ts`
- `src/stores/app.ts` (Zustand)
- `src/components/ui/dropdown-menu.tsx`
- `src/components/ui/dialog.tsx`
- `src/components/ui/avatar.tsx`
- `src/components/ui/tooltip.tsx`
- `src/components/ui/spinner.tsx`

## 依赖

```json
{
  "@radix-ui/react-dropdown-menu": "^2.1.16",
  "@radix-ui/react-avatar": "^1.1.11",
  "@radix-ui/react-tooltip": "^1.2.8",
  "@radix-ui/react-dialog": "^1.1.15",
  "zustand": "^5.0.11",
  "tailwind-merge": "^3.5.0",
  "clsx": "^2.1.1"
}
```

## 风险

1. Tailwind CSS 版本兼容性
2. Radix UI 组件与现有 shadcn/ui 组件整合
