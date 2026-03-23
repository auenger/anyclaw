"""PPTX 演示文稿处理技能

支持创建、编辑、分析 PowerPoint 演示文稿，包含模板使用和内容替换功能。
"""

import json
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from anyclaw.skills.base import Skill


# 内置配色方案
COLOR_SCHEMES = {
    "classic_blue": {
        "name": "Classic Blue",
        "primary": "1E3A5F",      # 深蓝
        "secondary": "4A90A4",    # 青蓝
        "accent": "E8B04B",       # 金色
        "text": "FFFFFF",         # 白色
        "background": "1E3A5F",   # 深蓝背景
    },
    "teal_coral": {
        "name": "Teal & Coral",
        "primary": "2C7873",      # 青绿
        "secondary": "FF6B6B",    # 珊瑚红
        "accent": "4ECDC4",       # 薄荷绿
        "text": "FFFFFF",         # 白色
        "background": "2C7873",
    },
    "bold_red": {
        "name": "Bold Red",
        "primary": "C0392B",      # 深红
        "secondary": "E74C3C",    # 红色
        "accent": "F39C12",       # 橙色
        "text": "FFFFFF",         # 白色
        "background": "C0392B",
    },
    "warm_blush": {
        "name": "Warm Blush",
        "primary": "8E44AD",      # 紫色
        "secondary": "E91E63",    # 粉红
        "accent": "FF9800",       # 橙色
        "text": "FFFFFF",         # 白色
        "background": "8E44AD",
    },
    "black_gold": {
        "name": "Black & Gold",
        "primary": "1A1A1A",      # 黑色
        "secondary": "333333",    # 深灰
        "accent": "FFD700",       # 金色
        "text": "FFFFFF",         # 白色
        "background": "1A1A1A",
    },
    "forest_green": {
        "name": "Forest Green",
        "primary": "1B4332",      # 深绿
        "secondary": "2D6A4F",    # 中绿
        "accent": "95D5B2",       # 浅绿
        "text": "FFFFFF",         # 白色
        "background": "1B4332",
    },
    "sunset_orange": {
        "name": "Sunset Orange",
        "primary": "E85D04",      # 橙色
        "secondary": "F48C06",    # 亮橙
        "accent": "FAA307",       # 黄橙
        "text": "FFFFFF",         # 白色
        "background": "E85D04",
    },
    "ocean_blue": {
        "name": "Ocean Blue",
        "primary": "0077B6",      # 海蓝
        "secondary": "00B4D8",    # 天蓝
        "accent": "90E0EF",       # 浅蓝
        "text": "FFFFFF",         # 白色
        "background": "0077B6",
    },
}

# Web-safe 字体列表
WEB_SAFE_FONTS = [
    "Arial", "Arial Black", "Helvetica",
    "Times New Roman", "Georgia",
    "Verdana", "Tahoma",
    "Trebuchet MS",
    "Courier New", "Courier",
    "Impact",
    "Comic Sans MS",
]


