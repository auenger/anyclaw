"""Tests for DOCX Skill"""

import os
import tempfile
from pathlib import Path

import pytest

from anyclaw.skills.builtin.docx.skill import DocxSkill


@pytest.fixture
def skill():
    """Create DocxSkill instance"""
    return DocxSkill()


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.mark.asyncio
async def test_skill_initialization(skill):
    """Test skill initialization"""
    assert skill.name == "docx"
    assert "create" in skill._help().lower()


@pytest.mark.asyncio
async def test_help_without_action(skill):
    """Test help message when no action provided"""
    result = await skill.execute()
    assert "DOCX Skill" in result
    assert "create" in result.lower()
    assert "read" in result.lower()


@pytest.mark.asyncio
async def test_create_simple_document(skill, temp_dir):
    """Test creating a simple document"""
    doc_path = temp_dir / "test.docx"

    result = await skill.execute(
        action="create",
        path=str(doc_path),
        content="# Test Document\n\nThis is a test paragraph."
    )

    assert "Created document" in result
    assert doc_path.exists()


@pytest.mark.asyncio
async def test_create_document_with_title(skill, temp_dir):
    """Test creating document with title"""
    doc_path = temp_dir / "test_title.docx"

    result = await skill.execute(
        action="create",
        path=str(doc_path),
        content="Content here",
        title="My Report"
    )

    assert "Created document" in result
    assert doc_path.exists()


@pytest.mark.asyncio
async def test_create_document_with_table(skill, temp_dir):
    """Test creating document with table"""
    doc_path = temp_dir / "test_table.docx"

    content = """
| Name | Value |
|------|-------|
| A    | 100   |
| B    | 200   |
"""
    result = await skill.execute(
        action="create",
        path=str(doc_path),
        content=content
    )

    assert "Created document" in result
    assert doc_path.exists()


@pytest.mark.asyncio
async def test_create_document_with_lists(skill, temp_dir):
    """Test creating document with lists"""
    doc_path = temp_dir / "test_lists.docx"

    content = """
# Shopping List

- Item 1
- Item 2
- Item 3

## Steps

1. First step
2. Second step
3. Third step
"""
    result = await skill.execute(
        action="create",
        path=str(doc_path),
        content=content
    )

    assert "Created document" in result
    assert doc_path.exists()


@pytest.mark.asyncio
async def test_read_nonexistent_file(skill):
    """Test reading non-existent file"""
    result = await skill.execute(
        action="read",
        path="/nonexistent/path/file.docx"
    )

    assert "not found" in result.lower()


@pytest.mark.asyncio
async def test_read_created_document(skill, temp_dir):
    """Test reading a created document"""
    doc_path = temp_dir / "test_read.docx"

    # Create document first
    await skill.execute(
        action="create",
        path=str(doc_path),
        content="# Test\n\nHello World"
    )

    # Read it back
    result = await skill.execute(
        action="read",
        path=str(doc_path)
    )

    # Should have content (either from pandoc or fallback)
    assert "Content of" in result or "Text from" in result or len(result) > 10


@pytest.mark.asyncio
async def test_extract_text(skill, temp_dir):
    """Test extracting text from document"""
    doc_path = temp_dir / "test_extract.docx"

    # Create document
    await skill.execute(
        action="create",
        path=str(doc_path),
        content="# Heading\n\nParagraph text here."
    )

    # Extract text
    result = await skill.execute(
        action="extract",
        path=str(doc_path)
    )

    assert "Text from" in result
    assert "Heading" in result or "Paragraph" in result


@pytest.mark.asyncio
async def test_extract_nonexistent_file(skill):
    """Test extracting from non-existent file"""
    result = await skill.execute(
        action="extract",
        path="/nonexistent/file.docx"
    )

    assert "not found" in result.lower()


@pytest.mark.asyncio
async def test_info_document(skill, temp_dir):
    """Test getting document info"""
    doc_path = temp_dir / "test_info.docx"

    # Create document
    await skill.execute(
        action="create",
        path=str(doc_path),
        content="# Info Test\n\nSome content.",
        title="Test Title"
    )

    # Get info
    result = await skill.execute(
        action="info",
        path=str(doc_path)
    )

    assert "Document:" in result
    assert "test_info.docx" in result
    assert "Paragraphs:" in result


