"""Command line interface for SwanLab MCP Server."""

import argparse
import sys

from .meta.info import get_server_name, get_server_name_with_version, get_server_version
from .server import create_mcp_server


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description=get_server_name_with_version(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                        # Run with stdio transport (default)
  %(prog)s --transport stdio      # Run with stdio transport
        """,
    )

    parser.add_argument(
        "--transport",
        choices=["stdio"],
        default="stdio",
        help="Transport type (default: stdio)",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {get_server_version()}",
    )

    return parser


def main() -> None:
    """Handle CLI entry point operations."""
    parser = create_parser()
    args = parser.parse_args()

    # Create and configure the MCP server
    try:
        mcp = create_mcp_server()
        print(f"MCP server created successfully on transport {args.transport}")
    except Exception as e:
        print(f"Error creating MCP server: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        print(f"Starting MCP server on transport {args.transport}...")
        mcp.run(transport=args.transport)
    except KeyboardInterrupt:
        print(f"\nShutting down {get_server_name()}...", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {e}", file=sys.stderr)
        sys.exit(1)
