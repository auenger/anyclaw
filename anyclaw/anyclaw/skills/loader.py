"""技能加载器 - 支持 Python Skill 类和 SKILL.md 格式

支持：
- 任意路径 Python skill 动态加载
- 多目录优先级合并 (workspace > managed > bundled)
- 运行时热重载
- SKILL.md 格式加载
"""
import sys
import uuid
import logging
import importlib.util
from typing import List, Dict, Optional, Any
from pathlib import Path
from dataclasses import dataclass

from .base import Skill
from .models import SkillDefinition, SkillFrontmatter
from .parser import parse_skill_md, validate_skill

logger = logging.getLogger(__name__)


@dataclass
class SkillSource:
    """Skill 来源信息"""
    name: str
    path: Path
    source_type: str  # "workspace", "managed", "bundled"
    priority: int  # 越高优先级越高


class SkillLoader:
    """技能加载器 - 支持多种格式和动态加载"""

    # 来源类型优先级
    SOURCE_PRIORITY = {
        "workspace": 100,
        "managed": 50,
        "bundled": 10,
    }

    def __init__(
        self,
        skills_dirs: Optional[List[str]] = None,
        skills_dir: Optional[str] = None,
        skills_dir_types: Optional[Dict[str, str]] = None,
    ):
        """
        初始化加载器

        Args:
            skills_dirs: 多个技能目录列表
            skills_dir: 单个技能目录（向后兼容）
            skills_dir_types: 目录到类型的映射，如 {"path": "workspace"}
        """
        self.skills_dir_types = skills_dir_types or {}

        if skills_dirs:
            self.skills_dirs = [Path(d) for d in skills_dirs]
        elif skills_dir:
            self.skills_dirs = [Path(skills_dir)]
        else:
            self.skills_dirs = []

        # 缓存
        self.python_skills: Dict[str, Skill] = {}
        self.md_skills: Dict[str, SkillDefinition] = {}
        self._skill_sources: Dict[str, SkillSource] = {}
        self._loaded_modules: Dict[str, str] = {}  # skill_name -> module_name

        # 热重载相关
        self._last_mtime: Optional[float] = None

    def load_all(self) -> List[Dict]:
        """加载所有技能"""
        # 按优先级顺序加载（低优先级先加载，高优先级覆盖）
        sorted_dirs = self._get_sorted_dirs()

        for skills_dir, source_type in sorted_dirs:
            self._load_from_directory(skills_dir, source_type)

        return self._get_all_skills_info()

    def _get_sorted_dirs(self) -> List[tuple]:
        """获取按优先级排序的目录列表"""
        dirs_with_type = []
        for skills_dir in self.skills_dirs:
            source_type = self.skills_dir_types.get(str(skills_dir), "bundled")
            priority = self.SOURCE_PRIORITY.get(source_type, 10)
            dirs_with_type.append((skills_dir, source_type, priority))

        # 按优先级升序排序（低优先级先加载）
        dirs_with_type.sort(key=lambda x: x[2])
        return [(d[0], d[1]) for d in dirs_with_type]

    def _load_from_directory(self, skills_dir: Path, source_type: str) -> None:
        """从目录加载所有技能"""
        if not skills_dir.exists():
            logger.debug(f"Skills directory does not exist: {skills_dir}")
            return

        logger.debug(f"Loading skills from {skills_dir} (type: {source_type})")

        for skill_path in skills_dir.iterdir():
            if not skill_path.is_dir():
                continue
            if skill_path.name.startswith('_') or skill_path.name.startswith('.'):
                continue

            self._load_skill(skill_path, source_type)

    def _load_skill(self, skill_path: Path, source_type: str) -> None:
        """加载单个技能"""
        # 尝试加载 Python skill
        skill = self._load_python_skill(skill_path, source_type)
        if skill:
            return

        # 尝试加载 SKILL.md
        self._load_md_skill(skill_path, source_type)

    def _load_python_skill(self, skill_path: Path, source_type: str) -> Optional[Skill]:
        """加载 Python 格式的技能（使用动态导入）"""
        skill_file = skill_path / "skill.py"
        if not skill_file.exists():
            return None

        try:
            # 生成唯一模块名（使用时间戳确保重载时模块名不同）
            import time
            module_name = f"skill_{skill_path.name}_{int(time.time() * 1000)}_{uuid.uuid4().hex[:4]}"

            # 使用 importlib.util 动态加载
            spec = importlib.util.spec_from_file_location(module_name, skill_file)
            if not spec or not spec.loader:
                logger.warning(f"Cannot load spec from {skill_file}")
                return None

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module

            # 执行模块
            spec.loader.exec_module(module)

            # 查找 Skill 子类
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, Skill) and attr != Skill:
                    skill_instance = attr()
                    skill_name = skill_instance.name

                    # 记录来源和模块
                    priority = self.SOURCE_PRIORITY.get(source_type, 10)
                    self._skill_sources[skill_name] = SkillSource(
                        name=skill_name,
                        path=skill_path,
                        source_type=source_type,
                        priority=priority,
                    )
                    self._loaded_modules[skill_name] = module_name
                    self.python_skills[skill_name] = skill_instance

                    logger.debug(f"Loaded Python skill: {skill_name} from {skill_path}")
                    return skill_instance

            logger.debug(f"No Skill subclass found in {skill_file}")
            return None

        except Exception as e:
            logger.error(f"Error loading Python skill {skill_path.name}: {e}")
            return None

    def _load_md_skill(self, skill_path: Path, source_type: str) -> None:
        """加载 SKILL.md 格式的技能"""
        skill_md = skill_path / "SKILL.md"
        if not skill_md.exists():
            return

        try:
            skill = parse_skill_md(skill_md)
            if not skill:
                return

            # 验证依赖
            skill = validate_skill(skill)
            skill_name = skill.name

            # 记录来源
            priority = self.SOURCE_PRIORITY.get(source_type, 10)
            self._skill_sources[skill_name] = SkillSource(
                name=skill_name,
                path=skill_path,
                source_type=source_type,
                priority=priority,
            )
            self.md_skills[skill_name] = skill

            logger.debug(f"Loaded MD skill: {skill_name} from {skill_path}")

        except Exception as e:
            logger.error(f"Error loading MD skill {skill_path.name}: {e}")

    def _get_all_skills_info(self) -> List[Dict]:
        """获取所有技能信息"""
        info = []

        # Python skills
        for name, skill in self.python_skills.items():
            skill_info = skill.get_info()
            source = self._skill_sources.get(name)
            if source:
                skill_info["source"] = source.source_type
            info.append(skill_info)

        # MD skills
        for name, skill in self.md_skills.items():
            skill_info = {
                "name": skill.name,
                "description": skill.description,
            }
            source = self._skill_sources.get(name)
            if source:
                skill_info["source"] = source.source_type
            info.append(skill_info)

        return info

    def get_skill_definitions(self) -> Dict[str, SkillDefinition]:
        """获取所有 SkillDefinition（用于 Tool Calling）"""
        definitions = {}

        # 转换 Python 技能为 SkillDefinition
        for name, skill in self.python_skills.items():
            info = skill.get_info()
            skill_name = info.get("name", name)
            source = self._skill_sources.get(name)
            definitions[skill_name] = SkillDefinition(
                name=skill_name,
                description=info.get("description", ""),
                content=info.get("description", ""),
                frontmatter=SkillFrontmatter(
                    name=skill_name,
                    description=info.get("description", "")
                ),
                source_path=str(source.path) if source else f"python:{name}"
            )

        # 添加 MD 技能
        definitions.update(self.md_skills)

        return definitions

    def get_python_skill(self, name: str) -> Optional[Skill]:
        """获取 Python Skill 实例"""
        return self.python_skills.get(name)

    def get_skill_source(self, name: str) -> Optional[SkillSource]:
        """获取 skill 来源信息"""
        return self._skill_sources.get(name)

    async def execute_skill(self, name: str, **kwargs) -> str:
        """执行技能（Python skill）"""
        skill = self.python_skills.get(name)
        if not skill:
            return f"Skill '{name}' not found"

        try:
            return await skill.execute(**kwargs)
        except Exception as e:
            return f"Error executing skill '{name}': {e}"

    # ==================== 热重载功能 ====================

    def reload_skill(self, name: str) -> bool:
        """
        重新加载单个 skill

        Args:
            name: skill 名称

        Returns:
            是否成功
        """
        source = self._skill_sources.get(name)
        if not source:
            logger.warning(f"Skill '{name}' not found, cannot reload")
            return False

        # 清理模块缓存
        module_name = self._loaded_modules.get(name)
        if module_name and module_name in sys.modules:
            del sys.modules[module_name]
        if name in self._loaded_modules:
            del self._loaded_modules[name]

        # 清理 skill 缓存
        if name in self.python_skills:
            del self.python_skills[name]
        if name in self.md_skills:
            del self.md_skills[name]
        del self._skill_sources[name]

        # 重新加载
        self._load_skill(source.path, source.source_type)

        # 检查是否成功
        success = name in self.python_skills or name in self.md_skills
        if success:
            logger.info(f"Reloaded skill: {name}")
        else:
            logger.warning(f"Failed to reload skill: {name}")
        return success

    def reload_all(self) -> Dict[str, int]:
        """
        重新加载所有 skills

        Returns:
            统计信息 {"total": N, "success": M, "failed": K}
        """
        # 记录所有 skill 来源
        sources = dict(self._skill_sources)

        # 清理所有缓存
        for module_name in self._loaded_modules.values():
            if module_name in sys.modules:
                del sys.modules[module_name]

        self._loaded_modules.clear()
        self.python_skills.clear()
        self.md_skills.clear()
        self._skill_sources.clear()

        # 重新加载
        stats = {"total": len(sources), "success": 0, "failed": 0}
        for name, source in sources.items():
            try:
                self._load_skill(source.path, source.source_type)
                # 检查是否成功加载
                if name in self.python_skills or name in self.md_skills:
                    stats["success"] += 1
                else:
                    stats["failed"] += 1
            except Exception as e:
                logger.error(f"Failed to reload skill {name}: {e}")
                stats["failed"] += 1

        logger.info(f"Reloaded all skills: {stats}")
        return stats

    # ==================== 渐进式加载功能 ====================

    def build_skills_summary(self) -> str:
        """构建 XML 格式的技能摘要

        Returns:
            XML 格式的技能摘要字符串
        """
        lines = ['<skills>']

        # 处理 Python skills
        for name, skill in self.python_skills.items():
            info = skill.get_info()
            source = self._skill_sources.get(name)
            available, missing = self._check_skill_requirements(name, info)

            lines.append(f'  <skill available="{str(available).lower()}">')
            lines.append(f'    <name>{info.get("name", name)}</name>')
            lines.append(f'    <description>{info.get("description", "")}</description>')
            if source:
                lines.append(f'    <location>{source.path / "skill.py"}</location>')
            if not available and missing:
                lines.append(f'    <requires>{" ".join(missing)}</requires>')
            lines.append('  </skill>')

        # 处理 MD skills
        for name, skill_def in self.md_skills.items():
            source = self._skill_sources.get(name)
            available, missing = self._check_skill_requirements(name, skill_def)

            lines.append(f'  <skill available="{str(available).lower()}">')
            lines.append(f'    <name>{skill_def.name}</name>')
            lines.append(f'    <description>{skill_def.description}</description>')
            if source:
                lines.append(f'    <location>{source.path / "SKILL.md"}</location>')
            if not available and missing:
                lines.append(f'    <requires>{" ".join(missing)}</requires>')
            lines.append('  </skill>')

        lines.append('</skills>')
        return '\n'.join(lines)

    def load_skills_for_context(self, skill_names: List[str]) -> str:
        """批量加载技能内容到上下文

        Args:
            skill_names: 要加载的技能名称列表

        Returns:
            合并后的技能内容
        """
        contents = []

        for name in skill_names:
            content = self.load_skill_content(name)
            if content:
                contents.append(f"## Skill: {name}\n\n{content}")

        return "\n\n---\n\n".join(contents)

    def load_skill_content(self, name: str) -> Optional[str]:
        """加载单个技能的完整内容（不含 frontmatter）

        Args:
            name: 技能名称

        Returns:
            技能内容或 None
        """
        # 检查 Python skill
        if name in self.python_skills:
            info = self.python_skills[name].get_info()
            return info.get("description", "")

        # 检查 MD skill
        if name in self.md_skills:
            skill_def = self.md_skills[name]
            return self._strip_frontmatter(skill_def.content)

        return None

    def _strip_frontmatter(self, content: str) -> str:
        """去除 YAML frontmatter

        Args:
            content: 原始内容

        Returns:
            去除 frontmatter 后的内容
        """
        if not content.startswith('---'):
            return content

        # 找到第二个 ---
        parts = content.split('---', 2)
        if len(parts) >= 3:
            return parts[2].strip()

        return content

    def _get_skill_description(self, skill_path: Path) -> str:
        """从 SKILL.md 获取技能描述

        Args:
            skill_path: 技能目录路径

        Returns:
            技能描述
        """
        skill_md = skill_path / "SKILL.md"
        if not skill_md.exists():
            return ""

        try:
            from .parser import parse_skill_md
            skill = parse_skill_md(skill_md)
            return skill.description if skill else ""
        except Exception:
            return ""

    def _check_skill_requirements(
        self, name: str, skill_info: Any
    ) -> tuple[bool, List[str]]:
        """检查技能依赖是否满足

        Args:
            name: 技能名称
            skill_info: 技能信息（Skill 实例或 SkillDefinition）

        Returns:
            (是否可用, 缺失的依赖列表)
        """
        # 获取 OpenClaw 元数据
        requires = None

        if isinstance(skill_info, dict):
            # Python skill info dict
            pass
        elif hasattr(skill_info, 'get_openclaw_metadata'):
            # SkillDefinition
            metadata = skill_info.get_openclaw_metadata()
            if metadata and metadata.requires:
                requires = metadata.requires

        if not requires:
            return True, []

        return self._check_requirements(requires)

    def _check_requirements(self, requires: Any) -> tuple[bool, List[str]]:
        """检查依赖项

        Args:
            requires: OpenClawRequires 对象

        Returns:
            (是否全部满足, 缺失项列表)
        """
        import shutil
        import os

        missing = []

        # 检查二进制命令
        if hasattr(requires, 'bins') and requires.bins:
            for bin_name in requires.bins:
                if not shutil.which(bin_name):
                    missing.append(f"CLI: {bin_name}")

        # 检查环境变量
        if hasattr(requires, 'env') and requires.env:
            for env_name in requires.env:
                if not os.environ.get(env_name):
                    missing.append(f"ENV: {env_name}")

        return len(missing) == 0, missing

    def get_always_skills(self) -> List[str]:
        """获取所有标记为 always=true 的技能

        Returns:
            always 技能名称列表
        """
        always_skills = []

        # 检查 MD skills
        for name, skill_def in self.md_skills.items():
            metadata = skill_def.get_openclaw_metadata()
            if metadata and metadata.always:
                # 检查依赖
                available, _ = self._check_skill_requirements(name, skill_def)
                if available:
                    always_skills.append(name)

        return always_skills

    # ==================== 热重载检测 ====================

    def get_skills_mtime(self) -> float:
        """
        获取技能目录的最新修改时间

        Returns:
            所有技能目录中最新的修改时间戳
        """
        import os

        max_mtime = 0.0

        for skills_dir in self.skills_dirs:
            if not skills_dir.exists():
                continue

            # 检查目录本身的修改时间
            try:
                dir_mtime = skills_dir.stat().st_mtime
                max_mtime = max(max_mtime, dir_mtime)
            except OSError:
                pass

            # 检查所有 SKILL.md 文件的修改时间
            for skill_md in skills_dir.rglob("SKILL.md"):
                try:
                    file_mtime = skill_md.stat().st_mtime
                    max_mtime = max(max_mtime, file_mtime)
                except OSError:
                    pass

            # 检查所有 skill.py 文件的修改时间
            for skill_py in skills_dir.rglob("skill.py"):
                try:
                    file_mtime = skill_py.stat().st_mtime
                    max_mtime = max(max_mtime, file_mtime)
                except OSError:
                    pass

        return max_mtime

    def has_skills_changed(self) -> bool:
        """
        检测技能目录是否有变化

        Returns:
            True 如果检测到变化，False 否则
        """
        current_mtime = self.get_skills_mtime()

        if self._last_mtime is None:
            # 首次调用，记录当前时间
            self._last_mtime = current_mtime
            return False

        if current_mtime > self._last_mtime:
            self._last_mtime = current_mtime
            return True

        return False

    def auto_reload_if_changed(self) -> Optional[Dict[str, int]]:
        """
        如果检测到变化则自动重载

        Returns:
            如果重载了，返回统计信息；否则返回 None
        """
        if self.has_skills_changed():
            logger.info("Detected skill changes, auto-reloading...")
            return self.reload_all()
        return None


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
        dirs = []
        dir_types = {}

        # 按优先级顺序添加
        if bundled_dir:
            dirs.append(bundled_dir)
            dir_types[bundled_dir] = "bundled"
        if managed_dir:
            dirs.append(managed_dir)
            dir_types[managed_dir] = "managed"
        if workspace_dir:
            dirs.append(workspace_dir)
            dir_types[workspace_dir] = "workspace"

        super().__init__(skills_dirs=dirs, skills_dir_types=dir_types)

        self.bundled_dir = Path(bundled_dir) if bundled_dir else None
        self.managed_dir = Path(managed_dir) if managed_dir else None
        self.workspace_dir = Path(workspace_dir) if workspace_dir else None
