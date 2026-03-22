"""DOCX 文档处理技能

支持创建、读取、编辑 Word 文档，包含追踪变更（redlining）功能。
"""

import os
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import List

from anyclaw.skills.base import Skill


class DocxSkill(Skill):
    """Word document operations: create, read, edit, extract

    Supports:
    - Creating formatted Word documents (titles, paragraphs, tables)
    - Reading documents with pandoc markdown conversion
    - Editing documents with OOXML unpack/pack workflow
    - Redlining workflow with tracked changes support
    """

    def __init__(self):
        super().__init__()
        self.name = "docx"

    async def execute(
        self,
        action: str = "",
        path: str = "",
        content: str = "",
        output: str = "",
        track_changes: bool = False,
        format: str = "markdown",
        **kwargs,
    ) -> str:
        """Execute DOCX operation

        Args:
            action: Operation to perform (create, read, edit, extract, info)
            path: Input file path
            content: Content for create/edit operations
            output: Output file path (optional, defaults to input path for edit)
            track_changes: Enable tracked changes mode for editing
            format: Output format for read (markdown, text)
            **kwargs: Additional parameters (title, template, etc.)

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
                "read": self._read,
                "edit": self._edit,
                "extract": self._extract,
                "info": self._info,
            }

            handler = action_handlers.get(action.lower())
            if not handler:
                return f"Unknown action: {action}. Supported: {', '.join(action_handlers.keys())}"

            return await handler(path, content, output, track_changes, format, **kwargs)

        except Exception as e:
            return f"Error: {str(e)}"

    def _help(self) -> str:
        """Return help message"""
        return """DOCX Skill - Word Document Operations

Actions:
  create  - Create a new Word document
  read    - Read document content (converts to markdown)
  edit    - Edit existing document with text replacement
  extract - Extract text content from document
  info    - Get document metadata

Parameters:
  path          - File path (required)
  content       - Content for create/edit operations
  output        - Output file path (optional)
  track_changes - Enable tracked changes mode (for edit)
  format        - Output format for read (markdown/text)
  title         - Document title (for create)

Examples:
  docx create /path/to/doc.docx --content "# Title\\nParagraph text"
  docx read /path/to/doc.docx
  docx edit /path/to/doc.docx --content "old:text|new:text"
  docx extract /path/to/doc.docx
  docx info /path/to/doc.docx
