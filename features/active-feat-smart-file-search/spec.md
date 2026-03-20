# Smart File Search

## 概述

优化 Agent 查找文件和目录的策略，减少盲目搜索，提高搜索效率。

## 背景问题

从日志分析，当前 Agent 在查找文件时存在以下问题：

1. **盲目搜索** - 一上来就 `find ~ -maxdepth 3`，没有先问用户或检查常见位置
2. **重复搜索** - 多次尝试不同策略（find → ls → find），浪费时间和 token
3. **搜索范围过大** - `find /Users/ryan -maxdepth 4` 花了 5.8 秒
4. **安全机制拦截** - 最后找到了文件，却被 PathGuard 拦截

```log
[22:06:45] TOOL exec [2187ms]  find ~ -maxdepth 3 -name "sync_comments.py"  # 失败
[22:06:48] TOOL exec [32ms]   ls -la /Users/ryan/Desktop/ | grep -i sync    # 失败
[22:06:57] TOOL exec [5849ms] find /Users/ryan -maxdepth 4 -name "*.xlsx"   # 5.8秒！
[22:07:01] TOOL read_file    Path traversal detected - path must be within base directory  # 被拦截
```

## 用户价值点

### VP1: 智能搜索策略 (SearchHeuristics)

**价值**: 减少盲目搜索，优先检查最可能的位置

**Gherkin 场景**:
```gherkin
Feature: 智能搜索策略

  Scenario: 按优先级搜索文件
    Given 用户请求查找 "config.xlsx"
    When Agent 执行搜索
    Then 按以下顺序搜索:
      | 优先级 | 目录           | 说明               |
      | 1      | Downloads      | 下载文件默认位置   |
      | 2      | Desktop        | 桌面临时文件       |
      | 3      | Documents      | 文档目录           |
      | 4      | 当前项目目录   | 项目相关文件       |
      | 5      | 用户主目录     | 其他位置           |
    And 在找到第一个匹配后立即返回

  Scenario: 使用文件名模式优化搜索
    Given 用户请求查找 "*.xlsx" 文件
    When Agent 执行搜索
    Then 使用高效的搜索策略:
      - 优先使用操作系统索引（如 macOS Spotlight）
      - 限制搜索深度（maxdepth=3）
      - 排除缓存目录（.git, node_modules, Library）
```

### VP1.5: 信息不足时主动询问 (ProactiveQuery)

**价值**: 避免信息不足时的盲目搜索，主动收集关键信息

**Gherkin 场景**:
```gherkin
Feature: 信息不足主动询问

  Scenario: 文件名模糊时询问
    Given 用户请求 "帮我找个文件"
    And 未提供文件名或路径信息
    When Agent 分析请求
    Then 不执行搜索
    And 主动询问:
      """
      请提供更多信息：
      - 文件名是什么？（支持通配符，如 *.xlsx）
      - 大概在哪个目录？（Downloads / Desktop / 项目目录）
      - 文件类型？（文档 / 图片 / 代码）
      """

  Scenario: 搜索范围过大时确认
    Given 用户请求查找 "*.py"
    And 搜索范围可能超过 1000 个文件
    When Agent 准备搜索
    Then 先询问用户:
      """
      搜索范围较大，可能找到很多文件。
      是否限定在特定目录？
      - [当前项目] /Users/ryan/myproject
      - [Downloads] /Users/ryan/Downloads
      - [全部搜索]
      """

  Scenario: 有足够信息时直接搜索
    Given 用户请求 "找 Downloads 目录里的 report.xlsx"
    And 已提供文件名和目录
    When Agent 分析请求
    Then 直接执行搜索，不询问
```

### VP1.6: 对话上下文关联 (ContextAwareSearch)

**价值**: 利用对话历史中提到的路径，优先搜索相关目录

