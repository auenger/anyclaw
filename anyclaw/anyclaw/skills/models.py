"""Skill 数据模型 - OpenClaw SKILL.md 兼容"""
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field


class OpenClawRequires(BaseModel):
    """OpenClaw 依赖检查配置"""
    bins: List[str] = Field(default_factory=list, description="需要检查的二进制命令")
    env: List[str] = Field(default_factory=list, description="需要检查的环境变量")
    config: List[str] = Field(default_factory=list, description="需要检查的配置项")


class OpenClawInstall(BaseModel):
    """安装指令"""
    id: str = Field(..., description="安装方法 ID")
    kind: str = Field(..., description="安装类型: brew, apt, npm 等")
    label: str = Field(..., description="安装标签")
    formula: Optional[str] = None
    package: Optional[str] = None
    bins: List[str] = Field(default_factory=list)


class OpenClawMetadata(BaseModel):
    """OpenClaw 特定元数据"""
    emoji: Optional[str] = Field(default=None, description="技能图标")
    requires: Optional[OpenClawRequires] = Field(default=None, description="依赖检查")
    install: List[OpenClawInstall] = Field(default_factory=list, description="安装方法")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="参数定义")
    # 新增字段 - 渐进式加载
    always: bool = Field(default=False, description="是否始终加载到上下文")
    scripts: List[str] = Field(default_factory=list, description="可执行脚本列表")
    references: List[str] = Field(default_factory=list, description="参考文档列表")


class SkillFrontmatter(BaseModel):
    """SKILL.md YAML frontmatter"""
    name: str = Field(..., description="技能名称")
    description: str = Field(..., description="技能描述")
    homepage: Optional[str] = Field(default=None, description="主页 URL")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="元数据")

    def get_openclaw_metadata(self) -> Optional[OpenClawMetadata]:
        """获取 OpenClaw 元数据"""
        if not self.metadata or "openclaw" not in self.metadata:
            return None
        return OpenClawMetadata.model_validate(self.metadata["openclaw"])


class SkillDefinition(BaseModel):
    """完整的 Skill 定义"""
    name: str = Field(..., description="技能名称")
    description: str = Field(..., description="技能描述")
    content: str = Field(..., description="Markdown 内容（指令）")
    frontmatter: SkillFrontmatter
    source_path: str = Field(..., description="源文件路径")
    eligible: bool = Field(default=True, description="是否可用（依赖检查通过）")
    eligibility_reasons: List[str] = Field(default_factory=list, description="不可用原因")

    def get_openclaw_metadata(self) -> Optional[OpenClawMetadata]:
        """获取 OpenClaw 元数据"""
        return self.frontmatter.get_openclaw_metadata()

    def get_commands(self) -> List[str]:
        """从 Markdown 内容中提取命令模板"""
        import re
        commands = []
        # 匹配 ```bash ... ``` 代码块
        pattern = r'```bash\s*\n(.*?)```'
        matches = re.findall(pattern, self.content, re.DOTALL)
        for match in matches:
            # 清理命令（去除注释、空行）
            lines = []
            for line in match.strip().split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    lines.append(line)
            if lines:
                commands.append('\n'.join(lines))
        return commands

    def get_parameters(self) -> Dict[str, Any]:
        """获取参数定义"""
        openclaw_meta = self.get_openclaw_metadata()
        if openclaw_meta and openclaw_meta.parameters:
            return openclaw_meta.parameters

        # 从命令中推断参数
        return self._infer_parameters_from_commands()

    def _infer_parameters_from_commands(self) -> Dict[str, Any]:
        """从命令模板推断参数"""
        import re
        properties = {}
        required = []

        # 匹配 {param} 格式的参数
        param_pattern = r'\{(\w+)\}'
        for cmd in self.get_commands():
            matches = re.findall(param_pattern, cmd)
            for param in matches:
                if param not in properties:
                    properties[param] = {
                        "type": "string",
                        "description": f"{param} parameter"
                    }
                    required.append(param)

        return {
            "type": "object",
            "properties": properties,
            "required": required
        }
