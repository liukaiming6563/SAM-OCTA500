"""
路径管理工具。

本文件将工程目录、数据目录、输出目录等统一从配置中解析，避免脚本中散落
硬编码路径。所有路径均使用 pathlib.Path 表达。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


PATH_KEYS = [
    "project_root",
    "data_root",
    "zip_root",
    "raw_root",
    "processed_root",
    "output_root",
    "manifest_dir",
    "report_dir",
    "visualization_dir",
    "log_dir",
    "config_snapshot_dir",
]


def as_path(config: dict[str, Any], key: str) -> Path:
    """
    从配置中读取路径字段。

    参数：
        config: 配置字典。
        key: 路径字段名。

    返回：
        Path 对象。
    """
    if key not in config:
        raise KeyError(f"配置缺少路径字段: {key}")
    return Path(str(config[key]))


def ensure_output_dirs(config: dict[str, Any]) -> None:
    """
    创建数据处理需要的输出目录。

    参数：
        config: 配置字典，必须包含 outputs、manifest、reports、logs 等路径。
    """
    for key in [
        "raw_root",
        "processed_root",
        "output_root",
        "manifest_dir",
        "report_dir",
        "visualization_dir",
        "log_dir",
        "config_snapshot_dir",
    ]:
        as_path(config, key).mkdir(parents=True, exist_ok=True)


def resolve_zip_root(config: dict[str, Any]) -> tuple[Path, str]:
    """
    解析真实 zip 所在目录。

    参数：
        config: 配置字典。优先使用 zip_root，如果没有 zip 文件，则回退到 data_root。

    返回：
        (真实 zip 目录, 说明文本)。
    """
    zip_root = as_path(config, "zip_root")
    data_root = as_path(config, "data_root")
    if zip_root.exists() and any(zip_root.glob("*.zip")):
        return zip_root, "使用配置中的 zip_root。"
    if data_root.exists() and any(data_root.glob("*.zip")):
        return data_root, "配置中的 zip_root 不存在或无 zip 文件，实际使用 data_root 下的 zip 文件。"
    return zip_root, "未找到 zip 文件。"


def processed_task_dir(config: dict[str, Any]) -> Path:
    """
    获取当前任务的 processed 输出目录。

    参数：
        config: 配置字典，包含 processed_root、fov、task。

    返回：
        例如 processed/OCTA500_2D/3M/FAZ。
    """
    return as_path(config, "processed_root") / "OCTA500_2D" / str(config["fov"]) / str(config["task"])