class PptxSkill(Skill):
    """PowerPoint presentation operations: create, edit, analyze, extract

    Supports:
    - Creating presentations with professional designs
    - Template-based creation with content replacement
    - Editing existing presentations
    - Extracting text content
    - Adding speaker notes
    - Generating thumbnails
    """

    def __init__(self):
        super().__init__()
        self.name = "pptx"

    async def execute(
        self,
        action: str = "",
        path: str = "",
        content: str = "",
        output: str = "",
        template: str = "",
        theme: str = "classic_blue",
        **kwargs,
    ) -> str:
        """Execute PPTX operation

        Args:
            action: Operation to perform (create, edit, extract, info, analyze-template,
                    use-template, replace-content, add-notes, thumbnail)
            path: Input file path
            content: Content for create/edit operations
            output: Output file path (optional)
            template: Template file path (for use-template)
            theme: Color theme (classic_blue, teal_coral, bold_red, warm_blush, black_gold)
            **kwargs: Additional parameters

        Returns:
            Operation result
        """
        if not action:
            return self._help()

        if not path:
            return "Please provide a file path"

        try:
            action_handlers = {
                "create": self._create,
                "edit": self._edit,
                "extract": self._extract,
                "info": self._info,
                "analyze-template": self._analyze_template,
                "use-template": self._use_template,
                "replace-content": self._replace_content,
                "add-notes": self._add_notes,
                "thumbnail": self._thumbnail,
            }

            handler = action_handlers.get(action.lower())
            if not handler:
                return f"Unknown action: {action}. Supported: {', '.join(action_handlers.keys())}"

            return await handler(
                path=path,
                content=content,
                output=output,
                template=template,
                theme=theme,
                **kwargs,
            )

        except Exception as e:
            return f"Error: {str(e)}"

    def _help(self) -> str:
        """Return help message"""
        return """PPTX Skill - PowerPoint Presentation Operations

Actions:
  create           - Create a new presentation
  edit             - Edit existing presentation
  extract          - Extract text content from presentation
  info             - Get presentation metadata
  analyze-template - Analyze template layouts and structure
  use-template     - Create from template with content
  replace-content  - Replace content in template slides
  add-notes        - Add speaker notes to slides
  thumbnail        - Generate thumbnail grid image

Parameters:
  path       - File path (required)
  content    - Slide content for create/edit
  output     - Output file path (optional)
  template   - Template file path (for use-template)
  theme      - Color theme (classic_blue, teal_coral, bold_red, warm_blush,
               black_gold, forest_green, sunset_orange, ocean_blue)

Content Format for Create:
JSON array of slides:
  [{"title": "Title", "content": ["bullet 1", "bullet 2"]}]
Or markdown-like:
  # Slide Title
  - Bullet 1
  - Bullet 2

Examples:
  pptx create /path/to/slides.pptx --content '[{"title":"Intro","content":["Point 1","Point 2"]}]'
  pptx create /path/to/slides.pptx --theme teal_coral --content '...'
  pptx extract /path/to/slides.pptx
  pptx info /path/to/slides.pptx
  pptx edit /path/to/slides.pptx --content "slide:1|old:text|new:text"
  pptx add-notes /path/to/slides.pptx --content '[{"slide":1,"notes":"Speaker notes"}]'
  pptx thumbnail /path/to/slides.pptx --output /path/to/preview.png
"""


