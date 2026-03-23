"""Tests for PPTX presentation skill."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from anyclaw.skills.builtin.pptx.skill import PptxSkill, COLOR_SCHEMES


class TestPptxSkill:
    """Test cases for PPTX skill."""

    @pytest.fixture
    def skill(self):
        """Create PptxSkill instance."""
        return PptxSkill()

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        with tempfile.TemporaryDirectory() as d:
            yield Path(d)

    # ==================== Help ====================

    @pytest.mark.asyncio
    async def test_help_without_action(self, skill):
        """Test help message when no action provided."""
        result = await skill.execute()
        assert "PPTX Skill" in result
        assert "create" in result
        assert "extract" in result

    @pytest.mark.asyncio
    async def test_missing_path(self, skill):
        """Test error when path is missing."""
        result = await skill.execute(action="create")
        assert "provide a file path" in result.lower()

    @pytest.mark.asyncio
    async def test_unknown_action(self, skill, temp_dir):
        """Test error for unknown action."""
        result = await skill.execute(action="invalid", path=str(temp_dir / "test.pptx"))
        assert "Unknown action" in result

    # ==================== Create ====================

    @pytest.mark.asyncio
    async def test_create_simple(self, skill, temp_dir):
        """Test creating simple presentation."""
        output_path = temp_dir / "test.pptx"
        content = json.dumps([
            {"title": "Title Slide", "content": ["Subtitle"]},
            {"title": "Content Slide", "content": ["Point 1", "Point 2"]}
        ])

        result = await skill.execute(
            action="create",
            path=str(output_path),
            content=content
        )

        assert "Created presentation" in result
        assert output_path.exists()

    @pytest.mark.asyncio
    async def test_create_with_theme(self, skill, temp_dir):
        """Test creating presentation with specific theme."""
        output_path = temp_dir / "test_theme.pptx"
        content = json.dumps([
            {"title": "Test", "content": ["Content"]}
        ])

        result = await skill.execute(
            action="create",
            path=str(output_path),
            content=content,
            theme="teal_coral"
        )

        assert "Created presentation" in result
        assert "Teal & Coral" in result

    @pytest.mark.asyncio
    async def test_create_markdown_format(self, skill, temp_dir):
        """Test creating presentation from markdown format."""
        output_path = temp_dir / "test_md.pptx"
        content = """# First Slide
- Point 1
- Point 2

