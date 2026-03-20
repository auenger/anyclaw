# Smart Search Integration - 智能搜索工具集成修复

## 概述

将智能文件搜索模块（`anyclaw/search/`）正确集成到工具系统中，使其可以被 LLM 调用。

## 背景

智能文件搜索功能已经实现（`done-feat-smart-file-search`），但存在以下问题：
1. `SearchFilesTool` 类不是 `Tool` 基类的子类，无法被工具注册表识别
2. 没有在 `AgentLoop` 中注册搜索工具
3. `PathAuthorizer` 默认不授权任何目录，导致搜索立即返回空结果
4. 达到迭代限制时返回空响应或被截断

## 修复内容

### 1. 创建 SearchFilesTool 包装器

**文件**: `anyclaw/tools/search.py`

将内部 `SearchFilesTool` 包装为符合 `Tool` 基类接口的工具：

```python
class SearchFilesTool(Tool):
    @property
    def name(self) -> str:
        return "search_files"

    @property
    def description(self) -> str:
        return """智能文件搜索工具..."""

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "文件名模式"},
                "search_paths": {"type": "array", "items": {"type": "string"}},
                "max_depth": {"type": "integer", "default": 3},
                "use_cache": {"type": "boolean", "default": True},
            },
            "required": ["pattern"],
        }

    async def execute(self, pattern: str, ...) -> str:
        # 调用内部搜索工具
```

### 2. 注册到 AgentLoop

**文件**: `anyclaw/agent/loop.py`

```python
from anyclaw.tools.search import SearchFilesTool

def _register_default_tools(self) -> None:
    # ... 其他工具 ...

    # 智能文件搜索工具
    self.tools.register(SearchFilesTool(
        workspace=self.workspace,
        timeout=getattr(settings, 'search_timeout', 5.0),
        max_depth=getattr(settings, 'search_max_depth', 3),
    ))
```

### 3. PathAuthorizer 预授权

**文件**: `anyclaw/search/authorizer.py`

1. 预授权常用目录：
   - ~/Downloads
   - ~/Desktop
   - ~/Documents
   - ~/mycode
   - ~/code
   - ~/workspace
   - ~/

2. 集成配置系统：
   - `search_allow_all_paths`: 允许搜索所有非危险路径
   - `search_extra_allowed_dirs`: 额外允许的目录

```python
def _load_from_config(self) -> None:
    # 1. 检查 search_allow_all_paths
    self._allow_all = getattr(settings, 'search_allow_all_paths', True)

    # 2. 加载额外允许目录
    search_extra_dirs = getattr(settings, 'search_extra_allowed_dirs', [])
    for dir_str in search_extra_dirs:
        path = Path(dir_str).expanduser().resolve()
        if not self.is_dangerous(path):
            self._session_allowed_dirs.add(path)

def is_authorized(self, path: Path) -> bool:
    # 全开放模式：允许所有非危险路径
    if self._allow_all:
        return True
    # ...
```

### 4. 扩展搜索路径

**文件**: `anyclaw/search/heuristics.py`

添加更多代码目录：

```python
DEFAULT_PRIORITY_DIRS = [
    "Downloads",
    "Desktop",
    "Documents",
    "mycode",    # 新增
    "code",      # 新增
    "projects",
    "workspace", # 新增
    "",
]

CODE_DIRS = ["mycode", "code", "projects", "workspace", "src", "repos"]
```

### 5. 配置系统更新

**文件**: `anyclaw/config/settings.py`

```python
# 搜索工具配置
search_allow_all_paths: bool = True
search_extra_allowed_dirs: List[str] = []
search_max_depth: int = 4
search_timeout: float = 10.0
```

**文件**: `anyclaw/config/loader.py`

```python
class SecurityConfig(BaseModel):
    # 搜索工具配置
    search_allow_all_paths: bool = True
    search_extra_allowed_dirs: List[str] = []
    search_max_depth: int = 4
    search_timeout: float = 10.0
```

### 6. Empty 响应修复

**文件**: `anyclaw/agent/summary.py`

```python
async def _call_llm(self, prompt: str) -> str:
    try:
        response = await acompletion(**kwargs)
        content = response.choices[0].message.content
        if content is None:
            return self._generate_simple_summary_fallback(max_iterations)
        return content
    except Exception as e:
        return self._generate_simple_summary_fallback(max_iterations)
```

**文件**: `anyclaw/agent/logger.py`

```python
def log_assistant_response(self, content: str, model: str = None, is_summary: bool = False):
    if is_summary:
        # 迭代摘要显示最多 2000 字符
        if len(content) > 2000:
            truncated = content[:2000] + "..."
```

## 配置项

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `search_allow_all_paths` | bool | true | 允许搜索所有非危险路径 |
| `search_extra_allowed_dirs` | list | [] | 额外允许搜索的目录 |
| `search_max_depth` | int | 4 | 默认搜索深度 |
| `search_timeout` | float | 10.0 | 默认搜索超时（秒） |

## 测试结果

```
Search config:
  search_allow_all_paths: True
  search_extra_allowed_dirs: []
  search_max_depth: 4
  search_timeout: 10.0

Tool: search_files
Result: 找到 4 个匹配文件（搜索用时 3.5s）:
  1. /Users/ryan/mycode/HRExcel/pyexcel/sync_comments.py
  ...
```

## 影响范围

- `anyclaw/tools/search.py` (新增)
- `anyclaw/agent/loop.py` (修改)
- `anyclaw/search/authorizer.py` (修改)
- `anyclaw/search/heuristics.py` (修改)
- `anyclaw/config/settings.py` (修改)
- `anyclaw/config/loader.py` (修改)
- `anyclaw/config/config.template.toml` (修改)
- `anyclaw/agent/summary.py` (修改)
- `anyclaw/agent/logger.py` (修改)
