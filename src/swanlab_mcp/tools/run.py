"""Run (Experiment) related MCP tools.

实验管理工具，用于获取实验信息、配置、元数据和依赖。
"""

from typing import Any, Dict, List

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from swanlab.api.utils import validate_filter, validate_update_active

from ..client import SwanLabClient
from ..constants import VALID_PAGE_SIZES
from ..models import Run, RunList
from ..utils import validate_page, validate_project_path, validate_run_path


def _flatten_runs(data: Any) -> List[Dict[str, Any]]:
    """Flatten grouped experiment data (dict of lists) into a flat list."""
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        return [item for _, value in data.items() for item in _flatten_runs(value)]
    return []


def _build_run_list(path: str, data: Dict[str, Any], page: int, size: int) -> RunList:
    """Build a RunList envelope from the raw paginated/filter response body."""
    runs = []
    for item in data.get("list", []):
        if not isinstance(item, dict):
            continue
        run = Run(**item)
        if not run.path:
            run.path = f"{path}/{run.run_id}"
        runs.append(run)
    return RunList(
        path=path,
        page=data.get("page", page),
        size=data.get("size", size),
        total=data.get("total", len(runs)),
        pages=data.get("pages", 0),
        runs=runs,
    )


class RunTools:
    """SwanLab Run (Experiment) management tools.

    实验是单次训练/推理任务，包含指标、配置、日志等数据。
    对应 OpenAPI 端点 GET /project/{path}/runs（分页）、POST /project/{path}/runs/shows（筛选）
    与 GET /project/{path}/runs/{run_id}（详情）。
    """

    def __init__(self, client: SwanLabClient):
        self.client = client

    async def list_runs(
        self,
        path: str,
        page: int = 1,
        page_size: int = 20,
    ) -> RunList:
        """
        List runs (experiments) under a project, paginated.

        Args:
            path: 项目路径，格式为 username/project_name
            page: 页码，>= 1
            page_size: 每页条数，必须是 10/12/15/20/24/27/50/100 之一

        Returns:
            RunList object with pagination info and run list
        """
        try:
            normalized_path = validate_project_path(path)
            validate_page(page, page_size, VALID_PAGE_SIZES)
            data = self.client.get_json(
                f"/project/{normalized_path}/runs",
                params={"page": page, "size": page_size},
            )
            if not isinstance(data, dict):
                raise RuntimeError(f"unexpected response type {type(data).__name__}.")
            return _build_run_list(normalized_path, data, page, page_size)
        except Exception as e:
            raise RuntimeError(f"Failed to list runs for project '{path}': {str(e)}") from e

    async def filter_runs(
        self,
        path: str,
        filters: List[Dict[str, Any]],
    ) -> RunList:
        """
        Filter runs (experiments) under a project by a structured query.

        Args:
            path: 项目路径，格式为 username/project_name
            filters: 筛选条件列表，每项格式为 {"key": ..., "type": ..., "op": ..., "value": [...]}
                     - type: STABLE（实验属性）、CONFIG（超参配置）、SCALAR（指标值）
                     - key:  STABLE 时可选 state/name 等；CONFIG 时为配置名；SCALAR 时为指标名
                     - op: EQ、NEQ、GTE、LTE、IN、NOT IN、CONTAIN
                     - value: 值列表，如 ["FINISHED"]
                     示例：[{"key": "state", "type": "STABLE", "op": "EQ", "value": ["FINISHED"]}]

        Returns:
            RunList object with matching runs (no pagination)
        """
        try:
            normalized_path = validate_project_path(path)
            if not isinstance(filters, list) or not filters:
                raise ValueError("`filters` must be a non-empty list of filter objects.")
            data = self.client.post_json(
                f"/project/{normalized_path}/runs/shows",
                data={
                    "filters": validate_update_active(filters, validate_filter, label="filters"),
                    "groups": [],
                    "sorts": [],
                },
            )
            runs = _flatten_runs(data)
            return _build_run_list(normalized_path, {"list": runs, "total": len(runs)}, 1, len(runs))
        except Exception as e:
            raise RuntimeError(f"Failed to filter runs for project '{path}': {str(e)}") from e

    async def get_run(self, path: str) -> Run:
        """
        Get detailed information about a specific run (experiment).

        Args:
            path: 实验路径，格式为 username/project_name/run_id

        Returns:
            Run object with detailed information including profile data
        """
        try:
            normalized_path = validate_run_path(path)
            proj_path, run_slug = normalized_path.rsplit("/", 1)
            data = self.client.fetch_run(normalized_path)
            # 详情接口可能不带 profile，按 cuid 再查一次即可拿到（与 SDK Experiment.profile 行为一致）
            if "profile" not in data:
                cuid = str(data.get("cuid") or "")
                if cuid:
                    detail = self.client.get_json(f"/project/{proj_path}/runs/{cuid}")
                    if isinstance(detail, dict):
                        data = detail
            run_model = Run(**data)
            if not run_model.path:
                run_model.path = normalized_path
            if not run_model.url:
                url_ref = str(data.get("slug") or run_slug or run_model.run_id)
                run_model.url = self.client.web_url(f"@{proj_path}/runs/{url_ref}/chart")
            return run_model
        except Exception as e:
            raise RuntimeError(f"Failed to get run '{path}': {str(e)}") from e

    async def _get_run_profile(self, path: str) -> Dict[str, Any]:
        """Fetch the profile section dict of a run."""
        run_model = await self.get_run(path)
        return run_model.profile.model_dump() if run_model.profile else {}

    async def get_run_config(self, path: str) -> Dict[str, Any]:
        """
        Get configuration for a run (experiment).

        Args:
            path: 实验路径，格式为 username/project_name/run_id

        Returns:
            Configuration dictionary
        """
        try:
            profile = await self._get_run_profile(path)
            config = profile.get("config")
            return config if isinstance(config, dict) else {}
        except Exception as e:
            raise RuntimeError(f"Failed to get config for run '{path}': {str(e)}") from e

    async def get_run_metadata(self, path: str) -> Dict[str, Any]:
        """
        Get metadata for a run (experiment).

        Args:
            path: 实验路径，格式为 username/project_name/run_id

        Returns:
            Metadata dictionary containing Python版本、硬件信息等
        """
        try:
            profile = await self._get_run_profile(path)
            metadata = profile.get("metadata")
            return metadata if isinstance(metadata, dict) else {}
        except Exception as e:
            raise RuntimeError(f"Failed to get metadata for run '{path}': {str(e)}") from e

    async def get_run_requirements(self, path: str) -> List[str]:
        """
        Get Python requirements for a run (experiment).

        Args:
            path: 实验路径，格式为 username/project_name/run_id

        Returns:
            List of Python package requirements
        """
        try:
            profile = await self._get_run_profile(path)
            requirements = profile.get("requirements")
            if requirements is None:
                return []
            if isinstance(requirements, list):
                return [str(req) for req in requirements]
            return [str(requirements)]
        except Exception as e:
            raise RuntimeError(f"Failed to get requirements for run '{path}': {str(e)}") from e


