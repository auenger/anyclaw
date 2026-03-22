# XLSX Spreadsheet Skill

Excel spreadsheet processing: create, read, edit, analyze .xlsx files with formula support.

## Usage

```
xlsx <action> <path> [options]
```

## Actions

| Action | Description |
|--------|-------------|
| `create` | Create a new spreadsheet with data and formulas |
| `read` | Read spreadsheet content (returns markdown table) |
| `edit` | Edit cells in existing spreadsheet |
| `analyze` | Analyze data with statistics and insights |
| `recalc` | Recalculate all formulas using LibreOffice |
| `info` | Get spreadsheet metadata |
| `errors` | Check for formula errors |

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `path` | Yes | File path |
| `content` | For create/edit | Data or cell updates |
| `output` | No | Output file path |
| `sheet` | No | Sheet name (default: active sheet) |
| `output_format` | No | Output format (markdown/json/csv) |
| `cell_range` | No | Cell range for analysis (e.g., "A1:D100") |

## Content Format

### For Create
JSON array of rows, or markdown-like table:
```json
[
  ["Name", "Q1", "Q2", "Total"],
  ["Alice", 100, 150, "=B2+C2"],
  ["Bob", 200, 180, "=B3+C3"],
  ["Sum", "=SUM(B2:B3)", "=SUM(C2:C3)", "=SUM(D2:D3)"]
]
```

Or markdown table:
```
| Name | Q1 | Q2 | Total |
|------|----|----|-------|
| Alice | 100 | 150 | =B2+C2 |
| Bob | 200 | 180 | =B3+C3 |
```

### For Edit
Cell updates in format: `A1:value|B2:=SUM(A1:A10)|C3:text`
- Plain value: `A1:Hello`
- Formula: `B2:=SUM(A1:A10)`
- Multiple: `A1:100|B1:200|C1:=A1+B1`

## Color Coding (Financial Models)

When creating financial models, use standard color coding:
- **Blue** (RGB: 0,0,255) - Input values (assumptions)
- **Black** (RGB: 0,0,0) - Formulas
- **Green** (RGB: 0,128,0) - Cross-sheet links
- **Red** (RGB: 255,0,0) - External links
- **Yellow background** - Key assumptions

## Format Specifications

| Type | Format | Example |
|------|--------|---------|
| Years | Text | "2024" not "2,024" |
| Currency | $#,##0 | $1,000 |
| Percent | 0.0% | 15.5% |
| Zero values | "-" | - |
| Negative | (123) | ($100) |

## Examples

### Create Spreadsheet

```bash
# Simple table with formulas
xlsx create /path/to/budget.xlsx --content '
| Item | Jan | Feb | Total |
|------|-----|-----|-------|
| Rent | 1000 | 1000 | =B2+C2 |
| Food | 500 | 600 | =B3+C3 |
| Sum | =SUM(B2:B3) | =SUM(C2:C3) | =SUM(D2:D3) |
'

# With sheet name
xlsx create /path/to/data.xlsx --sheet "Sales" --content '[["A","B"],[1,2]]'

# Financial model with color coding
xlsx create /path/to/model.xlsx --content '...' --financial
```

### Read Spreadsheet

```bash
# Read as markdown table
xlsx read /path/to/spreadsheet.xlsx

# Specific sheet
xlsx read /path/to/spreadsheet.xlsx --sheet "Sheet2"

# As JSON
xlsx read /path/to/spreadsheet.xlsx --format json
```

### Edit Spreadsheet

```bash
# Update single cell
xlsx edit /path/to/spreadsheet.xlsx --content "A1:New Value"

# Update multiple cells
xlsx edit /path/to/spreadsheet.xlsx --content "A1:100|B1:200|C1:=A1+B1"

# Add formula
xlsx edit /path/to/spreadsheet.xlsx --content "D10:=SUM(A1:A9)"
```

### Analyze Data

```bash
# Basic analysis
xlsx analyze /path/to/data.xlsx

# Specific sheet and range
xlsx analyze /path/to/data.xlsx --sheet "Sales" --range "A1:D100"
```

### Recalculate Formulas

```bash
# Recalculate all formulas
xlsx recalc /path/to/spreadsheet.xlsx
```

### Check Errors

```bash
# Find formula errors
xlsx errors /path/to/spreadsheet.xlsx
```

### Get Info

```bash
# Spreadsheet metadata
xlsx info /path/to/spreadsheet.xlsx
```

## Requirements

- **openpyxl**: For create, read, edit operations
  ```bash
  pip install openpyxl
  ```

- **pandas** (optional): For enhanced data analysis
  ```bash
  pip install pandas
  ```

- **LibreOffice** (optional): For formula recalculation
  ```bash
  # macOS
  brew install --cask libreoffice

  # Ubuntu/Debian
  sudo apt install libreoffice-calc
  ```

## Notes

- Always use formulas instead of hardcoded calculated values
- Formulas are preserved when editing
- Recalc requires LibreOffice to be installed
- Zero errors (#REF!, #DIV/0!, #VALUE!) must be fixed before delivery
- Maximum output is 50,000 characters to prevent context overflow
