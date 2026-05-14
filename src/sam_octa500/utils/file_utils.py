"""
文件操作工具。

本文件集中处理目录创建、覆盖检查和 CSV 写入，保证数据处理流程不会静默覆盖
已有结果。
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable


def ensure_parent(path: str | Path) -> None:
    """创建文件父目录。"""
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def assert_can_write(path: str | Path, allow_overwrite: bool) -> None:
    """
    检查文件是否允许写入。

    参数：
        path: 待写入文件。
        allow_overwrite: 是否允许覆盖已有文件。

    异常：
        FileExistsError: 文件已存在且不允许覆盖。
    """
    target = Path(path)
    if target.exists() and not allow_overwrite:
        raise FileExistsError(f"目标文件已存在，且配置不允许覆盖: {target}")


def write_csv(path: str | Path, rows: Iterable[dict], fieldnames: list[str]) -> None:
    """
    写入 CSV 表格。

    参数：
        path: 输出 CSV 文件。
        rows: 字典行迭代器。
        fieldnames: CSV 列名。
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: str | Path) -> list[dict[str, str]]:
    """
    读取 CSV 表格。

    参数：
        path: CSV 文件路径。

    返回：
        字典列表，所有值按字符串读取。
    """
    with Path(path).open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))
