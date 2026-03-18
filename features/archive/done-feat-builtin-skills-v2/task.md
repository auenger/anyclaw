# 任务分解：内置技能扩展 V2

## 任务列表

### 任务 1：实现 code_exec 技能

**文件**: `anyclaw/skills/builtin/code_exec/skill.py`

**实现要点**:
- 继承 Skill 基类
- 支持 python、javascript、bash 三种语言
- 使用 subprocess 执行，设置超时
- 捕获 stdout、stderr
- 错误处理和返回格式化

**代码框架**:
```python
class CodeExecSkill(Skill):
    """Execute code in various languages"""

    async def execute(
        self,
        language: str = "python",
        code: str = "",
        timeout: int = 30,
        **kwargs
    ) -> str:
        # 根据语言选择执行器
        # 执行代码
        # 返回结果
```

---

### 任务 2：实现 process 技能

**文件**: `anyclaw/skills/builtin/process/skill.py`

**实现要点**:
- 支持动作：start、status、log、kill、list
- 使用 asyncio 管理后台进程
- session_id 生成和管理
- 进程状态追踪

**代码框架**:
```python
class ProcessSkill(Skill):
    """Manage background processes"""

    async def execute(
        self,
        action: str = "list",
        command: str = "",
        session_id: str = "",
        **kwargs
    ) -> str:
        if action == "start":
            # 启动后台进程
        elif action == "status":
            # 查询状态
        elif action == "log":
            # 获取输出
        elif action == "kill":
            # 终止进程
        elif action == "list":
            # 列出所有进程
```

---

### 任务 3：实现 text 技能

**文件**: `anyclaw/skills/builtin/text/skill.py`

**实现要点**:
- 支持动作：stats、extract、replace、format
- 使用正则表达式提取
- 统计功能：字符数、单词数、行数
- 格式转换

**代码框架**:
```python
class TextSkill(Skill):
    """Text processing utilities"""

    async def execute(
        self,
        action: str = "stats",
        text: str = "",
        pattern: str = "",
        replacement: str = "",
        target_format: str = "",
        **kwargs
    ) -> str:
        if action == "stats":
            # 统计信息
        elif action == "extract":
            # 正则提取
        elif action == "replace":
            # 搜索替换
        elif action == "format":
            # 格式转换
```

---

### 任务 4：实现 system 技能

**文件**: `anyclaw/skills/builtin/system/skill.py`

**实现要点**:
- 支持动作：info、env、which
- 使用 platform、psutil 获取系统信息
- 安全的环境变量访问（过滤敏感信息）

**代码框架**:
```python
class SystemSkill(Skill):
    """System information and operations"""

    async def execute(
        self,
        action: str = "info",
        command: str = "",
        **kwargs
    ) -> str:
        if action == "info":
            # 获取系统信息
        elif action == "env":
            # 获取环境变量
        elif action == "which":
            # 检查命令可用性
```

---

### 任务 5：实现 data 技能

**文件**: `anyclaw/skills/builtin/data/skill.py`

**实现要点**:
- 支持 JSON 和 YAML
- 支持动作：parse、query、convert、validate
- 使用 jsonpath-ng 进行查询
- 使用 jsonschema 进行验证

**代码框架**:
```python
class DataSkill(Skill):
    """JSON/YAML data processing"""

    async def execute(
        self,
        action: str = "parse",
        data: str = "",
        format: str = "json",
        query: str = "",
        target_format: str = "",
        schema: str = "",
        **kwargs
    ) -> str:
        if action == "parse":
            # 解析数据
        elif action == "query":
            # JSONPath 查询
        elif action == "convert":
            # 格式转换
        elif action == "validate":
            # Schema 验证
```

---

### 任务 6：编写测试

**文件**: `tests/test_skills_extended.py`

**测试覆盖**:
- 每个技能的基本功能测试
- 边界情况测试
- 错误处理测试
- 超时测试

---

### 任务 7：更新文档和配置

**文件**:
- `CLAUDE.md` - 更新技能列表
- `anyclaw/config/settings.py` - 添加技能相关配置（如需要）

---

## 依赖关系

```
任务 1-5: 并行实现（无依赖）
    ↓
任务 6: 测试（依赖 1-5）
    ↓
任务 7: 文档更新（依赖 6）
```

## 预计工作量

| 任务 | 预计时间 | 复杂度 |
|------|----------|--------|
| 任务 1: code_exec | 30 min | 中 |
| 任务 2: process | 45 min | 高 |
| 任务 3: text | 20 min | 低 |
| 任务 4: system | 15 min | 低 |
| 任务 5: data | 25 min | 中 |
| 任务 6: 测试 | 30 min | 中 |
| 任务 7: 文档 | 10 min | 低 |

**总计**: ~3 小时
