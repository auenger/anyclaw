"""技能加载器 - 支持 Python Skill 类和 SKILL.md 格式"""
import importlib
from typing import List, Dict, Optional
from pathlib import Path

from .base import Skill
from .models import SkillDefinition
from .parser import parse_skill_md, validate_skill


class SkillLoader:
    """技能加载器 - 支持多种格式"""

    def __init__(
        self,
        skills_dirs: Optional[List[str]] = None,
        skills_dir: Optional[str] = None
    ):
        """
        初始化加载器

        Args:
            skills_dirs: 多个技能目录（优先级：后面的覆盖前面的）
            skills_dir: 单个技能目录（向后兼容）
        """
        if skills_dirs:
            self.skills_dirs = [Path(d) for d in skills_dirs]
        elif skills_dir:
            self.skills_dirs = [Path(skills_dir)]
        else:
            self.skills_dirs = []

        self.python_skills: Dict[str, Skill] = {}
        self.md_skills: Dict[str, SkillDefinition] = {}

    def load_all(self) -> List[Dict]:
        """加载所有技能"""
        # 加载 Python skills
        for skills_dir in self.skills_dirs:
            self._load_python_skills(skills_dir)

        # 加载 SKILL.md 格式
        for skills_dir in self.skills_dirs:
            self._load_md_skills(skills_dir)

        return self._get_all_skills_info()

    def _load_python_skills(self, skills_dir: Path) -> None:
        """加载 Python 格式的技能"""
        if not skills_dir.exists():
            return

        for skill_path in skills_dir.iterdir():
            if skill_path.is_dir() and not skill_path.name.startswith('_') and not skill_path.name.startswith('.'):
                try:
                    skill = self._load_python_skill(skill_path)
                    if skill:
                        self.python_skills[skill.name] = skill
                except OSError:
                    # 跳过无法访问的目录
                    continue

    def _load_python_skill(self, skill_path: Path) -> Optional[Skill]:
        """加载单个 Python 技能"""
        try:
            skill_file = skill_path / "skill.py"
            if not skill_file.exists():
                return None

            import sys
            skill_dir = skill_path.parent.parent
            if str(skill_dir) not in sys.path:
                sys.path.insert(0, str(skill_dir))

            module_name = f"anyclaw.skills.builtin.{skill_path.name}.skill"
            module = importlib.import_module(module_name)

            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, Skill) and attr != Skill:
                    return attr()

        except Exception as e:
            print(f"Error loading Python skill {skill_path.name}: {e}")

        return None

    def _load_md_skills(self, skills_dir: Path) -> None:
        """加载 SKILL.md 格式的技能"""
        if not skills_dir.exists():
            return

        # 遍历子目录查找 SKILL.md
        for skill_path in skills_dir.iterdir():
            if skill_path.is_dir() and not skill_path.name.startswith('_') and not skill_path.name.startswith('.'):
                try:
                    skill_md = skill_path / "SKILL.md"
                    if skill_md.exists():
                        skill = parse_skill_md(skill_md)
                        if skill:
                            # 验证依赖
                            skill = validate_skill(skill)
                            self.md_skills[skill.name] = skill
                except OSError:
                    # 跳过无法访问的目录
                    continue

    def _get_all_skills_info(self) -> List[Dict]:
        """获取所有技能信息"""
        info = []

        # Python skills
        for name, skill in self.python_skills.items():
            info.append(skill.get_info())

        # MD skills
        for name, skill in self.md_skills.items():
            info.append({
                "name": skill.name,
                "description": skill.description
            })

        return info

    def get_skill_definitions(self) -> Dict[str, SkillDefinition]:
        """获取所有 SkillDefinition（用于 Tool Calling）"""
        return self.md_skills.copy()

    def get_python_skill(self, name: str) -> Optional[Skill]:
        """获取 Python Skill 实例"""
        return self.python_skills.get(name)

    async def execute_skill(self, name: str, **kwargs) -> str:
        """执行技能（Python skill）"""
        skill = self.python_skills.get(name)
        if not skill:
            return f"Skill '{name}' not found"

        try:
            return await skill.execute(**kwargs)
        except Exception as e:
            return f"Error executing skill '{name}': {e}"


class MultiDirectorySkillLoader(SkillLoader):
    """多目录技能加载器 - 支持优先级合并"""

    def __init__(
        self,
        bundled_dir: str,
        managed_dir: Optional[str] = None,
        workspace_dir: Optional[str] = None
    ):
        """
        初始化多目录加载器

        优先级：workspace > managed > bundled

        Args:
            bundled_dir: 内置技能目录
            managed_dir: 管理的技能目录
            workspace_dir: 工作空间技能目录
        """
        dirs = [bundled_dir]
        if managed_dir:
            dirs.append(managed_dir)
        if workspace_dir:
            dirs.append(workspace_dir)

        super().__init__(skills_dirs=dirs)

        self.bundled_dir = Path(bundled_dir)
        self.managed_dir = Path(managed_dir) if managed_dir else None
        self.workspace_dir = Path(workspace_dir) if workspace_dir else None
