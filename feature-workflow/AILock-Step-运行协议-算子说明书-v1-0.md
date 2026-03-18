title: AILock-Step 运行协议 & 算子说明书 v1.0
author: Ryan Yang
date: 2026-03-04 16:33:30
tags:
---
# 📝 AILock-Step 运行协议 & 算子说明书 v1.0

## 1. 协议声明 (Protocol Declaration)

本协议定义了一种基于**状态锚点（STP）**的线性执行逻辑。执行器（AI）必须严格遵守 `[编号] [判断] [动作] [跳转]` 的单步逻辑，严禁在未收到 `-> STP-NEXT` 指令前进行跨步预测或语义扩充。

## 2. 语法解析定义 (Syntax Definitions)

* **`STP-[XXX]`**: 状态唯一标识符。执行指针必须停留在此处，直到动作完成。
* **`?? [Condition]`**: 逻辑门控。如果条件为 `VAL-NULL`（假），停止执行当前行并跳转至错误流。
* **`!! [Operator]`**: 原子算子。代表一个不可拆分的物理动作。
* **`>> [Target]`**: 数据流向。将左侧算子的输出压入右侧寄存器（`REG_`）。
* **`-> [Target_STP]`**: 强制跳转。唯一合法的逻辑演进路径。

---

## 3. 标准算子集 (Instruction Set)

| 算子 (Operator) | 参数 | 物理描述 (Action Description) |
| --- | --- | --- |
| **`OP_FS_READ`** | `(PATH)` | 物理读取文件系统内容。若路径不存在，返回 `VAL-NULL`。 |
| **`OP_FS_WRITE`** | `(PATH, CONTENT)` | 写入/覆盖指定路径文件。 |
| **`OP_CODE_GEN`** | `(CTX, TASK)` | 调用核心能力，基于上下文（CTX）实现具体任务（TASK）的代码。 |
| **`OP_ANALYSE`** | `(DATA, RULE)` | 结构化解析。将非结构化文档转化为 `REG_` 可识别的 Key-Value。 |
| **`OP_TASK_SYNC`** | `(ID, STATUS)` | 物理同步 `task.md` 状态。标记特定任务 ID 为 `done` 或 `error`。 |
| **`OP_GET_TOP`** | `(LIST, FILTER)` | 从列表寄存器中取出第一个符合过滤条件的项。 |
| **`OP_UI_NOTIFY`** | `(MSG)` | 向用户界面输出状态报告或询问确认。 |

---

## 4. 逻辑执行范例 (Implementation Flow)

### [Phase: Initialization]

* **STP-001** `?? OP_FS_READ("queue.yaml") CONTAINS("active") !! SET(REG_STATUS) >> "READY" -> STP-002`
* **STP-002** `?? CHECK_DIR("worktree/{ID}") == VAL-SET !! LOG("ENV_OK") -> STP-100`

### [Phase: Task Loop - 模拟非循环结构]

* **STP-300** `!! OP_FS_READ("task.md") >> REG_TASK_ALL -> STP-301`
* **STP-301** `?? REG_TASK_ALL HAS("open") !! OP_GET_TOP(REG_TASK_ALL, "open") >> REG_CUR_TASK -> STP-302`
* **STP-302** `!! OP_CODE_GEN(REG_SPEC, REG_CUR_TASK) >> REG_NEW_CODE -> STP-303`
* **STP-303** `!! OP_FS_WRITE(REG_CUR_TASK.path, REG_NEW_CODE) -> STP-304`
* **STP-304** `!! OP_TASK_SYNC(REG_CUR_TASK.id, "done") -> STP-300` *(回旋跳转，重新扫描任务)*

---

## 5. 异常处理 (Error Handling)

当任何 `??` 判断失败，且未定义 `STP-ERR` 路径时，执行器必须立即：

1. 停止所有物理写入操作。
2. 输出 `STATUS: ERROR` 并保留当前所有 `REG_` 寄存器快照。
3. 等待人工 `RESUME` 指令。

---


## 0. 方案优势分析 (Core Advantages)

执行器（AI）在加载本协议后，将获得以下维度的性能提升：

### 1. 彻底消除“幻觉性跳步” (Anti-Hallucination)

* **传统方案：** AI 看到 `for task in tasks` 时，往往会因为上下文窗口压力，自动简化中间步骤（如：“剩下的 5 个任务逻辑相似，已为您省略”）。
* **本协议方案：** 由于**禁止循环语义**，AI 必须通过 `STP-304 -> STP-300` 的物理跳转重新扫描任务列表。每一轮跳转都是一次全新的状态对齐，强迫 AI 保持 100% 的步骤完整性。

### 2. 状态可追溯与中断恢复 (Stateful Recovery)

* **传统方案：** 一旦生成中断（Token 溢出或网络报错），AI 很难找回“执行到哪了”。
* **本协议方案：** 每个 `STP` 节点都关联了 `REG_` 寄存器和物理存盘点（`OP_TASK_SYNC`）。即使执行中断，新会话只需读取 `task.md` 即可精准定位 `STP` 指针，实现**断点续传级**的开发。

### 3. 语义噪声屏蔽 (Semantic Noise Shielding)

* **传统方案：** AI 容易受到代码注释或需求文档中感性描述的影响，产生偏离目标的逻辑。
* **本协议方案：** 语法采用了**冷门符号逻辑 (`??`, `!!`, `>>`)**。这会触发 AI 的“指令解析模式”而非“文本续写模式”，使其将注意力集中在算子执行上，而非语义猜测。

### 4. 极端严格的依赖管理 (Strict Dependency Control)

* **传统方案：** AI 可能会在 `User` 模型还没建好时就去写 `Login` 接口。
* **本协议方案：** 通过 `STP` 序列硬性锁死执行路径。`STP-301` 的判断算子 `??` 充当了逻辑哨兵，如果前置任务未标记为 `done`，指针将永远无法移动至下一阶段。

---

## 如何将此优势转化为 Agent 指令？

在给其他 AI 的 Prompt 结尾，你可以加上这样一段话：

> **性能对齐：**
> “采用此 AILock-Step 协议是为了确保任务执行的**绝对幂等性**。你作为一个执行器，不需要理解任务的‘宏观意义’，只需确保每一个 `STP` 的 `REG_` 转换准确无误。如果你发现逻辑无法跳出 `STP-XXX`，请立即报告阻塞点，不要尝试自行修改跳转规则。”

---
