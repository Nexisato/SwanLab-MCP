#!/bin/bash
set -euo pipefail  # 开启严格模式，遇到错误立即退出

# 颜色输出函数（增强可读性）
green_echo() {
    echo -e "\033[32m$1\033[0m"
}

red_echo() {
    echo -e "\033[31m$1\033[0m"
}

# 检查 pre-commit 是否已安装（核心要求：不存在则直接退出）
check_pre_commit() {
    if ! command -v pre-commit &>/dev/null; then
        red_echo "错误：未找到 pre-commit 工具，请先安装后再执行本脚本！"
        exit 1
    fi
    green_echo "✅ 检测到 pre-commit 已安装"
}

# 为 scripts/ 目录下所有 .sh 脚本添加执行权限
set_scripts_permission() {
    green_echo "\n===== 开始设置 scripts/ 目录下脚本权限 ====="
    local scripts_dir="scripts"
    
    if [ ! -d "$scripts_dir" ]; then
        red_echo "警告：未找到 $scripts_dir 目录，跳过权限设置！"
        return
    fi

    # 检查是否存在 .sh 文件（避免循环空执行）
    if ! compgen -G "$scripts_dir/*.sh" >/dev/null; then
        red_echo "警告：$scripts_dir 目录下未找到任何 .sh 脚本文件，跳过权限设置！"
        return
    fi

    # 批量添加执行权限
    for sh_file in "$scripts_dir"/*.sh; do
        chmod +x "$sh_file"
        green_echo "✅ 已为 $sh_file 添加执行权限"
    done
}

# 安装 commit-msg 钩子（仅安装钩子，不安装 pre-commit 工具）
install_commit_msg_hook() {
    green_echo "\n===== 开始安装 commit-msg Git 钩子 ====="
    if pre-commit install --hook-type commit-msg; then
        green_echo "✅ commit-msg 钩子安装成功！"
    else
        red_echo "错误：commit-msg 钩子安装失败！"
        exit 1
    fi
}

# 主流程
main() {
    green_echo "===== 开始配置 Git Hooks 环境 ====="
    
    # 1. 检查 pre-commit 是否存在（核心要求）
    check_pre_commit

    # 2. 批量设置 scripts/ 目录下 .sh 脚本执行权限
    set_scripts_permission

    # 3. 安装 commit-msg 钩子（无需安装 pre-commit，仅挂载钩子）
    pre-commit clean
    pre-commit install
    install_commit_msg_hook
    pre-commit autoupdate

    green_echo "\n===== 所有配置完成！====="
    green_echo "提示：commit-msg 钩子已生效，后续提交信息会自动触发 scripts/commit-msg-check.sh 检查"
}

# 执行主流程
main