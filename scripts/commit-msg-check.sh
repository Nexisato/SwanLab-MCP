#!/bin/bash
set -euo pipefail  # 开启严格模式，避免静默错误

# Commit message format checker
# Validates commit messages follow the conventional commits format

# ===== 新增：参数及文件检查 =====
if [ $# -eq 0 ]; then
    echo "❌ 提交信息格式检查失败"
    echo "错误：未提供提交信息文件路径"
    exit 1
fi

COMMIT_MSG_FILE="$1"

# 检查文件是否存在（避免传了路径但文件不存在）
if [ ! -f "$COMMIT_MSG_FILE" ]; then
    echo "❌ 提交信息格式检查失败"
    echo "错误：提交信息文件不存在 → $COMMIT_MSG_FILE"
    exit 1
fi
# ===============================

COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")

# 忽略 merge commits
if echo "$COMMIT_MSG" | grep -qE "^Merge (branch|remote-tracking branch)"; then
    exit 0
fi

# 获取第一行（标题行）
TITLE=$(echo "$COMMIT_MSG" | head -n 1 | xargs)  # xargs 移除首尾空格，避免空行误判

# 规则1: 提交信息不能为空
if [ -z "$TITLE" ]; then
    echo "❌ 提交信息格式检查失败"
    echo ""
    echo "错误：提交信息不能为空"
    exit 1
fi

# 规则2: 检查第一行（标题行）的格式
# 格式：类型(范围)?: 描述
# 范围：可选，表示影响的范围
TYPES=(feat fix docs style refactor test chore perf revert build)

join_by() {
    local delimiter="$1"
    shift
    local first="$1"
    shift
    printf "%s" "$first" "${@/#/$delimiter}"
}

TYPES_REGEX=$(join_by "|" "${TYPES[@]}")
TYPES_LIST=$(join_by ", " "${TYPES[@]}")
PATTERN="^(${TYPES_REGEX})(\([a-zA-Z0-9_-]+\))?: .+"

if ! echo "$TITLE" | grep -qE "$PATTERN"; then
    echo "❌ 提交信息格式检查失败"
    echo ""
    echo "错误：提交信息格式不正确"
    echo ""
    echo "期望格式："
    echo "  类型(范围): 描述"
    echo ""
    echo "其中："
    echo "  - 类型必须是以下之一：${TYPES_LIST}"
    echo "  - 范围是可选的，用括号包围"
    echo "  - 冒号后必须有空格"
    echo ""
    echo "示例："
    echo "  feat(login): 添加验证码功能"
    echo "  fix: 修复用户登录问题"
    echo "  docs(readme): 更新安装说明"
    echo ""
    echo "您的提交信息："
    echo "  $TITLE"
    exit 1
fi

# 规则3: 检查标题行的最大长度（72个字符）
TITLE_LENGTH=${#TITLE}
if [ $TITLE_LENGTH -gt 72 ]; then
    echo "❌ 提交信息格式检查失败"
    echo ""
    echo "错误：标题行长度不能超过 72 个字符"
    echo "当前长度：$TITLE_LENGTH 字符"
    echo ""
    echo "您的提交信息："
    echo "  $TITLE"
    exit 1
fi

# 规则4: 如果有正文，标题行和正文之间必须有一个空行
LINE_COUNT=$(echo "$COMMIT_MSG" | wc -l | tr -d ' ')
if [ "$LINE_COUNT" -gt 1 ]; then
    SECOND_LINE=$(echo "$COMMIT_MSG" | sed -n '2p' | xargs)  # 移除首尾空格
    if [ -n "$SECOND_LINE" ]; then
        echo "❌ 提交信息格式检查失败"
        echo ""
        echo "错误：如果提交信息包含正文，标题行和正文之间必须有一个空行"
        echo ""
        echo "正确格式："
        echo "  feat(scope): 标题"
        echo "  "
        echo "  正文内容..."
        exit 1
    fi
fi

# 所有检查通过
echo "✅ 提交信息格式检查通过"
exit 0