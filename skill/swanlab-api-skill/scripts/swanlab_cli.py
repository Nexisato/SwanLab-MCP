#!/usr/bin/env python3
"""
SwanLab API CLI Tool

统一命令行工具，用于访问 SwanLab OpenAPI 的各种功能。
支持获取 workspaces、projects、runs、metrics、metadata 等资源。

环境变量:
    SWANLAB_API_KEY: API 密钥（必需）
    SWANLAB_HOST: SwanLab 主机地址（可选，默认 https://swanlab.cn）

使用方式:
    python swanlab_cli.py <command> <subcommand> [options]

规则:
    - 未指定 username 时，自动获取 personal workspace 作为默认 path 前缀
    - 只有 runs metrics 命令会保存 JSON 文件，其他命令只输出到控制台
"""

import argparse
import sys

from .projects import cmd_projects_get, cmd_projects_list, cmd_projects_runs
from .runs import (
    cmd_runs_config,
    cmd_runs_get,
    cmd_runs_list,
    cmd_runs_metadata,
    cmd_runs_metric_keys,
    cmd_runs_metrics,
    cmd_runs_requirements,
)
from .workspaces import cmd_workspaces_get, cmd_workspaces_list, cmd_workspaces_projects


def main():
    parser = argparse.ArgumentParser(
        description="SwanLab API CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
环境变量:
  SWANLAB_API_KEY    API 密钥（必需）
  SWANLAB_HOST       SwanLab 主机地址（可选，默认 https://swanlab.cn）

规则:
  - 未指定 username 时，自动获取 personal workspace 作为默认
  - path 格式支持简写：project_name/exp_id 会自动补全 username
  - 只有 runs metrics 命令会保存 JSON 文件，其他命令只输出到控制台

示例:
  # 列出所有 workspaces
  python -m scripts.swanlab_cli workspaces list

  # 获取默认 workspace 信息
  python -m scripts.swanlab_cli workspaces get

  # 列出 projects（输出到控制台）
  python -m scripts.swanlab_cli projects list

  # 获取 metrics（保存到 .cache/metrics.json）
  python -m scripts.swanlab_cli runs metrics myproject/exp_123 "loss,accuracy" -o metrics
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # Workspaces commands
    workspaces_parser = subparsers.add_parser("workspaces", help="Workspace 相关操作")
    workspaces_sub = workspaces_parser.add_subparsers(dest="subcommand")

    ws_list = workspaces_sub.add_parser("list", help="列出所有 workspaces")

    ws_get = workspaces_sub.add_parser("get", help="获取指定 workspace 信息")
    ws_get.add_argument("username", nargs="?", help="Workspace username（可选，默认 personal）")

    ws_proj = workspaces_sub.add_parser("projects", help="获取 workspace 下的 projects")
    ws_proj.add_argument("username", nargs="?", help="Workspace username（可选，默认 personal）")

    # Projects commands
    projects_parser = subparsers.add_parser("projects", help="Project 相关操作")
    projects_sub = projects_parser.add_subparsers(dest="subcommand")

    proj_list = projects_sub.add_parser("list", help="列出 projects")
    proj_list.add_argument("username", nargs="?", help="Workspace username（可选，默认 personal）")
    proj_list.add_argument("--sort", choices=["created_at", "updated_at"], help="排序方式")
    proj_list.add_argument("--search", help="搜索关键词")
    proj_list.add_argument("--detail", type=bool, default=True, help="是否返回详细信息")

    proj_get = projects_sub.add_parser("get", help="获取指定 project 信息")
    proj_get.add_argument("path", help="Project path（如 username/project_name 或 project_name）")

    proj_runs = projects_sub.add_parser("runs", help="获取 project 下的 runs")
    proj_runs.add_argument("path", help="Project path（如 username/project_name 或 project_name）")
    proj_runs.add_argument("--filter", action="append", help="筛选条件，如 state=FINISHED")

    # Runs commands
    runs_parser = subparsers.add_parser("runs", help="Run/Experiment 相关操作")
    runs_sub = runs_parser.add_subparsers(dest="subcommand")

    runs_list = runs_sub.add_parser("list", help="列出 runs")
    runs_list.add_argument("path", help="Project path（如 username/project_name 或 project_name）")
    runs_list.add_argument("--filter", action="append", help="筛选条件，如 state=FINISHED")

    runs_get = runs_sub.add_parser("get", help="获取指定 run 信息")
    runs_get.add_argument("path", help="Run path（如 username/project_name/exp_id 或 project_name/exp_id）")

    runs_config = runs_sub.add_parser("config", help="获取 run 的 config")
    runs_config.add_argument("path", help="Run path")

    runs_meta = runs_sub.add_parser("metadata", help="获取 run 的 metadata")
    runs_meta.add_argument("path", help="Run path")

    runs_req = runs_sub.add_parser("requirements", help="获取 run 的 requirements")
    runs_req.add_argument("path", help="Run path")

    runs_metric_keys = runs_sub.add_parser("metric-keys", help="列出 run 的所有可用 metric keys")
    runs_metric_keys.add_argument("path", help="Run path")

    runs_metrics = runs_sub.add_parser("metrics", help="获取 run 的 metrics（唯一保存文件的命令）")
    runs_metrics.add_argument("path", help="Run path")
    runs_metrics.add_argument("keys", help="指标名称，逗号分隔（如 loss,accuracy）")
    runs_metrics.add_argument("--x-axis", default="step", help="X轴维度（默认: step）")
    runs_metrics.add_argument("--sample", type=int, help="采样数量")
    runs_metrics.add_argument("--chunk-size", type=int, default=8192, help="分片大小（默认: 8192）")
    runs_metrics.add_argument("-o", "--output", help="输出文件路径（不含扩展名，默认保存到 .cache/ 目录）")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Route to appropriate handler
    handlers = {
        ("workspaces", "list"): cmd_workspaces_list,
        ("workspaces", "get"): cmd_workspaces_get,
        ("workspaces", "projects"): cmd_workspaces_projects,
        ("projects", "list"): cmd_projects_list,
        ("projects", "get"): cmd_projects_get,
        ("projects", "runs"): cmd_projects_runs,
        ("runs", "list"): cmd_runs_list,
        ("runs", "get"): cmd_runs_get,
        ("runs", "config"): cmd_runs_config,
        ("runs", "metadata"): cmd_runs_metadata,
        ("runs", "requirements"): cmd_runs_requirements,
        ("runs", "metric-keys"): cmd_runs_metric_keys,
        ("runs", "metrics"): cmd_runs_metrics,
    }

    handler = handlers.get((args.command, args.subcommand))
    if handler:
        handler(args)
    else:
        print(f"Unknown command: {args.command} {args.subcommand}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
