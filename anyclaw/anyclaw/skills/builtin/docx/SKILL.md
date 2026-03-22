# DOCX Document Skill

Word document processing: create, read, edit, and analyze .docx files.

## Usage

```
docx <action> <path> [options]
```

## Actions

| Action | Description |
|--------|-------------|
| `create` | Create a new Word document |
| `read` | Read document content (converts to markdown) |
| `edit` | Edit document with text replacement |
| `extract` | Extract plain text from document |
| `info` | Get document metadata |

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `path` | Yes | File path |
| `content` | For create/edit | Content or replacement rules |
| `output` | No | Output file path |
| `track_changes` | No | Enable tracked changes mode |
| `format` | No | Output format (markdown/text) |
| `title` | No | Document title (for create) |

## Content Format

### For Create
Supports markdown-like syntax:
- `# Heading 1` -> Heading 1
- `## Heading 2` -> Heading 2
- `**bold**` -> Bold text
- `*italic*` -> Italic text
- `- item` -> Bullet list
- `1. item` -> Numbered list
- `| cell | cell |` -> Table

### For Edit
Replacement format:
- Single: `"old_text|new_text"`
- Multiple: `"old1|new1||old2|new2"`

## Examples

### Create Document

```bash
# Simple document
docx create /path/to/report.docx --content "# Report\n\nThis is the content."

# With title
docx create /path/to/report.docx --title "Monthly Report" --content "Content here..."

# With table
docx create /path/to/data.docx --content "
| Name | Value |
|------|-------|
| A    | 100   |
| B    | 200   |
"
```

### Read Document

```bash
# Convert to markdown
docx read /path/to/document.docx

# With tracked changes
docx read /path/to/document.docx --track-changes
```

### Edit Document

```bash
# Simple replacement
docx edit /path/to/contract.docx --content "old company name|New Company Name"

# Multiple replacements
docx edit /path/to/contract.docx --content "old1|new1||old2|new2"

# With tracked changes (redlining)
docx edit /path/to/contract.docx --content "original clause|revised clause" --track-changes
```

### Extract Text

```bash
# Plain text extraction
docx extract /path/to/document.docx
```

### Get Info

```bash
# Document metadata
docx info /path/to/document.docx
```

## Requirements

- **python-docx**: For create and extract operations
  ```bash
  pip install python-docx
  ```

- **pandoc** (optional): For enhanced read conversion
  ```bash
  # macOS
  brew install pandoc

  # Ubuntu/Debian
  sudo apt install pandoc
  ```

## Notes

- Create supports markdown-like formatting
- Read uses pandoc if available, falls back to python-docx
- Edit preserves document structure and formatting
- Track changes creates redlining markup for review workflows
- Output is limited to 50,000 characters to prevent context overflow
