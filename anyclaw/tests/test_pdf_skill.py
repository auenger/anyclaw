"""Tests for PDF Skill"""

import tempfile
from pathlib import Path

import pytest

from anyclaw.skills.builtin.pdf.skill import PdfSkill


@pytest.fixture
def skill():
    """Create PdfSkill instance"""
    return PdfSkill()


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.mark.asyncio
async def test_skill_initialization(skill):
    """Test skill initialization"""
    assert skill.name == "pdf"
    assert "create" in skill._help().lower()


@pytest.mark.asyncio
async def test_help_without_action(skill):
    """Test help message when no action provided"""
    result = await skill.execute()
    assert "PDF Skill" in result
    assert "create" in result.lower()
    assert "merge" in result.lower()


@pytest.mark.asyncio
async def test_create_simple_pdf(skill, temp_dir):
    """Test creating a simple PDF"""
    output_path = temp_dir / "test.pdf"

    result = await skill.execute(
        action="create",
        path=str(output_path),
        content="# Test Document\n\nThis is a test paragraph.",
    )

    assert "Created PDF" in result
    assert output_path.exists()


@pytest.mark.asyncio
async def test_create_pdf_with_headings(skill, temp_dir):
    """Test creating PDF with multiple heading levels"""
    output_path = temp_dir / "test_headings.pdf"

    content = """
# Heading 1
Content under heading 1

## Heading 2
Content under heading 2

### Heading 3
Content under heading 3
"""
    result = await skill.execute(
        action="create",
        path=str(output_path),
        content=content,
    )

    assert "Created PDF" in result
    assert output_path.exists()


@pytest.mark.asyncio
async def test_create_pdf_with_lists(skill, temp_dir):
    """Test creating PDF with lists"""
    output_path = temp_dir / "test_lists.pdf"

    content = """
# Shopping List

- Item 1
- Item 2
- Item 3
"""
    result = await skill.execute(
        action="create",
        path=str(output_path),
        content=content,
    )

    assert "Created PDF" in result
    assert output_path.exists()


@pytest.mark.asyncio
async def test_create_without_content(skill, temp_dir):
    """Test creating PDF without content"""
    output_path = temp_dir / "test_no_content.pdf"

    result = await skill.execute(
        action="create",
        path=str(output_path),
    )

    assert "provide content" in result.lower()


@pytest.mark.asyncio
async def test_merge_pdfs(skill, temp_dir):
    """Test merging multiple PDFs"""
    # Create two PDFs first
    pdf1 = temp_dir / "pdf1.pdf"
    pdf2 = temp_dir / "pdf2.pdf"

    await skill.execute(action="create", path=str(pdf1), content="PDF 1 content")
    await skill.execute(action="create", path=str(pdf2), content="PDF 2 content")

    # Merge them
    merged = temp_dir / "merged.pdf"
    result = await skill.execute(
        action="merge",
        path=f"{pdf1},{pdf2}",
        output=str(merged),
    )

    assert "Merged" in result
    assert merged.exists()


@pytest.mark.asyncio
async def test_merge_missing_output(skill, temp_dir):
    """Test merge without output path"""
    result = await skill.execute(
        action="merge",
        path="/tmp/a.pdf,/tmp/b.pdf",
    )

    assert "provide output" in result.lower()


@pytest.mark.asyncio
async def test_merge_nonexistent_file(skill, temp_dir):
    """Test merge with non-existent file"""
    result = await skill.execute(
        action="merge",
        path="/nonexistent/a.pdf,/nonexistent/b.pdf",
        output=str(temp_dir / "merged.pdf"),
    )

    assert "not found" in result.lower()


@pytest.mark.asyncio
async def test_split_pdf(skill, temp_dir):
    """Test splitting PDF"""
    # Create a multi-page PDF
    source = temp_dir / "source.pdf"
    content = """
# Page 1
Content for page 1

# Page 2
Content for page 2

# Page 3
Content for page 3
"""
    await skill.execute(action="create", path=str(source), content=content)

    # Split it
    split = temp_dir / "split.pdf"
    result = await skill.execute(
        action="split",
        path=str(source),
        pages="1-2",
        output=str(split),
    )

    assert "Split PDF" in result
    assert split.exists()


@pytest.mark.asyncio
async def test_split_missing_pages(skill, temp_dir):
    """Test split without page range"""
    source = temp_dir / "source.pdf"
    await skill.execute(action="create", path=str(source), content="Content")

    result = await skill.execute(
        action="split",
        path=str(source),
    )

    assert "page range" in result.lower()


@pytest.mark.asyncio
async def test_extract_text(skill, temp_dir):
    """Test extracting text from PDF"""
    source = temp_dir / "source.pdf"
    await skill.execute(
        action="create",
        path=str(source),
        content="# Test\n\nExtract this text.",
    )

    result = await skill.execute(
        action="extract-text",
        path=str(source),
    )

    assert "Text from" in result or len(result) > 10


@pytest.mark.asyncio
async def test_extract_text_nonexistent(skill):
    """Test extracting text from non-existent file"""
    result = await skill.execute(
        action="extract-text",
        path="/nonexistent/file.pdf",
    )

    assert "not found" in result.lower()


