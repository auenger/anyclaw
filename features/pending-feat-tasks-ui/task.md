# feat-tasks-ui 任务分解

## Phase 1: API 集成

### 1.1 扩展 api/client.ts
- [ ] 添加 `getCronJobs()` 函数
- [ ] 添加 `createCronJob()` 函数
- [ ] 添加 `getCronJob()` 函数
- [ ] 添加 `updateCronJob()` 函数
- [ ] 添加 `deleteCronJob()` 函数
- [ ] 添加 `cloneCronJob()` 函数
- [ ] 添加 `runCronJob()` 函数
- [ ] 添加 `getCronJobLogs()` 函数

### 1.2 类型定义
- [ ] `CronJob` 接口
- [ ] `CreateJobRequest` 接口
- [ ] `UpdateJobRequest` 接口
- [ ] `RunLog` 接口
- [ ] `Schedule` 联合类型

---

## Phase 2: 基础布局

### 2.1 创建页面
- [ ] 创建 `web/src/pages/Tasks.tsx`
- [ ] 注册路由 `/tasks`
- [ ] 添加到侧边栏导航

### 2.2 布局结构
- [ ] 左侧 SidePanel
- [ ] 右侧 DetailPanel
- [ ] 状态管理 (selectedId, panelMode)

---

## Phase 3: 任务列表

### 3.1 SidePanel 头部
- [ ] 标题 "定时任务"
- [ ] "+" 新建按钮

### 3.2 TaskList 组件
- [ ] 加载任务列表
- [ ] 显示加载状态
- [ ] 空状态展示

### 3.3 TaskItem 组件
- [ ] 任务名称 (或 prompt 截断)
- [ ] 状态标签 (StatusBadge)
- [ ] 调度信息 (interval/cron/once)
- [ ] Agent 名称
- [ ] 点击选中效果

### 3.4 StatusBadge 组件
- [ ] active: 绿色
- [ ] paused: 黄色
- [ ] completed: 灰色

---

## Phase 4: 任务详情

### 4.1 TaskDetail 组件
- [ ] 任务名称 + 描述
- [ ] 操作按钮组

### 4.2 基本信息展示
- [ ] Agent 名称
- [ ] 状态标签
- [ ] 调度配置
- [ ] 下次运行时间
- [ ] 上次运行时间
- [ ] 创建时间
- [ ] 任务 ID

### 4.3 Prompt 展示
- [ ] 代码块样式
- [ ] 保留换行

### 4.4 执行历史
- [ ] 最近 20 条记录
- [ ] 状态图标 (成功/失败)
- [ ] 执行时间
- [ ] 耗时
- [ ] 错误信息 (红色)

---

## Phase 5: 任务表单

### 5.1 TaskForm 组件
- [ ] 创建/编辑模式切换
- [ ] 表单状态管理

### 5.2 基础字段
- [ ] 名称输入
- [ ] 描述输入
- [ ] Agent 选择 (创建时可选，编辑时禁用)

### 5.3 Prompt 输入
- [ ] 多行文本框
- [ ] 最小高度

### 5.4 调度配置
- [ ] 类型切换按钮 (interval/cron/once)
- [ ] Interval: 分钟数输入
- [ ] Cron: 表达式输入 + 帮助文本
- [ ] Once: datetime-local 选择器

### 5.5 表单验证
- [ ] 必填字段验证
- [ ] 提交按钮状态

### 5.6 提交处理
- [ ] 创建: POST /api/cron/jobs
- [ ] 编辑: PUT /api/cron/jobs/:id
- [ ] 成功后刷新列表

---

## Phase 6: 操作功能

### 6.1 编辑
- [ ] 切换到编辑模式
- [ ] 预填充表单数据

### 6.2 克隆
- [ ] 调用 cloneCronJob API
- [ ] 切换到新任务

### 6.3 暂停/恢复
- [ ] 调用 updateCronJob
- [ ] 切换 enabled 状态
- [ ] 刷新任务数据

### 6.4 手动执行
- [ ] 调用 runCronJob API
- [ ] 刷新执行历史

### 6.5 删除
- [ ] 显示确认对话框
- [ ] 调用 deleteCronJob API
- [ ] 清除选中状态

---

## Phase 7: i18n

### 7.1 中文翻译
- [ ] web/src/i18n/zh.ts 添加 tasks 命名空间

### 7.2 英文翻译
- [ ] web/src/i18n/en.ts 添加 tasks 命名空间

---

## Phase 8: 测试

### 8.1 组件测试
- [ ] TaskList 渲染测试
- [ ] TaskDetail 渲染测试
- [ ] TaskForm 验证测试

### 8.2 E2E 测试
- [ ] 创建任务流程
- [ ] 编辑任务流程
- [ ] 删除任务流程

---

## 文件变更

```
web/src/
├── pages/
│   └── Tasks.tsx         # 新增
├── api/
│   └── client.ts         # 扩展 cron API
├── i18n/
│   ├── zh.ts             # 添加 tasks 翻译
│   └── en.ts             # 添加 tasks 翻译
└── components/
    └── StatusBadge.tsx   # 新增 (如果不存在)
```

---

## 工作量估计

| Phase | 工作量 |
|-------|--------|
| Phase 1: API 集成 | 0.5 天 |
| Phase 2: 基础布局 | 0.5 天 |
| Phase 3: 任务列表 | 0.5 天 |
| Phase 4: 任务详情 | 0.5 天 |
| Phase 5: 任务表单 | 1 天 |
| Phase 6: 操作功能 | 0.5 天 |
| Phase 7: i18n | 0.25 天 |
| Phase 8: 测试 | 0.25 天 |
| **总计** | **4 天** |
