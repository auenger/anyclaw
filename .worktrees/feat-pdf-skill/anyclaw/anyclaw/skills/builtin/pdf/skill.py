"""PDF 文档处理技能

支持创建、合并、拆分、提取文本/表格、表单填充、OCR 等 PDF 操作。
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from anyclaw.skills.base import Skill


class PdfSkill(Skill):
    """PDF document operations: create, merge, split, extract, forms, ocr

    Supports:
    - Creating PDF documents from text/data
    - Merging and splitting PDFs
    - Extracting text and tables
    - Form filling
    - OCR for scanned documents
    - Watermarks and encryption
    """

    def __init__(self):
        super().__init__()
        self.name = "pdf"

    async def execute(
        self,
        action: str = "",
        path: str = "",
        output: str = "",
        pages: str = "",
        content: str = "",
        **kwargs,
    ) -> str:
        """Execute PDF operation

        Args:
            action: Operation (create, merge, split, extract-text, extract-tables,
                    info, rotate, watermark, fill-form, ocr)
            path: Input file path(s), comma-separated for merge
            output: Output file path
            pages: Page range for split (e.g., "1-3,5,7-10")
            content: Content for create/fill-form operations
            **kwargs: Additional parameters

        Returns:
            Operation result
        """
        if not action:
            return self._help()

        try:
            action_handlers = {
                "create": self._create,
                "merge": self._merge,
                "split": self._split,
                "extract-text": self._extract_text,
                "extract-tables": self._extract_tables,
                "extract_text": self._extract_text,  # alias
                "extract_tables": self._extract_tables,  # alias
                "info": self._info,
                "rotate": self._rotate,
                "watermark": self._watermark,
                "fill-form": self._fill_form,
                "fill_form": self._fill_form,  # alias
                "ocr": self._ocr,
            }

            handler = action_handlers.get(action.lower().replace("_", "-"))
            if not handler:
                return f"Unknown action: {action}. Supported: {', '.join(action_handlers.keys())}"

            return await handler(path, output, pages, content, **kwargs)

        except Exception as e:
            return f"Error: {str(e)}"

    def _help(self) -> str:
        """Return help message"""
        return """PDF Skill - PDF Document Operations

Actions:
  create         - Create PDF from text/data
  merge          - Merge multiple PDFs into one
  split          - Split PDF by page range
  extract-text   - Extract text content
  extract-tables - Extract tables to CSV/JSON
  info           - Get PDF metadata
  rotate         - Rotate pages
  watermark      - Add watermark
  fill-form      - Fill PDF form fields
  ocr            - OCR for scanned PDFs

Parameters:
  path     - Input file path(s), comma-separated for merge
  output   - Output file path
  pages    - Page range (e.g., "1-3,5,7-10")
  content  - Text content or form data (JSON)

Examples:
  pdf create /output.pdf --content "# Report\nContent here"
  pdf merge /file1.pdf,/file2.pdf --output /merged.pdf
  pdf split /input.pdf --pages "1-3" --output /part1.pdf
  pdf extract-text /input.pdf
  pdf extract-tables /input.pdf --format csv
  pdf info /input.pdf
  pdf rotate /input.pdf --degrees 90
  pdf fill-form /form.pdf --content '{"field1": "value1"}'
  pdf ocr /scanned.pdf
