"""Tests for XLSX skill."""

import os
import tempfile
from pathlib import Path

import pytest

from anyclaw.skills.builtin.xlsx.skill import XlsxSkill


@pytest.fixture
def xlsx_skill():
    """Create XLSX skill instance."""
    return XlsxSkill()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


class TestXlsxSkillHelp:
    """Test help and basic functionality."""

    @pytest.mark.asyncio
    async def test_help_without_action(self, xlsx_skill):
        """Test help message when no action provided."""
        result = await xlsx_skill.execute()
        assert "XLSX Skill" in result
        assert "create" in result
        assert "read" in result

    @pytest.mark.asyncio
    async def test_missing_path(self, xlsx_skill):
        """Test error when path is missing."""
        result = await xlsx_skill.execute(action="read")
        assert "provide a file path" in result.lower()

    @pytest.mark.asyncio
    async def test_unknown_action(self, xlsx_skill, temp_dir):
        """Test error for unknown action."""
        result = await xlsx_skill.execute(
            action="invalid",
            path=os.path.join(temp_dir, "test.xlsx")
        )
        assert "Unknown action" in result


class TestXlsxSkillCreate:
    """Test spreadsheet creation."""

    @pytest.mark.asyncio
    async def test_create_simple_table(self, xlsx_skill, temp_dir):
        """Test creating a simple table."""
        filepath = os.path.join(temp_dir, "simple.xlsx")
        content = """
| Name | Value |
|------|-------|
| A | 100 |
| B | 200 |
"""
        result = await xlsx_skill.execute(
            action="create",
            path=filepath,
            content=content
        )

        assert "Created spreadsheet" in result
        assert os.path.exists(filepath)

    @pytest.mark.asyncio
    async def test_create_with_formulas(self, xlsx_skill, temp_dir):
        """Test creating a spreadsheet with formulas."""
        filepath = os.path.join(temp_dir, "formulas.xlsx")
        content = """
| Item | Jan | Feb | Total |
|------|-----|-----|-------|
| Rent | 1000 | 1000 | =B2+C2 |
| Sum | =SUM(B2:B2) | =SUM(C2:C2) | =SUM(D2:D2) |
"""
        result = await xlsx_skill.execute(
            action="create",
            path=filepath,
            content=content
        )

        assert "Created spreadsheet" in result
        assert "Formulas: 4" in result

    @pytest.mark.asyncio
    async def test_create_with_json_content(self, xlsx_skill, temp_dir):
        """Test creating from JSON array."""
        filepath = os.path.join(temp_dir, "json.xlsx")
        content = '[["A", "B", "C"], [1, 2, 3], [4, 5, 6]]'

        result = await xlsx_skill.execute(
            action="create",
            path=filepath,
            content=content
        )

        assert "Created spreadsheet" in result

    @pytest.mark.asyncio
    async def test_create_with_sheet_name(self, xlsx_skill, temp_dir):
        """Test creating with custom sheet name."""
        filepath = os.path.join(temp_dir, "named.xlsx")
        content = '[["X", "Y"], [1, 2]]'

        result = await xlsx_skill.execute(
            action="create",
            path=filepath,
            content=content,
            sheet="Data"
        )

        assert "Created spreadsheet" in result

    @pytest.mark.asyncio
    async def test_create_financial_model(self, xlsx_skill, temp_dir):
        """Test creating with financial model styling."""
        filepath = os.path.join(temp_dir, "financial.xlsx")
        content = '[["Revenue", "Cost", "Profit"], [1000, 600, "=A2-B2"]]'

        result = await xlsx_skill.execute(
            action="create",
            path=filepath,
            content=content,
            financial=True
        )

        assert "Financial model styling applied" in result

    @pytest.mark.asyncio
    async def test_create_empty_content(self, xlsx_skill, temp_dir):
        """Test error when no content provided."""
        filepath = os.path.join(temp_dir, "empty.xlsx")

        result = await xlsx_skill.execute(
            action="create",
            path=filepath,
            content=""
        )

        assert "No content provided" in result


