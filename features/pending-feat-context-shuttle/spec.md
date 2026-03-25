# 上下文穿梭 (Context Shuttle)

> 一种创新的上下文管理策略，通过"思考-压缩-执行"模式减少 Token 消耗

## 背景

### 当前问题

传统 AI Agent 每次对话都需要：
1. 在 System Prompt 中携带所有技能的 description
2. 技能列表随对话累积，每轮都重复加载
3. 上下文随对话轮次线性增长

```
传统模式（累积式）:
Round 1: [Skills 全部 1700] + [User Msg 1] = 1800 tokens
Round 2: [Skills 全部 1700] + [Msg 1] + [Msg 2] = 2000 tokens
Round 3: [Skills 全部 1700] + [Msg 1-2] + [Msg 3] = 2200 tokens
                          ↑
                     每次都重复加载，累积增长
```

### 核心洞察

1. **技能列表是临时的** - 选择完成后可以删除
2. **选择过程不必要保留** - "我选择 X 因为 Y" 可以压缩成精简摘要
3. **前缀缓存友好** - 保持 History 不变可以最大化缓存命中

---

## 设计理念：上下文穿梭

**核心思想**：把"技能选择"作为一个**内部思考过程**，穿梭后删除技能列表，只保留决策结果。

```
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│ 阶段 1: 技能选择（临时上下文 - 不写入历史）                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Temp Context:                                                  │
│  ┌───────────────────────────────────────────────────────┐     │
│  │ History: [msg1, msg2]                                 │     │
│  ├───────────────────────────────────────────────────────┤     │
│  │ 技能摘要列表 (临时，会被删除！):                        │     │
│  │ - commit: 提交代码到 Git 仓库                          │     │
│  │ - pdf: 处理 PDF 文档，支持创建/合并/拆分               │     │
│  │ - loop: 循环执行任务，支持定时调度                      │     │
│  │ - documents: 文档处理，支持 DOCX/XLSX/PPTX             │     │
│  │ ...                                                   │     │
│  │ 请分析用户需求，选择需要的技能                          │     │
│  └───────────────────────────────────────────────────────┘     │
│                         ↓                                       │
│  LLM: "我需要以下技能:                                          │
│        1. commit - 因为用户要提交代码                           │
│        2. pdf - 因为用户要生成 PDF 文档"                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                           │
                           │ 🔮 穿梭（删除技能列表，只留决策）
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ 阶段 2: 正式执行（结果写入历史）                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Final Context:                                                 │
│  ┌───────────────────────────────────────────────────────┐     │
│  │ History: [msg1, msg2]                                 │ ← 不变
│  ├───────────────────────────────────────────────────────┤     │
│  │ 决策摘要 (进入历史):                                   │     │
│  │ "已选择: commit, pdf                                   │     │
│  │  原因: 提交代码并生成 PDF 文档"                         │     │
│  ├───────────────────────────────────────────────────────┤     │
│  │ 选中技能完整内容 (临时):                                │     │
│  │ commit: ...完整用法说明...                             │     │
│  │ pdf: ...完整用法说明...                                │     │
│  └───────────────────────────────────────────────────────┘     │
│                         ↓                                       │
│  LLM: 执行实际操作...                                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**关键点**：
- 技能列表需要 **description**（LLM 需要知道干嘛的才能选择）
- 穿梭后**整个技能列表删除**，不进入历史
- 只有精简的决策摘要进入历史

---

## 技术方案

### 1. 技能摘要列表（含 description）

LLM 需要知道每个技能是干嘛的才能做选择：

```xml
<skills>
  <skill name="commit">
    提交代码到 Git 仓库
  </skill>
  <skill name="pdf">
    处理 PDF 文档，支持创建/合并/拆分/提取
  </skill>
  <skill name="loop">
    循环执行任务，支持定时调度
  </skill>
  <skill name="documents">
    文档处理，支持 DOCX/XLSX/PPTX
  </skill>
  ...
</skills>

