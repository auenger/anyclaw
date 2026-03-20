# Smart File Search - 任务分解

## 任务列表

### Phase 1: 搜索启发式 (SearchHeuristics)

- [ ] **T1.1** 创建 `anyclaw/search/` 模块目录结构
- [ ] **T1.2** 实现 `SearchHeuristics` 类
  - 默认优先级目录列表（Downloads > Desktop > Documents > Projects > Home）
  - `get_search_paths(file_pattern: str) -> List[Path]` 方法
  - 文件类型 → 目录关联（.xlsx/.dmg → Downloads, .py → Projects）
- [ ] **T1.3** 添加配置支持
  - `search.priority_dirs` 配置项
  - `search.file_type_dirs` 映射配置

### Phase 1.5: 对话上下文关联 (ContextAwareSearch)

- [ ] **T1.5.1** 实现 `ContextPathExtractor` 类
  - 路径正则匹配（Unix/Windows/相对路径）
  - `extract_from_history(messages) -> List[ContextPath]` 方法
- [ ] **T1.5.2** 上下文路径排序
  - 按新鲜度排序（最近提到优先）
  - 按提到次数加权
  - 过滤过期路径（超过 10 轮对话）
- [ ] **T1.5.3** 集成到 SearchHeuristics
  - `get_search_paths()` 接收上下文路径参数
  - 合并上下文路径到默认优先级

### Phase 1.6: 信息不足主动询问 (ProactiveQuery)

- [ ] **T1.6.1** 实现 `SearchQueryAnalyzer` 类
  - `analyze(user_request, context_paths) -> SearchQuery` 方法
  - `needs_more_info(query) -> Optional[QuerySuggestion]` 方法
- [ ] **T1.6.2** 询问判断逻辑
  - 无文件名 → 询问文件名
  - 模式太宽泛 + 范围大 → 建议限定目录
  - 有足够信息 → 直接搜索
- [ ] **T1.6.3** 集成到 SearchFilesTool
  - 搜索前检查信息是否充足
  - 返回询问建议而非执行搜索

### Phase 2: 搜索缓存 (SearchCache)

- [ ] **T2.1** 实现 `SearchCache` 类
  - 最近访问文件缓存（LRU，max=100）
  - 常用目录缓存（访问次数阈值=3）
  - 缓存过期（TTL=24h）
- [ ] **T2.2** 缓存持久化
  - 缓存存储路径：`~/.anyclaw/cache/search.json`
  - 启动时加载，关闭时保存
- [ ] **T2.3** 缓存 API
  - `get_cached_path(filename: str) -> Optional[Path]`
  - `record_access(path: Path)` - 记录访问
  - `get_frequent_dirs() -> List[Path]` - 获取常用目录

### Phase 3: 动态路径授权 (PathAuthorizer)

- [ ] **T3.1** 实现 `PathAuthorizer` 类
  - 会话级临时授权（`session_allowed_dirs: Set[Path]`）
  - `authorize(dir: Path, persist: bool = False)` 方法
  - `is_authorized(dir: Path) -> bool` 方法
  - `is_dangerous(dir: Path) -> bool` - 危险路径检查
- [ ] **T3.2** 实现 `AuthorizationRequiredError` 异常
  - 携带 `path` 和 `suggested_dir` 属性
  - 用于 Channel 层识别并触发授权流程
- [ ] **T3.3** 集成 PathGuard
  - 修改 `PathGuard._check_in_allowed_dir()` 检查授权列表
  - 危险路径直接拒绝，不抛出授权异常
  - 非危险路径抛出 `AuthorizationRequiredError`
- [ ] **T3.4** 持久化授权
  - 写入配置 `path_extra_allowed_dirs`
  - 启动时加载持久化授权

### Phase 3.5: 跨渠道授权交互 (Channel Authorization)

- [ ] **T3.5.1** 扩展 `BaseChannel` 基类
  - 添加 `request_authorization(error: AuthorizationRequiredError) -> Optional[str]` 抽象方法
- [ ] **T3.5.2** 实现 `CLIChannel.request_authorization()`
  - 使用 `rich.prompt.Prompt` 交互式菜单
  - 显示选项: [y]临时 [p]永久 [n]拒绝
- [ ] **T3.5.3** 实现 `DiscordChannel.request_authorization()`
  - 使用 Discord Button 组件
  - 等待用户点击（超时 60s）
- [ ] **T3.5.4** 实现 `FeishuChannel.request_authorization()`
  - 使用飞书交互式卡片
  - 处理卡片按钮回调
- [ ] **T3.5.5** AgentLoop 集成
  - 捕获 `AuthorizationRequiredError`
  - 调用 `channel.request_authorization()`
  - 根据用户决策调用 `PathAuthorizer.authorize()`

### Phase 4: 搜索工具 (SearchFilesTool)

- [ ] **T4.1** 实现 `SearchFilesTool` 类
  - 参数：pattern, search_paths, file_type, max_depth, use_cache
  - 集成 SearchHeuristics + SearchCache
  - 超时控制（默认 5 秒）
- [ ] **T4.2** 搜索逻辑
  - 优先检查缓存
  - 按启发式顺序搜索
  - 找到第一个匹配即返回（可配置为全部返回）
- [ ] **T4.3** 格式化输出
  - 搜索用时、缓存命中数
  - 文件列表（带大小）
  - 授权提示（如被拦截）

### Phase 5: 集成和测试

- [ ] **T5.1** 注册 `search_files` 工具到 ToolRegistry
- [ ] **T5.2** 更新 AgentLoop 工具加载
- [ ] **T5.3** 单元测试
  - SearchHeuristics 测试（优先级顺序、文件类型关联）
  - SearchCache 测试（缓存命中、过期、LRU）
  - PathAuthorizer 测试（临时授权、持久化）
  - SearchFilesTool 测试（各种搜索场景）
- [ ] **T5.4** 集成测试
  - 端到端搜索流程
  - 授权流程
- [ ] **T5.5** 文档更新
  - 更新 CLAUDE.md 工具说明
  - 添加配置文档

## 估算

| Phase | 预计时间 | 复杂度 |
|-------|----------|--------|
| Phase 1 | 1h | 中 |
| Phase 1.5 | 1h | 中 |
| Phase 1.6 | 1h | 中 |
| Phase 2 | 1.5h | 中 |
| Phase 3 | 1h | 中 |
| Phase 3.5 | 2h | 高 |
| Phase 4 | 1.5h | 高 |
| Phase 5 | 1h | 中 |
| **总计** | **10h** | |

## 依赖关系

```
T1.x (Heuristics) ──┐
                    │
T1.5.x (Context) ───┤
                    │
T1.6.x (Analyzer) ──┼──> T4.x (Tool) ──> T5.x (Integration)
                    │         ↑
T2.x (Cache) ───────┤         │
                    │         │
T3.x (Authorizer) ──┘         │
        │                     │
        └──> T3.5.x (Channel) ─┘
```