class TestXlsxSkillRead:
    """Test spreadsheet reading."""

    @pytest.mark.asyncio
    async def test_read_nonexistent_file(self, xlsx_skill, temp_dir):
        """Test error when file doesn't exist."""
        result = await xlsx_skill.execute(
            action="read",
            path=os.path.join(temp_dir, "nonexistent.xlsx")
        )
        assert "not found" in result.lower()

    @pytest.mark.asyncio
    async def test_read_created_file(self, xlsx_skill, temp_dir):
        """Test reading a created file."""
        filepath = os.path.join(temp_dir, "read_test.xlsx")

        # Create first
        await xlsx_skill.execute(
            action="create",
            path=filepath,
            content='[["A", "B"], [1, 2]]'
        )

        # Then read
        result = await xlsx_skill.execute(
            action="read",
            path=filepath
        )

        assert "Content of" in result
        assert "A | B" in result

    @pytest.mark.asyncio
    async def test_read_json_format(self, xlsx_skill, temp_dir):
        """Test reading as JSON."""
        filepath = os.path.join(temp_dir, "json_read.xlsx")

        await xlsx_skill.execute(
            action="create",
            path=filepath,
            content='[["X", "Y"], [10, 20]]'
        )

        result = await xlsx_skill.execute(
            action="read",
            path=filepath,
            output_format="json"
        )

        assert "[" in result and "]" in result

    @pytest.mark.asyncio
    async def test_read_csv_format(self, xlsx_skill, temp_dir):
        """Test reading as CSV."""
        filepath = os.path.join(temp_dir, "csv_read.xlsx")

        await xlsx_skill.execute(
            action="create",
            path=filepath,
            content='[["Col1", "Col2"], ["a", "b"]]'
        )

        result = await xlsx_skill.execute(
            action="read",
            path=filepath,
            output_format="csv"
        )

        assert "Col1" in result and "Col2" in result


class TestXlsxSkillEdit:
    """Test spreadsheet editing."""

    @pytest.mark.asyncio
    async def test_edit_single_cell(self, xlsx_skill, temp_dir):
        """Test editing a single cell."""
        filepath = os.path.join(temp_dir, "edit_single.xlsx")

        # Create first
        await xlsx_skill.execute(
            action="create",
            path=filepath,
            content='[["A", "B"], [1, 2]]'
        )

        # Edit
        result = await xlsx_skill.execute(
            action="edit",
            path=filepath,
            content="A1:Updated"
        )

        assert "Edited spreadsheet" in result
        assert "Cells updated: 1" in result

    @pytest.mark.asyncio
    async def test_edit_multiple_cells(self, xlsx_skill, temp_dir):
        """Test editing multiple cells."""
        filepath = os.path.join(temp_dir, "edit_multi.xlsx")

        await xlsx_skill.execute(
            action="create",
            path=filepath,
            content='[["X", "Y"], [0, 0]]'
        )

        result = await xlsx_skill.execute(
            action="edit",
            path=filepath,
            content="A2:100|B2:200"
        )

        assert "Cells updated: 2" in result

    @pytest.mark.asyncio
    async def test_edit_with_formula(self, xlsx_skill, temp_dir):
        """Test adding a formula via edit."""
        filepath = os.path.join(temp_dir, "edit_formula.xlsx")

        await xlsx_skill.execute(
            action="create",
            path=filepath,
            content='[["A", "B", "Sum"], [10, 20, 0]]'
        )

        result = await xlsx_skill.execute(
            action="edit",
            path=filepath,
            content="C2:=A2+B2"
        )

        assert "Cells updated: 1" in result

    @pytest.mark.asyncio
    async def test_edit_missing_content(self, xlsx_skill, temp_dir):
        """Test error when no edit content provided."""
        filepath = os.path.join(temp_dir, "no_content.xlsx")

        await xlsx_skill.execute(
            action="create",
            path=filepath,
            content='[["A"], [1]]'
        )

        result = await xlsx_skill.execute(
            action="edit",
            path=filepath,
            content=""
        )

        assert "provide cell updates" in result.lower()


class TestXlsxSkillInfo:
    """Test spreadsheet info."""

    @pytest.mark.asyncio
    async def test_info(self, xlsx_skill, temp_dir):
        """Test getting spreadsheet info."""
        filepath = os.path.join(temp_dir, "info_test.xlsx")

        await xlsx_skill.execute(
            action="create",
            path=filepath,
            content='[["Col1", "Col2"], [1, 2], [3, 4]]'
        )

        result = await xlsx_skill.execute(
            action="info",
            path=filepath
        )

        assert "Spreadsheet:" in result
        assert "Sheets" in result