# Second Slide
- More content
"""

        result = await skill.execute(
            action="create",
            path=str(output_path),
            content=content
        )

        assert "Created presentation" in result
        assert output_path.exists()

    @pytest.mark.asyncio
    async def test_create_no_content(self, skill, temp_dir):
        """Test error when no content provided."""
        output_path = temp_dir / "test.pptx"

        result = await skill.execute(
            action="create",
            path=str(output_path),
            content=""
        )

        assert "No slide content" in result

    @pytest.mark.asyncio
    async def test_create_all_themes(self, skill, temp_dir):
        """Test creating with all available themes."""
        content = json.dumps([{"title": "Test", "content": ["Content"]}])

        for theme_name in COLOR_SCHEMES.keys():
            output_path = temp_dir / f"test_{theme_name}.pptx"

            result = await skill.execute(
                action="create",
                path=str(output_path),
                content=content,
                theme=theme_name
            )

            assert "Created presentation" in result, f"Failed for theme: {theme_name}"
            assert output_path.exists(), f"File not created for theme: {theme_name}"

    # ==================== Extract ====================

    @pytest.mark.asyncio
    async def test_extract_text(self, skill, temp_dir):
        """Test extracting text from presentation."""
        # First create a presentation
        pptx_path = temp_dir / "extract_test.pptx"
        content = json.dumps([
            {"title": "Test Title", "content": ["Point 1", "Point 2"]}
        ])

        await skill.execute(
            action="create",
            path=str(pptx_path),
            content=content
        )

        # Then extract
        result = await skill.execute(
            action="extract",
            path=str(pptx_path)
        )

        assert "Test Title" in result
        assert "Point 1" in result

    @pytest.mark.asyncio
    async def test_extract_file_not_found(self, skill, temp_dir):
        """Test extract with non-existent file."""
        result = await skill.execute(
            action="extract",
            path=str(temp_dir / "nonexistent.pptx")
        )

        assert "not found" in result.lower()

    # ==================== Info ====================

    @pytest.mark.asyncio
    async def test_info(self, skill, temp_dir):
        """Test getting presentation info."""
        # First create a presentation
        pptx_path = temp_dir / "info_test.pptx"
        content = json.dumps([
            {"title": "Test", "content": ["Content"]}
        ])

        await skill.execute(
            action="create",
            path=str(pptx_path),
            content=content
        )

        # Get info
        result = await skill.execute(
            action="info",
            path=str(pptx_path)
        )

        assert "Presentation:" in result
        assert "Slides:" in result

    @pytest.mark.asyncio
    async def test_info_file_not_found(self, skill, temp_dir):
        """Test info with non-existent file."""
        result = await skill.execute(
            action="info",
            path=str(temp_dir / "nonexistent.pptx")
        )

        assert "not found" in result.lower()

    # ==================== Edit ====================

    @pytest.mark.asyncio
    async def test_edit_text_replacement(self, skill, temp_dir):
        """Test editing presentation with text replacement."""
        # First create a presentation
        pptx_path = temp_dir / "edit_test.pptx"
        content = json.dumps([
            {"title": "Original Title", "content": ["Original Content"]}
        ])

        await skill.execute(
            action="create",
            path=str(pptx_path),
            content=content
        )

        # Edit
        result = await skill.execute(
            action="edit",
            path=str(pptx_path),
            content="slide:1|Original|Updated"
        )

        assert "Edited" in result

    @pytest.mark.asyncio
    async def test_edit_no_content(self, skill, temp_dir):
        """Test edit without content."""
        pptx_path = temp_dir / "test.pptx"
        pptx_path.touch()

        result = await skill.execute(
            action="edit",
            path=str(pptx_path),
            content=""
        )

        assert "provide replacement content" in result.lower()

    # ==================== Add Notes ====================

    @pytest.mark.asyncio
    async def test_add_notes(self, skill, temp_dir):
        """Test adding speaker notes."""
        # First create a presentation
        pptx_path = temp_dir / "notes_test.pptx"
        content = json.dumps([
            {"title": "Test", "content": ["Content"]}
        ])

        await skill.execute(
            action="create",
            path=str(pptx_path),
            content=content
        )

        # Add notes
        notes = json.dumps([
            {"slide": 1, "notes": "Speaker notes for slide 1"}
        ])

        result = await skill.execute(
            action="add-notes",
            path=str(pptx_path),
            content=notes
        )

        assert "Added notes" in result

    @pytest.mark.asyncio
    async def test_add_notes_invalid_json(self, skill, temp_dir):
        """Test add notes with invalid JSON."""
        pptx_path = temp_dir / "test.pptx"
        pptx_path.touch()

        result = await skill.execute(
            action="add-notes",
            path=str(pptx_path),
            content="not json"
        )

        assert "Invalid JSON" in result

    # ==================== Replace Content ====================

    @pytest.mark.asyncio
    async def test_replace_content(self, skill, temp_dir):
        """Test replacing content in template."""
        # First create a presentation
        pptx_path = temp_dir / "replace_test.pptx"
        content = json.dumps([
            {"title": "Placeholder Title", "content": ["Placeholder Content"]}
        ])

        await skill.execute(
            action="create",
            path=str(pptx_path),
            content=content
        )

        # Replace content
        replacements = json.dumps([
            {
                "slide": 1,
                "replacements": {
                    "Placeholder": "Replaced"
                }
            }
        ])

        result = await skill.execute(
            action="replace-content",
            path=str(pptx_path),
            content=replacements
        )

        assert "Replaced content" in result

    @pytest.mark.asyncio
    async def test_replace_content_no_content(self, skill, temp_dir):
        """Test replace content without content parameter."""
        pptx_path = temp_dir / "test.pptx"
        pptx_path.touch()

        result = await skill.execute(
            action="replace-content",
            path=str(pptx_path),
            content=""
        )

        assert "provide replacement content" in result.lower() or "provide" in result.lower()

    # ==================== Analyze Template ====================

    @pytest.mark.asyncio
    async def test_analyze_template(self, skill, temp_dir):
        """Test analyzing template."""
        # First create a presentation
        pptx_path = temp_dir / "template_test.pptx"
        content = json.dumps([
            {"title": "Slide 1", "content": ["Content A"]},
            {"title": "Slide 2", "content": ["Content B"]}
        ])

        await skill.execute(
            action="create",
            path=str(pptx_path),
            content=content
        )

        # Analyze
        result = await skill.execute(
            action="analyze-template",
            path=str(pptx_path)
        )

        assert "Template Analysis" in result
        assert "Slides: 2" in result

    # ==================== Use Template ====================

    @pytest.mark.asyncio
    async def test_use_template(self, skill, temp_dir):
        """Test using template to create presentation."""
        # First create a template
        template_path = temp_dir / "template.pptx"
        content = json.dumps([
            {"title": "Template", "content": ["Content"]}
        ])

        await skill.execute(
            action="create",
            path=str(template_path),
            content=content
        )

        # Use template
        output_path = temp_dir / "from_template.pptx"

        result = await skill.execute(
            action="use-template",
            path=str(output_path),
            template=str(template_path)
        )

        assert "Created presentation from template" in result
        assert output_path.exists()

    @pytest.mark.asyncio
    async def test_use_template_missing(self, skill, temp_dir):
        """Test use template without template parameter."""
        output_path = temp_dir / "test.pptx"

        result = await skill.execute(
            action="use-template",
            path=str(output_path)
        )

        assert "provide a template" in result.lower()

    # ==================== Thumbnail ====================

    @pytest.mark.asyncio
    async def test_thumbnail_file_not_found(self, skill, temp_dir):
        """Test thumbnail with non-existent file."""
        result = await skill.execute(
            action="thumbnail",
            path=str(temp_dir / "nonexistent.pptx")
        )

        assert "not found" in result.lower()

    # ==================== Content Parsing ====================

    def test_parse_slide_content_json(self, skill):
        """Test parsing JSON content."""
        content = '[{"title": "Test", "content": ["A", "B"]}]'
        result = skill._parse_slide_content(content)

        assert len(result) == 1
        assert result[0]["title"] == "Test"
        assert result[0]["content"] == ["A", "B"]

    def test_parse_slide_content_markdown(self, skill):
        """Test parsing markdown content."""
        content = """# First Slide
