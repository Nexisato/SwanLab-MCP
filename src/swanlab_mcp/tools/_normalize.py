"""Shared normalization and validation helpers for SwanLab SDK objects."""

import json
import re
from collections.abc import Iterable, Mapping
from typing import Any, Dict, List

PROJECT_PATH_PATTERN = re.compile(r"^[^/\s]+/[^/\s]+$")
RUN_PATH_PATTERN = re.compile(r"^[^/\s]+/[^/\s]+/[^/\s]+$")
SUPPORTED_PROJECT_SORTS = {"created_at", "updated_at"}
SUPPORTED_RUN_STATES = {"FINISHED", "RUNNING", "CRASHED", "ABORTED"}


def ensure_username(username: str | None) -> str | None:
    """Validate workspace username."""
    if username is None:
        return None
    normalized = username.strip()
    if not normalized:
        raise ValueError("`username` cannot be empty.")
    if "/" in normalized:
        raise ValueError("`username` must not contain '/'.")
    return normalized


def ensure_project_path(path: str) -> str:
    """Validate project path: username/project_name."""
    normalized = path.strip()
    if not PROJECT_PATH_PATTERN.fullmatch(normalized):
        raise ValueError("`path` must follow 'username/project_name'.")
    return normalized


def ensure_run_path(path: str) -> str:
    """Validate run path: username/project_name/experiment_id."""
    normalized = path.strip()
    if not RUN_PATH_PATTERN.fullmatch(normalized):
        raise ValueError("`path` must follow 'username/project_name/experiment_id'.")
    return normalized


def ensure_project_sort(sort: str | None) -> str | None:
    """Validate supported project sort options."""
    if sort is None:
        return None
    normalized = sort.strip()
    if normalized not in SUPPORTED_PROJECT_SORTS:
        supported = ", ".join(sorted(SUPPORTED_PROJECT_SORTS))
        raise ValueError(f"`sort` must be one of: {supported}.")
    return normalized


def ensure_run_filters(filters: Dict[str, Any] | None) -> Dict[str, Any] | None:
    """Validate run filters defined by SwanLab OpenAPI docs."""
    if filters is None:
        return None
    if not isinstance(filters, dict):
        raise ValueError("`filters` must be a dictionary.")

    validated: Dict[str, Any] = {}
    for key, value in filters.items():
        if key == "state":
            if value not in SUPPORTED_RUN_STATES:
                supported = ", ".join(sorted(SUPPORTED_RUN_STATES))
                raise ValueError(f"`filters.state` must be one of: {supported}.")
            validated[key] = value
            continue
        if key.startswith("config.") and len(key) > len("config."):
            validated[key] = value
            continue
        raise ValueError("`filters` only supports `state` and `config.<name>` keys.")
    return validated


def to_plain_dict(obj: Any) -> Dict[str, Any]:
    """Convert SwanLab SDK object to plain dict."""
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


def to_plain_dict_list(items: Iterable[Any]) -> List[Dict[str, Any]]:
    """Convert iterable SDK objects to list of dictionaries."""
    return [to_plain_dict(item) for item in items]


def profile_section(run_obj: Any, section: str) -> Any:
    """Extract section from run profile."""
    profile = getattr(run_obj, "profile", None)
    if profile is None:
        run_data = to_plain_dict(run_obj)
        return run_data.get("profile", {}).get(section)

    if isinstance(profile, Mapping):
        return profile.get(section)

    return getattr(profile, section, None)
