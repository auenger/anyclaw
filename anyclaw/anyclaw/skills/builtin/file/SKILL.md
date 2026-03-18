# File Operations Skill

Execute basic file read/write operations.

## Usage

```
file <action> <path> [--content "content"]
```

## Actions

- `read`: Read file content
- `write`: Write content to file
- `list`: List directory contents
- `delete`: Delete file
- `exists`: Check if file/directory exists

## Parameters

- `action`: Operation to perform (required)
- `path`: File or directory path
- `content`: Content to write (for write action)

## Examples

```bash
# Read file
file read /path/to/file.txt

# Write file
file write /path/to/file.txt --content "Hello World"

# List directory
file list /path/to/directory

# Check if exists
file exists /path/to/file.txt

# Delete file
file delete /path/to/file.txt
```

## Notes

- Read output is limited to 10,000 characters
- Write operation creates parent directories if needed
- Delete only works on files, not directories