"""

    async def _create(
        self,
        path: str,
        content: str = "",
        output: str = "",
        track_changes: bool = False,
        format: str = "markdown",
        **kwargs,
    ) -> str:
        """Create a new Word document

        Supports markdown-like content:
        - # Title -> Heading 1
        - ## Section -> Heading 2
        - **bold** -> Bold text
        - *italic* -> Italic text
        - Tables, lists
        """
        try:
            # Check if python-docx is available
            try:
                from docx import Document
            except ImportError:
                return "Error: python-docx not installed. Run: pip install python-docx"

            path_obj = Path(path).expanduser().resolve()
            path_obj.parent.mkdir(parents=True, exist_ok=True)

            doc = Document()

            # Add title if provided
            title = kwargs.get("title", "")
            if title:
                doc.add_heading(title, level=0)

            # Parse and add content
            if content:
                self._parse_content(doc, content)

            # Save document
            doc.save(str(path_obj))
            return f"✓ Created document: {path_obj}"

        except Exception as e:
            return f"Error creating document: {str(e)}"

    def _parse_content(self, doc, content: str):
        """Parse markdown-like content and add to document"""

        lines = content.split("\n")
        i = 0

        while i < len(lines):
            line = lines[i]

            # Heading detection
            if line.startswith("### "):
                doc.add_heading(line[4:].strip(), level=3)
            elif line.startswith("## "):
                doc.add_heading(line[3:].strip(), level=2)
            elif line.startswith("# "):
                doc.add_heading(line[2:].strip(), level=1)
            # Table detection (simple)
            elif "|" in line and i + 1 < len(lines) and "---" in lines[i + 1]:
                # Parse table
                table_lines = [line]
                i += 1
                while i < len(lines) and "|" in lines[i]:
                    table_lines.append(lines[i])
                    i += 1
                self._add_table(doc, table_lines)
                continue
            # List detection
            elif line.startswith("- ") or line.startswith("* "):
                doc.add_paragraph(line[2:].strip(), style="List Bullet")
            elif line.strip().startswith(("1. ", "2. ", "3. ", "4. ", "5. ")):
                # Numbered list
                text = line.strip()
                if ". " in text:
                    text = text.split(". ", 1)[1]
                doc.add_paragraph(text, style="List Number")
            # Empty line
            elif not line.strip():
                pass
            # Regular paragraph
            else:
                para = doc.add_paragraph()
                self._add_formatted_text(para, line)

            i += 1

    def _add_table(self, doc, table_lines: List[str]):
        """Add a table from pipe-separated content"""
        if len(table_lines) < 2:
            return

        # Parse rows
        rows = []
        for line in table_lines:
            if "---" in line:
                continue
            cells = [cell.strip() for cell in line.split("|") if cell.strip()]
            if cells:
                rows.append(cells)

        if not rows:
            return

        # Create table
        num_cols = len(rows[0])
        table = doc.add_table(rows=len(rows), cols=num_cols)
        table.style = "Table Grid"

        for i, row_data in enumerate(rows):
            row = table.rows[i]
            for j, cell_text in enumerate(row_data):
                if j < num_cols:
                    row.cells[j].text = cell_text

    def _add_formatted_text(self, para, text: str):
        """Add text with inline formatting (bold, italic)"""
        import re

        # Simple formatting: **bold** and *italic*
        pattern = r"(\*\*[^*]+\*\*)|(\*[^*]+\*)|([^*]+)"
        matches = re.findall(pattern, text)

        for match in matches:
            bold_text, italic_text, plain_text = match
            if bold_text:
                run = para.add_run(bold_text[2:-2])
                run.bold = True
            elif italic_text:
                run = para.add_run(italic_text[1:-1])
                run.italic = True
            elif plain_text:
                para.add_run(plain_text)

    async def _read(
        self,
        path: str,
        content: str = "",
        output: str = "",
        track_changes: bool = False,
        format: str = "markdown",
        **kwargs,
    ) -> str:
        """Read document content using pandoc conversion"""
        path_obj = Path(path).expanduser().resolve()

        if not path_obj.exists():
            return f"File not found: {path}"

        if not path_obj.suffix.lower() == ".docx":
            return f"Not a DOCX file: {path}"

        # Check pandoc availability
        if not shutil.which("pandoc"):
            # Fallback to python-docx extraction
            return await self._extract(path, content, output, track_changes, format, **kwargs)

        try:
            # Build pandoc command
            cmd = ["pandoc", "-f", "docx", "-t", "markdown"]

            if track_changes:
                cmd.extend(["--track-changes", "all"])

            cmd.append(str(path_obj))

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                return f"Pandoc error: {result.stderr}"

            output_text = result.stdout

            # Limit output size
            if len(output_text) > 50000:
                output_text = output_text[:50000] + "\n\n... [content truncated]"

            return f"Content of {path_obj.name}:\n\n{output_text}"

        except subprocess.TimeoutExpired:
            return "Error: Pandoc conversion timed out"
        except Exception as e:
            return f"Error reading document: {str(e)}"

    async def _edit(
        self,
        path: str,
        content: str = "",
        output: str = "",
        track_changes: bool = False,
        format: str = "markdown",
        **kwargs,
    ) -> str:
        """Edit document with text replacement

        Content format: "old_text|new_text" for replacement
        Multiple replacements: "old1|new1||old2|new2"
        """
        path_obj = Path(path).expanduser().resolve()

        if not path_obj.exists():
            return f"File not found: {path}"

        if not content:
            return "Please provide replacement content in format: 'old_text|new_text'"

        output_path = Path(output).expanduser().resolve() if output else path_obj

        try:
            # Use OOXML unpack/edit/pack workflow
            with tempfile.TemporaryDirectory() as temp_dir:
                # Unpack DOCX
                unpack_dir = Path(temp_dir) / "unpacked"
                self._unpack_docx(path_obj, unpack_dir)

                # Edit document.xml
                doc_xml = unpack_dir / "word" / "document.xml"
                if not doc_xml.exists():
                    return "Error: Invalid DOCX structure (no document.xml)"

                # Read and modify content
                with open(doc_xml, "r", encoding="utf-8") as f:
                    xml_content = f.read()

                # Parse replacements
                replacements = self._parse_replacements(content)

                # Apply replacements
                if track_changes:
                    xml_content = self._apply_tracked_changes(xml_content, replacements)
                else:
                    for old_text, new_text in replacements:
                        xml_content = xml_content.replace(old_text, new_text)

                # Write back
                with open(doc_xml, "w", encoding="utf-8") as f:
                    f.write(xml_content)

                # Repack DOCX
                self._pack_docx(unpack_dir, output_path)

            return f"✓ Edited document: {output_path}\n  Replacements made: {len(replacements)}"

        except Exception as e:
            return f"Error editing document: {str(e)}"

    def _parse_replacements(self, content: str) -> List[tuple]:
        """Parse replacement pairs from content string"""
        replacements = []

        # Split by double pipe for multiple replacements
        pairs = content.split("||")

        for pair in pairs:
            if "|" in pair:
                parts = pair.split("|", 1)
                if len(parts) == 2:
                    old_text, new_text = parts
                    replacements.append((old_text.strip(), new_text.strip()))

        return replacements

    def _apply_tracked_changes(self, xml_content: str, replacements: List[tuple]) -> str:
        """Apply tracked changes markup to replacements"""
        for old_text, new_text in replacements:
            # Simple tracked changes: wrap deletion/insertion in OOXML markup
            # This is a simplified implementation
            del_markup = (
                f'<w:del w:id="1" w:author="Agent">'
                f"<w:r><w:delText>{old_text}</w:delText></w:r></w:del>"
            )
            ins_markup = (
                f'<w:ins w:id="2" w:author="Agent">'
                f"<w:r><w:t>{new_text}</w:t></w:r></w:ins>"
            )
            xml_content = xml_content.replace(
                f"<w:t>{old_text}</w:t>", del_markup + ins_markup
            )

        return xml_content

    async def _extract(
        self,
        path: str,
        content: str = "",
        output: str = "",
        track_changes: bool = False,
        format: str = "markdown",
        **kwargs,
    ) -> str:
        """Extract plain text content from document using python-docx"""
        path_obj = Path(path).expanduser().resolve()

        if not path_obj.exists():
            return f"File not found: {path}"

        try:
            from docx import Document
        except ImportError:
            return "Error: python-docx not installed. Run: pip install python-docx"

        try:
            doc = Document(str(path_obj))

            text_parts = []

            for para in doc.paragraphs:
                text = para.text.strip()
                if text:
                    # Add heading markers
                    if para.style.name.startswith("Heading"):
                        level = para.style.name.replace("Heading ", "")
                        try:
                            level_num = int(level)
                            text = "#" * level_num + " " + text
                        except ValueError:
                            pass
                    text_parts.append(text)

            # Extract table text
            for table in doc.tables:
                for row in table.rows:
                    row_text = " | ".join(cell.text.strip() for cell in row.cells)
                    if row_text.strip():
                        text_parts.append(row_text)

            result = "\n\n".join(text_parts)

            # Limit output
            if len(result) > 50000:
                result = result[:50000] + "\n\n... [content truncated]"

            return f"Text from {path_obj.name}:\n\n{result}"

        except Exception as e:
            return f"Error extracting text: {str(e)}"

    async def _info(
        self,
        path: str,
        content: str = "",
        output: str = "",
        track_changes: bool = False,
        format: str = "markdown",
        **kwargs,
    ) -> str:
        """Get document metadata"""
        path_obj = Path(path).expanduser().resolve()

        if not path_obj.exists():
            return f"File not found: {path}"

        try:
            from docx import Document
        except ImportError:
            return "Error: python-docx not installed. Run: pip install python-docx"

        try:
            doc = Document(str(path_obj))

            info_lines = [f"Document: {path_obj.name}"]
            info_lines.append(f"Path: {path_obj}")
            info_lines.append(f"Size: {path_obj.stat().st_size} bytes")

            # Core properties
            props = doc.core_properties
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
            if props.last_modified_by:
                info_lines.append(f"Last Modified By: {props.last_modified_by}")

            # Document stats
            para_count = len(doc.paragraphs)
            table_count = len(doc.tables)
            word_count = sum(len(p.text.split()) for p in doc.paragraphs)

            info_lines.append("\nStatistics:")
            info_lines.append(f"  Paragraphs: {para_count}")
            info_lines.append(f"  Tables: {table_count}")
            info_lines.append(f"  Words (approx): {word_count}")

            return "\n".join(info_lines)

        except Exception as e:
            return f"Error getting document info: {str(e)}"

    def _unpack_docx(self, docx_path: Path, output_dir: Path):
        """Unpack DOCX file to directory"""
        output_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(docx_path, "r") as zf:
            zf.extractall(output_dir)

    def _pack_docx(self, source_dir: Path, output_path: Path):
        """Pack directory back to DOCX file"""
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(source_dir)
                    zf.write(file_path, arcname)