**Gherkin 场景**:
```gherkin
Feature: 对话上下文关联搜索

  Scenario: 优先搜索对话中提到的目录
    Given 对话历史中用户提到:
      """
      我在 /Users/ryan/projects/myapp 里有个配置文件
      """
    When 用户后续请求 "帮我找 config.yaml"
    Then 优先搜索 /Users/ryan/projects/myapp
    And 搜索顺序为:
      | 优先级 | 目录                          |
      | 1      | /Users/ryan/projects/myapp   | (对话上下文)
      | 2      | Downloads                     |
      | 3      | Desktop                       |
      | 4      | 其他默认目录                  |

  Scenario: 提取多个上下文路径
    Given 对话历史中提到多个路径:
      - "/Users/ryan/projects/myapp/src"
      - "/Users/ryan/projects/myapp/config"
    When 用户请求查找 "settings.json"
    Then 合并上下文路径到搜索优先级:
      | 优先级 | 目录                                    |
      | 1      | /Users/ryan/projects/myapp/config      |
      | 2      | /Users/ryan/projects/myapp/src         |
      | 3      | /Users/ryan/projects/myapp (父目录)    |
      | 4      | 默认目录                                |

  Scenario: 无上下文时使用默认策略
    Given 对话历史中未提到任何路径
    When 用户请求查找文件
    Then 使用默认搜索优先级（VP1）

  Scenario: 上下文路径过期
    Given 对话历史中提到的路径距今超过 10 轮对话
    When 用户请求查找文件
    Then 降低该路径的优先级
    Or 忽略该上下文路径
```

### VP2: 搜索缓存 (SearchCache)

**价值**: 记住常用目录和最近访问的文件，避免重复搜索

**Gherkin 场景**:
```gherkin
Feature: 搜索缓存

  Scenario: 缓存成功找到的文件位置
    Given Agent 成功找到文件 "/Users/ryan/Downloads/report.xlsx"
    When 后续请求查找类似文件
    Then 优先在缓存目录中搜索
    And 显示缓存命中率统计

  Scenario: 缓存常用目录
    Given 用户频繁访问 "/Users/ryan/projects/myapp"
    When 该目录被访问超过 3 次
    Then 将其添加到常用目录缓存
    And 后续搜索优先检查常用目录

  Scenario: 缓存过期
    Given 缓存中有条目超过 24 小时未使用
    When 执行缓存清理
    Then 移除过期条目
    And 保留最近使用的条目
```

### VP3: 动态路径授权 (DynamicPathAuthorization)

**价值**: 在安全限制下，允许用户临时授权访问特定目录，支持多渠道交互

**跨渠道授权设计**:

| 渠道 | 交互方式 | 用户体验 |
|------|----------|----------|
| CLI | 交互式菜单 (rich.prompt) | 键盘选择 y/p/n |
| Discord | Button 组件 | 点击按钮授权 |
| 飞书 | 交互式卡片 | 点击卡片按钮 |
| 其他 | 回复式授权 | 回复 y/p/n |

