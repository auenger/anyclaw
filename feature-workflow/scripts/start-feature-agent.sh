#!/bin/bash
#
# start-feature-agent.sh - 启动一个独立的 Feature Agent 进程
#
# 用法: ./start-feature-agent.sh <feature-id> <worktree-path> [branch-name]
#
# 这个脚本会:
# 1. 初始化 .status 文件
# 2. 启动 claude --print 后台进程
# 3. 进程会自动执行 implement → verify → complete 生命周期
# 4. 通过 EVENT token 输出进度事件
#

# 不使用 set -e，手动处理错误
# set -e

# 参数检查
FEATURE_ID="${1:-}"
WORKTREE="${2:-}"
BRANCH="${3:-feature/${FEATURE_ID#feat-}}"

if [ -z "$FEATURE_ID" ] || [ -z "$WORKTREE" ]; then
    echo "用法: $0 <feature-id> <worktree-path> [branch-name]"
    echo ""
    echo "示例:"
    echo "  $0 feat-auth ../OA_Tool-feat-auth"
    echo "  $0 feat-dashboard ../OA_Tool-feat-dashboard feature/dashboard"
    exit 1
fi

# 确定仓库根目录
if [ -d "feature-workflow" ]; then
    REPO_ROOT="$(pwd)"
elif [ -d "../feature-workflow" ]; then
    REPO_ROOT="$(cd .. && pwd)"
else
    REPO_ROOT="$(pwd)"
fi

# 路径定义
FEATURE_DIR="$REPO_ROOT/features/active-$FEATURE_ID"
STATUS_FILE="$FEATURE_DIR/.status"
LOG_FILE="$FEATURE_DIR/.log"
SPEC_FILE="$FEATURE_DIR/spec.md"
TASK_FILE="$FEATURE_DIR/task.md"
CHECKLIST_FILE="$FEATURE_DIR/checklist.md"

# 检查 feature 目录是否存在
if [ ! -d "$FEATURE_DIR" ]; then
    echo "错误: Feature 目录不存在: $FEATURE_DIR"
    echo "请先运行 /start-feature $FEATURE_ID"
    exit 1
fi

# 检查 worktree 是否存在
if [ ! -d "$WORKTREE" ]; then
    echo "错误: Worktree 不存在: $WORKTREE"
    echo "请先运行 /start-feature $FEATURE_ID"
    exit 1
fi

# 获取 feature 名称
FEATURE_NAME=$(grep '^# ' "$SPEC_FILE" 2>/dev/null | head -1 | sed 's/^# //' || echo "$FEATURE_ID")

# 获取任务数量
TASKS_TOTAL=$(grep -c '^\s*- \[' "$TASK_FILE" 2>/dev/null || echo "0")

echo "=================================================="
echo "启动 Feature Agent"
echo "=================================================="
echo "Feature ID:    $FEATURE_ID"
echo "Feature Name:  $FEATURE_NAME"
echo "Worktree:      $WORKTREE"
echo "Branch:        $BRANCH"
echo "Tasks:         $TASKS_TOTAL"
echo "Status File:   $STATUS_FILE"
echo "Log File:      $LOG_FILE"
echo "=================================================="

# 初始化状态文件
cat > "$STATUS_FILE" << EOF
feature_id: $FEATURE_ID
feature_name: $FEATURE_NAME
status: started
stage: init
progress:
  tasks_total: $TASKS_TOTAL
  tasks_done: 0
  current_task: 初始化
started_at: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
updated_at: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
EOF

echo "✅ 状态文件已初始化"

# 初始化日志文件并写入 START 事件
echo "# Feature Agent Log: $FEATURE_ID" > "$LOG_FILE"
echo "# Started: $(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
echo "EVENT:START $FEATURE_ID" >> "$LOG_FILE"

# 读取配置获取 main_branch
CONFIG_FILE="$REPO_ROOT/feature-workflow/config.yaml"
MAIN_BRANCH="main"
if [ -f "$CONFIG_FILE" ]; then
    MAIN_BRANCH=$(grep 'main_branch:' "$CONFIG_FILE" | awk '{print $2}' || echo "main")
fi

# 构建 System Prompt (使用 heredoc 直接写入变量)
SYSTEM_PROMPT="你是 Feature Agent，负责完成一个 feature 的完整开发生命周期。

你是一个独立的工作单元，必须严格按照 implement → verify → complete 三个阶段顺序执行。
⚠️ 你不能跳过任何阶段，每个阶段必须完成后才能进入下一阶段。

## EVENT Token 输出规则

在执行过程中，你必须输出 EVENT token 到标准输出，格式如下：