请分析用户需求，选择需要的技能
```

### 2. LLM 自然语言回答选择

不需要 skill.select 工具，LLM 直接用自然语言回答：

```
用户: "帮我提交代码并生成 PDF"

LLM 思考后回答:
┌────────────────────────────────────────────────────────────┐
│ 我需要以下技能:                                             │
│                                                            │
│ 1. commit - 因为用户要提交代码到 Git                        │
│ 2. pdf - 因为用户要生成 PDF 文档                            │
│                                                            │
│ 不需要 loop、documents 等其他技能                           │
└────────────────────────────────────────────────────────────┘
```

然后解析这个回答，提取出 `["commit", "pdf"]`。

### 3. 穿梭流程实现

```python
async def process_with_shuttle(self, user_input: str) -> str:
    """带穿梭的处理流程"""

    # ========== 阶段 1: 技能选择（不写入历史） ==========

    # 构建技能摘要 (name + description)
    skill_summary = self.loader.build_skill_summary()  # XML 格式，含 description

    selection_context = self.history.get_history() + [
        {"role": "system", "content": skill_summary},
        {"role": "system", "content": "请分析用户需求，选择需要的技能"},
        {"role": "user", "content": user_input}
    ]

    selection_response = await self.llm.call(selection_context)
    # "我需要 commit 和 pdf，因为..."

    # 解析选择结果
    selected = self._parse_skill_selection(selection_response)
    # {"skills": ["commit", "pdf"], "reason": "提交代码并生成 PDF"}

    # ========== 🔮 穿梭点：删除技能列表，只留决策 ==========

    # 加载选中技能的完整内容
    skill_contents = self.loader.load_skills_for_context(selected["skills"])

    # 构建决策摘要（替代整个技能列表）
    decision_summary = f"已选择: {', '.join(selected['skills'])}\n原因: {selected['reason']}"

    # ========== 阶段 2: 正式执行 ==========

    # 注意：不包含 skill_summary！已删除
    execution_context = self.history.get_history() + [
        {"role": "system", "content": decision_summary},   # 精简决策
        {"role": "system", "content": skill_contents},     # 选中技能完整内容
        {"role": "user", "content": user_input}
    ]

    final_response = await self.llm.call(execution_context)

    # 写入历史（只有 user + response，没有技能列表）
    self.history.add_user(user_input)
    self.history.add_assistant(final_response)

    return final_response
```

### 4. 会话级缓存

已选择的技能在当前会话中缓存，避免重复加载：

```python
class SessionSkillCache:
    """会话级技能缓存"""

    def __init__(self):
        self.loaded_skills: Dict[str, str] = {}  # skill_name -> content

    def get(self, skill_name: str) -> Optional[str]:
        return self.loaded_skills.get(skill_name)

    def set(self, skill_name: str, content: str):
        self.loaded_skills[skill_name] = content

    def get_all_loaded(self) -> Dict[str, str]:
        return self.loaded_skills.copy()

    def has(self, skill_name: str) -> bool:
        return skill_name in self.loaded_skills
