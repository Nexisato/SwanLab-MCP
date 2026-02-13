"""
SwanLab API CLI - Workspaces 命令模块
"""

import json
import sys
from typing import Optional

import swanlab

from .utils import get_api, get_default_username


def cmd_workspaces_list(args):
    """列出所有 workspaces。"""
    api = get_api()
    try:
        workspaces = api.workspaces()
        result = []
        for ws in workspaces:
            result.append(
                {
                    "username": ws.username,
                    "name": ws.name,
                    "workspace_type": ws.workspace_type,
                    "role": ws.role,
                    "profile": ws.profile,
                }
            )
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_workspaces_get(args):
    """获取指定 workspace 信息。"""
    api = get_api()
    username = args.username or get_default_username(api)

    try:
        ws = api.workspace(username=username)
        result = {
            "username": ws.username,
            "name": ws.name,
            "workspace_type": ws.workspace_type,
            "role": ws.role,
            "profile": ws.profile,
        }
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_workspaces_projects(args):
    """获取 workspace 下的所有 projects。"""
    api = get_api()
    username = args.username or get_default_username(api)

    try:
        ws = api.workspace(username=username)
        projects = ws.projects()
        result = []
        for proj in projects:
            result.append(
                {
                    "name": proj.name,
                    "path": proj.path,
                    "description": proj.description,
                    "labels": proj.labels,
                    "created_at": proj.created_at,
                    "updated_at": proj.updated_at,
                    "url": proj.url,
                    "visibility": proj.visibility,
                    "count": proj.count,
                }
            )
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