**Gherkin 场景**:
```gherkin
Feature: 动态路径授权

  Scenario: CLI 渠道交互式授权
    Given 用户通过 CLI 渠道使用 Agent
    And Agent 尝试访问 "/Users/ryan/Downloads/report.xlsx"
    And 该目录不在允许列表中
    When PathGuard 拦截访问
    Then 显示交互式菜单:
      """
      ┌─ 需要授权 ─────────────────────────────────┐
      │ 访问 /Users/ryan/Downloads 需要授权        │
      │                                             │
      │ [y] 临时授权  [p] 永久授权  [n] 拒绝        │
      │                                             │
      │ 选择: _                                     │
      └─────────────────────────────────────────────┘
      """
    When 用户输入 "y"
    Then 临时授权成功
    And 继续执行原任务

  Scenario: Discord 渠道按钮授权
    Given 用户通过 Discord 渠道使用 Agent
    And Agent 尝试访问受限目录
    When PathGuard 拦截访问
    Then 发送带按钮的消息:
      """
      🤖 AnyClaw
      ━━━━━━━━━━━━━━━━━━━━
      🔐 访问 /Users/ryan/Downloads 需要授权

      [✅ 临时授权] [🔒 永久授权] [❌ 拒绝]
      """
    When 用户点击 "✅ 临时授权" 按钮
    Then Bot 处理授权
    And 继续执行原任务

  Scenario: 飞书渠道卡片授权
    Given 用户通过飞书渠道使用 Agent
    And Agent 尝试访问受限目录
    When PathGuard 拦截访问
    Then 发送交互式卡片:
      """
      ┌─────────────────────────────────┐
      │ 🔐 需要授权                      │
      │                                  │
      │ 访问 /Users/ryan/Downloads       │
      │ 需要您的授权                     │
      │                                  │
      │ [临时授权] [永久授权] [拒绝]      │
      └─────────────────────────────────┘
      """
    When 用户点击卡片按钮
    Then 处理授权并继续执行

  Scenario: 回复式授权（回退方案）
    Given 渠道不支持交互式组件
    And Agent 尝试访问受限目录
    When PathGuard 拦截访问
    Then 显示文本提示:
      """
      🔐 需要授权访问 /Users/ryan/Downloads
      回复 y(临时) / p(永久) / n(拒绝)
      """
    When 用户回复 "y"
    Then 授权成功并继续执行

  Scenario: 危险路径永久拒绝
    Given Agent 尝试访问 "~/.ssh/id_rsa"
    When PathGuard 检测到危险路径
    Then 直接拒绝，不提示授权:
      """
      ❌ 禁止访问敏感路径: ~/.ssh
      此目录包含安全凭证，不允许授权访问。
      """
    And 不提供授权选项

  Scenario: 持久化授权
    Given 用户选择 "永久授权"
    When 授权被添加
    Then 写入配置文件 path_extra_allowed_dirs
    And 下次启动时自动加载
```

### VP4: 搜索工具增强 (EnhancedSearchTool)

**价值**: 提供更智能的搜索工具，减少 shell 命令使用

**Gherkin 场景**:
```gherkin
Feature: 搜索工具增强

  Scenario: 使用 search_files 工具
    Given Agent 需要查找文件
    When 使用 search_files 工具
    Then 工具提供以下参数:
      | 参数          | 说明                       |
      | pattern       | 文件名模式（支持通配符）   |
      | search_paths  | 指定搜索路径（可选）       |
      | file_type     | 文件类型（file/dir/any）   |
      | max_depth     | 最大搜索深度（默认 3）     |
      | use_cache     | 是否使用缓存（默认 true）  |

  Scenario: 搜索结果格式化
    Given search_files 工具找到 5 个文件
    When 返回结果
    Then 格式化输出:
      """
      找到 5 个匹配文件（搜索用时 0.3s，缓存命中 2 个）:

      1. /Users/ryan/Downloads/report.xlsx (1.2 MB)
      2. /Users/ryan/Desktop/data.xlsx (500 KB)
      3. ...
      """
```

## 非功能性需求

### 性能
- 单次搜索应在 2 秒内完成（本地文件系统）
- 缓存命中应在 100ms 内返回

### 安全
- 所有搜索路径仍需通过 PathGuard 验证
- 临时授权不绕过危险路径检查（如 /etc, ~/.ssh）

### 可配置性
- 搜索优先级目录列表可配置
- 缓存大小和过期时间可配置
- 动态授权模式可开关

## 技术方案

### 核心组件

1. **SearchHeuristics** - 搜索启发式规则引擎
   - 默认优先级目录列表
   - 文件类型关联目录（.xlsx → Downloads）
   - 项目上下文感知

2. **ContextPathExtractor** - 对话上下文路径提取器（新增）
   - 从对话历史中提取路径信息
   - 路径优先级排序（最近提到 > 较早提到）
   - 上下文过期机制（超过 10 轮对话降权）

3. **SearchQueryAnalyzer** - 搜索请求分析器（新增）
   - 判断信息是否充足
   - 识别模糊请求 vs 精确请求
   - 生成询问问题模板

