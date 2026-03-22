# PDF Document Skill

PDF document processing: create, merge, split, extract text/tables, forms, OCR.

## Usage

```
pdf <action> <path> [options]
```

## Actions

| Action | Description |
|--------|-------------|
| `create` | Create PDF from text/data |
| `merge` | Merge multiple PDFs into one |
| `split` | Split PDF by page range |
| `extract-text` | Extract text content |
| `extract-tables` | Extract tables to CSV/JSON |
| `info` | Get PDF metadata |
| `rotate` | Rotate pages |
| `watermark` | Add watermark |
| `fill-form` | Fill PDF form fields |
| `ocr` | OCR for scanned PDFs |

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `path` | Yes | Input file path(s), comma-separated for merge |
| `output` | For some actions | Output file path |
| `pages` | No | Page range (e.g., "1-3,5,7-10") |
| `content` | For create/fill-form | Text content or form data (JSON) |
| `format` | No | Output format for tables (json/csv) |
| `degrees` | For rotate | Rotation angle (90, 180, 270) |

## Examples

### Create PDF

```bash
# Simple PDF
pdf create /output.pdf --content "# Report\n\nThis is the content."

# With headings and lists
pdf create /output.pdf --content "
# Title
## Section 1
- Item 1
- Item 2

## Section 2
Paragraph text here.
"
```

### Merge PDFs

```bash
# Merge multiple files
pdf merge /file1.pdf,/file2.pdf,/file3.pdf --output /merged.pdf
```

### Split PDF

```bash
# Extract specific pages
pdf split /input.pdf --pages "1-3" --output /part1.pdf

# Multiple ranges
pdf split /input.pdf --pages "1-3,5,7-10" --output /selected.pdf
```

### Extract Text

```bash
# All pages
pdf extract-text /input.pdf

# Specific pages
pdf extract-text /input.pdf --pages "1-5"

# Save to file
pdf extract-text /input.pdf --output /output.txt
```

### Extract Tables

```bash
# JSON format (default)
pdf extract-tables /input.pdf

# CSV format
pdf extract-tables /input.pdf --format csv

# Save to file
pdf extract-tables /input.pdf --output /tables.json
```

### Get Info

```bash
# View metadata
pdf info /input.pdf
```

### Rotate Pages

```bash
# Rotate all pages 90°
pdf rotate /input.pdf --degrees 90

# Rotate specific pages
pdf rotate /input.pdf --pages "1,3,5" --degrees 180
```

### Add Watermark

```bash
pdf watermark /input.pdf --content "CONFIDENTIAL" --output /watermarked.pdf
```

### Fill Form

```bash
# List available fields
pdf fill-form /form.pdf

# Fill fields
pdf fill-form /form.pdf --content '{"name": "John Doe", "date": "2024-01-15"}'

# Save to new file
pdf fill-form /form.pdf --content '{"field1": "value1"}' --output /filled.pdf
```

### OCR

```bash
# Extract text from scanned PDF
pdf ocr /scanned.pdf

# Save result
pdf ocr /scanned.pdf --output /ocr_result.txt
```

## Requirements

### Core Dependencies

```bash
pip install pypdf pdfplumber reportlab
```

### Optional Dependencies

```bash
# For OCR support
pip install pdf2image pytesseract
brew install tesseract  # macOS
sudo apt install tesseract-ocr  # Ubuntu

# For table extraction
pip install pandas
```

## Notes

- Page numbers are 1-indexed
- Page ranges support comma-separated values and hyphens
- Large PDFs may have output truncated to prevent context overflow
- OCR requires tesseract to be installed on the system
- Form filling supports text fields, checkboxes, and radio buttons
