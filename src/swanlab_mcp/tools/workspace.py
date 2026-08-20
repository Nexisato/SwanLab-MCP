"""Workspace related MCP tools.

工作空间管理工具，用于获取用户可访问的空间信息。
"""

from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from mcp.types import ToolAnnotations

from ..client import SwanLabClient
from ..models import Workspace
from ..utils import validate_workspace_name


class WorkspaceTools:
    """SwanLab Workspace management tools.

    工作空间是项目的集合，对应一个研发团队（如"SwanLab"），分为个人空间（PERSON）和组织空间（TEAM）。
    对应 OpenAPI 端点 GET /group/{username} 与 GET /user/{username}/groups。
    """

    def __init__(self, client: SwanLabClient):
        self.client = client

    async def list_workspaces(self, username: Optional[str] = None) -> List[Workspace]:
        """
        List all workspaces accessible to a user.

        Args:
            username: 可选，用户名。为空时默认当前登录用户。

        Returns:
            List of Workspace objects containing username, name, role, workspace_type and profile.
        """
        try:
            normalized = validate_workspace_name(username) if username else self.client.username
            data = self.client.get_json(f"/user/{normalized}/groups")
            items = data if isinstance(data, list) else []
            return [Workspace(**item) for item in items if isinstance(item, dict)]
        except Exception as e:
            raise RuntimeError(f"Failed to list workspaces: {str(e)}") from e

    async def get_workspace(self, username: Optional[str] = None) -> Workspace:
        """
        Get a specific workspace by username.

        Args:
            username: 空间用户名，即唯一ID；不传时默认当前登录用户

        Returns:
            Workspace object with detailed information
        """
        try:
            normalized = validate_workspace_name(username) if username else self.client.username
            data = self.client.get_json(f"/group/{normalized}")
            if not isinstance(data, dict):
                raise RuntimeError(f"unexpected response type {type(data).__name__}.")
            return Workspace(**data)
        except Exception as e:
            workspace_name = username if username else "<current-user>"
            raise RuntimeError(f"Failed to get workspace '{workspace_name}': {str(e)}") from e


def register_workspace_tools(mcp: FastMCP, client: SwanLabClient) -> None:
    """
    Register workspace-related MCP tools.

    Args:
        mcp: FastMCP server instance
        client: SwanLab OpenAPI client
    """
    workspace_tools = WorkspaceTools(client)

    @mcp.tool(
        name="swanlab_list_workspaces",
        title="List all workspaces accessible to a user.",
        description="List all workspaces accessible to a user. 工作空间是项目的集合，对应一个研发团队。",
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def list_workspaces(username: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all workspaces accessible to a user.

        Args:
            username: 可选，用户名。为空时默认当前登录用户。

        Returns:
            List of workspaces with their names, usernames, roles, and types.
            返回空间列表，包含用户名、名称、角色和类型等信息。
        """
        workspaces = await workspace_tools.list_workspaces(username=username)
        return [ws.model_dump() for ws in workspaces]

    @mcp.tool(
        name="swanlab_get_workspace",
        title="Get detailed information about a specific workspace.",
        description="Get detailed information about a specific workspace. 获取指定工作空间的详细信息。",
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def get_workspace(username: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed information about a specific workspace.

        Args:
            username: 空间用户名，即唯一ID；不传时默认当前登录用户

        Returns:
            Workspace details including name, role, type, and profile.
            返回空间详情，包含名称、角色、类型和介绍信息。
        """
        workspace = await workspace_tools.get_workspace(username)
        return workspace.model_dump()
