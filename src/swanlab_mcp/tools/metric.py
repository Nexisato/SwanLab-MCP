"""Metric related MCP tools.

指标管理工具，用于查询实验的指标键、标量数据、统计摘要、媒体数据和控制台日志。
"""

from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from swanlab.api.typings.common import RangeQuery
from swanlab.utils.time import parse_timestamp_s

from ..client import SwanLabClient
from ..constants import MAX_METRIC_SAMPLE
from ..models import LogData, LogExport, MediaData, MetricData, SeriesList, SummaryData
from ..utils import unwrap_response, validate_run_path

_VALID_METRIC_TYPES = ("SCALAR", "MEDIA")
_VALID_METRIC_CLASSES = ("CUSTOM", "SYSTEM")
_VALID_LOG_LEVELS = ("DEBUG", "INFO", "WARN", "ERROR")

# 系统指标 key 前缀（与 SDK Series 行为一致）：SCALAR 类型且以此前缀开头的 key 分类为 SYSTEM
_SYSTEM_KEY_PREFIX = "__swanlab__"
# series keys 接口的游标分页页大小（与 SDK Series._PAGE_SIZE 一致）
_SERIES_PAGE_SIZE = 2000


def _normalize_enum(value: str, valid: tuple, label: str) -> str:
    """Normalize an enum-like parameter to upper case and validate it."""
    normalized = (value or "").strip().upper()
    if normalized not in valid:
        raise ValueError(f"`{label}` must be one of {list(valid)}, got '{value}'.")
    return normalized


def _normalize_keys(keys: List[str]) -> List[str]:
    """Strip metric keys, drop empty ones and keep order (deduplicated)."""
    if not isinstance(keys, list) or not keys:
        raise ValueError("`keys` must be a non-empty list of metric keys.")
    return list(dict.fromkeys(k.strip() for k in keys if isinstance(k, str) and k.strip()))


def _build_range_query(params: Dict[str, Optional[int]], range_type: Optional[str]) -> Optional[RangeQuery]:
    """Build a RangeQuery from flat range parameters; None if no range option given."""
    if not any(
        params.get(field) is not None for field in ("range_start", "range_end", "range_last", "range_head", "range_tail")
    ):
        return None
    normalized_type = (range_type or "step").strip().lower()
    if normalized_type not in ("step", "timestamp"):
        raise ValueError("`range_type` must be 'step' or 'timestamp'.")
    return RangeQuery(
        type=normalized_type,  # type: ignore[arg-type]
        start=params.get("range_start"),
        end=params.get("range_end"),
        last=params.get("range_last"),
        head=params.get("range_head"),
        tail=params.get("range_tail"),
    )


