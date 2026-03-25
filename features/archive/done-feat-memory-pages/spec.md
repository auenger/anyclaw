# Memory 页面功能实现

## 概述

为 Tauri 桌面应用的 Memory 页面实现完整的记忆管理功能，支持全局记忆和 Agent 级记忆的查看、编辑和管理。

## 目标

- 连接前端到后端 Memory API
- 支持全局记忆和 Agent 级记忆切换
- 实现记忆内容的查看和编辑
- 实现每日日志查看
- 实现记忆搜索功能

## 技术实现

### 后端 API

创建 `anyclaw/anyclaw/api/routes/memory.py`，提供以下端点：

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/memory` | GET | 获取记忆列表（全局 + Agent 级） |
| `/api/memory/{memory_id}` | GET | 获取记忆内容 |
| `/api/memory/{memory_id}` | PUT | 更新记忆内容 |
| `/api/memory/{memory_id}/daily-logs` | GET | 获取每日日志 |
| `/api/memory/{memory_id}/stats` | GET | 获取统计信息 |
| `/api/memory/search` | POST | 搜索记忆 |

### 前端实现

1. **useMemory Hook** (`tauri-app/src/hooks/useMemory.ts`)
   - 封装 Memory API 调用
   - 管理记忆状态（列表、内容、日志、统计）
   - 提供加载、保存、搜索功能

2. **Memory 页面** (`tauri-app/src/pages/Memory.tsx`)
   - 左侧面板：记忆列表（全局 + Agent 级）
   - 中央面板：记忆内容编辑器
   - 右侧面板：每日日志 + 搜索

3. **类型定义** (`tauri-app/src/types/index.ts`)
   - MemoryInfo
   - MemoryContent
   - DailyLogInfo
   - MemoryStats
   - SearchMatch
   - SearchResponse

## 依赖

- 现有 MemoryManager (`anyclaw/memory/manager.py`)
- FastAPI 路由系统
- Tauri 桌面应用前端

## 验收标准

- [x] 后端 API 端点正常工作
- [x] 前端连接到 API
- [x] 全局记忆可查看和编辑
- [x] Agent 级记忆可查看和编辑
- [x] 每日日志可查看
- [x] 搜索功能正常工作
- [x] TypeScript 编译通过
- [x] Python 测试通过
