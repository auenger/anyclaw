---
description: 'Complete a feature - commit, merge to main, create archive tag, cleanup worktree and branch.'
---

# Skill: complete-feature

Complete a feature by committing code, merging to main, creating an archive tag, and cleaning up.

## Usage

```
/complete-feature <feature-id> [options]
```

Options:
- `--message=<msg>`: Custom commit message
- `--skip-checklist`: Skip checklist verification
- `--no-merge`: Commit only, don't merge
- `--keep-branch`: Keep branch after merge
- `--resume`: Continue after resolving rebase conflicts

## Pre-flight Checks

### Check 1: Feature Status
- Feature must be in `queue.yaml` active list

### Check 2: Worktree Exists
- Verify worktree path exists
- Verify it's a valid git worktree

### Check 3: Checklist Complete
- Read `features/active-{id}/checklist.md`
- Count unchecked items
- If incomplete and not `--skip-checklist`: warn user

## Execution Steps

### Step 1: Get Feature Info

From `queue.yaml`:
- name, branch, worktree, started timestamp
- Calculate development duration

### Step 2: Check Checklist

```
🔍 Checking checklist...

⚠️ Incomplete items:
  - [ ] Unit tests written
  - [ ] Documentation updated

Continue anyway? (y/n)
```

### Step 3: Commit Code

```bash
cd {worktree_path}
git add .
git status  # Show changes
git commit -m "feat({id}): {name}"
```

Record commit hash.

### Step 4: Merge to Main

**Step 4.1: Get Config Values**

Read from `config.yaml`:
```yaml
project:
  main_branch: main    # Default target branch

git:
  remote: origin       # Remote name
  merge_strategy: "--no-ff"
  auto_push: false
```

```bash
MAIN_BRANCH={config.project.main_branch || "main"}
REMOTE={config.git.remote || "origin"}
```

**Step 4.2: Update Main Branch**

```bash
cd {repo_path}  # Main repo (use repo_path from config if set)
git checkout {main_branch}
git pull {remote} {main_branch}  # Get latest changes
```

**Step 4.3: Rebase Feature Branch**

Rebase feature branch onto latest main to get linear history and detect conflicts early:

```bash
git checkout {branch}
git rebase {main_branch}
```

**Step 4.4: Handle Rebase Conflict (if any)**

If rebase encounters conflicts:

```
❌ Rebase 冲突检测到

冲突文件:
  - src/auth/login.ts

请在 worktree 中解决冲突:
  1. cd {worktree_path}
  2. 打开冲突文件，解决 <<<< 标记
  3. git add .
  4. git rebase --continue
  5. /verify-feature {id}        ← 重新验证
  6. /complete-feature {id} --no-commit --resume

💡 冲突在当前 feature 内解决，不影响其他 feature
```

**Conflict Resolution Flow:**
```
冲突发生 → 在 worktree 中解决 → git rebase --continue
    → 重新验证 /verify-feature → 继续 /complete-feature --resume
```

**Step 4.5: Fast-Forward Merge**

After successful rebase, merge is a fast-forward (no conflicts possible):

```bash
git checkout {main_branch}
git merge {branch}  # Fast-forward merge
```

Record merge commit hash.

**Step 4.6: Push (if configured)**

If `config.yaml` git.auto_push: `git push {remote} {main_branch}`

### Step 5: Create Archive Tag

```bash
TAG_NAME="{id}-{date}"  # e.g., feat-auth-20260302
git tag -a "$TAG_NAME" -m "Archive: {name}"
```

If `config.yaml` git.push_tags: `git push origin "$TAG_NAME"`

### Step 6: Copy Feature Documents to Archive (BEFORE Worktree Cleanup)

**IMPORTANT: This step MUST be executed BEFORE deleting the worktree!**

Copy all feature documents to the archive directory to ensure they are preserved:

```bash
# Create archive directory first
mkdir -p features/archive/done-{id}-{date}

# Copy all standard documents from active to archive
# ⭐ This ensures spec.md, task.md, checklist.md are preserved even if worktree is deleted
cp features/active-{id}/spec.md features/archive/done-{id}-{date}/
cp features/active-{id}/task.md features/archive/done-{id}-{date}/
cp features/active-{id}/checklist.md features/archive/done-{id}-{date}/

# Copy evidence directory if it exists (from verify-feature)
if [ -d "features/active-{id}/evidence" ]; then
  cp -r features/active-{id}/evidence features/archive/done-{id}-{date}/
fi
```