@pytest.mark.asyncio
async def test_info_nonexistent_file(skill):
    """Test info on non-existent file"""
    result = await skill.execute(
        action="info",
        path="/nonexistent/file.docx"
    )

    assert "not found" in result.lower()


@pytest.mark.asyncio
async def test_edit_document_simple(skill, temp_dir):
    """Test simple text replacement in document"""
    doc_path = temp_dir / "test_edit.docx"

    # Create document
    await skill.execute(
        action="create",
        path=str(doc_path),
        content="Hello World"
    )

    # Edit it
    result = await skill.execute(
        action="edit",
        path=str(doc_path),
        content="World|Universe"
    )

    assert "Edited document" in result


@pytest.mark.asyncio
async def test_edit_nonexistent_file(skill):
    """Test editing non-existent file"""
    result = await skill.execute(
        action="edit",
        path="/nonexistent/file.docx",
        content="old|new"
    )

    assert "not found" in result.lower()


@pytest.mark.asyncio
async def test_edit_without_content(skill, temp_dir):
    """Test edit without providing content"""
    doc_path = temp_dir / "test_edit_no_content.docx"

    # Create document
    await skill.execute(
        action="create",
        path=str(doc_path),
        content="Some content"
    )

    # Try to edit without content
    result = await skill.execute(
        action="edit",
        path=str(doc_path)
    )

    assert "provide replacement" in result.lower()


@pytest.mark.asyncio
async def test_unknown_action(skill):
    """Test unknown action"""
    result = await skill.execute(
        action="unknown",
        path="/some/path.docx"
    )

    assert "Unknown action" in result


@pytest.mark.asyncio
async def test_missing_path(skill):
    """Test missing path parameter"""
    result = await skill.execute(action="create")

    assert "provide a file path" in result.lower()


@pytest.mark.asyncio
async def test_parse_replacements(skill):
    """Test parsing replacement pairs"""
    # Single replacement
    replacements = skill._parse_replacements("old|new")
    assert len(replacements) == 1
    assert replacements[0] == ("old", "new")

    # Multiple replacements
    replacements = skill._parse_replacements("old1|new1||old2|new2")
    assert len(replacements) == 2
    assert replacements[0] == ("old1", "new1")
    assert replacements[1] == ("old2", "new2")


@pytest.mark.asyncio
async def test_create_document_with_formatting(skill, temp_dir):
    """Test creating document with bold and italic formatting"""
    doc_path = temp_dir / "test_formatting.docx"

    content = "# Formatted Text\n\nThis is **bold** and *italic* text."
    result = await skill.execute(
        action="create",
        path=str(doc_path),
        content=content
    )

    assert "Created document" in result
    assert doc_path.exists()


@pytest.mark.asyncio
async def test_create_document_with_headings(skill, temp_dir):
    """Test creating document with multiple heading levels"""
    doc_path = temp_dir / "test_headings.docx"

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
        path=str(doc_path),
        content=content
    )

    assert "Created document" in result
    assert doc_path.exists()


@pytest.mark.asyncio
async def test_edit_with_output_path(skill, temp_dir):
    """Test editing document to a new output path"""
    source_path = temp_dir / "source.docx"
    output_path = temp_dir / "output.docx"

    # Create source document
    await skill.execute(
        action="create",
        path=str(source_path),
        content="Original content"
    )

    # Edit to new path
    result = await skill.execute(
        action="edit",
        path=str(source_path),
        content="Original|Modified",
        output=str(output_path)
    )

    assert "Edited document" in result
    assert output_path.exists()


@pytest.mark.asyncio
async def test_edit_with_tracked_changes(skill, temp_dir):
    """Test editing with track changes enabled"""
    doc_path = temp_dir / "test_track_changes.docx"

    # Create document
    await skill.execute(
        action="create",
        path=str(doc_path),
        content="Original text"
    )

    # Edit with track changes
    result = await skill.execute(
        action="edit",
        path=str(doc_path),
        content="Original|Modified",
        track_changes=True
    )

    assert "Edited document" in result