```

---

## Token 节省分析

假设 17 个技能，每个 description 平均 30 tokens，完整内容平均 100 tokens：

```
┌─────────────────────────────────────────────────────────────────┐
│                      传统模式 vs 穿梭模式                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  传统模式 (累积)                    穿梭模式 (压缩)              │
│  ════════════════                   ════════════════            │
│                                                                 │
│  Round 1:                          Round 1:                     │
│  ┌─────────────────────┐           ┌─────────────────────┐      │
│  │ Skills: 1700 tokens │           │ 选择阶段:            │      │
│  │ User: 100 tokens    │           │   Skills: 500       │ ← 有description │
│  │ ─────────────────── │           │   User: 100         │   但穿梭后删除
│  │ Total: 1800         │           │   LLM选择: 100      │      │
│  └─────────────────────┘           │ ─────────────────── │      │
│                                    │ 执行阶段:            │      │
│                                    │   决策: 50          │ ← 精简摘要
│                                    │   选中技能: 200     │      │
│                                    │   User: 100         │      │
│                                    │ Total: 1050         │      │
│                                    └─────────────────────┘      │
│                                                                 │
│  Round 2:                          Round 2:                     │
│  ┌─────────────────────┐           ┌─────────────────────┐      │
│  │ Skills: 1700        │           │ 选择阶段:            │      │
│  │ Round1: 200         │           │   Skills: 500       │      │
│  │ User: 100           │           │   Hist: 200         │      │
│  │ ─────────────────── │           │ ─────────────────── │      │
│  │ Total: 2000         │           │ 执行阶段:            │      │
│  └─────────────────────┘           │   决策: 50          │      │
│                                    │   技能(缓存): 0     │ ← 命中缓存!
│                                    │   Hist: 200         │      │
│                                    │   User: 100         │      │
│                                    │ Total: 850          │      │
│                                    └─────────────────────┘      │
│                                                                 │
│  3 轮合计: ~6000 tokens            3 轮合计: ~3000 tokens       │
│                                    节省: ~50%                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Token 节省来源**：
1. 技能列表不进入历史（每轮省 ~1200 tokens）
2. 决策摘要替代完整选择过程
3. 选中技能可缓存（后续轮次省更多）

---

## 与现有机制的关系

### 与 Always Skills

- Always 技能**自动预加载**，不参与穿梭选择
- 穿梭只处理非 Always 技能
- 检测已加载技能，避免重复

### 与上下文压缩 (feat-context-compression)

- 压缩处理**对话历史**（旧消息摘要）
- 穿梭处理**技能加载**（按需选择）
- 两者互补，可叠加使用

### 与前缀缓存

```
传统模式（每次变化）:
Round 1: [System 1700] + [History]  → 缓存 A
Round 2: [System 1700] + [History+] → 缓存可能失效

穿梭模式（History 不变）:
Round 1: [History] + [临时技能选择] → 选择过程不缓存
Round 2: [History] + [已选技能]     → History 部分命中缓存
```

---

## 配置项

```toml
[context_shuttle]
enabled = true                    # 启用穿梭模式
cache_across_session = false      # 跨会话缓存（默认关闭）
max_shuttles_per_turn = 3         # 每轮最大穿梭次数
```

---

## 验收标准

### 功能验收

```gherkin
Feature: 上下文穿梭

Scenario: 首次对话技能选择
  Given 用户发送 "帮我提交代码并生成 PDF"
  When Agent 处理消息
  Then 应触发技能选择阶段
  And 技能列表包含 description 信息
  And 穿梭后历史中只包含决策摘要
  And 历史中不包含完整技能列表

Scenario: 已缓存技能跳过加载
  Given 当前会话已加载 commit 技能
  When 用户再次请求提交相关操作
  Then commit 技能应命中缓存
  And 不应重复加载 commit 完整内容

Scenario: Always 技能自动预加载
  Given save_memory 标记为 always=true
  When 任何用户消息
  Then save_memory 自动包含在上下文中
  And 不参与穿梭选择

Scenario: 技能列表不累积
  Given 执行 3 轮对话
  When 每轮都选择不同技能
  Then 历史中只包含每轮的决策摘要
  And 历史中不包含任何技能列表
```

### 性能验收

```gherkin
Scenario: Token 节省验证
  Given 17 个可用技能
  When 执行 3 轮对话
  Then 累计 Token 消耗应低于传统模式的 60%
```

---

## 风险与缓解

| 风险 | 缓解措施 |
|------|---------|
| LLM 选择错误技能 | 保留用户可手动指定技能的机制 |
| 两阶段请求延迟 | 技能缓存减少后续加载；选择阶段 token 少 |
| 选择解析失败 | 使用正则 + LLM 结构化输出双重保障 |

---

## 后续扩展

1. **智能预测**：基于用户输入关键词预测可能技能，跳过选择阶段
2. **技能组合模板**：常用场景预定义技能组合
3. **穿梭可视化**：在 UI 中展示穿梭过程和决策
