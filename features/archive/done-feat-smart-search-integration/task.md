# Smart Search Integration - 任务列表

## Phase 1: Tool 包装器
- [x] 创建 `anyclaw/tools/search.py`
- [x] 实现 `SearchFilesTool` 类继承 `Tool` 基类
- [x] 实现 `name`, `description`, `parameters` 属性
- [x] 实现 `execute` 方法

## Phase 2: 工具注册
- [x] 在 `agent/loop.py` 中导入 `SearchFilesTool`
- [x] 在 `_register_default_tools()` 中注册工具

## Phase 3: 权限修复
- [x] 修改 `PathAuthorizer.__init__()` 添加预授权
- [x] 添加 `_preauthorize_common_dirs()` 方法
- [x] 添加 `_load_from_config()` 方法
- [x] 修改 `is_authorized()` 支持 `allow_all` 模式

## Phase 4: 搜索路径扩展
- [x] 添加 `CODE_DIRS` 常量
- [x] 修改 `get_search_paths()` 对代码文件添加所有代码目录
- [x] 添加 `mycode`, `code`, `workspace` 到 `DEFAULT_PRIORITY_DIRS`

## Phase 5: 配置集成
- [x] 在 `settings.py` 添加搜索配置项
- [x] 在 `loader.py` 添加 `SecurityConfig` 字段
- [x] 在 `config.template.toml` 添加配置说明
- [x] 更新 `~/.anyclaw/config.toml`

## Phase 6: Empty 响应修复
- [x] 修改 `summary.py` 处理 LLM 返回 None
- [x] 修改 `logger.py` 对迭代摘要显示更多内容
- [x] 添加 `is_summary` 参数

## Phase 7: 测试验证
- [x] 测试工具导入
- [x] 测试工具注册
- [x] 测试搜索功能
- [x] 测试配置加载