def register_run_tools(mcp: FastMCP, client: SwanLabClient) -> None:
    """
    Register run-related MCP tools.

    Args:
        mcp: FastMCP server instance
        client: SwanLab OpenAPI client
    """
    run_tools = RunTools(client)

    @mcp.tool(
        name="swanlab_list_runs",
        title="List runs under a project.",
        description="List runs (experiments) under a project, paginated. "
        "实验是单次训练/推理任务，包含指标、配置、日志等数据。",
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def list_runs(
        path: str,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """
        List runs (experiments) under a project, paginated.

        Args:
            path: 项目路径，格式为 username/project_name
            page: 页码，>= 1，默认 1
            page_size: 每页条数，必须是 10/12/15/20/24/27/50/100 之一，默认 20

        Returns:
            Paginated run list with names, states, descriptions, and metadata.
            返回分页的实验列表，包含名称、状态、描述和元数据。
        """
        run_list = await run_tools.list_runs(path=path, page=page, page_size=page_size)
        return run_list.model_dump()

    @mcp.tool(
        name="swanlab_filter_runs",
        title="Filter runs under a project with a structured query.",
        description="Filter runs (experiments) under a project by a structured query. "
        "按结构化条件筛选项目下的实验，支持按实验属性(state等)、超参配置(config.xxx)和指标值筛选。",
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def filter_runs(
        path: str,
        filters: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Filter runs (experiments) under a project by a structured query.

        Args:
            path: 项目路径，格式为 username/project_name
            filters: 筛选条件列表，每项格式为 {"key": ..., "type": ..., "op": ..., "value": [...]}
                     - type: STABLE（实验属性）、CONFIG（超参配置）、SCALAR（指标值）
                     - key:  STABLE 时如 state/name；CONFIG 时为配置名（如 batch_size）；SCALAR 时为指标名
                     - op: EQ、NEQ、GTE、LTE、IN、NOT IN、CONTAIN
                     - value: 值列表，如 ["FINISHED"] 或 ["64"]
                     示例：[{"key": "state", "type": "STABLE", "op": "EQ", "value": ["FINISHED"]}]

        Returns:
            Matching runs without pagination.
            返回符合条件的实验列表（不分页）。
        """
        run_list = await run_tools.filter_runs(path=path, filters=filters)
        return run_list.model_dump()

    @mcp.tool(
        name="swanlab_get_run",
        title="Get detailed information about a specific run.",
        description="Get detailed information about a specific run (experiment). 获取指定实验的详细信息。",
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def get_run(path: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific run (experiment).

        Args:
            path: 实验路径，格式为 username/project_name/run_id

        Returns:
            Run details including profile data, configuration, and metadata.
            返回实验详情，包含 profile 数据、配置和元数据。
        """
        run = await run_tools.get_run(path)
        return run.model_dump()

    @mcp.tool(
        name="swanlab_get_run_config",
        title="Get run configuration.",
        description="Get the configuration (config) for a specific run (experiment). 获取实验的配置信息。",
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def get_run_config(path: str) -> Dict[str, Any]:
        """
        Get the configuration for a specific run (experiment).

        Args:
            path: 实验路径，格式为 username/project_name/run_id

        Returns:
            Configuration dictionary containing hyperparameters and settings.
            返回配置字典，包含超参数和设置。
        """
        return await run_tools.get_run_config(path)

    @mcp.tool(
        name="swanlab_get_run_metadata",
        title="Get run metadata.",
        description="Get the environment metadata for a specific run (experiment). "
        "获取实验的环境元数据，如 Python 版本、硬件信息。",
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def get_run_metadata(path: str) -> Dict[str, Any]:
        """
        Get the environment metadata for a specific run (experiment).

        Args:
            path: 实验路径，格式为 username/project_name/run_id

        Returns:
            Metadata dictionary containing Python version, hardware info, etc.
            返回元数据字典，包含 Python 版本、硬件信息等。
        """
        return await run_tools.get_run_metadata(path)

    @mcp.tool(
        name="swanlab_get_run_requirements",
        title="Get run requirements.",
        description="Get the Python requirements for a specific run (experiment). 获取实验的 Python 依赖信息。",
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def get_run_requirements(path: str) -> List[str]:
        """
        Get the Python requirements for a specific run (experiment).

        Args:
            path: 实验路径，格式为 username/project_name/run_id

        Returns:
            List of Python package requirements.
            返回 Python 包依赖列表。
        """
        return await run_tools.get_run_requirements(path)
