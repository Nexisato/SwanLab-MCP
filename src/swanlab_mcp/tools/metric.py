"""Metric related MCP tools.

指标管理工具，用于获取实验的指标数据。
"""

from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from swanlab import Api

from ..models import MetricKey, MetricKeyList, MetricTable
from ..utils import validate_run_path


class MetricTools:
    """SwanLab Metric (指标) management tools.

    获取实验的指标数据，返回 pandas DataFrame 格式的数据。
    """

    def __init__(self, api: Api):
        self.api = api

    async def list_run_metric_keys(self, path: str) -> MetricKeyList:
        """
        List all available metric keys for a run (experiment).

        Args:
            path: 实验路径，格式为 username/project_name/experiment_id

        Returns:
            MetricKeyList containing all metric keys with their types and classes.
        """
        try:
            normalized_path = validate_run_path(path)
            run = self.api.run(path=normalized_path)
            columns_resp, _ = run._client.get(f"/experiment/{run.id}/column", params={"all": True})
            columns = columns_resp.get("list", [])

            metric_keys = [
                MetricKey(
                    key=col.get("key", ""),
                    type=col.get("type", ""),
                    cls=col.get("class", ""),
                    error=col.get("error"),
                )
                for col in columns
            ]

            return MetricKeyList(
                path=normalized_path,
                keys=metric_keys,
                total=len(metric_keys),
            )
        except Exception as e:
            raise RuntimeError(f"Failed to list metric keys for run '{path}': {str(e)}") from e

    async def get_run_metrics(
        self,
        path: str,
        keys: Optional[List[str]] = None,
        x_axis: str = "step",
        sample: Optional[int] = None,
    ) -> MetricTable:
        """
        Get metric data for a run (experiment).

        Args:
            path: 实验路径，格式为 username/project_name/experiment_id
            keys: 要获取的指标名称列表，如 ['loss', 'acc']；不传则返回空DataFrame
            x_axis: X轴维度，可选：step（步数）、指标名（如 acc）
            sample: 采样数量，限制返回的行数；不传则返回全部数据

        Returns:
            MetricTable object containing query information and metric rows
        """
        try:
            normalized_path = validate_run_path(path)
            normalized_x_axis = x_axis.strip()
            if not normalized_x_axis:
                raise ValueError("`x_axis` cannot be empty.")
            run = self.api.run(path=normalized_path)
            kwargs: Dict[str, Any] = {"x_axis": normalized_x_axis}
            if keys:
                kwargs["keys"] = keys
            if sample is not None:
                if sample <= 0:
                    raise ValueError("`sample` must be greater than 0.")
                kwargs["sample"] = sample
            #!TMP: sample 设定为 1000，避免一次性返回过多数据导致性能问题；后续可优化为分页查询
            if sample is None:
                kwargs["sample"] = 1000
            metrics_df = run.metrics(**kwargs)
            rows: List[Dict[str, Any]] = []
            columns: List[str] = []
            if metrics_df is not None and hasattr(metrics_df, "to_dict"):
                rows = metrics_df.to_dict(orient="records")
                if hasattr(metrics_df, "columns"):
                    columns = [str(column) for column in metrics_df.columns]

            return MetricTable(
                path=normalized_path,
                keys=keys or [],
                x_axis=normalized_x_axis,
                sample=sample,
                columns=columns,
                rows=rows,
                total=len(rows),
            )
        except Exception as e:
            raise RuntimeError(f"Failed to get metrics for run '{path}': {str(e)}") from e


def register_metric_tools(mcp: FastMCP, api: Api) -> None:
    """
    Register metric-related MCP tools.

    Args:
        mcp: FastMCP server instance
        api: SwanLab Api instance
    """
    metric_tools = MetricTools(api)

    @mcp.tool(
        name="swanlab_list_run_metric_keys",
        description="List all available metric keys for a run (experiment). "
        "Use this to discover metric names before calling swanlab_get_run_metrics. "
        "列出实验的所有可用指标键名，在调用 swanlab_get_run_metrics 前使用此工具发现指标名。",
        annotations=ToolAnnotations(
            title="List metric keys for a run.",
            readOnlyHint=True,
        ),
    )
    async def list_run_metric_keys(path: str) -> Dict[str, Any]:
        """
        List all available metric keys for a run (experiment).

        Args:
            path: 实验路径，格式为 username/project_name/experiment_id

        Returns:
            MetricKeyList with all available metric keys, their types (e.g. SCALAR) and classes (e.g. STABLE, SYSTEM).
            返回指标键列表，包含指标名、数据类型和分类信息。
        """
        metric_key_list = await metric_tools.list_run_metric_keys(path)
        return metric_key_list.model_dump()

    @mcp.tool(
        name="swanlab_get_run_metrics",
        description="Get metric data for a run (experiment). Returns a list of metric records. "
        "获取实验的指标数据，返回指标记录列表。",
        annotations=ToolAnnotations(
            title="Get metric data for a run.",
            readOnlyHint=True,
        ),
    )
    async def get_run_metrics(
        path: str,
        keys: Optional[List[str]] = None,
        x_axis: str = "step",
        sample: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get metric data for a run (experiment).

        Args:
            path: 实验路径，格式为 username/project_name/experiment_id
            keys: 要获取的指标名称列表，如 ['loss', 'acc']；不传则返回空结果
            x_axis: X轴维度，可选：step（步数）、指标名（如 acc）
            sample: 采样数量，限制返回的行数；不传则返回全部数据

        Returns:
            Structured metric table with rows, columns and query metadata.
            返回结构化指标表，包含行数据、列名和查询元数据。
        """
        metric_table = await metric_tools.get_run_metrics(path, keys, x_axis, sample)
        return metric_table.model_dump()