**Why this step is critical:**
- The worktree contains the actual code changes, but the feature documents (spec.md, task.md, checklist.md) are in the active directory
- If worktree is deleted before copying, these documents would be lost
- Evidence from verify-feature must also be preserved

### Step 7: Cleanup Worktree and Branch

```bash
git worktree remove {worktree_path}
git branch -d {branch}
```

Note: Branch can be restored from tag anytime.

### Step 8: Verify Archive Completeness (Warning Mode)

**Archive Integrity Check - Warning mode, does NOT block completion!**

Verify that all required files exist in the archive directory:

```bash
# Required files check
REQUIRED_FILES=(
  "features/archive/done-{id}-{date}/spec.md"
  "features/archive/done-{id}-{date}/task.md"
  "features/archive/done-{id}-{date}/checklist.md"
  "features/archive/done-{id}-{date}/archive-meta.yaml"
)

MISSING_FILES=()
for file in "${REQUIRED_FILES[@]}"; do
  if [ ! -f "$file" ]; then
    echo "⚠️ WARNING: Missing file: $file"
    MISSING_FILES+=("$file")
  fi
done

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
  echo ""
  echo "    ⚠️ Archive integrity check found missing files"
  echo "    Missing files can be recovered from git tag:"
  echo "    git show {tag_name}:features/active-{id}/spec.md"
  echo ""
  echo "    Continuing with completion - please verify archive later."
  # Record missing files in archive-meta.yaml
else
  echo "✅ Archive integrity check passed"
fi
```

**Behavior when files are missing:**
- **Log warning** but continue with completion (DO NOT exit with error)
- Files can be recovered from git tag: `git show {tag_name}:path/to/file`
- Add note to archive-meta.yaml about missing files
- User should verify archive manually after completion

### Step 9: Update spec.md

Add merge record to `features/active-{id}/spec.md`:

```markdown
## Merge Record
- **Completed**: {timestamp}
- **Merged to**: main
- **Merge strategy**: rebase + fast-forward
- **Merge commit**: {hash}
- **Archive tag**: {tag_name}

## Rebase Conflict Record (if any)
- **Had conflict**: true/false
- **Conflict files**: [list of files]
- **Resolved at**: {timestamp}
- **Re-verified**: true/false

## Verification Evidence
<!-- If evidence/ directory exists from verify-feature -->
- **Report**: [verification-report.md](./evidence/verification-report.md)
- **Screenshots**: [screenshots/](./evidence/screenshots/)
- **Traces**: [traces/](./evidence/traces/)

## Development Stats
- **Duration**: {duration}
- **Commits**: {count}
- **Files changed**: {count}
- **Code changes**: +{additions} / -{deletions}
```

### Step 10: Archive Feature (with Evidence)

Move feature directory to archive, preserving all evidence:

```bash
mv features/active-{id} features/archive/done-{id}
```

Update `features/archive/archive-log.yaml`:

```yaml
archived:
  - id: {id}
    name: {name}
    completed: {timestamp}
    tag: {tag_name}
    merge_commit: {hash}
    merged_to: main
    branch_deleted: true
    branch_name: {branch}
    worktree_deleted: true
    worktree_path: {path}
    docs_path: done-{id}

    # Rebase/Merge Conflict Record (if any)
    conflicts:
      had_conflict: false | true
      conflict_files: []  # List of conflicting files
      resolved_at: {timestamp}  # When conflict was resolved
      re_verified: false | true  # Whether re-verification was performed after resolution

    # Verification Summary (if evidence exists)
    verification:
      status: passed | warning | failed
      scenarios_total: {n}
      scenarios_passed: {n}
      evidence_path: evidence/

    stats:
      started: {started}
      duration: {duration}
      commits: {count}
      files_changed: {count}
```

### Step 11: Update Queue

Remove from `queue.yaml` active list.
Update `meta.last_updated`.

### Step 12: Update Project Context (Incremental)

Analyze if this feature introduced changes that should be reflected in `project-context.md`.

**Step 12.1: Analyze Feature Impact**

Review the completed feature for context-relevant changes:

```yaml
analysis_checklist:
  tech_stack_changes:
    - New dependencies added?
    - Version upgrades?
    - New configuration files?

  code_patterns:
    - New naming conventions?
    - New file organization patterns?
    - New import patterns?

  architectural:
    - New directories/modules?
    - New API patterns?
    - New state management patterns?

  testing:
    - New test patterns?
    - New mock strategies?

  anti_patterns:
    - New "don't do" rules discovered?
```