4. **SearchCache** - 搜索缓存管理器
   - 最近访问文件记录（LRU，最多 100 条）
   - 常用目录缓存（访问次数 > 3）
   - 24 小时过期策略

5. **PathAuthorizer** - 动态路径授权器
   - 会话级临时授权（内存）
   - 持久化授权（写入配置）
   - 危险路径黑名单（~/.ssh, /etc/passwd 等）
   - 线程安全设计

6. **SearchFilesTool** - 增强搜索工具
   - 替代盲目 find 命令
   - 集成缓存和启发式
   - 格式化输出
   - 信息不足时返回询问建议

### 跨渠道授权架构

```
┌─────────────────────────────────────────────────────────────┐
│                      AgentLoop                              │
│                         │                                   │
│                    Tool 执行                                │
│                         │                                   │
│                    PathGuard                                │
│                         │                                   │
│              ┌──────────┴──────────┐                        │
│              │ 路径在允许范围内?    │                        │
│              └──────────┬──────────┘                        │
│                    │    │                                   │
│               Yes  │    │ No                                │
│                    ▼    ▼                                   │
│                 继续   抛出 AuthorizationRequiredError       │
│                              │                              │
│                              ▼                              │
│                    ┌─────────────────┐                      │
│                    │     Channel     │                      │
│                    │  (CLI/Discord/  │                      │
│                    │   Feishu/...)   │                      │
│                    └────────┬────────┘                      │
│                             │                               │
│              ┌──────────────┼──────────────┐                │
│              │              │              │                │
│              ▼              ▼              ▼                │
│         CLI 渠道      Discord 渠道    飞书渠道              │
│         rich.prompt   Button 组件    交互式卡片             │
│              │              │              │                │
│              └──────────────┼──────────────┘                │
│                             │                               │
│                             ▼                               │
│                    用户授权决策                              │
│                    (session/persist/deny)                   │
│                             │                               │
│                             ▼                               │
│                    PathAuthorizer.authorize()               │
│                             │                               │
│                             ▼                               │
│                      继续执行任务                           │
└─────────────────────────────────────────────────────────────┘
```

### 关键类设计

```python
# anyclaw/search/authorizer.py

class AuthorizationRequiredError(Exception):
    """需要授权异常 - 携带授权上下文"""
    def __init__(self, path: Path, suggested_dir: Path):
        self.path = path
        self.suggested_dir = suggested_dir


class PathAuthorizer:
    # 危险路径黑名单
    DANGEROUS_PATHS = {
        Path.home() / ".ssh",
        Path.home() / ".gnupg",
        Path("/etc/passwd"),
        Path("/etc/shadow"),
    }

    def authorize(self, dir_path: Path, persist: bool = False) -> bool: ...
    def is_authorized(self, dir_path: Path) -> bool: ...
    def is_dangerous(self, dir_path: Path) -> bool: ...


# anyclaw/channels/base.py

class BaseChannel(ABC):
    @abstractmethod
    async def request_authorization(
        self,
        error: AuthorizationRequiredError
    ) -> Optional[str]:
        """请求用户授权，返回 'session'/'persist'/'deny'/None"""
        pass


# anyclaw/channels/cli.py

class CLIChannel(BaseChannel):
    async def request_authorization(self, error) -> Optional[str]:
        from rich.prompt import Prompt
        choice = Prompt.ask(
            f"[yellow]🔐 需要授权[/] 访问 {error.suggested_dir}",
            choices=["y", "p", "n"],
            default="y"
        )
        return {"y": "session", "p": "persist", "n": "deny"}.get(choice)


# anyclaw/channels/discord.py

class DiscordChannel(BaseChannel):
    async def request_authorization(self, error) -> Optional[str]:
        view = AuthorizationButtons(error.suggested_dir)
        await self.send_message(
            f"🔐 需要授权访问 `{error.suggested_dir}`",
            view=view
        )
        return await view.wait_for_click()
```

### 文件结构

