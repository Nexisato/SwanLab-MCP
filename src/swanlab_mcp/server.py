"""SwanLab MCP Server."""

from mcp.server.fastmcp import FastMCP
from swanlab import Api

from .config import get_config
from .meta.info import get_server_name_with_version
from .tools import register_metric_tools, register_project_tools, register_run_tools, register_workspace_tools


def create_mcp_server():
    # Load configuration
    config = get_config()

    # Initialize SwanLab API
    swanlab_api = Api(api_key=config.api_key, host=config.host)

    # Initialize MCP server
    mcp = FastMCP(
        name=get_server_name_with_version(),
        instructions="""
        A Model Context Protocol (MCP) server for SwanLab - a collaborative machine learning experiment tracking platform.

        This server provides tools to:
        - Query workspace metadata and workspace projects
        - Query project metadata and project runs
        - Query run metadata, config, requirements and environment profile
        - Query run metrics as structured tables

        All operations require a valid SWANLAB_API_KEY set in the environment.
        """,
    )

    # Register all tools
    register_workspace_tools(mcp, swanlab_api)
    register_project_tools(mcp, swanlab_api)
    register_run_tools(mcp, swanlab_api)
    register_metric_tools(mcp, swanlab_api)
    return mcp
