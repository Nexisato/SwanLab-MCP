"""SwanLab MCP utility functions.

公共工具函数，提供参数校验和响应解包功能。
"""

import re
from collections.abc import Mapping
from typing import Any, Dict, List, Optional

from swanlab.api.typings.common import ApiResponseType

# 预编译的正则表达式
PROJECT_PATH_PATTERN = re.compile(r"^[^/\s]+/[^/\s]+$")
RUN_PATH_PATTERN = re.compile(r"^[^/\s]+/[^/\s]+/[^/\s]+$")
WORKSPACE_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_\-]+$")


def _normalize_to_str(value: Any) -> str:
    """Normalize any value to string, returning empty string for None."""
    if value is None:
        return ""
    return str(value)


def _normalize_to_list(value: Any) -> List[Any]:
    """Normalize any value to list."""
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return value
    return [value]


def _normalize_to_dict(value: Any) -> Dict[str, Any]:
    """Normalize any value to dict."""
    if value is None or value == "":
        return {}
    if isinstance(value, Mapping):
        return dict(value)
    return {}


def validate_project_path(path: str) -> str:
    """Validate project path format: username/project_name."""
    normalized = path.strip()
    if not PROJECT_PATH_PATTERN.fullmatch(normalized):
        raise ValueError("`path` must follow 'username/project_name'.")
    return normalized


def validate_run_path(path: str) -> str:
    """Validate run path format: username/project_name/run_id."""
    normalized = path.strip()
    if not RUN_PATH_PATTERN.fullmatch(normalized):
        raise ValueError("`path` must follow 'username/project_name/run_id'.")
    return normalized


def validate_workspace_name(username: Optional[str]) -> str:
    """Validate workspace username format.

    用户名应该只包含字母、数字、下划线和连字符。
    """
    normalized = (username or "").strip()
    if not normalized:
        raise ValueError("`workspace` must be a non-empty username.")
    if not WORKSPACE_NAME_PATTERN.fullmatch(normalized):
        raise ValueError("`workspace` must contain only letters, digits, underscores and hyphens.")
    return normalized


def validate_page(page: int, page_size: int, valid_sizes: Any) -> int:
    """Validate pagination parameters, returning the normalized page size."""
    if page < 1:
        raise ValueError("`page` must be >= 1.")
    if page_size not in valid_sizes:
        raise ValueError(f"`page_size` must be one of {list(valid_sizes)}.")
    return page_size


def unwrap_response(resp: ApiResponseType, context: str) -> Any:
    """Unwrap an ApiResponseType, raising RuntimeError with context on failure.

    解包 swanlab SDK 的响应对象（如 export_logs 的返回值），
    失败时附带上下文信息抛出 RuntimeError。
    """
    if not resp.ok:
        raise RuntimeError(f"{context}: {resp.errmsg or 'unknown API error'}")
    return resp.data
