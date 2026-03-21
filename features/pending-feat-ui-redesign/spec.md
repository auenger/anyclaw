# feat-ui-redesign: Tauri 桌面应用 UI 复刻

## 概述

参考 youclaw 前端设计，全面重构 AnyClaw Tauri 桌面应用的 UI 组件和样式。

**注意**: 积分和账号登录功能暂不实现。

## 价值点

### 1. UI 设计系统 (feat-ui-design-core)
- oklch 颜色空间 + 自定义 CSS 变量
- Tailwind CSS 4.x 升级
- 暗色/亮色主题支持
- 流畅动画过渡效果

### 2. 布局组件 (feat-ui-design-core)
- 可折叠侧边栏 (AppSidebar)
- 左侧面板 (SidePanel)
- 平台适配 (macOS traffic light, Windows drag region)

### 3. 聊天功能增强 (feat-ui-chat-redesign)
- 会话列表 + 搜索 + 按日期分组
- 流式消息渲染
- Markdown 渲染 + 代码高亮 (streamdown + shiki)
- 附件支持 (图片、文档)
- Agent 选择器
- 欢迎页动画效果

### 4. 其他页面 (feat-ui-pages-i18n)
- Agents 管理页面（创建、编辑、技能绑定、技能市场）
- Tasks 定时任务页面（CRUD、执行历史、状态管理）
- Memory 记忆页面（完整功能）
  - Global Memory + Agent Memory 编辑
  - 每日日志查看
  - 对话归档查看
  - 跨 Agent 搜索
- Logs 日志页面（完整功能）
  - 日期/分类/级别/搜索过滤
  - SSE 实时更新
  - 分页加载
  - JSON 详情展开
- Settings 设置对话框
  - General（主题、语言、端口）
  - Models（活跃模型、自定义模型管理）
  - Skills（技能管理）
  - About（关于）

### 5. 国际化 (feat-ui-pages-i18n)
- 中英文支持
- 语言切换
- 自动检测系统语言
- 偏好持久化

## 子特性

| ID | 名称 | 优先级 | 大小 | 依赖 |
|---|---|---|---|---|
| feat-ui-design-core | UI 设计系统 + 布局 | 80 | M | - |
| feat-ui-chat-redesign | 聊天功能复刻 | 75 | M | feat-ui-design-core |
| feat-ui-pages-i18n | 页面 + 国际化 | 70 | M | feat-ui-design-core |

## 技术参考

- 参考项目: `reference/youclaw/web/`
- 目标项目: `tauri-app/src/`

## 验收标准

```gherkin
Feature: Tauri 桌面应用 UI 复刻

  Background:
    Given 用户已启动 AnyClaw 桌面应用

  Scenario: 侧边栏折叠
    When 用户点击侧边栏折叠按钮
    Then 侧边栏平滑折叠至 52px 宽度
    And 导航图标保持可见
    And 文字标签淡出

  Scenario: 主题切换
    When 用户切换暗色/亮色主题
    Then 界面颜色平滑过渡
    And 所有组件颜色正确更新

  Scenario: 聊天会话管理
    Given 用户进入聊天页面
    When 用户创建新会话
    Then 显示欢迎页动画
    And 输入框居中显示
    When 用户发送消息
    Then 输入框移动到底部
    And 消息流式显示

  Scenario: 会话列表搜索
    When 用户在会话列表搜索框输入关键词
    Then 会话列表实时过滤
    And 按日期分组显示

  Scenario: 附件上传
    When 用户点击附件按钮选择文件
    Then 文件预览显示在输入框上方
    When 用户发送消息
    Then 附件随消息一起发送

  Scenario: Memory 每日日志查看
    Given 用户在 Memory 页面选择了某个 Agent
    When 用户点击右侧面板的 Daily Logs
    Then 显示按日期分组的日志列表
    When 用户点击某个日期
    Then 展开显示该日日志内容

  Scenario: Memory 对话归档查看
    Given 用户在 Memory 页面选择了某个 Agent
    When 用户点击右侧面板的 Archives
    Then 显示历史对话归档列表
    When 用户点击某个归档
    Then 展开显示对话内容

  Scenario: Memory 搜索
    Given 用户在 Memory 页面
    When 用户在搜索框输入关键词并搜索
    Then 显示跨 Agent 的搜索结果

  Scenario: Logs 实时更新
    Given 用户查看今天的日志
    Then 显示 Live 实时状态指示器
    When 后端产生新日志
    Then 日志列表自动更新
    And 自动滚动到底部

  Scenario: Logs 过滤
    Given 用户在 Logs 页面
    When 用户选择分类和级别
    Then 日志列表只显示符合条件的日志

  Scenario: Settings 主题切换
    Given 用户打开设置对话框
    When 用户在 General 面板选择 Dark 主题
    Then 界面切换为暗色主题
    And 偏好持久化

  Scenario: Settings 自定义模型
    Given 用户在 Models 面板
    When 用户添加自定义模型
    Then 模型添加成功
    And 可以切换为活跃模型

  Scenario: 多语言支持
    Given 用户打开设置对话框
    When 用户在 General 面板切换语言
    Then 所有界面文字更新
    And 偏好持久化
```

## 风险

1. **依赖升级**: Tailwind CSS 4.x 可能与现有配置不兼容
2. **流式渲染**: streamdown 库集成需要测试
3. **平台差异**: macOS/Windows 窗口控制差异
