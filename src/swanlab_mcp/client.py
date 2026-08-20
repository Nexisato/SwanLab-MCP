"""Thin client over the raw SwanLab OpenAPI HTTP endpoints.

复用 swanlab SDK 的 `Api` 完成凭证解析（环境变量 / `swanlab login` 的 .netrc）、
登录与会话重试，但绕过实体层直接调用 OpenAPI 端点：

- 响应为原始 dict / list（与 `swanlab.api.typings` 中的 OpenAPI 类型对齐）
- 非 2xx 响应由底层 session 抛出 `ApiError`（含后端 code/message/traceId），
  此处转为 RuntimeError 上抛，由各工具层补充操作上下文，
  不会像实体层那样被吞成空数据
"""

from typing import Any, Dict, Optional

import requests
from swanlab.api import Api
from swanlab.api.base import ApiClientContext
from swanlab.api.experiment import Experiment
from swanlab.exceptions import ApiError

from .utils import validate_run_path


class SwanLabClient:
    """SwanLab OpenAPI client shared by all MCP tools.

    通过 `Api` 引导出共享的 `ApiClientContext`（client / web_host / username），
    之后所有请求走原始端点。
    """

    def __init__(self, api_key: Optional[str] = None, host: Optional[str] = None) -> None:
        self._api = Api(api_key=api_key, host=host)
        self._ctx: ApiClientContext = self._api._ctx
        self.username: str = self._ctx.username
        self.name: str = self._ctx.name
        self.web_host: str = self._ctx.web_host

    # ------------------------------------------------------------------
    # 原始 OpenAPI 请求
    # ------------------------------------------------------------------
    def get_json(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """GET an OpenAPI endpoint and return the raw JSON body.

        Args:
            path: 端点路径，如 "/user/profile"
            params: 查询参数

        Returns:
            解析后的 JSON body（dict / list / str）

        Raises:
            RuntimeError: HTTP 错误或网络异常时抛出（错误信息含后端 code/message）
        """
        try:
            resp = self._ctx.client.get(path, params=params)
        except ApiError as e:
            raise RuntimeError(str(e)) from e
        except requests.RequestException as e:
            raise RuntimeError(f"request failed: {e}") from e
        return self._ensure_body(resp.data, path)

    def post_json(self, path: str, data: Optional[Dict[str, Any]] = None) -> Any:
        """POST an OpenAPI endpoint and return the raw JSON body.

        Args:
            path: 端点路径，如 "/house/metrics/scalar/keys"
            data: 请求体（JSON）

        Returns:
            解析后的 JSON body（dict / list / str）

        Raises:
            RuntimeError: HTTP 错误或网络异常时抛出（错误信息含后端 code/message）
        """
        try:
            resp = self._ctx.client.post(path, data=data)
        except ApiError as e:
            raise RuntimeError(str(e)) from e
        except requests.RequestException as e:
            raise RuntimeError(f"request failed: {e}") from e
        return self._ensure_body(resp.data, path)

    @staticmethod
    def _ensure_body(data: Any, path: str) -> Any:
        if data is None or data == "":
            raise RuntimeError(f"empty response body for '{path}'.")
        return data

    # ------------------------------------------------------------------
    # 组合辅助
    # ------------------------------------------------------------------
    def fetch_run(self, path: str) -> Dict[str, Any]:
        """Fetch raw run detail via GET /project/{proj_path}/runs/{run_id}.

        Args:
            path: 实验路径，格式为 username/project_name/run_id

        Returns:
            实验详情原始 dict（cuid/createdAt/profile 等）

        Raises:
            ValueError: 路径格式非法
            RuntimeError: 实验不存在或请求失败
        """
        normalized = validate_run_path(path)
        proj_path, run_id = normalized.rsplit("/", 1)
        data = self.get_json(f"/project/{proj_path}/runs/{run_id}")
        if not isinstance(data, dict):
            raise RuntimeError(f"unexpected response type {type(data).__name__}.")
        return data

    def experiment(self, path: str) -> Experiment:
        """Build an SDK Experiment with raw detail data pre-injected.

        先用原始端点校验实验存在（错误立即上抛），再把数据注入实体，
        供 metrics/summary/medias/logs 等复杂查询复用 SDK 机制
        （预签名下载、CSV 解析、LTTB 采样等）。
        """
        normalized = validate_run_path(path)
        data = self.fetch_run(path)
        return Experiment(self._ctx, path=normalized, data=data)

    def web_url(self, suffix: str) -> str:
        """Build a frontend web page URL from the web host."""
        return f"{self.web_host}/{suffix.lstrip('/')}"
