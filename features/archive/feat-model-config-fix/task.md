# feat-model-config-fix 任务分解

## 任务列表

### Task 1: 修复 CLI Channel 配置引用

**文件**: `anyclaw/channels/cli.py`

**修改内容**:
1. 在文件顶部添加导入:
   ```python
   from anyclaw.config.settings import settings
   ```
2. 第 204 行修改:
   ```python
   # 修改前
   config=self._config,
   # 修改后
   config=settings,
   ```

**验证**: 运行 `poetry run pytest tests/test_commands/ -v -k "cli"`

---

### Task 2: 修复 model.py 兼容 Settings 结构

**文件**: `anyclaw/commands/handlers/model.py`

**修改内容**:
第 61-62 行修改:
```python
# 修改前
current_model = getattr(config.llm, "model", "unknown") if hasattr(config, "llm") else "unknown"
current_provider = getattr(config.llm, "provider", "unknown") if hasattr(config, "llm") else "unknown"

# 修改后
if hasattr(config, "llm"):
    # Config 结构 (loader.py)
    current_model = getattr(config.llm, "model", "unknown")
    current_provider = getattr(config.llm, "provider", "unknown")
elif hasattr(config, "llm_model"):
    # Settings 结构 (settings.py)
    current_model = config.llm_model
    current_provider = config.llm_provider
else:
    current_model = "unknown"
    current_provider = "unknown"
```

**验证**: 运行 `poetry run pytest tests/test_commands/test_handlers.py -v -k "model"`

---

### Task 3: 手动验证

**步骤**:
1. 启动 CLI: `poetry run python -m anyclaw chat`
2. 输入 `/model`
3. 验证显示正确的模型配置（应与 `~/.anyclaw/config.toml` 一致）

---

## 依赖关系

```
Task 1 ──> Task 3
Task 2 ──> Task 3
```

Task 1 和 Task 2 可以并行执行，Task 3 在两者完成后执行。