EVENT:START <feature-id>
EVENT:STAGE <feature-id> <stage>
EVENT:PROGRESS <feature-id> <done>/<total>
EVENT:BLOCKED <feature-id> \"<reason>\"
EVENT:COMPLETE <feature-id> <tag>
EVENT:ERROR <feature-id> \"<message>\"

这些 token 会被记录到日志文件，用于主 Agent 监控进度。

## 环境变量 (由脚本注入)

- FEATURE_ID: Feature 标识
- FEATURE_NAME: Feature 名称
- WORKTREE: 工作目录路径
- BRANCH: Git 分支名
- REPO_ROOT: 主仓库路径
- STATUS_FILE: 状态文件路径
- SPEC_FILE: 需求文档路径
- TASK_FILE: 任务文档路径
- CHECKLIST_FILE: 检查清单路径
- MAIN_BRANCH: 主分支名 (通常是 main)

## 执行阶段 (必须严格按顺序)

### 阶段 1: IMPLEMENT (实现)

**必须执行的步骤:**

1. 输出: EVENT:STAGE \$FEATURE_ID implement
2. 更新 \$STATUS_FILE:
   \`\`\`yaml
   status: implementing
   stage: implement
   updated_at: $(date -u +\"%Y-%m-%dT%H:%M:%SZ\")
   \`\`\`
3. 读取 \$SPEC_FILE 了解需求
4. 读取 \$TASK_FILE 了解任务列表
5. 切换到 worktree: cd \$WORKTREE
6. 逐一实现每个未完成的任务
7. 每完成一个任务:
   - 更新 \$STATUS_FILE 的 progress.tasks_done
   - 输出: EVENT:PROGRESS \$FEATURE_ID <done>/<total>
8. 所有任务完成后才能进入下一阶段

### 阶段 2: VERIFY (验证) - ⚠️ 强制执行，不能跳过

**必须执行的步骤:**

1. 输出: EVENT:STAGE \$FEATURE_ID verify
2. 更新 \$STATUS_FILE:
   \`\`\`yaml
   status: verifying
   stage: verify
   updated_at: $(date -u +\"%Y-%m-%dT%H:%M:%SZ\")
   \`\`\`
3. 在 worktree 目录执行以下验证:
   a. 检查代码语法: npm run lint (如果 lint 脚本存在)
   b. 运行测试: npm test
   c. 读取 \$CHECKLIST_FILE，逐项验证每一项
4. 如果任何验证失败:
   - 输出: EVENT:BLOCKED \$FEATURE_ID \"验证失败: <具体原因>\"
   - 更新 \$STATUS_FILE: status: blocked
   - 停止执行，等待主 Agent 处理
5. 只有所有验证通过才能进入下一阶段

### 阶段 3: COMPLETE (完成)

**必须执行的步骤:**

1. 输出: EVENT:STAGE \$FEATURE_ID complete
2. 更新 \$STATUS_FILE:
   \`\`\`yaml
   status: completing
   stage: complete
   updated_at: $(date -u +\"%Y-%m-%dT%H:%M:%SZ\")
   \`\`\`
3. 在 worktree 中提交代码:
   \`\`\`bash
   cd \$WORKTREE
   git add .
   git commit -m \"feat(\$FEATURE_ID): \$FEATURE_NAME\"
   \`\`\`
4. ⚠️ 不要尝试合并到 main（由主 Agent 处理）
5. 更新最终状态:
   \`\`\`yaml
   status: done
   stage: complete
   completion:
     commit: <commit-hash>
     finished_at: $(date -u +\"%Y-%m-%dT%H:%M:%SZ\")
   updated_at: $(date -u +\"%Y-%m-%dT%H:%M:%SZ\")
   \`\`\`
6. 输出: EVENT:COMPLETE \$FEATURE_ID done

## 状态文件更新规则

每次阶段变化或进度更新时，必须写入完整的 \$STATUS_FILE。

状态文件格式:
\`\`\`yaml
feature_id: <id>
feature_name: <name>
status: started | implementing | verifying | completing | done | blocked | error
stage: init | implement | verify | complete
progress:
  tasks_total: <n>
  tasks_done: <n>
  current_task: <描述>
started_at: <ISO8601>
updated_at: <ISO8601>
\`\`\`

## 阻塞处理

遇到无法解决的问题时:
1. 输出: EVENT:BLOCKED \$FEATURE_ID \"<具体原因>\"
2. 更新 \$STATUS_FILE:
   \`\`\`yaml
   status: blocked
   blocked:
     reason: \"<具体原因>\"
     stage: <当前阶段>
   updated_at: $(date -u +\"%Y-%m-%dT%H:%M:%SZ\")
   \`\`\`
3. 停止执行

## 错误处理

如果遇到无法恢复的错误:
1. 输出: EVENT:ERROR \$FEATURE_ID \"<错误信息>\"
2. 更新 \$STATUS_FILE:
   \`\`\`yaml
   status: error
   error:
     message: \"<错误信息>\"
     stage: <当前阶段>
   updated_at: $(date -u +\"%Y-%m-%dT%H:%M:%SZ\")
   \`\`\`

## 可用工具

你可以使用: Bash, Read, Write, Edit, Glob, Grep
你不能使用: Task, Skill

## 重要规则

1. 只操作你自己的 worktree 目录 (\$WORKTREE)
2. 必须严格按照 implement → verify → complete 顺序执行
3. 每个阶段变化时必须输出 EVENT token
4. 每个阶段变化时必须更新 \$STATUS_FILE
5. verify 阶段是强制的，不能跳过
6. 完成后必须设置 status: done 并输出 EVENT:COMPLETE
7. 阻塞时设置 status: blocked 并输出 EVENT:BLOCKED
8. 所有时间使用 UTC，格式: YYYY-MM-DDTHH:MM:SSZ"

# 构建用户 prompt
USER_PROMPT="请执行 feature **$FEATURE_ID** ($FEATURE_NAME) 的完整开发流程。

## 环境信息
- FEATURE_ID: $FEATURE_ID
- FEATURE_NAME: $FEATURE_NAME
- WORKTREE: $WORKTREE
- BRANCH: $BRANCH
- REPO_ROOT: $REPO_ROOT
- STATUS_FILE: $STATUS_FILE
- SPEC_FILE: $SPEC_FILE
- TASK_FILE: $TASK_FILE
- CHECKLIST_FILE: $CHECKLIST_FILE
- MAIN_BRANCH: $MAIN_BRANCH

## 执行步骤

1. 首先输出: EVENT:START $FEATURE_ID
2. 读取 \$SPEC_FILE 了解需求
3. 读取 \$TASK_FILE 了解任务
4. 按 implement → verify → complete 顺序执行
5. 每个阶段:
   - 输出 EVENT:STAGE token
   - 更新 \$STATUS_FILE
   - 执行该阶段的工作
6. 完成后:
   - 输出 EVENT:COMPLETE $FEATURE_ID <tag>
   - 更新 \$STATUS_FILE 为 done

遇到无法解决的问题:
- 输出 EVENT:BLOCKED 或 EVENT:ERROR
- 更新 \$STATUS_FILE
- 停止执行"

# 启动 claude --print
echo ""
echo "🚀 启动 claude --print..."

# 检测操作系统
OS="$(uname -s)"
case "$OS" in
    Linux*)     PLATFORM="linux" ;;
    Darwin*)    PLATFORM="macos" ;;
    CYGWIN*|MINGW*|MSYS*)    PLATFORM="windows" ;;
    *)          PLATFORM="unknown" ;;
esac

echo "平台: $PLATFORM"

# 启动后台进程
# 注意: 不使用 set -e，所以需要手动检查错误
if [ "$PLATFORM" = "windows" ]; then
    # Windows - 使用后台运行
    claude --print \
        --allowed-tools "Bash,Read,Write,Edit,Glob,Grep" \
        --append-system-prompt "$SYSTEM_PROMPT" \
        "$USER_PROMPT" \
        >> "$LOG_FILE" 2>&1 &
    LAUNCH_STATUS=$?
else
    # macOS/Linux - 标准 Unix 方式
    claude --print \
        --allowed-tools "Bash,Read,Write,Edit,Glob,Grep" \
        --append-system-prompt "$SYSTEM_PROMPT" \
        "$USER_PROMPT" \
        >> "$LOG_FILE" 2>&1 &
    LAUNCH_STATUS=$?
fi

# 等待一小段时间确保进程启动
sleep 1

# 检查进程是否还在运行
PID=$!
if kill -0 $PID 2>/dev/null; then
    echo "✅ 后台进程已启动: PID $PID"
    echo "📄 日志文件: $LOG_FILE"
    echo ""
    echo "监控命令:"
    echo "  查看状态: cat $STATUS_FILE"
    echo "  查看日志: tail -f $LOG_FILE"
    echo "  查看事件: grep '^EVENT:' $LOG_FILE"
    echo "  检查进程: ps -p $PID"
    echo ""
    echo "💡 主 Agent 可以通过读取 .status 文件或监控日志中的 EVENT token 来跟踪进度"
    exit 0
else
    echo "❌ 后台进程启动失败"
    echo "请检查日志文件: $LOG_FILE"
    exit 1
fi
