# Smart Search Integration - 验收检查清单

## 功能验收

### 搜索工具可用性
- [x] `search_files` 工具在工具列表中可见
- [x] LLM 可以调用 `search_files` 工具
- [x] 搜索返回正确的结果

### 权限控制
- [x] `search_allow_all_paths = true` 时可搜索所有非危险路径
- [x] `search_allow_all_paths = false` 时仅搜索授权目录
- [x] 危险路径（~/.ssh, /etc/passwd）永远不可搜索
- [x] `search_extra_allowed_dirs` 配置生效

### 搜索路径
- [x] 代码文件（.py）可搜索 mycode, code, projects, workspace
- [x] 下载文件（.xlsx）优先搜索 Downloads
- [x] 文档文件（.pdf）优先搜索 Documents

### 配置加载
- [x] 配置文件正确加载
- [x] 配置项可通过 `settings` 访问
- [x] 配置模板包含所有搜索配置项

### Empty 响应修复
- [x] LLM 返回 None 时生成降级汇报
- [x] 迭代摘要日志显示更多内容
- [x] 不再出现 `(empty)` 响应

## 代码质量

- [x] 新代码有类型注解
- [x] 使用 Black 格式化
- [x] 现有测试通过

## 文档

- [x] spec.md 包含完整修复说明
- [x] task.md 包含任务列表
- [x] config.template.toml 包含配置说明
