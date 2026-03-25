# Logs 页面功能 - 任务分解

## Phase 1: 后端 API 实现

### 1.1 系统日志收集器
- [x] 创建 `anyclaw/utils/log_collector.py`
- [x] 实现 `SystemLogCollector` 类
- [x] 实现 `LogEntry` 数据类
- [x] 实现 `add_handler()` 方法注册到 logging
- [x] 实现 `get_logs()` 过滤方法
- [x] 实现内存限制（max_entries）

### 1.2 创建 Logs API 路由
- [x] 创建 `anyclaw/api/routes/logs.py`
- [x] 实现 `GET /api/logs/stats` 统计端点
- [x] 实现 `GET /api/logs/sessions` 会话列表端点
- [x] 实现 `GET /api/logs/sessions/:id` 会话详情端点
- [x] 实现 `GET /api/logs/sessions/search` 搜索端点
- [x] 实现 `GET /api/logs/system` 系统日志端点
- [x] 实现 `GET /api/logs/stream` SSE 实时流端点

### 1.3 集成 SessionArchiveManager
- [x] 在 API 中注入 SessionArchiveManager
- [x] 实现会话列表查询
- [x] 实现会话详情查询
- [x] 实现会话搜索

### 1.4 注册路由
- [x] 在 `api/server.py` 中注册 logs 路由
- [x] 在 `api/routes/__init__.py` 中导出 logs_router

### 1.5 单元测试
- [x] 创建 `tests/test_logs_api.py`
- [x] 测试会话日志 API
- [x] 测试系统日志 API
- [x] 测试搜索功能

## Phase 2: 前端实现

### 2.1 创建 API Hooks
- [x] 创建 `src/hooks/useLogs.ts`
- [x] 实现 `loadSessionLogs(date)` 方法
- [x] 实现 `loadSessionDetail(id)` 方法
- [x] 实现 `loadSystemLogs(level, date)` 方法
- [x] 实现 `searchSessions(query)` 方法
- [x] 实现 SSE 实时流支持

### 2.2 重构 Logs 页面
- [x] 更新 `src/pages/Logs.tsx`
- [x] 对接 useLogs hooks
- [x] 实现会话归档列表
- [x] 实现系统日志列表
- [x] 实现标签切换
- [x] 实现日期选择器
- [x] 实现类别/级别过滤
- [x] 实现搜索功能
- [x] 实现日志详情展开/收起

### 2.3 更新 API 客户端
- [x] 添加 logs API 方法到 `src/lib/api.ts`
- [x] 添加 logs 类型到 `src/types/index.ts`
- [x] 导出 useLogs hook

### 2.4 国际化
- [x] 添加中文翻译键
- [x] 添加英文翻译键

## 完成状态

✅ 所有任务已完成

## 实际工作量

- Phase 1 (后端): ~1.5 小时
- Phase 2 (前端): ~1.5 小时
- 测试和调试: ~0.5 小时
- **总计**: ~3.5 小时