**Step 12.2: Determine Update Action**

```
📊 Project Context Analysis

Feature: {feature_id}

Changes detected:
├── Tech Stack: {changes or "None"}
├── Code Patterns: {changes or "None"}
├── Architecture: {changes or "None"}
├── Testing: {changes or "None"}
└── Anti-patterns: {changes or "None"}

Action: {SKIP | UPDATE}
```

**Step 12.3: Skip Conditions**

Skip updating project-context.md if:
- Feature only modified existing code without new patterns
- Feature was a bug fix or minor enhancement
- No new conventions or rules introduced
- No new dependencies or configurations

**Step 12.4: Incremental Update**

If update needed, modify only relevant sections.

### Step 13: Auto-Schedule Next

If `config.yaml` workflow.auto_start: true:
- Check if pending list is not empty
- Get highest priority feature
- Call start-feature for it

## Output

### Standard Completion

```
✅ Feature feat-auth completed!

┌───────────────────────────────────────────────┐
│ Completion Report                               │
├───────────────────────────────────────────────┤
│ Commit: feat(feat-auth): User Authentication    │
│ Merge: feature/auth → main (rebase)             │
│ Archive: feat-auth-20260302 (tag)               │
│                                                │
│ 📊 Stats:                                       │
│ - Duration: 2h 30m                              │
│ - Commits: 5                                    │
│ - Files changed: 8                              │
│                                                │
│ 🗑️ Cleaned up:                                  │
│ - worktree: deleted                             │
│ - branch: deleted (recoverable via tag)         │
└───────────────────────────────────────────────┘

📁 Archived to: features/archive/done-feat-auth

🚀 Auto-started next: feat-dashboard
cd ../OA_Tool-feat-dashboard
```

### Completion with Rebase Conflict

```
✅ Feature feat-auth completed! (with conflict resolution)

┌───────────────────────────────────────────────┐
│ Completion Report                               │
├───────────────────────────────────────────────┤
│ Commit: feat(feat-auth): User Authentication    │
│ Merge: feature/auth → main (rebase)             │
│ Archive: feat-auth-20260302 (tag)               │
│                                                │
│ ⚠️ Conflict Resolution:                         │
│ - Files: src/auth/login.ts                      │
│ - Resolved at: 2026-03-02 15:30                 │
│ - Re-verified: ✅ Yes                            │
│                                                │
│ 📊 Stats:                                       │
│ - Duration: 2h 45m (incl. conflict resolution)  │
│ - Commits: 5                                    │
│ - Files changed: 8                              │
└───────────────────────────────────────────────┘

📁 Archived to: features/archive/done-feat-auth
```

## Error Handling

| Error | Description | Solution |
|-------|-------------|----------|
| NOT_FOUND | Feature not in active list | Check ID |
| WORKTREE_NOT_FOUND | Worktree missing | Check if manually deleted |
| NOTHING_TO_COMMIT | No changes to commit | Confirm development done |
| REBASE_CONFLICT | Rebase conflict occurred | Resolve in worktree, re-verify, retry |
| TAG_EXISTS | Tag already exists | Use different tag name |
| GIT_ERROR | Git operation failed | Check Git status |

## Rebase Conflict Resolution

```
❌ Rebase 冲突检测到

冲突文件:
  - src/auth/login.ts

解决步骤:
  1. cd {worktree_path}              ← 在 worktree 中解决
  2. 打开冲突文件，解决 <<<< 标记
  3. git add .
  4. git rebase --continue
  5. /verify-feature {id}           ← 重新验证
  6. /complete-feature {id} --resume

💡 冲突在当前 feature 内解决，不影响其他 feature
```

## Resume Option

Use `--resume` to continue after resolving conflicts:
```
/complete-feature {id} --resume
```

Skip Steps 1-3 (get info, check checklist, commit) and go directly to merge.

## Restoring Archived Branch

```bash
# Create new branch from tag
git checkout -b feature/auth-restored feat-auth-20260302

# View history
git log feat-auth-20260302
```

## Notes

1. **Tag naming conflicts**: Auto-append sequence number (feat-auth-20260302-2)
2. **Rebase conflicts**: Resolved in worktree, re-verification recommended
3. **Empty commits**: Warn user if no changes
4. **Checklist skips**: Recorded in archive-log.yaml
5. **Branch recovery**: Always possible via tag
6. **Conflict tracking**: All conflicts recorded in archive-log.yaml for traceability
