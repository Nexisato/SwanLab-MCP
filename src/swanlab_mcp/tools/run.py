"""Run (Experiment) related MCP tools.

实验管理工具，用于获取实验信息、配置、元数据和依赖。
"""

from collections.abc import Mapping
from typing import Any, Dict, List, Optional

import pandas as pd
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from swanlab import Api

from ..models import Run
from ..utils import to_plain_dict, validate_project_path, validate_run_path


def _profile_section(run_obj: Any, section: str) -> Any:
    """Extract a section from run profile.

    从实验 profile 中提取指定部分（config、metadata、requirements）。
    """
    profile = getattr(run_obj, "profile", None)
    if profile is None:
        run_data = to_plain_dict(run_obj)
        return run_data.get("profile", {}).get(section)
    if isinstance(profile, Mapping):
        return profile.get(section)
    return getattr(profile, section, None)


class RunTools:
    """SwanLab Run (Experiment) management tools.

    实验是单次训练/推理任务，包含指标、配置、日志等数据。
    """

    def __init__(self, api: Api):
        self.api = api

    async def list_runs(
        self,
        path: str,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Run]:
        """
        List all runs (experiments) in a project with optional filtering.

        Args:
            path: 项目路径，格式为 username/project_name
            filters: 筛选条件，比如 {'state': 'FINISHED', 'config.batch_size': '64'}
                     支持的筛选条件：
                     - state: 实验状态，可选：FINISHED、RUNNING、CRASHED、ABORTED
                     - config.<配置名>: 配置名，需要 config. 前缀

        Returns:
            List of Run objects containing:
            - id: 实验ID
            - name: 实验名
            - path: 实验路径
            - description: 实验描述
            - state: FINISHED、RUNNING、CRASHED、ABORTED
            - group: 实验组
            - labels: 实验标签
            - created_at/finished_at: 时间戳
            - url: 实验URL
            - job_type: 任务类型
            - show: 显示状态
            - user: 实验用户信息
            - profile: 实验配置信息
        """
        try:
            kwargs: Dict[str, Any] = {"path": validate_project_path(path)}
            if filters:
                kwargs["filters"] = filters

            runs = self.api.runs(**kwargs)
            return [Run(**to_plain_dict(run)) for run in runs]
        except Exception as e:
            raise RuntimeError(f"Failed to list runs for project '{path}': {str(e)}") from e

    async def get_run(self, path: str) -> Run:
        """
        Get detailed information about a specific run (experiment).

        Args:
            path: 实验路径，格式为 username/project_name/experiment_id

        Returns:
            Run object with detailed information including profile data
        """
        try:
            normalized_path = validate_run_path(path)
            run = self.api.run(path=normalized_path)
            return Run(**to_plain_dict(run))
        except Exception as e:
            raise RuntimeError(f"Failed to get run '{path}': {str(e)}") from e

    async def get_run_config(self, path: str) -> Dict[str, Any]:
        """
        Get configuration for a run (experiment).

        Args:
            path: 实验路径，格式为 username/project_name/experiment_id

        Returns:
            Configuration dictionary
        """
        try:
            normalized_path = validate_run_path(path)
            run = self.api.run(path=normalized_path)
            config = _profile_section(run, "config")
            return config if isinstance(config, dict) else {}
        except Exception as e:
            raise RuntimeError(f"Failed to get config for run '{path}': {str(e)}") from e

    async def get_run_metadata(self, path: str) -> Dict[str, Any]:
        """
        Get metadata for a run (experiment).

        Args:
            path: 实验路径，格式为 username/project_name/experiment_id

        Returns:
            Metadata dictionary containing Python版本、硬件信息等
        """
        try:
            normalized_path = validate_run_path(path)
            run = self.api.run(path=normalized_path)
            metadata = _profile_section(run, "metadata")
            return metadata if isinstance(metadata, dict) else {}
        except Exception as e:
            raise RuntimeError(f"Failed to get metadata for run '{path}': {str(e)}") from e

    async def get_run_requirements(self, path: str) -> List[str]:
        """
        Get Python requirements for a run (experiment).

        Args:
            path: 实验路径，格式为 username/project_name/experiment_id

        Returns:
            List of Python package requirements
        """
        try:
            normalized_path = validate_run_path(path)
            run = self.api.run(path=normalized_path)
            requirements = _profile_section(run, "requirements")
            if requirements is None:
                return []
            if isinstance(requirements, list):
                return [str(req) for req in requirements]
            return [str(requirements)]
        except Exception as e:
            raise RuntimeError(f"Failed to get requirements for run '{path}': {str(e)}") from e