class TestXlsxSkillErrors:
    """Test error detection."""

    @pytest.mark.asyncio
    async def test_no_errors(self, xlsx_skill, temp_dir):
        """Test when no errors found."""
        filepath = os.path.join(temp_dir, "no_errors.xlsx")

        await xlsx_skill.execute(
            action="create",
            path=filepath,
            content='[["A", "B"], [1, 2]]'
        )

        result = await xlsx_skill.execute(
            action="errors",
            path=filepath
        )

        assert "No formula errors found" in result


class TestXlsxSkillAnalyze:
    """Test data analysis."""

    @pytest.mark.asyncio
    async def test_analyze(self, xlsx_skill, temp_dir):
        """Test analyzing spreadsheet data."""
        filepath = os.path.join(temp_dir, "analyze_test.xlsx")

        content = '[["Name", "Value"], ["A", 100], ["B", 200], ["C", 300]]'
        await xlsx_skill.execute(
            action="create",
            path=filepath,
            content=content
        )

        result = await xlsx_skill.execute(
            action="analyze",
            path=filepath
        )

        assert "Analysis of" in result
        assert "Shape:" in result


class TestXlsxSkillRecalc:
    """Test formula recalculation."""

    @pytest.mark.asyncio
    async def test_recalc_without_libreoffice(self, xlsx_skill, temp_dir):
        """Test recalc when LibreOffice is not available."""
        filepath = os.path.join(temp_dir, "recalc_test.xlsx")

        await xlsx_skill.execute(
            action="create",
            path=filepath,
            content='[["A", "B", "Sum"], [10, 20, "=A2+B2"]]'
        )

        # This will fail if LibreOffice is not installed
        result = await xlsx_skill.execute(
            action="recalc",
            path=filepath
        )

        # Either success or LibreOffice not found error
        assert "Recalculated" in result or "LibreOffice not found" in result


class TestParseHelpers:
    """Test internal parsing helpers."""

    def test_parse_markdown_table(self, xlsx_skill):
        """Test markdown table parsing."""
        content = """
| Name | Value |
|------|-------|
| A | 100 |
| B | 200 |
"""
        result = xlsx_skill._parse_markdown_table(content)

        assert len(result) == 3
        assert result[0] == ["Name", "Value"]
        assert result[1] == ["A", 100]
        assert result[2] == ["B", 200]

    def test_parse_json_content(self, xlsx_skill):
        """Test JSON content parsing."""
        content = '[["A", "B"], [1, 2]]'
        result = xlsx_skill._parse_content(content)

        assert len(result) == 2
        assert result[0] == ["A", "B"]

    def test_parse_value_formula(self, xlsx_skill):
        """Test parsing formula values."""
        assert xlsx_skill._parse_value("=SUM(A1:A10)") == "=SUM(A1:A10)"
        assert xlsx_skill._parse_value("=A1+B1") == "=A1+B1"

    def test_parse_value_number(self, xlsx_skill):
        """Test parsing numeric values."""
        assert xlsx_skill._parse_value("100") == 100
        assert xlsx_skill._parse_value("3.14") == 3.14

    def test_parse_value_string(self, xlsx_skill):
        """Test parsing string values."""
        assert xlsx_skill._parse_value("hello") == "hello"
        assert xlsx_skill._parse_value("") == ""

    def test_parse_cell_updates(self, xlsx_skill):
        """Test parsing cell update strings."""
        result = xlsx_skill._parse_cell_updates("A1:100|B2:=SUM(A1:A10)|C3:text")

        assert len(result) == 3
        assert result[0] == ("A1", "100")
        assert result[1] == ("B2", "=SUM(A1:A10)")
        assert result[2] == ("C3", "text")

    def test_to_markdown_table(self, xlsx_skill):
        """Test converting to markdown table."""
        data = [["A", "B"], [1, 2], [3, 4]]
        result = xlsx_skill._to_markdown_table(data)

        assert "| A | B |" in result
        assert "---" in result  # Separator line
        assert "| 1 | 2 |" in result

    def test_to_csv(self, xlsx_skill):
        """Test converting to CSV."""
        data = [["A", "B"], [1, 2]]
        result = xlsx_skill._to_csv(data)

        assert "A,B" in result
        assert "1,2" in result