class MetricTools:
    """SwanLab Metric (指标) management tools.

    对应 OpenAPI 端点 POST /house/metrics/{type}/keys（指标键发现），
    以及 SDK 的 metrics/summary/medias/logs 复合查询机制（预签名下载、CSV 解析、LTTB 采样）。
    """

    def __init__(self, client: SwanLabClient):
        self.client = client

    async def list_run_series(
        self,
        path: str,
        metric_type: str = "SCALAR",
        metric_class: str = "CUSTOM",
        search: Optional[str] = None,
    ) -> SeriesList:
        """
        List metric keys (series) of a run.

        Args:
            path: 实验路径，格式为 username/project_name/run_id
            metric_type: 指标类型：SCALAR（标量，默认）或 MEDIA（媒体）
            metric_class: 指标分类：CUSTOM（用户自定义，默认）或 SYSTEM（系统监控，如 CPU/GPU/内存）
            search: 模糊搜索关键词（对指标名做大小写不敏感的子串匹配）

        Returns:
            SeriesList containing all matching metric keys.
        """
        try:
            normalized_path = validate_run_path(path)
            normalized_type = _normalize_enum(metric_type, _VALID_METRIC_TYPES, "metric_type")
            normalized_class = _normalize_enum(metric_class, _VALID_METRIC_CLASSES, "metric_class")
            normalized_search = search.strip() if search else ""
            proj_path, _ = normalized_path.rsplit("/", 1)
            run_data = self.client.fetch_run(normalized_path)
            project_id = str(run_data.get("project_id") or "")
            if not project_id:
                project_data = self.client.get_json(f"/project/{proj_path}")
                project_id = str(project_data.get("cuid") or "") if isinstance(project_data, dict) else ""
            # 克隆实验的数据存在根实验下，查询时使用根实验的 ID（与 SDK Experiment.series 行为一致）
            query_pro_id = str(run_data.get("rootProId") or project_id)
            query_exp_id = str(run_data.get("rootExpId") or run_data.get("cuid") or "")
            created_at = parse_timestamp_s(run_data.get("createdAt", ""))

            keys: List[str] = []
            cursor = ""
            endpoint = f"/house/metrics/{normalized_type.lower()}/keys"
            while True:
                page = self.client.post_json(
                    endpoint,
                    data={
                        "experiments": [
                            {"projectId": query_pro_id, "experimentId": query_exp_id, "createdAt": created_at}
                        ],
                        "limit": _SERIES_PAGE_SIZE,
                        "cursor": cursor,
                    },
                )
                if not isinstance(page, dict):
                    raise RuntimeError(f"unexpected response type {type(page).__name__}.")
                keys.extend(str(key) for key in page.get("keys", []))
                if not page.get("hasMore", False) or not page.get("nextCursor", ""):
                    break
                cursor = str(page["nextCursor"])

            if normalized_type == "SCALAR":
                if normalized_class == "SYSTEM":
                    keys = [key for key in keys if key.startswith(_SYSTEM_KEY_PREFIX)]
                else:
                    keys = [key for key in keys if not key.startswith(_SYSTEM_KEY_PREFIX)]
            elif normalized_class == "SYSTEM":
                # MEDIA 指标均为 CUSTOM
                keys = []
            if normalized_search:
                needle = normalized_search.lower()
                keys = [key for key in keys if needle in key.lower()]

            return SeriesList(
                path=normalized_path,
                metric_type=normalized_type,
                metric_class=normalized_class,
                search=normalized_search,
                keys=keys,
                total=len(keys),
            )
        except Exception as e:
            raise RuntimeError(f"Failed to list series for run '{path}': {str(e)}") from e

    async def get_run_metrics(
        self,
        path: str,
        keys: List[str],
        sample: int = MAX_METRIC_SAMPLE,
        fetch_all: bool = False,
        ignore_timestamp: bool = True,
        range_type: Optional[str] = None,
        range_start: Optional[int] = None,
        range_end: Optional[int] = None,
        range_last: Optional[int] = None,
        range_head: Optional[int] = None,
        range_tail: Optional[int] = None,
    ) -> MetricData:
        """
        Get scalar metric data of a run for specified keys.

        Args:
            path: 实验路径，格式为 username/project_name/run_id
            keys: 指标名列表，如 ['loss', 'acc']
            sample: 采样数量上限（1-1500，服务端 LTTB 降采样），默认 1500
            fetch_all: 跳过采样，下载全量数据（数据量大时慎用）
            ignore_timestamp: 是否去除数据点中的时间戳字段，默认 True
            range_type: 范围过滤轴：step（默认）或 timestamp（毫秒时间戳）
            range_start: 范围起始值（含），step 为步数、timestamp 为 Unix 毫秒时间戳
            range_end: 范围结束值（含），同上
            range_last: 最近 N 毫秒的数据，与 range_start/range_end 互斥
            range_head: 仅取前 N 个数据点，与 range_tail 互斥
            range_tail: 仅取后 N 个数据点，与 range_head 互斥

        Returns:
            MetricData object containing per-key data points and statistics.
        """
        try:
            normalized_path = validate_run_path(path)
            normalized_keys = _normalize_keys(keys)
            if fetch_all:
                normalized_sample = None
            else:
                if not isinstance(sample, int) or sample < 1:
                    raise ValueError("`sample` must be >= 1.")
                normalized_sample = min(sample, MAX_METRIC_SAMPLE)
            range_query = _build_range_query(
                {
                    "range_start": range_start,
                    "range_end": range_end,
                    "range_last": range_last,
                    "range_head": range_head,
                    "range_tail": range_tail,
                },
                range_type,
            )
            experiment = self.client.experiment(normalized_path)
            result = experiment.metrics(
                keys=normalized_keys,
                sample=sample,
                ignore_timestamp=ignore_timestamp,
                all=fetch_all,
                range_query=range_query,
            )
            series = result.get("list", []) if isinstance(result, dict) else []
            return MetricData(
                path=normalized_path,
                keys=normalized_keys,
                metric_type="SCALAR",
                sample=normalized_sample,
                fetch_all=fetch_all,
                series=series,
                total=len(series),
            )
        except Exception as e:
            raise RuntimeError(f"Failed to get metrics for run '{path}': {str(e)}") from e

    async def get_run_summary(
        self,
        path: str,
        keys: Optional[List[str]] = None,
    ) -> SummaryData:
        """
        Get scalar metric summary (statistics) of a run.

        Args:
            path: 实验路径，格式为 username/project_name/run_id
            keys: 指标名列表，如 ['loss', 'acc']；不传则返回全部标量指标

        Returns:
            SummaryData object containing per-key statistics (min/max/avg/median/stdDev, etc.).
        """
        try:
            normalized_path = validate_run_path(path)
            normalized_keys = _normalize_keys(keys) if keys else None
            experiment = self.client.experiment(normalized_path)
            result = experiment.summary(keys=normalized_keys)
            summary = result if isinstance(result, dict) else {}
            return SummaryData(
                path=normalized_path,
                keys=normalized_keys,
                summary=summary,
                total=len(summary),
            )
        except Exception as e:
            raise RuntimeError(f"Failed to get summary for run '{path}': {str(e)}") from e

    async def get_run_medias(
        self,
        path: str,
        keys: List[str],
        step: Optional[int] = 0,
        fetch_all: bool = False,
    ) -> MediaData:
        """
        Get media metric data of a run for specified keys.

        Args:
            path: 实验路径，格式为 username/project_name/run_id
            keys: 媒体指标名列表，如 ['image', 'audio']
            step: 获取的步数，默认 0
            fetch_all: 获取全部步数的媒体数据

        Returns:
            MediaData object containing per-key media entries with downloadable URLs.
        """
        try:
            normalized_path = validate_run_path(path)
            normalized_keys = _normalize_keys(keys)
            experiment = self.client.experiment(normalized_path)
            try:
                result = experiment.medias(keys=normalized_keys, step=step, all=fetch_all)
            except TypeError:
                # SDK 0.9.x 单步媒体查询对部分历史数据会崩溃（响应含 None 条目），
                # 回退到全量路径并按步数过滤，保证工具仍可用
                if fetch_all:
                    raise
                result = experiment.medias(keys=normalized_keys, all=True)
                if step is not None:
                    for entry in result.get("list", []) if isinstance(result, dict) else []:
                        points = entry.get("metrics")
                        if isinstance(points, list):
                            entry["metrics"] = [p for p in points if isinstance(p, dict) and p.get("index") == step]
            medias = result.get("list", []) if isinstance(result, dict) else []
            return MediaData(
                path=normalized_path,
                keys=normalized_keys,
                step=step,
                fetch_all=fetch_all,
                medias=medias,
                total=len(medias),
            )
        except Exception as e:
            raise RuntimeError(f"Failed to get medias for run '{path}': {str(e)}") from e

    async def get_run_logs(
        self,
        path: str,
        offset: int = 0,
        level: str = "INFO",
        ignore_timestamp: bool = True,
    ) -> LogData:
        """
        Get console logs captured during a run.

        Args:
            path: 实验路径，格式为 username/project_name/run_id
            offset: 日志分片偏移量（shard index），默认 0
            level: 日志级别：DEBUG、INFO（默认）、WARN、ERROR
            ignore_timestamp: 是否去除日志条目中的时间戳字段，默认 True

        Returns:
            LogData object containing log entries.
        """
        try:
            normalized_path = validate_run_path(path)
            normalized_level = _normalize_enum(level, _VALID_LOG_LEVELS, "level")
            experiment = self.client.experiment(normalized_path)
            result = experiment.logs(offset=offset, level=normalized_level, ignore_timestamp=ignore_timestamp)  # type: ignore[arg-type]
            logs = result.get("logs", []) if isinstance(result, dict) else []
            count = result.get("count", len(logs)) if isinstance(result, dict) else len(logs)
            return LogData(
                path=normalized_path,
                offset=offset,
                level=normalized_level,
                logs=logs,
                count=count,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to get logs for run '{path}': {str(e)}") from e

    async def export_run_logs(
        self,
        path: str,
        start: int = 0,
        rows: int = 500000,
    ) -> LogExport:
        """
        Export console logs of a run as a downloadable .log file.

        Args:
            path: 实验路径，格式为 username/project_name/run_id
            start: 导出起始行（0-based），默认 0
            rows: 导出行数（1-500000），默认 500000

        Returns:
            LogExport object containing a presigned download URL.
        """
        try:
            normalized_path = validate_run_path(path)
            if not isinstance(start, int) or start < 0:
                raise ValueError("`start` must be >= 0.")
            if not isinstance(rows, int) or not 1 <= rows <= 500000:
                raise ValueError("`rows` must be between 1 and 500000.")
            experiment = self.client.experiment(normalized_path)
            data = unwrap_response(
                experiment.export_logs(start=start, rows=rows),
                f"Failed to export logs for run '{path}'",
            )
            url = data.get("url", "") if isinstance(data, dict) else ""
            return LogExport(path=normalized_path, start=start, rows=rows, url=url)
        except Exception as e:
            raise RuntimeError(f"Failed to export logs for run '{path}': {str(e)}") from e


def register_metric_tools(mcp: FastMCP, client: SwanLabClient) -> None:
    """
    Register metric-related MCP tools.

    Args:
        mcp: FastMCP server instance
        client: SwanLab OpenAPI client
    """
    metric_tools = MetricTools(client)

    @mcp.tool(
        name="swanlab_list_run_series",
        title="List metric keys of a run.",
        description="List metric keys (series) of a run, with optional type/class filters and fuzzy search. "
        "Use this to discover metric names before calling swanlab_get_run_metrics. "
        "列出实验的指标键名（支持按类型/分类过滤和模糊搜索），在调用 swanlab_get_run_metrics 前使用此工具发现指标名。",
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def list_run_series(
        path: str,
        metric_type: str = "SCALAR",
        metric_class: str = "CUSTOM",
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List metric keys (series) of a run.

        Args:
            path: 实验路径，格式为 username/project_name/run_id
            metric_type: 指标类型：SCALAR（标量，默认）或 MEDIA（媒体）
            metric_class: 指标分类：CUSTOM（用户自定义，默认）或 SYSTEM（系统监控，如 CPU/GPU/内存）
            search: 可选，模糊搜索关键词（大小写不敏感的子串匹配）

        Returns:
            Metric key list with query metadata.
            返回指标键列表及查询元信息。
        """
        series = await metric_tools.list_run_series(path, metric_type, metric_class, search)
        return series.model_dump()

    @mcp.tool(
        name="swanlab_get_run_metrics",
        title="Get scalar metric data of a run.",
        description="Get scalar metric data of a run for specified keys, with sampling and range query support. "
        "You SHOULD call `swanlab_list_run_series` first to discover available metric keys. "
        "获取实验的标量指标数据，支持采样和范围查询。你应该先调用 `swanlab_list_run_series` 发现可用指标键名。",
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def get_run_metrics(
        path: str,
        keys: List[str],
        sample: int = MAX_METRIC_SAMPLE,
        fetch_all: bool = False,
        ignore_timestamp: bool = True,
        range_type: Optional[str] = None,
        range_start: Optional[int] = None,
        range_end: Optional[int] = None,
        range_last: Optional[int] = None,
        range_head: Optional[int] = None,
        range_tail: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get scalar metric data of a run for specified keys.

        Args:
            path: 实验路径，格式为 username/project_name/run_id
            keys: 指标名列表，如 ['loss', 'acc']
            sample: 采样数量上限（1-1500，服务端 LTTB 降采样），默认 1500
            fetch_all: 跳过采样，下载全量数据（数据量大时慎用）
            ignore_timestamp: 是否去除数据点中的时间戳字段，默认 True
            range_type: 范围过滤轴：step（默认）或 timestamp（Unix 毫秒时间戳）
            range_start: 范围起始值（含），step 为步数、timestamp 为毫秒时间戳
            range_end: 范围结束值（含），同上；与 range_last 互斥
            range_last: 最近 N 毫秒的数据，与 range_start/range_end 互斥
            range_head: 仅取前 N 个数据点，与 range_tail 互斥
            range_tail: 仅取后 N 个数据点，与 range_head 互斥

        Returns:
            Per-key metric data points (step/value) and statistics (min/max/avg/median/latest).
            返回每个指标的数据点（step/value）和统计值（min/max/avg/median/latest）。
        """
        metrics = await metric_tools.get_run_metrics(
            path,
            keys,
            sample,
            fetch_all,
            ignore_timestamp,
            range_type,
            range_start,
            range_end,
            range_last,
            range_head,
            range_tail,
        )
        return metrics.model_dump()

    @mcp.tool(
        name="swanlab_get_run_summary",
        title="Get scalar metric summary of a run.",
        description="Get scalar metric summary (statistics) of a run: latest/min/max/avg/median/stdDev per key. "
        "获取实验标量指标的统计摘要，适合快速了解训练结果而无需拉取全部数据。",
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def get_run_summary(
        path: str,
        keys: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Get scalar metric summary (statistics) of a run.

        Args:
            path: 实验路径，格式为 username/project_name/run_id
            keys: 可选，指标名列表；不传则返回全部标量指标

        Returns:
            Per-key statistics including step, value, min, max, avg, median and stdDev.
            返回每个指标的统计信息，包含 step、value、min、max、avg、median 和 stdDev。
        """
        summary = await metric_tools.get_run_summary(path, keys)
        return summary.model_dump()

    @mcp.tool(
        name="swanlab_get_run_medias",
        title="Get media metric data of a run.",
        description="Get media metric data (images/audio/text, etc.) of a run for specified keys. "
        "获取实验的媒体指标数据（图片/音频/文本等），返回可下载的 URL。",
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def get_run_medias(
        path: str,
        keys: List[str],
        step: Optional[int] = 0,
        fetch_all: bool = False,
    ) -> Dict[str, Any]:
        """
        Get media metric data of a run for specified keys.

        Args:
            path: 实验路径，格式为 username/project_name/run_id
            keys: 媒体指标名列表；如不清楚键名请先调用 swanlab_list_run_series（metric_type=MEDIA）
            step: 获取的步数，默认 0
            fetch_all: 获取全部步数的媒体数据

        Returns:
            Per-key media entries with downloadable presigned URLs.
            返回每个媒体指标的数据及可下载的预签名 URL。
        """
        medias = await metric_tools.get_run_medias(path, keys, step, fetch_all)
        return medias.model_dump()

    @mcp.tool(
        name="swanlab_get_run_logs",
        title="Get console logs of a run.",
        description="Get console logs captured during a run. 获取实验运行期间采集的控制台日志。",
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def get_run_logs(
        path: str,
        offset: int = 0,
        level: str = "INFO",
        ignore_timestamp: bool = True,
    ) -> Dict[str, Any]:
        """
        Get console logs captured during a run.

        Args:
            path: 实验路径，格式为 username/project_name/run_id
            offset: 日志分片偏移量（shard index），默认 0
            level: 日志级别：DEBUG、INFO（默认）、WARN、ERROR
            ignore_timestamp: 是否去除日志条目中的时间戳字段，默认 True

        Returns:
            Log entries with level, message, etc.
            返回日志条目列表，包含 level、message 等字段。
        """
        logs = await metric_tools.get_run_logs(path, offset, level, ignore_timestamp)
        return logs.model_dump()

    @mcp.tool(
        name="swanlab_export_run_logs",
        title="Export console logs of a run.",
        description="Export console logs of a run as a downloadable .log file (returns a presigned URL). "
        "导出实验控制台日志为 .log 文件，返回带时效的下载 URL。",
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def export_run_logs(
        path: str,
        start: int = 0,
        rows: int = 500000,
    ) -> Dict[str, Any]:
        """
        Export console logs of a run as a downloadable .log file.

        Args:
            path: 实验路径，格式为 username/project_name/run_id
            start: 导出起始行（0-based），默认 0
            rows: 导出行数（1-500000），默认 500000

        Returns:
            Presigned download URL for the exported log file.
            返回导出日志文件的预签名下载 URL。
        """
        export = await metric_tools.export_run_logs(path, start, rows)
        return export.model_dump()