- Point 1
- Point 2

# Second Slide
- Point 3"""
        result = skill._parse_slide_content(content)

        assert len(result) == 2
        assert result[0]["title"] == "First Slide"
        assert "Point 1" in result[0]["content"]

    def test_parse_slide_content_empty(self, skill):
        """Test parsing empty content."""
        result = skill._parse_slide_content("")
        assert result == []

    # ==================== Color Schemes ====================

    def test_color_schemes_defined(self):
        """Test that color schemes are properly defined."""
        assert len(COLOR_SCHEMES) >= 5

        for name, scheme in COLOR_SCHEMES.items():
            assert "name" in scheme
            assert "primary" in scheme
            assert "secondary" in scheme
            assert "text" in scheme
            assert "background" in scheme

    # ==================== Integration ====================

    @pytest.mark.asyncio
    async def test_full_workflow(self, skill, temp_dir):
        """Test full workflow: create, extract, info."""
        pptx_path = temp_dir / "workflow.pptx"

        # Create
        content = json.dumps([
            {"title": "Introduction", "content": ["Welcome", "Overview"]},
            {"title": "Features", "content": ["Feature 1", "Feature 2", "Feature 3"]},
            {"title": "Conclusion", "content": ["Thank you", "Questions"]}
        ])

        create_result = await skill.execute(
            action="create",
            path=str(pptx_path),
            content=content,
            theme="ocean_blue"
        )
        assert "Created presentation" in create_result

        # Extract
        extract_result = await skill.execute(
            action="extract",
            path=str(pptx_path)
        )
        assert "Introduction" in extract_result
        assert "Features" in extract_result

        # Info
        info_result = await skill.execute(
            action="info",
            path=str(pptx_path)
        )
        assert "Slides: 3" in info_result

    @pytest.mark.asyncio
    async def test_create_preserves_parent_directory(self, skill, temp_dir):
        """Test that create creates parent directories if needed."""
        output_path = temp_dir / "subdir" / "nested" / "test.pptx"
        content = json.dumps([{"title": "Test", "content": ["Content"]}])

        result = await skill.execute(
            action="create",
            path=str(output_path),
            content=content
        )

        assert "Created presentation" in result
        assert output_path.exists()


class TestPptxSkillEdgeCases:
    """Edge case tests for PPTX skill."""

    @pytest.fixture
    def skill(self):
        return PptxSkill()

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as d:
            yield Path(d)

    @pytest.mark.asyncio
    async def test_create_with_special_characters(self, skill, temp_dir):
        """Test creating presentation with special characters."""
        output_path = temp_dir / "special.pptx"
        content = json.dumps([
            {"title": "Test & <Special> \"Chars\"", "content": ["A & B", "<tag>", "quote: \"test\""]}
        ])

        result = await skill.execute(
            action="create",
            path=str(output_path),
            content=content
        )

        assert "Created presentation" in result

    @pytest.mark.asyncio
    async def test_create_with_unicode(self, skill, temp_dir):
        """Test creating presentation with unicode characters."""
        output_path = temp_dir / "unicode.pptx"
        content = json.dumps([
            {"title": "中文标题", "content": ["日本語", "한국어", "Emoji 🎉"]}
        ])

        result = await skill.execute(
            action="create",
            path=str(output_path),
            content=content
        )

        assert "Created presentation" in result

    @pytest.mark.asyncio
    async def test_create_many_slides(self, skill, temp_dir):
        """Test creating presentation with many slides."""
        output_path = temp_dir / "many_slides.pptx"
        slides = [{"title": f"Slide {i}", "content": [f"Point {j}" for j in range(5)]} for i in range(20)]
        content = json.dumps(slides)

        result = await skill.execute(
            action="create",
            path=str(output_path),
            content=content
        )

        assert "Created presentation" in result
        assert "Slides: 20" in result

    @pytest.mark.asyncio
    async def test_create_long_content(self, skill, temp_dir):
        """Test creating slide with long content."""
        output_path = temp_dir / "long.pptx"
        long_text = "A" * 1000
        content = json.dumps([
            {"title": "Long Content", "content": [long_text]}
        ])

        result = await skill.execute(
            action="create",
            path=str(output_path),
            content=content
        )

        assert "Created presentation" in result

    @pytest.mark.asyncio
    async def test_extract_truncates_long_content(self, skill, temp_dir):
        """Test that extract truncates very long content."""
        # Create presentation with many slides
        pptx_path = temp_dir / "long_extract.pptx"
        slides = [{"title": f"Slide {i}", "content": ["Content " * 100]} for i in range(50)]
        content = json.dumps(slides)

        await skill.execute(
            action="create",
            path=str(pptx_path),
            content=content
        )

        # Extract should truncate
        result = await skill.execute(
            action="extract",
            path=str(pptx_path)
        )

        # Should have truncation marker if content is long
        assert len(result) <= 55000  # 50k + some buffer for header
