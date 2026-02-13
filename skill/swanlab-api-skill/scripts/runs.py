"""
SwanLab API CLI - Runs/Experiments 命令模块
"""

import json
import os
import sys

import pandas as pd
import swanlab

from .utils import DEFAULT_OUTPUT_DIR, ensure_output_dir, get_api, get_default_username


def _resolve_run_path(api: swanlab.Api, path: str) -> str:
    """解析 run path，简写格式补全 username。"""
    parts = path.split("/")
    if len(parts) == 1:
        print(
            "Error: Path must be in format 'username/project_name/experiment_id' or 'project_name/experiment_id'",
            file=sys.stderr,
        )
        sys.exit(1)
    elif len(parts) == 2:
        username = get_default_username(api)
        return f"{username}/{path}"
    return path


def _resolve_run_path_lenient(api: swanlab.Api, path: str) -> str:
    """解析 run path（宽松模式，只处理 2 段的情况）。"""
    parts = path.split("/")
    if len(parts) == 2:
        username = get_default_username(api)
        return f"{username}/{path}"
    return path


def cmd_runs_list(args):
    """列出 runs（同 projects runs）。"""
    from .projects import cmd_projects_runs

    cmd_projects_runs(args)


def cmd_runs_get(args):
    """获取指定 run 信息。"""
    api = get_api()
    path = _resolve_run_path(api, args.path)

    try:
        run = api.run(path=path)
        result = {
            "name": run.name,
            "path": run.path,
            "id": run.id,
            "description": run.description,
            "state": run.state,
            "group": run.group,
            "labels": run.labels,
            "created_at": run.created_at,
            "finished_at": run.finished_at,
            "url": run.url,
            "job_type": run.job_type,
            "profile": run.profile,
            "show": run.show,
            "user": run.user,
        }
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_runs_config(args):
    """获取 run 的 config。"""
    api = get_api()
    path = _resolve_run_path_lenient(api, args.path)

    try:
        run = api.run(path=path)
        config = run.profile.config if hasattr(run.profile, "config") else {}
        print(json.dumps(config, indent=2, ensure_ascii=False, default=str))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_runs_metadata(args):
    """获取 run 的 metadata（环境信息）。"""
    api = get_api()
    path = _resolve_run_path_lenient(api, args.path)

    try:
        run = api.run(path=path)
        metadata = run.profile.metadata if hasattr(run.profile, "metadata") else {}
        print(json.dumps(metadata, indent=2, ensure_ascii=False, default=str))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_runs_requirements(args):
    """获取 run 的 requirements（Python 依赖）。"""
    api = get_api()
    path = _resolve_run_path_lenient(api, args.path)

    try:
        run = api.run(path=path)
        requirements = run.profile.requirements if hasattr(run.profile, "requirements") else {}
        print(json.dumps(requirements, indent=2, ensure_ascii=False, default=str))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_runs_metrics(args):
    """获取 run 的 metrics 数据。"""
    api = get_api()
    path = _resolve_run_path_lenient(api, args.path)

    # 从 path 中提取 experiment_id
    experiment_id = path.split("/")[-1]

    keys = [k.strip() for k in args.keys.split(",")] if args.keys else []

    try:
        run = api.run(path=path)
        metrics_df = run.metrics(keys=keys, x_axis=args.x_axis, sample=args.sample)

        if metrics_df.empty:
            print("No metrics data found.")
            return

        # 确定哪些列是 metrics key（排除 step/index 列和 _timestamp 后缀的列）
        exclude_cols = {"step", "index", "_step"}
        all_cols = set(metrics_df.columns)

        # 识别 metric keys（排除 _timestamp 列）
        metric_keys = []
        timestamp_map = {}  # key_name -> timestamp_col_name

        for col in metrics_df.columns:
            if col in exclude_cols:
                continue
            # 检查是否是 timestamp 列
            if col.endswith("_timestamp"):
                # 找到对应的 metric key
                base_key = col[: -len("_timestamp")]  # 去掉 _timestamp 后缀
                if base_key in all_cols:
                    timestamp_map[base_key] = col
            else:
                metric_keys.append(col)

        # 获取 step/index 列作为索引
        index_col = None
        for col in ["step", "index", "_step"]:
            if col in metrics_df.columns:
                index_col = col
                break

        if not metric_keys:
            print("No metric keys found in data.")
            return

        # 为每个 key 创建输出目录和文件
        output_dir = os.path.join(DEFAULT_OUTPUT_DIR, experiment_id)
        os.makedirs(output_dir, exist_ok=True)

        saved_files = []

        for key_name in metric_keys:
            # 构建该 key 的数据列表
            metrics_list = []

            # 将 key_name 中的 / 替换为 _，避免路径问题
            safe_key_name = key_name.replace("/", "_")

            # 获取对应的时间戳列名
            ts_col = timestamp_map.get(key_name)

            for idx, row in metrics_df.iterrows():
                # index 使用行号或 step 值
                index_val = int(row[index_col]) if index_col and not pd.isna(row[index_col]) else idx
                data_val = row[key_name]

                # 跳过 NaN 值
                if pd.isna(data_val):
                    continue

                # 尝试转换为数值
                try:
                    data_val = float(data_val)
                except (ValueError, TypeError):
                    pass

                # 获取时间戳（如果存在）
                timestamp_val = None
                if ts_col and not pd.isna(row[ts_col]):
                    timestamp_val = row[ts_col]

                metrics_list.append({"index": index_val, "data": data_val, "timestamp": timestamp_val})

            if not metrics_list:
                continue

            # 按 chunk_size 分片保存
            chunk_size = args.chunk_size
            if len(metrics_list) <= chunk_size:
                # 单文件保存
                output_data = {"metrics": metrics_list}
                output_path = os.path.join(output_dir, f"{safe_key_name}-0.json")
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(output_data, f, indent=2, ensure_ascii=False, default=str)
                saved_files.append(output_path)
                print(f"Saved to: {output_path}")
            else:
                # 分片保存
                for i in range(0, len(metrics_list), chunk_size):
                    chunk = metrics_list[i : i + chunk_size]
                    chunk_idx = i // chunk_size
                    output_data = {"metrics": chunk}
                    output_path = os.path.join(output_dir, f"{safe_key_name}-{chunk_idx}.json")
                    with open(output_path, "w", encoding="utf-8") as f:
                        json.dump(output_data, f, indent=2, ensure_ascii=False, default=str)
                    saved_files.append(output_path)
                    print(f"Saved to: {output_path}")

        if not saved_files:
            print("No metrics data to save.")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
