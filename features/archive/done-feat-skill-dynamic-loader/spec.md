# Feature: Skill 动态加载修复

## 概述

修复 AnyClaw Skill 系统的动态加载问题，支持从任意路径加载 Python skill，支持热重载和 .skill 文件安装。

**优先级**: 80 (高)
**大小**: M
**依赖**: feat-skill-toolkit

## 背景与动机

当前 AnyClaw 的 Python skill 加载存在严重问题：

**问题代码** (`anyclaw/skills/loader.py:75`):
```python
module_name = f"anyclaw.skills.builtin.{skill_path.name}.skill"
module = importlib.import_module(module_name)
```

这导致：
- 只能加载 `anyclaw.skills.builtin.*` 下的 skill
- workspace 目录下的 Python skill 无法被识别
- 用户自定义路径的 skill 无法加载
- 不支持运行时热重载

## 用户价值点

### VP1: 任意路径 Python Skill 加载

支持从任意目录加载 Python skill。

```gherkin
Feature: 任意路径加载

  Scenario: 加载 workspace skill
    Given 用户在 ~/.anyclaw/workspace/skills/my-helper/ 有 skill.py
    When SkillLoader 扫描 skills 目录
    Then my-helper skill 被正确加载
    And skill 实例可用

  Scenario: 加载 managed skill
    Given 用户在 ~/.anyclaw/managed-skills/custom-tool/ 有 skill.py
    When SkillLoader 扫描 managed 目录
    Then custom-tool skill 被正确加载

  Scenario: 加载成功返回 skill 实例
    Given skill.py 定义了 class MyHelper(Skill)
    When 加载 skill
    Then 返回 MyHelper 实例
    And skill.name == "MyHelper"
```

### VP2: .skill 文件安装

支持从打包的 .skill 文件安装 skill。

```gherkin
Feature: .skill 文件安装

  Scenario: 安装 .skill 文件
    Given 存在 my-helper.skill 打包文件
    When 执行 "anyclaw skill install my-helper.skill"
    Then 解压到 managed-skills 目录
    And 验证 SKILL.md 格式
    And 显示安装成功

  Scenario: 覆盖已存在的 skill
    Given managed-skills/my-helper 已存在
    When 安装同名 skill
    Then 提示确认覆盖
    And 用户确认后替换

  Scenario: 安装无效 skill 失败
    Given .skill 文件内没有 SKILL.md
    When 执行安装
    Then 返回验证错误
    And 不创建目录
```

### VP3: 运行时热重载

支持运行时重新加载 skill（开发模式）。

```gherkin
Feature: 热重载

  Scenario: 重新加载单个 skill
    Given skill "my-helper" 已加载
    And 用户修改了 skill.py
    When 执行热重载
    Then 重新导入模块
    And 新代码生效

  Scenario: 重新加载所有 skills
    Given 多个 skills 已加载
    When 执行 "anyclaw skill reload"
    Then 清除所有已加载的 skill 实例
    And 重新扫描所有目录
    And 重新加载所有 skills
```

### VP4: Skill 优先级合并

多目录 skill 同名时的优先级处理。

```gherkin
Feature: 优先级合并

  Scenario: workspace 覆盖 builtin
    Given builtin 有 skill "weather"
    And workspace 也有 skill "weather"
    When 加载 skills
    Then 使用 workspace 版本
    And builtin 版本被忽略

  Scenario: 优先级顺序
    Given bundled/managed/workspace 都有同名 skill
    When 加载 skills
    Then 使用 workspace 版本（最高优先级）
```

## 技术设计

### 动态加载方案

**方案 A：使用 importlib.util（推荐）**

```python
import importlib.util

def load_python_skill(skill_path: Path) -> Optional[Skill]:
    skill_file = skill_path / "skill.py"
    if not skill_file.exists():
        return None

    # 动态加载模块
    spec = importlib.util.spec_from_file_location(
        f"skill_{skill_path.name}",
        skill_file
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    # 查找 Skill 子类
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if isinstance(attr, type) and issubclass(attr, Skill) and attr != Skill:
            return attr()
    return None
```

### 目录结构

```
~/.anyclaw/
├── workspace/
│   └── skills/           # 最高优先级
├── managed-skills/       # 中等优先级（用户安装）
└── bundled-skills/       # 最低优先级（内置）

anyclaw/anyclaw/skills/
└── builtin/              # 打包内置的 skills
```

### 热重载机制

```python
class SkillLoader:
    def __init__(self):
        self._loaded_modules: Dict[str, Any] = {}

    def reload_skill(self, name: str) -> Optional[Skill]:
        # 清除缓存的模块
        module_name = f"skill_{name}"
        if module_name in sys.modules:
            del sys.modules[module_name]
        # 重新加载
        return self._load_python_skill(self._find_skill_path(name))
```

### 安装流程

```python
def install_skill(source: Path, target_dir: Path) -> Path:
    if source.suffix == '.skill':
        # 解压 ZIP 文件
        with zipfile.ZipFile(source) as zf:
            zf.extractall(target_dir)
    else:
        # 复制目录
        shutil.copytree(source, target_dir / source.name)

    # 验证
    skill_path = target_dir / source.stem
    valid, msg = validate_skill(skill_path)
    if not valid:
        shutil.rmtree(skill_path)
        raise ValueError(msg)

    return skill_path
```

## 验收标准

- [ ] 能从 workspace 目录加载 Python skill
- [ ] 能从 managed 目录加载 Python skill
- [ ] 不再硬编码 `anyclaw.skills.builtin.*` 路径
- [ ] 能安装 .skill 打包文件
- [ ] 同名 skill 按优先级正确合并
- [ ] 热重载功能正常工作
- [ ] 有完整的单元测试
