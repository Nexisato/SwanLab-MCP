"""Constants for SwanLab MCP Server."""

# 分页大小必须为后端允许的取值之一（与 swanlab sdk PaginatedQuery 约束一致）
VALID_PAGE_SIZES = (10, 12, 15, 20, 24, 27, 50, 100)
DEFAULT_PAGE_SIZE = 20
# 标量指标单次采样的上限（与 swanlab sdk Metrics 约束一致）
MAX_METRIC_SAMPLE = 1500