```
anyclaw/
├── search/
│   __init__.py
│   heuristics.py      # SearchHeuristics
│   context.py         # ContextPathExtractor (新增)
│   analyzer.py        # SearchQueryAnalyzer (新增)
│   cache.py           # SearchCache
│   authorizer.py      # PathAuthorizer + AuthorizationRequiredError
│   └── tool.py        # SearchFilesTool
├── channels/
│   base.py            # BaseChannel.request_authorization() (新增)
│   cli.py             # CLIChannel 交互式菜单
│   discord.py         # DiscordChannel Button 组件
│   └── feishu.py      # FeishuChannel 交互式卡片
└── security/
    └── path.py        # PathGuard 集成 AuthorizationRequiredError
```

### 新增关键类设计

```python
# anyclaw/search/context.py

import re
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class ContextPath:
    """对话上下文中提取的路径"""
    path: Path
    mention_turn: int      # 提到的对话轮次
    mention_count: int     # 提到次数


class ContextPathExtractor:
    """从对话历史中提取路径信息"""

    # 路径匹配模式
    PATH_PATTERNS = [
        r'/[\w/.-]+',                    # Unix 绝对路径
        r'~/[\w/.-]+',                   # 用户目录
        r'[A-Z]:\\[\w\\.-]+',            # Windows 路径
        r'\./[\w/.-]+',                  # 相对路径
    ]

    def __init__(self, max_context_turns: int = 10):
        self.max_context_turns = max_context_turns

    def extract_from_history(self, messages: List[dict]) -> List[ContextPath]:
        """从对话历史提取路径，按优先级排序"""
        ...

    def get_priority_paths(self, messages: List[dict]) -> List[Path]:
        """获取优先搜索路径列表"""
        context_paths = self.extract_from_history(messages)
        # 按新鲜度排序（最近提到优先）
        # 过滤过期路径（超过 max_context_turns）
        ...


# anyclaw/search/analyzer.py

from dataclasses import dataclass
from typing import Optional, List

@dataclass
class SearchQuery:
    """解析后的搜索请求"""
    pattern: Optional[str]           # 文件名模式
    directory: Optional[Path]        # 指定目录
    file_type: Optional[str]         # 文件类型
    is_specific: bool                # 是否足够具体


@dataclass
class QuerySuggestion:
    """询问建议"""
    questions: List[str]             # 需要询问的问题
    suggested_dirs: List[Path]       # 建议的目录选项


class SearchQueryAnalyzer:
    """分析搜索请求，判断信息是否充足"""

    def analyze(self, user_request: str, context_paths: List[Path]) -> SearchQuery:
        """分析用户请求"""
        ...

    def needs_more_info(self, query: SearchQuery) -> Optional[QuerySuggestion]:
        """判断是否需要更多信息"""
        # 无文件名 → 需要询问
        # 模式太宽泛 (*.py) + 范围大 → 建议限定目录
        ...

    def is_ambiguous(self, query: SearchQuery) -> bool:
        """判断请求是否模糊"""
        # "找个文件" → True
        # "找 report.xlsx" → False
        ...
```

## 风险和缓解

| 风险 | 缓解措施 |
|------|----------|
| 缓存污染（错误路径） | 缓存条目验证 + TTL |
| 授权滥用 | 临时授权仅当前会话 + 危险路径黑名单 |
| 性能回退 | 缓存失效时回退到原搜索方式 |
| Discord/飞书授权超时 | 设置 60s 超时，超时视为拒绝 |
| 渠道能力不一致 | 提供回退方案（回复式授权） |
| 授权状态同步 | PathAuthorizer 单例模式，全局共享 |
| 上下文路径提取误判 | 使用正则 + 验证路径存在性 |
| 过度询问影响体验 | 设置询问阈值，信息充足时直接搜索 |

## 依赖

- 无外部依赖
- 依赖现有 PathGuard 安全框架

## 参考

- 日志分析：用户提供的搜索日志
- 类似实现：macOS Spotlight, Windows Search Indexer