"""

    async def _create(
        self,
        path: str,
        output: str = "",
        pages: str = "",
        content: str = "",
        **kwargs,
    ) -> str:
        """Create PDF from text content"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import (
                SimpleDocTemplate,
                Paragraph,
                Spacer,
                Table,
                TableStyle,
            )
            from reportlab.lib import colors
        except ImportError:
            return "Error: reportlab not installed. Run: pip install reportlab"

        if not path:
            return "Please provide output path"

        if not content:
            return "Please provide content for PDF"

        try:
            output_path = Path(path).expanduser().resolve()
            output_path.parent.mkdir(parents=True, exist_ok=True)

            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72,
            )

            styles = getSampleStyleSheet()
            story = []

            # Parse content
            lines = content.split("\n")
            for line in lines:
                line = line.rstrip()
                if not line:
                    story.append(Spacer(1, 0.2 * inch))
                elif line.startswith("# "):
                    # Heading 1
                    style = ParagraphStyle(
                        "Heading1Custom",
                        parent=styles["Heading1"],
                        fontSize=18,
                        spaceAfter=12,
                    )
                    story.append(Paragraph(line[2:], style))
                elif line.startswith("## "):
                    # Heading 2
                    style = ParagraphStyle(
                        "Heading2Custom",
                        parent=styles["Heading2"],
                        fontSize=14,
                        spaceAfter=10,
                    )
                    story.append(Paragraph(line[3:], style))
                elif line.startswith("### "):
                    # Heading 3
                    style = ParagraphStyle(
                        "Heading3Custom",
                        parent=styles["Heading3"],
                        fontSize=12,
                        spaceAfter=8,
                    )
                    story.append(Paragraph(line[4:], style))
                elif line.startswith("- ") or line.startswith("* "):
                    # Bullet list
                    story.append(Paragraph(f"• {line[2:]}", styles["Normal"]))
                elif "|" in line and "---" not in line:
                    # Potential table - skip header separator
                    story.append(Paragraph(line, styles["Code"]))
                else:
                    # Normal paragraph
                    story.append(Paragraph(line, styles["Normal"]))

            doc.build(story)
            return f"✓ Created PDF: {output_path}"

        except Exception as e:
            return f"Error creating PDF: {str(e)}"

    async def _merge(
        self,
        path: str,
        output: str = "",
        pages: str = "",
        content: str = "",
        **kwargs,
    ) -> str:
        """Merge multiple PDFs into one"""
        try:
            from pypdf import PdfWriter, PdfReader
        except ImportError:
            return "Error: pypdf not installed. Run: pip install pypdf"

        if not path:
            return "Please provide input PDF paths (comma-separated)"

        if not output:
            return "Please provide output path"

        try:
            # Parse input paths
            input_paths = [p.strip() for p in path.split(",")]
            input_paths = [Path(p).expanduser().resolve() for p in input_paths]

            # Validate all files exist
            for p in input_paths:
                if not p.exists():
                    return f"File not found: {p}"

            output_path = Path(output).expanduser().resolve()
            output_path.parent.mkdir(parents=True, exist_ok=True)

            writer = PdfWriter()

            for input_path in input_paths:
                reader = PdfReader(str(input_path))
                for page in reader.pages:
                    writer.add_page(page)

            with open(output_path, "wb") as f:
                writer.write(f)

            return f"✓ Merged {len(input_paths)} PDFs into: {output_path}"

        except Exception as e:
            return f"Error merging PDFs: {str(e)}"

    async def _split(
        self,
        path: str,
        output: str = "",
        pages: str = "",
        content: str = "",
        **kwargs,
    ) -> str:
        """Split PDF by page range"""
        try:
            from pypdf import PdfReader, PdfWriter
        except ImportError:
            return "Error: pypdf not installed. Run: pip install pypdf"

        if not path:
            return "Please provide input PDF path"

        if not pages:
            return "Please provide page range (e.g., '1-3,5,7-10')"

        try:
            input_path = Path(path).expanduser().resolve()
            if not input_path.exists():
                return f"File not found: {path}"

            reader = PdfReader(str(input_path))
            total_pages = len(reader.pages)

            # Parse page ranges
            page_numbers = self._parse_page_range(pages, total_pages)
            if not page_numbers:
                return f"Invalid page range. PDF has {total_pages} pages."

            # Determine output path
            if output:
                output_path = Path(output).expanduser().resolve()
            else:
                output_path = input_path.with_suffix(f".split{input_path.suffix}")

            output_path.parent.mkdir(parents=True, exist_ok=True)

            writer = PdfWriter()
            for page_num in page_numbers:
                writer.add_page(reader.pages[page_num - 1])  # 0-indexed

            with open(output_path, "wb") as f:
                writer.write(f)

            return f"✓ Split PDF: {output_path}\n  Pages extracted: {len(page_numbers)} ({pages})"

        except Exception as e:
            return f"Error splitting PDF: {str(e)}"

    def _parse_page_range(self, pages: str, max_pages: int) -> List[int]:
        """Parse page range string into list of page numbers"""
        result = []
        parts = pages.split(",")

        for part in parts:
            part = part.strip()
            if "-" in part:
                # Range
                try:
                    start, end = part.split("-", 1)
                    start, end = int(start), int(end)
                    for p in range(start, min(end + 1, max_pages + 1)):
                        if 1 <= p <= max_pages and p not in result:
                            result.append(p)
                except ValueError:
                    continue
            else:
                # Single page
                try:
                    p = int(part)
                    if 1 <= p <= max_pages and p not in result:
                        result.append(p)
                except ValueError:
                    continue

        return sorted(result)

    async def _extract_text(
        self,
        path: str,
        output: str = "",
        pages: str = "",
        content: str = "",
        **kwargs,
    ) -> str:
        """Extract text from PDF"""
        try:
            import pdfplumber
        except ImportError:
            return "Error: pdfplumber not installed. Run: pip install pdfplumber"

        if not path:
            return "Please provide PDF path"

        try:
            input_path = Path(path).expanduser().resolve()
            if not input_path.exists():
                return f"File not found: {path}"

            text_parts = []

            with pdfplumber.open(str(input_path)) as pdf:
                # Determine page range
                if pages:
                    page_nums = self._parse_page_range(pages, len(pdf.pages))
                else:
                    page_nums = range(1, len(pdf.pages) + 1)

                for page_num in page_nums:
                    page = pdf.pages[page_num - 1]
                    text = page.extract_text()
                    if text:
                        text_parts.append(f"--- Page {page_num} ---\n{text}")

            result = "\n\n".join(text_parts)

            # Limit output
            if len(result) > 50000:
                result = result[:50000] + "\n\n... [content truncated]"

            if output:
                output_path = Path(output).expanduser().resolve()
                output_path.write_text(result, encoding="utf-8")
                return f"✓ Extracted text to: {output_path}"

            return f"Text from {input_path.name}:\n\n{result}"

        except Exception as e:
            return f"Error extracting text: {str(e)}"

    async def _extract_tables(
        self,
        path: str,
        output: str = "",
        pages: str = "",
        content: str = "",
        **kwargs,
    ) -> str:
        """Extract tables from PDF"""
        try:
            import pdfplumber
        except ImportError:
            return "Error: pdfplumber not installed. Run: pip install pdfplumber"

        if not path:
            return "Please provide PDF path"

        try:
            input_path = Path(path).expanduser().resolve()
            if not input_path.exists():
                return f"File not found: {path}"

            all_tables = []
            format_type = kwargs.get("format", "json").lower()

            with pdfplumber.open(str(input_path)) as pdf:
                # Determine page range
                if pages:
                    page_nums = self._parse_page_range(pages, len(pdf.pages))
                else:
                    page_nums = range(1, len(pdf.pages) + 1)

                for page_num in page_nums:
                    page = pdf.pages[page_num - 1]
                    tables = page.extract_tables()
                    for i, table in enumerate(tables):
                        if table:
                            all_tables.append(
                                {
                                    "page": page_num,
                                    "table_index": i,
                                    "data": table,
                                }
                            )

            if not all_tables:
                return f"No tables found in {input_path.name}"

            # Format output
            if format_type == "csv":
                import csv
                import io

                output_lines = []
                for t in all_tables:
                    output_lines.append(f"# Page {t['page']}, Table {t['table_index']}")
                    buffer = io.StringIO()
                    writer = csv.writer(buffer)
                    for row in t["data"]:
                        writer.writerow(row)
                    output_lines.append(buffer.getvalue())
                    output_lines.append("")

                result = "\n".join(output_lines)
            else:
                import json

                result = json.dumps(all_tables, indent=2, ensure_ascii=False)

            if output:
                output_path = Path(output).expanduser().resolve()
                output_path.write_text(result, encoding="utf-8")
                return f"✓ Extracted {len(all_tables)} tables to: {output_path}"

            return f"Tables from {input_path.name}:\n\n{result}"

        except Exception as e:
            return f"Error extracting tables: {str(e)}"

    async def _info(
        self,
        path: str,
        output: str = "",
        pages: str = "",
        content: str = "",
        **kwargs,
    ) -> str:
        """Get PDF metadata"""
        try:
            from pypdf import PdfReader
        except ImportError:
            return "Error: pypdf not installed. Run: pip install pypdf"

        if not path:
            return "Please provide PDF path"

        try:
            input_path = Path(path).expanduser().resolve()
            if not input_path.exists():
                return f"File not found: {path}"

            reader = PdfReader(str(input_path))

            info_lines = [f"PDF: {input_path.name}"]
            info_lines.append(f"Path: {input_path}")
            info_lines.append(f"Size: {input_path.stat().st_size} bytes")
            info_lines.append(f"Pages: {len(reader.pages)}")

            # Metadata
            meta = reader.metadata
            if meta:
                info_lines.append("\nMetadata:")
                if meta.title:
                    info_lines.append(f"  Title: {meta.title}")
                if meta.author:
                    info_lines.append(f"  Author: {meta.author}")
                if meta.subject:
                    info_lines.append(f"  Subject: {meta.subject}")
                if meta.creator:
                    info_lines.append(f"  Creator: {meta.creator}")
                if meta.producer:
                    info_lines.append(f"  Producer: {meta.producer}")
                if meta.creation_date:
                    info_lines.append(f"  Created: {meta.creation_date}")
                if meta.modification_date:
                    info_lines.append(f"  Modified: {meta.modification_date}")

            # Check for encryption
            if reader.is_encrypted:
                info_lines.append("\n⚠️ Document is encrypted")

            return "\n".join(info_lines)

        except Exception as e:
            return f"Error getting PDF info: {str(e)}"

    async def _rotate(
        self,
        path: str,
        output: str = "",
        pages: str = "",
        content: str = "",
        **kwargs,
    ) -> str:
        """Rotate PDF pages"""
        try:
            from pypdf import PdfReader, PdfWriter
        except ImportError:
            return "Error: pypdf not installed. Run: pip install pypdf"

        if not path:
            return "Please provide PDF path"

        degrees = kwargs.get("degrees", 90)
        try:
            degrees = int(degrees)
            if degrees not in [90, 180, 270]:
                return "Degrees must be 90, 180, or 270"
        except ValueError:
            return "Invalid degrees value"

        try:
            input_path = Path(path).expanduser().resolve()
            if not input_path.exists():
                return f"File not found: {path}"

            reader = PdfReader(str(input_path))
            writer = PdfWriter()

            # Determine which pages to rotate
            if pages:
                page_nums = set(self._parse_page_range(pages, len(reader.pages)))
            else:
                page_nums = set(range(1, len(reader.pages) + 1))

            for i, page in enumerate(reader.pages):
                writer.add_page(page)
                if (i + 1) in page_nums:
                    writer.pages[-1].rotate(degrees)

            if output:
                output_path = Path(output).expanduser().resolve()
            else:
                output_path = input_path.with_suffix(f".rotated{input_path.suffix}")

            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "wb") as f:
                writer.write(f)

            return f"✓ Rotated {len(page_nums)} pages by {degrees}°: {output_path}"

        except Exception as e:
            return f"Error rotating PDF: {str(e)}"

    async def _watermark(
        self,
        path: str,
        output: str = "",
        pages: str = "",
        content: str = "",
        **kwargs,
    ) -> str:
        """Add watermark to PDF"""
        try:
            from pypdf import PdfReader, PdfWriter, Transformation
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            from reportlab.lib import colors
        except ImportError as e:
            return f"Error: Required library not installed. Run: pip install pypdf reportlab"

        if not path:
            return "Please provide PDF path"

        if not content:
            return "Please provide watermark text"

        try:
            input_path = Path(path).expanduser().resolve()
            if not input_path.exists():
                return f"File not found: {path}"

            # Create watermark PDF
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp_path = tmp.name

            c = canvas.Canvas(tmp_path, pagesize=letter)
            c.setFont("Helvetica", 60)
            c.setFillColor(colors.Color(0.5, 0.5, 0.5, alpha=0.3))
            c.rotate(45)
            c.drawString(200, 100, content)
            c.save()

            # Apply watermark
            watermark_reader = PdfReader(tmp_path)
            watermark_page = watermark_reader.pages[0]

            reader = PdfReader(str(input_path))
            writer = PdfWriter()

            for page in reader.pages:
                page.merge_transformed_page(
                    watermark_page, Transformation().rotate(0).translate(0, 0)
                )
                writer.add_page(page)

            if output:
                output_path = Path(output).expanduser().resolve()
            else:
                output_path = input_path.with_suffix(f".watermarked{input_path.suffix}")

            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "wb") as f:
                writer.write(f)

            # Cleanup temp file
            os.unlink(tmp_path)

            return f"✓ Added watermark to: {output_path}"

        except Exception as e:
            return f"Error adding watermark: {str(e)}"

    async def _fill_form(
        self,
        path: str,
        output: str = "",
        pages: str = "",
        content: str = "",
        **kwargs,
    ) -> str:
        """Fill PDF form fields"""
        try:
            from pypdf import PdfReader, PdfWriter
        except ImportError:
            return "Error: pypdf not installed. Run: pip install pypdf"

        if not path:
            return "Please provide PDF form path"

        try:
            input_path = Path(path).expanduser().resolve()
            if not input_path.exists():
                return f"File not found: {path}"

            reader = PdfReader(str(input_path))

            # Check if form has fields
            if not reader.get_fields():
                return "This PDF has no fillable form fields"

            # Parse form data
            import json

            try:
                if content:
                    form_data = json.loads(content)
                else:
                    # List available fields
                    fields = reader.get_fields()
                    field_names = [f"/{k}" if not k.startswith("/") else k for k in fields.keys()]
                    return f"Available form fields:\n" + "\n".join(f"  - {f}" for f in field_names)
            except json.JSONDecodeError:
                return "Invalid JSON format for form data"

            # Fill form
            writer = PdfWriter()
            writer.clone_reader_document_root(reader)

            # Update form fields
            writer.update_page_form_field_values(
                writer.pages[0],
                form_data,
            )

            if output:
                output_path = Path(output).expanduser().resolve()
            else:
                output_path = input_path.with_suffix(f".filled{input_path.suffix}")

            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "wb") as f:
                writer.write(f)

            return f"✓ Filled form: {output_path}\n  Fields filled: {len(form_data)}"

        except Exception as e:
            return f"Error filling form: {str(e)}"

    async def _ocr(
        self,
        path: str,
        output: str = "",
        pages: str = "",
        content: str = "",
        **kwargs,
    ) -> str:
        """OCR for scanned PDF"""
        # Check for required tools
        if not shutil.which("tesseract"):
            return (
                "Error: tesseract not installed.\n"
                "Install with:\n"
                "  macOS: brew install tesseract\n"
                "  Ubuntu: sudo apt install tesseract-ocr"
            )

        try:
            import pdf2image
            import pytesseract
        except ImportError:
            return "Error: Required libraries not installed. Run: pip install pdf2image pytesseract"

        if not path:
            return "Please provide PDF path"

        try:
            input_path = Path(path).expanduser().resolve()
            if not input_path.exists():
                return f"File not found: {path}"

            # Convert PDF to images
            images = pdf2image.convert_from_path(str(input_path))

            if not images:
                return "No pages found in PDF"

            # Determine page range
            if pages:
                page_nums = self._parse_page_range(pages, len(images))
            else:
                page_nums = range(1, len(images) + 1)

            # OCR each page
            text_parts = []
            for page_num in page_nums:
                image = images[page_num - 1]
                text = pytesseract.image_to_string(image)
                text_parts.append(f"--- Page {page_num} ---\n{text.strip()}")

            result = "\n\n".join(text_parts)

            if output:
                output_path = Path(output).expanduser().resolve()
                output_path.write_text(result, encoding="utf-8")
                return f"✓ OCR result saved to: {output_path}"

            return f"OCR result from {input_path.name}:\n\n{result}"

        except Exception as e:
            return f"Error performing OCR: {str(e)}"
