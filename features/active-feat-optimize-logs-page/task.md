# task: feat-optimize-logs-page

## 任务分解

### Phase 1: 简化 Logs 页面（移除会话归档）

- [ ] **1.1 简化 Logs.tsx 前端页面**
  - 移除 `activeTab` 状态和 Tab 切换 UI
  - 移除 Sessions 相关代码（sessionLogs 渲染、selectedSession 详情）
  - 简化组件结构，直接显示系统日志
  - 保留日期选择、类别/级别过滤、搜索、实时模式

- [ ] **1.2 简化 useLogs.ts Hook**
  - 移除 `sessionLogs`, `selectedSession` 状态
  - 移除 `loadSessionLogs`, `loadSessionDetail`, `clearSelection` 方法
  - 保留 `systemLogs`, `loadSystemLogs`, `isLive`, `toggleLive`, `stats`

- [ ] **1.3 清理 API 客户端和类型定义（可选）**
  - 检查 `api.ts` 中 session 相关 API 是否被其他地方使用
  - 如无其他使用，移除 `getSessionLogs`, `getSessionDetail`, `searchSessionLogs`
  - 清理 `types/index.ts` 中未使用的类型定义

### Phase 2: 实现日志持久化

- [ ] **2.1 修改 SystemLogCollector 支持文件持久化**
  - 添加日志目录配置：`~/.anyclaw/logs/`
  - 实现 `FileLogCollectorHandler` 或扩展现有 `LogCollectorHandler`
  - 日志写入 `system-{YYYY-MM-DD}.jsonl` 文件
  - 每条日志一行 JSON（JSON Lines 格式）

- [ ] **2.2 修改 get_logs() 支持读取历史文件**
  - 如果 `date` 参数是今天，从内存读取
  - 如果 `date` 参数是历史日期，从对应文件读取
  - 处理文件不存在的情况（返回空列表）

- [ ] **2.3 实现日志文件自动轮转**
  - 检测日期变更时切换到新文件
  - 可选：实现日志清理策略（保留最近 N 天）

- [ ] **2.4 更新 API 端点**
  - 确保 `/api/logs/system` 端点正确处理日期参数
  - 更新 stats 统计（可选包含历史日志统计）

### Phase 3: 测试和验证

- [ ] **3.1 编写单元测试**
  - 测试日志文件写入
  - 测试历史日志读取
  - 测试日期过滤

- [ ] **3.2 手动验证**
  - 启动应用，产生日志
  - 选择今天日期，确认日志显示
  - 重启应用，选择之前日期，确认历史日志可查看
  - 验证实时模式正常工作

## 执行顺序

1. Phase 1 和 Phase 2 可以并行开发
2. Phase 3 在 Phase 1-2 完成后执行

## 注意事项

- 日志文件可能包含敏感信息，注意权限设置
- 考虑日志文件大小限制，避免磁盘占用过多
- 前端日期选择器可能需要限制可选范围（有日志的日期）
