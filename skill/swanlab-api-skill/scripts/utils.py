"""
SwanLab API CLI 辅助函数模块

提供 API 初始化、默认用户获取、文件保存等通用功能。
"""

import netrc
import os
import sys
from pathlib import Path
from typing import Optional

import swanlab

NETRC_PATH = Path.home() / ".swanlab" / "netrc"


def _get_api_key_from_netrc() -> Optional[str]:
    """从 ~/.swanlab/netrc 文件中读取 api_key。

    netrc 文件格式示例：
        machine https://api.swanlab.cn
            login https://swanlab.cn
            password xxxxxx
    """
    if not NETRC_PATH.exists():
        return None

    try:
        nrc = netrc.netrc(str(NETRC_PATH))
        # 尝试从 netrc 中获取 password 作为 api_key
        # 优先尝试常见的 machine 名称
        for machine in ["https://api.swanlab.cn", "api.swanlab.cn", "swanlab.cn"]:
            entry = nrc.authenticators(machine)
            if entry:
                # entry 格式: (login, account, password)
                _, _, password = entry
                if password:
                    return password
        return None
    except Exception:
        return None


def get_api() -> swanlab.Api:
    """初始化并返回 SwanLab API 客户端。

    API Key 读取优先级：
    1. 环境变量 SWANLAB_API_KEY
    2. ~/.swanlab/netrc 文件中的 password 字段
    """
    host = os.environ.get("SWANLAB_HOST", "https://swanlab.cn")

    # 1. 优先从环境变量读取
    api_key = os.environ.get("SWANLAB_API_KEY")

    # 2. 如果环境变量没有，尝试从 netrc 读取
    if not api_key:
        api_key = _get_api_key_from_netrc()

    if not api_key:
        print(
            "Error: SWANLAB_API_KEY not found.\n"
            "Please set one of:\n"
            "  1. Environment variable: SWANLAB_API_KEY\n"
            f"  2. Netrc file: {NETRC_PATH} (machine password field)",
            file=sys.stderr,
        )
        sys.exit(1)

    return swanlab.Api(api_key=api_key, host=host)


def get_default_username(api: swanlab.Api) -> str:
    """获取默认的 personal workspace username。"""
    try:
        workspaces = api.workspaces()
        for ws in workspaces:
            if ws.workspace_type == "PERSON":
                return ws.username
        # 如果没有 PERSON 类型，返回第一个
        if workspaces:
            return workspaces[0].username
    except Exception as e:
        print(f"Error fetching workspaces: {e}", file=sys.stderr)
        sys.exit(1)

    print("Error: No workspace found", file=sys.stderr)
    sys.exit(1)


DEFAULT_OUTPUT_DIR = ".cache"


def ensure_output_dir():
    """确保默认输出目录存在。"""
    if not os.path.exists(DEFAULT_OUTPUT_DIR):
        os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)


def save_json_chunk(data: list, output_path: str):
    """将数据保存为 JSON 文件。"""
    # 如果 output_path 不包含目录部分，添加到默认目录
    if os.path.dirname(output_path) == "":
        ensure_output_dir()
        output_path = os.path.join(DEFAULT_OUTPUT_DIR, output_path)

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        import json

        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    print(f"Saved to: {output_path}")
