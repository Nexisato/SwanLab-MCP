"""
SwanLab API CLI - Projects 命令模块
"""

import json
import sys

import swanlab

from .utils import get_api, get_default_username


def _resolve_project_path(api: swanlab.Api, path: str) -> str:
    """解析 project path，简写格式补全 username。"""
    if "/" not in path:
        username = get_default_username(api)
        return f"{username}/{path}"
    return path


def cmd_projects_list(args):
    """列出 projects。"""
    api = get_api()
    username = args.username or get_default_username(api)

    try:
        projects = api.projects(path=username, sort=args.sort, search=args.search, detail=args.detail)
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


def cmd_projects_get(args):
    """获取指定 project 信息。"""
    api = get_api()
    path = _resolve_project_path(api, args.path)

    try:
        proj = api.project(path=path)
        result = {
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
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_projects_runs(args):
    """获取 project 下的所有 runs。"""
    api = get_api()
    path = _resolve_project_path(api, args.path)

    # 解析 filters
    filters = {}
    if args.filter:
        for f in args.filter:
            if "=" in f:
                key, value = f.split("=", 1)
                filters[key] = value

    try:
        runs = api.runs(path=path, filters=filters if filters else None)
        result = []
        for run in runs:
            result.append(
                {
                    "name": run.name,
                    "path": run.path,
                    "id": run.id,
                    "state": run.state,
                    "group": run.group,
                    "labels": run.labels,
                    "created_at": run.created_at,
                    "finished_at": run.finished_at,
                    "url": run.url,
                    "job_type": run.job_type,
                    "show": run.show,
                    "user": run.user,
                }
            )
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
