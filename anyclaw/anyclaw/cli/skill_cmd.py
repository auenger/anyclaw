"""Skill CLI 命令"""
from pathlib import Path
from typing import Optional, List

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from anyclaw.skills.toolkit import (
    validate_skill_dir,
    init_skill,
    package_skill,
    normalize_skill_name,
)
from anyclaw.skills.toolkit.validator import ValidationResult
from anyclaw.config.settings import settings

app = typer.Typer(help="Skill management commands")
console = Console()


def create_skill_app() -> typer.Typer:
    """创建 skill 命令组"""
    return app


@app.command("create")
def skill_create(
    name: str = typer.Argument(..., help="Skill name (will be normalized to hyphen-case)"),
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Output directory"),
    resources: Optional[str] = typer.Option(None, "--resources", "-r", help="Resource directories (comma-separated)"),
    examples: bool = typer.Option(False, "--examples", "-e", help="Create example files"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Skill description"),
):
    """Create a new skill directory with SKILL.md template"""
    try:
        # 解析资源目录
        resource_list = None
        if resources:
            resource_list = [r.strip() for r in resources.split(',') if r.strip()]

        # 确定输出目录
        output_path = Path(path) if path else None

        # 创建 skill
        skill_dir = init_skill(
            name=name,
            path=output_path,
            resources=resource_list,
            examples=examples,
            description=description,
        )

        console.print(f"[green]✓[/green] Created skill: [cyan]{skill_dir}[/cyan]")
        console.print(f"\n[bold]Files created:[/bold]")
        console.print(f"  ├── SKILL.md")

        if resource_list:
            for res in resource_list:
                console.print(f"  └── {res}/")

        console.print(f"\n[dim]Edit SKILL.md to add your skill instructions.[/dim]")

    except FileExistsError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("validate")
def skill_validate(
    path: str = typer.Argument(..., help="Path to skill directory or SKILL.md file"),
):
    """Validate a skill directory or SKILL.md file"""
    skill_path = Path(path).resolve()

    result = validate_skill_dir(skill_path)

    if result.valid:
        console.print(f"[green]✓ Skill is valid![/green]")
        if result.skill_name:
            console.print(f"  Name: [cyan]{result.skill_name}[/cyan]")
        if result.skill_description:
            desc = result.skill_description[:80] + "..." if len(result.skill_description) > 80 else result.skill_description
            console.print(f"  Description: {desc}")
    else:
        console.print(f"[red]✗ Validation failed[/red]")
        for error in result.errors:
            console.print(f"  [red]-[/red] {error}")

    if result.warnings:
        console.print(f"\n[yellow]Warnings:[/yellow]")
        for warning in result.warnings:
            console.print(f"  [yellow]-[/yellow] {warning}")

    if not result.valid:
        raise typer.Exit(1)


@app.command("package")
def skill_package(
    path: str = typer.Argument(..., help="Path to skill directory"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory"),
    no_validate: bool = typer.Option(False, "--no-validate", help="Skip validation"),
):
    """Package a skill directory into a .skill file"""
    skill_path = Path(path).resolve()
    output_path = Path(output) if output else None

    try:
        console.print(f"[dim]Packaging skill: {skill_path}[/dim]")

        output_file = package_skill(
            skill_path=skill_path,
            output_dir=output_path,
            validate=not no_validate,
        )

        # 显示文件大小
        size_kb = output_file.stat().st_size / 1024

        console.print(f"[green]✓[/green] Created: [cyan]{output_file}[/cyan]")
        console.print(f"  Size: {size_kb:.1f} KB")

    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("list")
def skill_list(
    all_skills: bool = typer.Option(False, "--all", "-a", help="Show all skills including built-in"),
):
    """List installed skills"""
    from anyclaw.skills.loader import SkillLoader

    console.print("\n[bold]Installed Skills[/bold]\n")

    # 加载技能
    loader = SkillLoader(skills_dir=settings.skills_dir)
    skills = loader.load_all()

    if not skills:
        console.print("[dim]No skills found.[/dim]")
        console.print(f"\n[dim]Skills directory: {settings.skills_dir}[/dim]")
        return

    table = Table()
    table.add_column("Name", style="cyan")
    table.add_column("Description")
    table.add_column("Source", style="dim")

    for skill in skills:
        name = skill.get("name", "unknown")
        desc = skill.get("description", "")
        if len(desc) > 50:
            desc = desc[:47] + "..."
        source = skill.get("source", "unknown")
        table.add_row(name, desc, source)

    console.print(table)
    console.print(f"\n[dim]Total: {len(skills)} skill(s)[/dim]")


@app.command("install")
def skill_install(
    path: str = typer.Argument(..., help="Path to skill directory or .skill file"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing"),
):
    """Install a skill from directory or .skill file"""
    from anyclaw.skills.toolkit.packager import unpackage_skill
    import shutil

    source_path = Path(path).resolve()
    skills_dir = Path(settings.skills_dir)
    skills_dir.mkdir(parents=True, exist_ok=True)

    # 检查源路径
    if not source_path.exists():
        console.print(f"[red]Error:[/red] Path not found: {source_path}")
        raise typer.Exit(1)

    # 确定目标目录
    if source_path.suffix == '.skill':
        # 从 .skill 文件安装
        skill_name = source_path.stem
        target_dir = skills_dir / skill_name

        if target_dir.exists() and not force:
            console.print(f"[red]Error:[/red] Skill already exists: {skill_name}")
            console.print("Use --force to overwrite")
            raise typer.Exit(1)

        # 删除现有目录
        if target_dir.exists():
            shutil.rmtree(target_dir)

        # 解压
        try:
            unpackage_skill(source_path, skills_dir)
            console.print(f"[green]✓[/green] Installed from .skill file: [cyan]{skill_name}[/cyan]")
        except Exception as e:
            console.print(f"[red]Error:[/red] Failed to install: {e}")
            raise typer.Exit(1)

    elif source_path.is_dir():
        # 从目录安装
        skill_name = source_path.name
        target_dir = skills_dir / skill_name

        if target_dir.exists() and not force:
            console.print(f"[red]Error:[/red] Skill already exists: {skill_name}")
            console.print("Use --force to overwrite")
            raise typer.Exit(1)

        # 验证源 skill
        result = validate_skill_dir(source_path)
        if not result.valid:
            console.print(f"[red]Error:[/red] Invalid skill:")
            for error in result.errors:
                console.print(f"  [red]-[/red] {error}")
            raise typer.Exit(1)

        # 删除现有目录
        if target_dir.exists():
            shutil.rmtree(target_dir)

        # 复制
        try:
            shutil.copytree(source_path, target_dir)
            console.print(f"[green]✓[/green] Installed: [cyan]{skill_name}[/cyan]")
        except Exception as e:
            console.print(f"[red]Error:[/red] Failed to install: {e}")
            raise typer.Exit(1)

    else:
        console.print(f"[red]Error:[/red] Invalid path (must be directory or .skill file)")
        raise typer.Exit(1)

    console.print(f"[dim]Location: {target_dir}[/dim]")


@app.command("show")
def skill_show(
    name: str = typer.Argument(..., help="Skill name"),
):
    """Show skill details"""
    from anyclaw.skills.loader import SkillLoader
    from anyclaw.skills.parser import parse_skill_md

    skills_dir = Path(settings.skills_dir)
    skill_path = skills_dir / name / "SKILL.md"

    if not skill_path.exists():
        # 尝试在 builtin 中查找
        builtin_path = Path(__file__).parent.parent / "skills" / "builtin" / name / "SKILL.md"
        if builtin_path.exists():
            skill_path = builtin_path
        else:
            console.print(f"[red]Error:[/red] Skill not found: {name}")
            raise typer.Exit(1)

    # 解析 skill
    skill_def = parse_skill_md(skill_path)

    if not skill_def:
        console.print(f"[red]Error:[/red] Failed to parse skill: {skill_path}")
        raise typer.Exit(1)

    # 显示详情
    console.print(f"\n[bold cyan]{skill_def.name}[/bold cyan]\n")
    console.print(f"[bold]Description:[/bold]")
    console.print(f"  {skill_def.description}")
    console.print(f"\n[bold]Source:[/bold]")
    console.print(f"  {skill_def.source_path}")

    # 显示内容摘要
    content_lines = skill_def.content.strip().split('\n')[:10]
    console.print(f"\n[bold]Content Preview:[/bold]")
    console.print(Panel('\n'.join(content_lines), expand=False))

    # 显示依赖状态
    openclaw_meta = skill_def.get_openclaw_metadata()
    if openclaw_meta and openclaw_meta.requires:
        console.print(f"\n[bold]Dependencies:[/bold]")
        from anyclaw.skills.parser import check_skill_eligibility

        eligible, reasons = check_skill_eligibility(skill_def)
        if eligible:
            console.print(f"  [green]✓ All dependencies satisfied[/green]")
        else:
            console.print(f"  [red]✗ Missing dependencies:[/red]")
            for reason in reasons:
                console.print(f"    [red]-[/red] {reason}")
