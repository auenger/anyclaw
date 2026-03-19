---
name: skill-creator
description: Create or update AgentSkills. Use when designing, structuring, or packaging skills with scripts, references, and assets.
---

# Skill Creator

Create or update AgentSkills. Use when designing, structuring, or packaging skills with scripts, references, and assets.

## About Skills

Skills are modular, self-contained packages that extend the agent's capabilities by providing specialized knowledge, workflows, and tools. Think of them as "onboarding guides" for specific domains or tasks.

### What Skills Provide

1. **Specialized workflows** - Multi-step procedures for specific domains
2. **Tool integrations** - Instructions for working with specific file formats or APIs
3. **Domain expertise** - Company-specific knowledge, schemas, business logic
4. **Bundled resources** - Scripts, references, and assets for complex and repetitive tasks

## Core Principles

### Concise is Key

The context window is a public good. Skills share the context window with everything else the agent needs.

**Default assumption: the agent is already very smart.** Only add context the agent doesn't already have. Challenge each piece of information: "Does the agent really need this explanation?"

Prefer concise examples over verbose explanations.

### Set Appropriate Degrees of Freedom

Match the level of specificity to the task's fragility and variability:

- **High freedom (text-based instructions)**: Use when multiple approaches are valid
- **Medium freedom (pseudocode or scripts with parameters)**: Use when a preferred pattern exists
- **Low freedom (specific scripts, few parameters)**: Use when operations are fragile and error-prone

## Skill Structure

Every skill consists of a required SKILL.md file and optional bundled resources:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter metadata (required)
│   │   ├── name: (required)
│   │   └── description: (required)
│   └── Markdown instructions (required)
└── Bundled Resources (optional)
    ├── scripts/          - Executable code (Python/Bash/etc.)
    ├── references/       - Documentation to load into context as needed
    └── assets/           - Files used in output (templates, icons, fonts)
```

### SKILL.md (required)

- **Frontmatter** (YAML): Contains `name` and `description` fields
- **Body** (Markdown): Instructions and guidance for using the skill

### Bundled Resources (optional)

- **scripts/**: Executable code for deterministic reliability or repeated tasks
- **references/**: Documentation loaded as needed into context
- **assets/**: Files used in output (templates, images, fonts)

## Skill Naming

- Use lowercase letters, digits, and hyphens only
- Normalize to hyphen-case (e.g., "Plan Mode" -> `plan-mode`)
- Keep names under 64 characters
- Prefer short, verb-led phrases that describe the action
- Name the skill folder exactly after the skill name

## Skill Creation Process

### Step 1: Understand the Skill with Concrete Examples

Ask clarifying questions:
- "What functionality should this skill support?"
- "Can you give examples of how this skill would be used?"
- "What would a user say that should trigger this skill?"

### Step 2: Plan Reusable Skill Contents

Analyze each example to identify what scripts, references, and assets would be helpful.

### Step 3: Initialize the Skill

Use the `create_skill` tool:

```
create_skill(name="my-skill", description="A helper skill", resources=["scripts", "references"])
```

This creates:
- `skills/my-skill/SKILL.md` with template
- `skills/my-skill/scripts/` directory
- `skills/my-skill/references/` directory

### Step 4: Edit the Skill

Write instructions for using the skill. Include:
- Clear workflow guidance
- Code examples for technical skills
- Decision trees for complex workflows

### Step 5: Validate and Package

Validate the skill:
```
validate_skill(path="skills/my-skill")
```

Package for distribution:
```
package_skill(path="skills/my-skill")
```

### Step 6: Reload and Test

Reload the skill to make it immediately available:
```
reload_skill()
```

## Frontmatter Best Practices

Write description that includes both WHAT and WHEN:

```yaml
---
name: docx-processor
description: Comprehensive document creation, editing, and analysis with support for tracked changes, comments, and formatting preservation. Use when working with professional documents (.docx files) for creating, modifying, or extracting content.
---
```

## Progressive Disclosure

Skills use a three-level loading system:

1. **Metadata (name + description)** - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<5k words)
3. **Bundled resources** - As needed by the agent

Keep SKILL.md body under 500 lines. Split content into separate files when approaching this limit.

## Example Skills

- **file**: Basic file read/write operations
- **http**: HTTP requests and API interactions
- **calc**: Calculator and math operations
- **weather**: Weather information lookup
- **code_exec**: Code execution in sandboxed environment

## Tools Available

| Tool | Description |
|------|-------------|
| `create_skill` | Create a new skill directory with SKILL.md template |
| `reload_skill` | Reload all skills (hot reload) |
| `validate_skill` | Validate a skill's format and structure |
| `show_skill` | Display skill details and content preview |
