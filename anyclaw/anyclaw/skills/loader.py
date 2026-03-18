"""技能加载器"""
import importlib
from typing import List, Dict
from pathlib import Path
from .base import Skill


class SkillLoader:
    """技能加载器"""

    def __init__(self, skills_dir: str):
        self.skills_dir = Path(skills_dir)
        self.skills: Dict[str, Skill] = {}

    def load_all(self) -> List[Dict]:
        """加载所有技能"""
        skills_info = []

        for skill_path in self.skills_dir.iterdir():
            if skill_path.is_dir() and not skill_path.name.startswith('_'):
                skill = self._load_skill(skill_path)
                if skill:
                    self.skills[skill.name] = skill
                    skills_info.append(skill.get_info())

        return skills_info

    def _load_skill(self, skill_path: Path) -> Skill:
        """加载单个技能"""
        try:
            # 查找 skill.py 文件
            skill_file = skill_path / "skill.py"
            if not skill_file.exists():
                return None

            # 动态导入 - 使用绝对路径导入
            import sys
            from pathlib import Path

            # 将技能目录添加到 Python 路径
            skill_dir = skill_path.parent.parent
            if str(skill_dir) not in sys.path:
                sys.path.insert(0, str(skill_dir))

            # 模块导入
            module_name = f"anyclaw.skills.builtin.{skill_path.name}.skill"
            module = importlib.import_module(module_name)

            # 查找 Skill 类
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, Skill) and attr != Skill:
                    return attr()

        except Exception as e:
            print(f"Error loading skill {skill_path.name}: {e}")

        return None

    async def execute_skill(self, name: str, **kwargs) -> str:
        """执行技能"""
        skill = self.skills.get(name)
        if not skill:
            return f"Skill '{name}' not found"

        try:
            return await skill.execute(**kwargs)
        except Exception as e:
            return f"Error executing skill '{name}': {e}"
