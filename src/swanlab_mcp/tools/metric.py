"""Metric related MCP tools."""

from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from swanlab import Api

from ..models import MetricTable
from ._normalize import ensure_run_path


class MetricTools:
    """SwanLab Metric (指标) management tools."""

    def __init__(self, api: Api):
        self.api = api

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
            normalized_path = ensure_run_path(path)
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
        name="swanlab_get_run_metrics",
        description="Get metric data for a run (experiment). Returns a list of metric records.",
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
        """
        metric_table = await metric_tools.get_run_metrics(path, keys, x_axis, sample)
        return metric_table.model_dump()
