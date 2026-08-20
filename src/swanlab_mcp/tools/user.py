"""User related MCP tools.

用户管理工具，用于获取当前认证用户的信息。
"""

from typing import Any, Dict

from fastmcp import FastMCP
from mcp.types import ToolAnnotations

from ..client import SwanLabClient
from ..models import User


class UserTools:
    """SwanLab User management tools.

    用户信息查询，对应 OpenAPI 端点 GET /user/profile。
    """

    def __init__(self, client: SwanLabClient):
        self.client = client

    async def get_user(self) -> User:
        """
        Get the authenticated user's profile.

        Returns:
            User object containing name, username, bio, email, etc.
        """
        try:
            data = self.client.get_json("/user/profile")
            if not isinstance(data, dict):
                raise RuntimeError(f"unexpected response type {type(data).__name__}.")
            profile = {k: v for k, v in data.items() if isinstance(v, (str, int, float)) or v is None}
            profile["username"] = self.client.username
            profile["name"] = self.client.name or self.client.username
            return User(**profile)
        except Exception as e:
            raise RuntimeError(f"Failed to get user info: {str(e)}") from e


def register_user_tools(mcp: FastMCP, client: SwanLabClient) -> None:
    """
    Register user-related MCP tools.

    Args:
        mcp: FastMCP server instance
        client: SwanLab OpenAPI client
    """
    user_tools = UserTools(client)

    @mcp.tool(
        name="swanlab_get_user",
        title="Get the authenticated user's profile.",
        description="Get the profile of the currently authenticated user. 获取当前认证用户的个人信息。",
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def get_user() -> Dict[str, Any]:
        """
        Get the profile of the currently authenticated user.

        Returns:
            User profile with name, username, bio, email, institution, etc.
            返回当前用户信息，包含显示名、用户名、简介、邮箱、机构等。
        """
        user = await user_tools.get_user()
        return user.model_dump()
