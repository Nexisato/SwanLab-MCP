"""SwanLab MCP Server."""

from mcp.server.fastmcp import FastMCP
from swanlab import OpenApi

from .config import get_config
from .meta.info import get_server_name_with_version
from .tools import register_experiment_tools, register_project_tools, register_workspace_tools


def create_mcp_server():
    # Load configuration
    config = get_config()

    # Initialize SwanLab API
    swanlab_api = OpenApi(api_key=config.api_key or "")

    # Initialize MCP server
    mcp = FastMCP(
        name=get_server_name_with_version(),
        instructions="""
        A Model Context Protocol (MCP) server for SwanLab - a collaborative machine learning experiment tracking platform.

        This server provides tools to:
        - List and manage workspaces
        - List, get, and delete projects
        - List, get, and delete experiments
        - Retrieve experiment metrics and summaries

        All operations require a valid SWANLAB_API_KEY set in the environment.
        """,
    )

    # Register all tools
    register_workspace_tools(mcp, swanlab_api)
    register_project_tools(mcp, swanlab_api)
    register_experiment_tools(mcp, swanlab_api)
    return mcp