# For the rest of the implementation, we need to continue...
# Let me create the rest of the methods

    async def _create(
        self,
        path: str,
        content: str = "",
        output: str = "",
        template: str = "",
        theme: str = "classic_blue",
        **kwargs,
    ) -> str:
        """Create a new presentation with professional design"""
        try:
            from pptx import Presentation
            from pptx.util import Inches, Pt
            from pptx.dml.color import RGBColor
            from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
        except ImportError:
            return "Error: python-pptx not installed. Run: pip install python-pptx"

        path_obj = Path(path).expanduser().resolve()
        path_obj.parent.mkdir(parents=True, exist_ok=True)

        # Get color scheme
        scheme = COLOR_SCHEMES.get(theme, COLOR_SCHEMES["classic_blue"])

        # Parse content
        slides_data = self._parse_slide_content(content)
        if not slides_data:
            return "Error: No slide content provided. Use JSON array or markdown format."

        # Create presentation
        prs = Presentation()
        prs.slide_width = Inches(13.333)  # 16:9 aspect ratio
        prs.slide_height = Inches(7.5)

        for slide_data in slides_data:
            self._add_slide(prs, slide_data, scheme)

        # Save
        prs.save(str(path_obj))

        result = f"Created presentation: {path_obj}\n"
        result += f"  Slides: {len(slides_data)}\n"
        result += f"  Theme: {scheme['name']}"

        return result

    def _parse_slide_content(self, content: str) -> List[Dict[str, Any]]:
        """Parse slide content from JSON or markdown format"""
        content = content.strip()

        # Try JSON first
        if content.startswith("["):
            try:
                data = json.loads(content)
                if isinstance(data, list):
                    return data
            except json.JSONDecodeError:
                pass

        # Try markdown-like format
        slides = []
        current_slide = None

        for line in content.split("\n"):
            line = line.strip()

            # New slide (heading 1)
            if line.startswith("# "):
                if current_slide:
                    slides.append(current_slide)
                current_slide = {"title": line[2:], "content": []}
            # Bullet point
            elif line.startswith("- ") or line.startswith("* "):
                if current_slide:
                    current_slide["content"].append(line[2:])
            # Regular content
            elif line and current_slide:
                current_slide["content"].append(line)

        if current_slide:
            slides.append(current_slide)

        return slides

    def _add_slide(self, prs, slide_data: Dict[str, Any], scheme: Dict[str, str]):
        """Add a slide to the presentation"""
        from pptx import Presentation
        from pptx.util import Inches, Pt
        from pptx.dml.color import RGBColor
        from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

        slide_layout = prs.slide_layouts[6]  # Blank layout
        slide = prs.slides.add_slide(slide_layout)

        title = slide_data.get("title", "")
        content = slide_data.get("content", [])
        slide_type = slide_data.get("type", "content")

        # Parse color
        def hex_to_rgb(hex_color: str) -> RGBColor:
            hex_color = hex_color.lstrip("#")
            return RGBColor(int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16))

        # Add background
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = hex_to_rgb(scheme["background"])

        # Add title
        if title:
            title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(12.333), Inches(1.2))
            title_frame = title_box.text_frame
            title_frame.word_wrap = True

            p = title_frame.paragraphs[0]
            p.text = title
            p.font.size = Pt(44)
            p.font.bold = True
            p.font.color.rgb = hex_to_rgb(scheme["text"])
            p.font.name = "Arial"
            p.alignment = PP_ALIGN.LEFT

        # Add content
        if content:
            content_top = Inches(2.0) if title else Inches(1.0)
            content_box = slide.shapes.add_textbox(Inches(0.5), content_top, Inches(12.333), Inches(5.0))
            content_frame = content_box.text_frame
            content_frame.word_wrap = True

            for i, item in enumerate(content):
                if i == 0:
                    p = content_frame.paragraphs[0]
                else:
                    p = content_frame.add_paragraph()

                p.text = "• " + str(item) if not str(item).startswith(("•", "-")) else str(item)
                p.font.size = Pt(24)
                p.font.color.rgb = hex_to_rgb(scheme["text"])
                p.font.name = "Arial"
                p.space_after = Pt(12)
                p.alignment = PP_ALIGN.LEFT

    async def _extract(
        self,
        path: str,
        content: str = "",
        output: str = "",
        template: str = "",
        theme: str = "",
        **kwargs,
    ) -> str:
        """Extract text content from presentation using python-pptx"""
        path_obj = Path(path).expanduser().resolve()

        if not path_obj.exists():
            return f"File not found: {path}"

        if path_obj.suffix.lower() != ".pptx":
            return f"Not a PPTX file: {path}"

        try:
            from pptx import Presentation
        except ImportError:
            return "Error: python-pptx not installed. Run: pip install python-pptx"

        try:
            prs = Presentation(str(path_obj))

            text_parts = []

            for i, slide in enumerate(prs.slides, start=1):
                text_parts.append(f"## Slide {i}")

                for shape in slide.shapes:
                    if shape.has_text_frame:
                        for paragraph in shape.text_frame.paragraphs:
                            text = paragraph.text.strip()
                            if text:
                                text_parts.append(text)

                text_parts.append("")

            result = "\n".join(text_parts)

            # Limit output
            if len(result) > 50000:
                result = result[:50000] + "\n\n... [content truncated]"

            return f"Content of {path_obj.name}:\n\n{result}"

        except Exception as e:
            return f"Error extracting text: {str(e)}"

    async def _info(
        self,
        path: str,
        content: str = "",
        output: str = "",
        template: str = "",
        theme: str = "",
        **kwargs,
    ) -> str:
        """Get presentation metadata"""
        path_obj = Path(path).expanduser().resolve()

        if not path_obj.exists():
            return f"File not found: {path}"

        try:
            from pptx import Presentation
        except ImportError:
            return "Error: python-pptx not installed. Run: pip install python-pptx"

        try:
            prs = Presentation(str(path_obj))

            info_lines = [f"Presentation: {path_obj.name}"]
            info_lines.append(f"Path: {path_obj}")
            info_lines.append(f"Size: {path_obj.stat().st_size} bytes")
            info_lines.append(f"Slides: {len(prs.slides)}")
            info_lines.append(f"Width: {prs.slide_width.inches:.2f} inches")
            info_lines.append(f"Height: {prs.slide_height.inches:.2f} inches")

            # Core properties
            props = prs.core_properties
            if props.title:
                info_lines.append(f"Title: {props.title}")
            if props.author:
                info_lines.append(f"Author: {props.author}")
            if props.subject:
                info_lines.append(f"Subject: {props.subject}")
            if props.created:
                info_lines.append(f"Created: {props.created}")
            if props.modified:
                info_lines.append(f"Modified: {props.modified}")

            return "\n".join(info_lines)

        except Exception as e:
            return f"Error getting presentation info: {str(e)}"

    async def _edit(
        self,
        path: str,
        content: str = "",
        output: str = "",
        template: str = "",
        theme: str = "",
        **kwargs,
    ) -> str:
        """Edit presentation with text replacement

        Content format: "slide:1|old_text|new_text"
        Multiple replacements: "slide:1|old1|new1||slide:2|old2|new2"
        """
        path_obj = Path(path).expanduser().resolve()

        if not path_obj.exists():
            return f"File not found: {path}"

        if not content:
            return "Please provide replacement content in format: 'slide:1|old_text|new_text'"

        try:
            # Use OOXML unpack/edit/pack workflow
            with tempfile.TemporaryDirectory() as temp_dir:
                # Unpack PPTX
                unpack_dir = Path(temp_dir) / "unpacked"
                self._unpack_pptx(path_obj, unpack_dir)

                # Parse and apply replacements
                replacements = self._parse_pptx_replacements(content)
                replacements_made = 0

                for slide_num, old_text, new_text in replacements:
                    slide_file = unpack_dir / "ppt" / "slides" / f"slide{slide_num}.xml"
                    if slide_file.exists():
                        with open(slide_file, "r", encoding="utf-8") as f:
                            xml_content = f.read()

                        if old_text in xml_content:
                            xml_content = xml_content.replace(old_text, new_text)
                            with open(slide_file, "w", encoding="utf-8") as f:
                                f.write(xml_content)
                            replacements_made += 1

                # Repack PPTX
                output_path = Path(output).expanduser().resolve() if output else path_obj
                self._pack_pptx(unpack_dir, output_path)

            return f"Edited presentation: {output_path}\n  Replacements made: {replacements_made}"

        except Exception as e:
            return f"Error editing presentation: {str(e)}"

    def _parse_pptx_replacements(self, content: str) -> List[Tuple[int, str, str]]:
        """Parse replacement pairs from content string"""
        replacements = []

        # Split by double pipe for multiple replacements
        pairs = content.split("||")

        for pair in pairs:
            parts = pair.split("|")
            if len(parts) >= 3:
                slide_part = parts[0].strip()
                if slide_part.startswith("slide:"):
                    try:
                        slide_num = int(slide_part.replace("slide:", ""))
                        old_text = parts[1].strip()
                        new_text = "|".join(parts[2:]).strip()
                        replacements.append((slide_num, old_text, new_text))
                    except ValueError:
                        pass

        return replacements

    async def _analyze_template(
        self,
        path: str,
        content: str = "",
        output: str = "",
        template: str = "",
        theme: str = "",
        **kwargs,
    ) -> str:
        """Analyze template layouts and structure"""
        path_obj = Path(path).expanduser().resolve()

        if not path_obj.exists():
            return f"File not found: {path}"

        try:
            from pptx import Presentation
        except ImportError:
            return "Error: python-pptx not installed. Run: pip install python-pptx"

        try:
            prs = Presentation(str(path_obj))

            result_lines = [f"Template Analysis: {path_obj.name}"]
            result_lines.append(f"Total Slides: {len(prs.slides)}")
            result_lines.append("")
            result_lines.append("Slide Layouts:")

            for i, slide in enumerate(prs.slides, start=1):
                result_lines.append(f"\n--- Slide {i} ---")

                # Analyze shapes
                shape_count = len(slide.shapes)
                result_lines.append(f"Shapes: {shape_count}")

                # Extract text placeholders
                placeholders = []
                for shape in slide.shapes:
                    if shape.has_text_frame:
                        text = shape.text_frame.text.strip()
                        if text:
                            placeholders.append(text[:50])  # Truncate long text

                if placeholders:
                    result_lines.append("Text content:")
                    for p in placeholders[:5]:  # Limit to 5
                        result_lines.append(f"  - {p}")

            return "\n".join(result_lines)

        except Exception as e:
            return f"Error analyzing template: {str(e)}"

    async def _use_template(
        self,
        path: str,
        content: str = "",
        output: str = "",
        template: str = "",
        theme: str = "",
        **kwargs,
    ) -> str:
        """Create presentation from template"""
        if not template:
            return "Please provide a template file path with --template"

        template_obj = Path(template).expanduser().resolve()
        if not template_obj.exists():
            return f"Template not found: {template}"

        output_path = Path(output).expanduser().resolve() if output else Path(path).expanduser().resolve()

        try:
            # Copy template to output
            shutil.copy2(template_obj, output_path)

            # If content provided, apply replacements
            if content:
                slides_data = self._parse_slide_content(content)

                with tempfile.TemporaryDirectory() as temp_dir:
                    unpack_dir = Path(temp_dir) / "unpacked"
                    self._unpack_pptx(output_path, unpack_dir)

                    # Apply content to slides
                    for slide_data in slides_data:
                        slide_num = slide_data.get("slide", 1)
                        slide_file = unpack_dir / "ppt" / "slides" / f"slide{slide_num}.xml"

                        if slide_file.exists():
                            with open(slide_file, "r", encoding="utf-8") as f:
                                xml_content = f.read()

                            # Replace title and content placeholders
                            if "title" in slide_data:
                                # Simple replacement for common placeholder patterns
                                xml_content = re.sub(
                                    r'<a:t>[^<]*</a:t>',
                                    f'<a:t>{slide_data["title"]}</a:t>',
                                    xml_content,
                                    count=1
                                )

                            with open(slide_file, "w", encoding="utf-8") as f:
                                f.write(xml_content)

                    self._pack_pptx(unpack_dir, output_path)

            return f"Created presentation from template: {output_path}"

        except Exception as e:
            return f"Error using template: {str(e)}"

    async def _replace_content(
        self,
        path: str,
        content: str = "",
        output: str = "",
        template: str = "",
        theme: str = "",
        **kwargs,
    ) -> str:
        """Replace content in template slides

        Content format: JSON array [{"slide": 1, "replacements": {"old": "new"}}]
        """
        path_obj = Path(path).expanduser().resolve()

        if not path_obj.exists():
            return f"File not found: {path}"

        if not content:
            return "Please provide replacement content as JSON array"

        try:
            replacements_data = json.loads(content)
        except json.JSONDecodeError:
            return "Invalid JSON content. Expected: [{\"slide\": 1, \"replacements\": {\"old\": \"new\"}}]"

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                unpack_dir = Path(temp_dir) / "unpacked"
                self._unpack_pptx(path_obj, unpack_dir)

                total_replacements = 0

                for item in replacements_data:
                    slide_num = item.get("slide", 1)
                    replacements = item.get("replacements", {})

                    slide_file = unpack_dir / "ppt" / "slides" / f"slide{slide_num}.xml"
                    if slide_file.exists():
                        with open(slide_file, "r", encoding="utf-8") as f:
                            xml_content = f.read()

                        for old_text, new_text in replacements.items():
                            if old_text in xml_content:
                                xml_content = xml_content.replace(old_text, new_text)
                                total_replacements += 1

                        with open(slide_file, "w", encoding="utf-8") as f:
                            f.write(xml_content)

                output_path = Path(output).expanduser().resolve() if output else path_obj
                self._pack_pptx(unpack_dir, output_path)

            return f"Replaced content in: {output_path}\n  Total replacements: {total_replacements}"

        except Exception as e:
            return f"Error replacing content: {str(e)}"

    async def _add_notes(
        self,
        path: str,
        content: str = "",
        output: str = "",
        template: str = "",
        theme: str = "",
        **kwargs,
    ) -> str:
        """Add speaker notes to slides

        Content format: JSON array [{"slide": 1, "notes": "Speaker notes text"}]
        """
        path_obj = Path(path).expanduser().resolve()

        if not path_obj.exists():
            return f"File not found: {path}"

        if not content:
            return "Please provide notes content as JSON array"

        try:
            notes_data = json.loads(content)
        except json.JSONDecodeError:
            return "Invalid JSON content. Expected: [{\"slide\": 1, \"notes\": \"text\"}]"

        try:
            from pptx import Presentation
        except ImportError:
            return "Error: python-pptx not installed. Run: pip install python-pptx"

        try:
            prs = Presentation(str(path_obj))
            notes_added = 0

            for item in notes_data:
                slide_num = item.get("slide", 1)
                notes_text = item.get("notes", "")

                if 1 <= slide_num <= len(prs.slides):
                    slide = prs.slides[slide_num - 1]

                    # Get or create notes slide
                    notes_slide = slide.notes_slide
                    text_frame = notes_slide.notes_text_frame
                    text_frame.text = notes_text
                    notes_added += 1

            output_path = Path(output).expanduser().resolve() if output else path_obj
            prs.save(str(output_path))

            return f"Added notes to: {output_path}\n  Slides with notes: {notes_added}"

        except Exception as e:
            return f"Error adding notes: {str(e)}"

    async def _thumbnail(
        self,
        path: str,
        content: str = "",
        output: str = "",
        template: str = "",
        theme: str = "",
        **kwargs,
    ) -> str:
        """Generate thumbnail grid image from presentation"""
        path_obj = Path(path).expanduser().resolve()

        if not path_obj.exists():
            return f"File not found: {path}"

        # Check for LibreOffice (for PDF conversion)
        libreoffice_paths = [
            "/Applications/LibreOffice.app/Contents/MacOS/soffice",
            "libreoffice",
            "soffice",
        ]

        soffice = None
        for p in libreoffice_paths:
            if shutil.which(p):
                soffice = p
                break
            if Path(p).exists():
                soffice = p
                break

        if not soffice:
            return "Error: LibreOffice not found. Install: brew install --cask libreoffice"

        # Check for pdf2image
        try:
            from pdf2image import convert_from_path
        except ImportError:
            return "Error: pdf2image not installed. Run: pip install pdf2image"

        output_path = Path(output).expanduser().resolve() if output else path_obj.with_suffix(".png")

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Convert PPTX to PDF using LibreOffice
                cmd = [
                    soffice,
                    "--headless",
                    "--convert-to", "pdf",
                    "--outdir", temp_dir,
                    str(path_obj),
                ]

                result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

                if result.returncode != 0:
                    return f"LibreOffice error: {result.stderr}"

                # Find generated PDF
                pdf_file = Path(temp_dir) / (path_obj.stem + ".pdf")
                if not pdf_file.exists():
                    return "Error: PDF conversion failed"

                # Convert PDF to images
                images = convert_from_path(str(pdf_file), dpi=150)

                if not images:
                    return "Error: No slides converted"

                # Create thumbnail grid
                from PIL import Image

                # Calculate grid dimensions
                cols = min(4, len(images))
                rows = (len(images) + cols - 1) // cols

                thumb_width = 400
                thumb_height = 300

                grid_width = cols * thumb_width
                grid_height = rows * thumb_height

                grid = Image.new("RGB", (grid_width, grid_height), "white")

                for i, img in enumerate(images):
                    # Resize to thumbnail
                    thumb = img.copy()
                    thumb.thumbnail((thumb_width, thumb_height), Image.Resampling.LANCZOS)

                    # Calculate position
                    row = i // cols
                    col = i % cols
                    x = col * thumb_width + (thumb_width - thumb.width) // 2
                    y = row * thumb_height + (thumb_height - thumb.height) // 2

                    grid.paste(thumb, (x, y))

                grid.save(str(output_path))

            return f"Generated thumbnail grid: {output_path}\n  Slides: {len(images)}\n  Grid: {cols}x{rows}"

        except subprocess.TimeoutExpired:
            return "Error: LibreOffice conversion timed out"
        except Exception as e:
            return f"Error generating thumbnail: {str(e)}"

    def _unpack_pptx(self, pptx_path: Path, output_dir: Path):
        """Unpack PPTX file to directory"""
        output_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(pptx_path, "r") as zf:
            zf.extractall(output_dir)

    def _pack_pptx(self, source_dir: Path, output_path: Path):
        """Pack directory back to PPTX file"""
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(source_dir)
                    zf.write(file_path, arcname)
