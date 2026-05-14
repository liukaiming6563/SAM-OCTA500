"""
配置读取工具。

本文件负责集中读取数据处理、模型和实验配置。工程优先使用 PyYAML；
如果当前环境没有安装 PyYAML，则使用一个轻量级解析器读取本项目使用的
简单 YAML 配置。这样可以保证数据准备脚本在基础 Python 环境中也能运行。
"""

from __future__ import annotations

import ast
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any


def _parse_scalar(value: str) -> Any:
    """
    解析 YAML 标量。

    参数：
        value: 等号右侧或冒号右侧的文本值。

    返回：
        Python 类型的值，包括 str、int、float、bool、None 或 list。
    """
    text = value.strip()
    if text == "":
        return ""
    if text.lower() == "true":
        return True
    if text.lower() == "false":
        return False
    if text.lower() in {"null", "none"}:
        return None
    if text.startswith("[") and text.endswith("]"):
        return ast.literal_eval(text)
    if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
        return ast.literal_eval(text)
    try:
        return int(text)
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        return text


def _load_simple_yaml(config_path: Path) -> dict[str, Any]:
    """
    读取本项目的简单 YAML 配置。

    参数：
        config_path: YAML 配置文件路径。

    返回：
        嵌套字典。支持键值对、二级或三级缩进字典、行内列表和基础标量。
    """
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]
    for raw_line in config_path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        key = key.strip()
        value = value.strip()
        if value == "":
            child: dict[str, Any] = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = _parse_scalar(value)
    return root


def load_config(config_path: str | Path) -> dict[str, Any]:
    """
    加载配置文件。

    参数：
        config_path: 配置文件路径，支持字符串或 Path。

    返回：
        配置字典。路径字段保持字符串形式，由调用方按需转换为 Path。
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"配置文件不存在: {path}")
    try:
        import yaml  # type: ignore

        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            raise ValueError("配置文件顶层必须是字典")
        return data
    except ModuleNotFoundError:
        return _load_simple_yaml(path)


def save_json(data: dict[str, Any], output_path: str | Path) -> None:
    """
    保存 JSON 文件。

    参数：
        data: 需要保存的字典。
        output_path: 输出 JSON 路径。
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def snapshot_config(config_path: str | Path, snapshot_dir: str | Path, tag: str) -> Path:
    """
    保存配置文件副本，便于复现实验。

    参数：
        config_path: 原始配置文件。
        snapshot_dir: 配置快照保存目录。
        tag: 当前处理阶段名称。

    返回：
        已写入的配置快照路径。
    """
    source = Path(config_path)
    target_dir = Path(snapshot_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = target_dir / f"{source.stem}_{tag}_{stamp}{source.suffix}"
    shutil.copy2(source, target)
    return target