def register_run_tools(mcp: FastMCP, api: Api) -> None:
    """
    Register run-related MCP tools.

    Args:
        mcp: FastMCP server instance
        api: SwanLab Api instance
    """
    run_tools = RunTools(api)

    @mcp.tool(
        name="swanlab_list_runs",
        description="List all runs (experiments) in a project with optional filtering. "
        "实验是单次训练/推理任务，包含指标、配置、日志等数据。",
        annotations=ToolAnnotations(
            title="List all runs in a project.",
            readOnlyHint=True,
        ),
    )
    async def list_runs(
        path: str,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        List all runs (experiments) in a project with optional filtering.

        Args:
            path: 项目路径，格式为 username/project_name
            filters: 筛选条件，比如 {'state': 'FINISHED', 'config.batch_size': '64'}
                     支持的筛选条件：
                     - state: 实验状态，可选：FINISHED、RUNNING、CRASHED、ABORTED
                     - config.<配置名>: 配置名，需要 config. 前缀

        Returns:
            List of runs with their names, states, descriptions, and metadata.
            返回实验列表，包含名称、状态、描述和元数据。
        """
        runs = await run_tools.list_runs(path=path, filters=filters)
        return [run.model_dump() for run in runs]

    @mcp.tool(
        name="swanlab_get_run",
        description="Get detailed information about a specific run (experiment). 获取指定实验的详细信息。",
        annotations=ToolAnnotations(
            title="Get detailed information about a specific run.",
            readOnlyHint=True,
        ),
    )
    async def get_run(path: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific run (experiment).

        Args:
            path: 实验路径，格式为 username/project_name/experiment_id

        Returns:
            Run details including profile data, configuration, and metadata.
            返回实验详情，包含 profile 数据、配置和元数据。
        """
        run = await run_tools.get_run(path)
        return run.model_dump()

    @mcp.tool(
        name="swanlab_get_run_config",
        description="Get the configuration (config) for a specific run (experiment). 获取实验的配置信息。",
        annotations=ToolAnnotations(
            title="Get run configuration.",
            readOnlyHint=True,
        ),
    )
    async def get_run_config(path: str) -> Dict[str, Any]:
        """
        Get the configuration for a specific run (experiment).

        Args:
            path: 实验路径，格式为 username/project_name/experiment_id

        Returns:
            Configuration dictionary containing hyperparameters and settings.
            返回配置字典，包含超参数和设置。
        """
        return await run_tools.get_run_config(path)

    @mcp.tool(
        name="swanlab_get_run_metadata",
        description="Get the environment metadata for a specific run (experiment). "
        "获取实验的环境元数据，如 Python 版本、硬件信息。",
        annotations=ToolAnnotations(
            title="Get run metadata.",
            readOnlyHint=True,
        ),
    )
    async def get_run_metadata(path: str) -> Dict[str, Any]:
        """
        Get the environment metadata for a specific run (experiment).

        Args:
            path: 实验路径，格式为 username/project_name/experiment_id

        Returns:
            Metadata dictionary containing Python version, hardware info, etc.
            返回元数据字典，包含 Python 版本、硬件信息等。
        """
        return await run_tools.get_run_metadata(path)

    @mcp.tool(
        name="swanlab_get_run_requirements",
        description="Get the Python requirements for a specific run (experiment). 获取实验的 Python 依赖信息。",
        annotations=ToolAnnotations(
            title="Get run requirements.",
            readOnlyHint=True,
        ),
    )
    async def get_run_requirements(path: str) -> List[str]:
        """
        Get the Python requirements for a specific run (experiment).

        Args:
            path: 实验路径，格式为 username/project_name/experiment_id

        Returns:
            List of Python package requirements.
            返回 Python 包依赖列表。
        """
        return await run_tools.get_run_requirements(path)
