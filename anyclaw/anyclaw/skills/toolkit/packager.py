"""Skill 打包器 - 将 skill 打包为 .skill 文件"""
import zipfile
from pathlib import Path
from typing import Optional, List

from .validator import validate_skill_dir, ValidationResult


# 打包时排除的文件/目录
EXCLUDE_PATTERNS = {
    '.git',
    '__pycache__',
    '.DS_Store',
    '*.pyc',
    '*.pyo',
    '.env',
    '.venv',
    'venv',
    'node_modules',
    '.skill',  # 避免嵌套打包
}


def _should_exclude(path: Path, skill_dir: Path) -> bool:
    """检查是否应该排除该文件/目录"""
    name = path.name

    # 检查排除模式
    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith('*'):
            if name.endswith(pattern[1:]):
                return True
        elif name == pattern:
            return True

    return False


def _check_security(skill_dir: Path) -> List[str]:
    """
    安全检查

    Returns:
        安全问题列表
    """
    issues = []

    for path in skill_dir.rglob('*'):
        if not path.exists():
            continue

        # 检查符号链接
        if path.is_symlink():
            issues.append(f"Symlink not allowed: {path.relative_to(skill_dir)}")

        # 检查绝对路径符号链接
        try:
            resolved = path.resolve()
            if path.is_symlink() and not str(resolved).startswith(str(skill_dir.resolve())):
                issues.append(f"Symlink points outside skill directory: {path.relative_to(skill_dir)}")
        except Exception:
            pass

    return issues


def package_skill(
    skill_path: Path,
    output_dir: Optional[Path] = None,
    validate: bool = True,
) -> Path:
    """
    将 skill 目录打包为 .skill 文件

    Args:
        skill_path: skill 目录路径
        output_dir: 输出目录（默认为 skill 目录所在目录）
        validate: 打包前是否验证

    Returns:
        生成的 .skill 文件路径

    Raises:
        ValueError: 验证失败
        FileNotFoundError: skill 目录不存在
    """
    skill_path = Path(skill_path).resolve()

    # 检查目录存在
    if not skill_path.exists():
        raise FileNotFoundError(f"Skill directory not found: {skill_path}")

    if not skill_path.is_dir():
        raise ValueError(f"Not a directory: {skill_path}")

    # 验证
    if validate:
        result = validate_skill_dir(skill_path)
        if not result.valid:
            errors = '\n'.join(f"  - {e}" for e in result.errors)
            raise ValueError(f"Skill validation failed:\n{errors}")

    # 安全检查
    security_issues = _check_security(skill_path)
    if security_issues:
        issues = '\n'.join(f"  - {i}" for i in security_issues)
        raise ValueError(f"Security issues found:\n{issues}")

    # 确定输出路径
    if output_dir is None:
        output_dir = skill_path.parent
    else:
        output_dir = Path(output_dir).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

    skill_name = skill_path.name
    output_file = output_dir / f"{skill_name}.skill"

    # 创建 ZIP 文件
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for path in skill_path.rglob('*'):
            if not path.is_file():
                continue

            # 跳过排除的文件
            if _should_exclude(path, skill_path):
                continue

            # 添加到 ZIP
            arcname = path.relative_to(skill_path)
            zf.write(path, arcname)

    return output_file


def unpackage_skill(skill_file: Path, output_dir: Optional[Path] = None) -> Path:
    """
    解压 .skill 文件

    Args:
        skill_file: .skill 文件路径
        output_dir: 输出目录（默认为文件所在目录）

    Returns:
        解压后的 skill 目录路径

    Raises:
        FileNotFoundError: 文件不存在
        ValueError: 文件格式无效
    """
    skill_file = Path(skill_file).resolve()

    if not skill_file.exists():
        raise FileNotFoundError(f"Skill file not found: {skill_file}")

    if not skill_file.suffix == '.skill':
        raise ValueError(f"Invalid skill file extension: {skill_file.suffix}")

    # 确定输出目录
    if output_dir is None:
        output_dir = skill_file.parent
    else:
        output_dir = Path(output_dir).resolve()

    # skill 目录名（去除 .skill 扩展名）
    skill_name = skill_file.stem
    skill_dir = output_dir / skill_name

    # 检查目录是否已存在
    if skill_dir.exists():
        raise FileExistsError(f"Directory already exists: {skill_dir}")

    # 解压
    with zipfile.ZipFile(skill_file, 'r') as zf:
        zf.extractall(skill_dir)

    return skill_dir
