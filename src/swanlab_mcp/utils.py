"""SwanLab MCP utility functions.

公共工具函数，提供类型转换和验证功能。
"""

import json
import re
from collections.abc import Mapping
from typing import Any, Dict, List, Optional

# 预编译的正则表达式
PROJECT_PATH_PATTERN = re.compile(r"^[^/\s]+/[^/\s]+$")
RUN_PATH_PATTERN = re.compile(r"^[^/\s]+/[^/\s]+/[^/\s]+$")


def _normalize_to_str(value: Any) -> str:
    """Normalize any value to string, returning empty string for None."""
    if value is None:
        return ""
    return str(value)


def _normalize_to_list(value: Any) -> List[str]:
    """Normalize any value to list of strings."""
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def _normalize_to_dict(value: Any) -> Dict[str, Any]:
    """Normalize any value to dict."""
    if value is None or value == "":
        return {}
    if isinstance(value, Mapping):
        return dict(value)
    return {}


def to_plain_dict(obj: Any) -> Dict[str, Any]:
    """Convert any object to a plain dictionary.

    处理 swanlab SDK 返回的各种对象类型。
    支持：dict、Mapping、有 json()/model_dump() 方法的对象、__dict__ 属性。
    """
    if isinstance(obj, dict):
        return dict(obj)
    if isinstance(obj, Mapping):
        return dict(obj.items())
    if hasattr(obj, "json"):
        data = obj.json()
    elif hasattr(obj, "model_dump"):
        data = obj.model_dump()
    elif hasattr(obj, "__dict__"):
        data = obj.__dict__
    else:
        data = dict(obj)
    if isinstance(data, str):
        data = json.loads(data)
    if not isinstance(data, dict):
        raise TypeError(f"Expected dictionary-like data, got {type(data).__name__}.")
    return data


def validate_project_path(path: str) -> str:
    """Validate project path format: username/project_name."""
    normalized = path.strip()
    if not PROJECT_PATH_PATTERN.fullmatch(normalized):
        raise ValueError("`path` must follow 'username/project_name'.")
    return normalized


def validate_run_path(path: str) -> str:
    """Validate run path format: username/project_name/experiment_id."""
    normalized = path.strip()
    if not RUN_PATH_PATTERN.fullmatch(normalized):
        raise ValueError("`path` must follow 'username/project_name/experiment_id'.")
    return normalized


def validate_workspace_path(username: Optional[str]) -> Optional[str]:
    """Validate workspace username format.

    用户名应该只包含字母、数字、下划线和连字符。
    如果输入为空或 None，返回 None。
    """
    if not username:
        return None
    normalized = username.strip()
    if not normalized:
        return None
    return normalized
