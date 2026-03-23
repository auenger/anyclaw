# PPTX Presentation Skill

PowerPoint presentation processing: create, edit, analyze .pptx files with professional designs.

## Usage

```
pptx <action> <path> [options]
```

## Actions

| Action | Description |
|--------|-------------|
| `create` | Create a new presentation with professional design |
| `edit` | Edit existing presentation with text replacement |
| `extract` | Extract text content from presentation |
| `info` | Get presentation metadata |
| `analyze-template` | Analyze template layouts and structure |
| `use-template` | Create from template with content |
| `replace-content` | Replace content in template slides |
| `add-notes` | Add speaker notes to slides |
| `thumbnail` | Generate thumbnail grid image |

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `path` | Yes | File path |
| `content` | For create/edit | Slide content or replacements |
| `output` | No | Output file path |
| `template` | For use-template | Template file path |
| `theme` | No | Color theme (default: classic_blue) |

## Color Themes

Built-in professional color schemes:

| Theme | Description | Colors |
|-------|-------------|--------|
| `classic_blue` | Deep blue professional | Navy, teal, gold |
| `teal_coral` | Modern teal & coral | Teal, coral, mint |
| `bold_red` | Bold and energetic | Red, orange |
| `warm_blush` | Warm and inviting | Purple, pink, orange |
| `black_gold` | Elegant and premium | Black, gold |
| `forest_green` | Natural and calm | Forest green tones |
| `sunset_orange` | Vibrant and warm | Orange gradient |
| `ocean_blue` | Fresh and professional | Ocean blue tones |

## Content Format

### For Create

JSON array of slides:
```json
[
  {
    "title": "Slide Title",
    "content": ["Bullet point 1", "Bullet point 2", "Bullet point 3"],
    "type": "content"
  },
  {
    "title": "Second Slide",
    "content": ["More content", "Additional points"]
  }
]
```

Or markdown-like format:
```
# First Slide Title
- Bullet point 1
- Bullet point 2
- Bullet point 3

# Second Slide Title
- More content
- Additional points
```

### For Edit

Text replacement format:
```
slide:1|old text|new text
```

Multiple replacements:
```
slide:1|old1|new1||slide:2|old2|new2
```

### For Replace-Content

JSON array with replacements:
```json
[
  {
    "slide": 1,
    "replacements": {
      "Placeholder Title": "Actual Title",
      "Placeholder Content": "Actual Content"
    }
  }
]
```

### For Add-Notes

JSON array with speaker notes:
```json
[
  {
    "slide": 1,
    "notes": "Speaker notes for slide 1"
  },
  {
    "slide": 2,
    "notes": "Speaker notes for slide 2"
  }
]
```

## Design Principles

When creating presentations:

1. **Web-safe Fonts**: Use Arial, Helvetica, Georgia, Verdana for cross-platform compatibility
2. **Visual Hierarchy**: Large titles (44pt), clear content (24pt)
3. **Color Consistency**: One theme throughout the presentation
4. **Readable Text**: High contrast between text and background
5. **Clean Layout**: 16:9 aspect ratio, proper margins

## Examples

### Create Presentation

```bash
# Simple presentation
pptx create /path/to/slides.pptx --content '[
  {"title": "Introduction", "content": ["Welcome", "Agenda", "Overview"]},
  {"title": "Features", "content": ["Feature 1", "Feature 2", "Feature 3"]}
]'

# With theme
pptx create /path/to/slides.pptx --theme teal_coral --content '...'

# From markdown
pptx create /path/to/slides.pptx --content '
# Introduction
- Welcome
- Agenda
- Overview

# Features
- Feature 1
- Feature 2
'
```

### Extract Content

```bash
# Extract all text
pptx extract /path/to/slides.pptx
```

### Get Info

```bash
# Presentation metadata
pptx info /path/to/slides.pptx
```

### Edit Presentation

```bash
# Replace text on slide 1
pptx edit /path/to/slides.pptx --content "slide:1|Old Title|New Title"

# Multiple replacements
pptx edit /path/to/slides.pptx --content "slide:1|old1|new1||slide:2|old2|new2"
```

### Use Template

```bash
# Create from template
pptx use-template /path/to/output.pptx --template /path/to/template.pptx

# With content replacements
pptx use-template /path/to/output.pptx --template /path/to/template.pptx --content '...'
```

### Replace Content

```bash
# Replace placeholders
pptx replace-content /path/to/template.pptx --content '[
  {"slide": 1, "replacements": {"{{title}}": "My Presentation", "{{date}}": "2026-03-23"}}
]'
```

### Add Speaker Notes

```bash
# Add notes to slides
pptx add-notes /path/to/slides.pptx --content '[
  {"slide": 1, "notes": "Welcome everyone to the presentation."},
  {"slide": 2, "notes": "Discuss the key features in detail."}
]'
```

### Generate Thumbnails

```bash
# Create thumbnail grid
pptx thumbnail /path/to/slides.pptx --output /path/to/preview.png
```

## Requirements

- **python-pptx**: For create, read, edit, extract, info operations
  ```bash
  pip install python-pptx
  ```

- **pdf2image** (optional): For thumbnail generation
  ```bash
  pip install pdf2image
  ```

- **LibreOffice** (optional): For thumbnail generation via PDF conversion
  ```bash
  # macOS
  brew install --cask libreoffice

  # Ubuntu/Debian
  sudo apt install libreoffice-impress
  ```

## Notes

- Presentations use 16:9 aspect ratio (13.333" x 7.5")
- All fonts default to Arial for cross-platform compatibility
- Maximum output is 50,000 characters to prevent context overflow
- Template analysis helps identify replaceable content