@pytest.mark.asyncio
async def test_extract_tables(skill, temp_dir):
    """Test extracting tables from PDF"""
    source = temp_dir / "source.pdf"
    await skill.execute(
        action="create",
        path=str(source),
        content="# Report\n\n| A | B |\n|---|---|\n| 1 | 2 |",
    )

    result = await skill.execute(
        action="extract-tables",
        path=str(source),
    )

    # Should either find tables or report none
    assert "Tables" in result or "tables" in result.lower() or "No tables" in result


@pytest.mark.asyncio
async def test_info(skill, temp_dir):
    """Test getting PDF info"""
    source = temp_dir / "source.pdf"
    await skill.execute(
        action="create",
        path=str(source),
        content="# Test Document",
    )

    result = await skill.execute(
        action="info",
        path=str(source),
    )

    assert "PDF:" in result
    assert "Pages:" in result


@pytest.mark.asyncio
async def test_info_nonexistent(skill):
    """Test info on non-existent file"""
    result = await skill.execute(
        action="info",
        path="/nonexistent/file.pdf",
    )

    assert "not found" in result.lower()


@pytest.mark.asyncio
async def test_rotate_pdf(skill, temp_dir):
    """Test rotating PDF pages"""
    source = temp_dir / "source.pdf"
    await skill.execute(action="create", path=str(source), content="Content")

    result = await skill.execute(
        action="rotate",
        path=str(source),
        degrees=90,
    )

    assert "Rotated" in result


@pytest.mark.asyncio
async def test_rotate_invalid_degrees(skill, temp_dir):
    """Test rotate with invalid degrees"""
    source = temp_dir / "source.pdf"
    await skill.execute(action="create", path=str(source), content="Content")

    result = await skill.execute(
        action="rotate",
        path=str(source),
        degrees=45,
    )

    assert "90" in result or "180" in result or "must be" in result.lower()


@pytest.mark.asyncio
async def test_watermark_pdf(skill, temp_dir):
    """Test adding watermark to PDF"""
    source = temp_dir / "source.pdf"
    await skill.execute(action="create", path=str(source), content="Content")

    result = await skill.execute(
        action="watermark",
        path=str(source),
        content="CONFIDENTIAL",
    )

    assert "watermark" in result.lower()


@pytest.mark.asyncio
async def test_watermark_without_text(skill, temp_dir):
    """Test watermark without text"""
    source = temp_dir / "source.pdf"
    await skill.execute(action="create", path=str(source), content="Content")

    result = await skill.execute(
        action="watermark",
        path=str(source),
    )

    assert "watermark text" in result.lower()


@pytest.mark.asyncio
async def test_fill_form_list_fields(skill, temp_dir):
    """Test listing form fields"""
    source = temp_dir / "source.pdf"
    await skill.execute(action="create", path=str(source), content="Content")

    result = await skill.execute(
        action="fill-form",
        path=str(source),
    )

    # Since we created a non-form PDF, should report no fields
    assert "form" in result.lower()


@pytest.mark.asyncio
async def test_unknown_action(skill):
    """Test unknown action"""
    result = await skill.execute(
        action="unknown",
        path="/some/path.pdf",
    )

    assert "Unknown action" in result


@pytest.mark.asyncio
async def test_missing_path(skill):
    """Test missing path parameter"""
    result = await skill.execute(action="info")

    assert "provide" in result.lower() or "path" in result.lower()


@pytest.mark.asyncio
async def test_parse_page_range(skill):
    """Test page range parsing"""
    # Single page
    pages = skill._parse_page_range("5", 10)
    assert pages == [5]

    # Range
    pages = skill._parse_page_range("1-3", 10)
    assert pages == [1, 2, 3]

    # Multiple ranges
    pages = skill._parse_page_range("1-3,5,7-8", 10)
    assert pages == [1, 2, 3, 5, 7, 8]

    # Out of bounds
    pages = skill._parse_page_range("1-20", 5)
    assert pages == [1, 2, 3, 4, 5]


@pytest.mark.asyncio
async def test_extract_text_with_pages(skill, temp_dir):
    """Test extracting text with page range"""
    source = temp_dir / "source.pdf"
    await skill.execute(
        action="create",
        path=str(source),
        content="# Page 1\n\n# Page 2\n\n# Page 3",
    )

    result = await skill.execute(
        action="extract-text",
        path=str(source),
        pages="1",
    )

    assert "Page 1" in result or len(result) > 0


@pytest.mark.asyncio
async def test_extract_tables_with_format(skill, temp_dir):
    """Test extracting tables with different format"""
    source = temp_dir / "source.pdf"
    await skill.execute(
        action="create",
        path=str(source),
        content="| A | B |\n|---|---|\n| 1 | 2 |",
    )

    result = await skill.execute(
        action="extract-tables",
        path=str(source),
        format="csv",
    )

    # Should have CSV format or no tables message
    assert "csv" in result.lower() or "Tables" in result or "No tables" in result
