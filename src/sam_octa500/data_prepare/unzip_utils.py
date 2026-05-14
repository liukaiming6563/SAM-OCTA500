"""
解压辅助说明。

实际解压由 PowerShell 脚本调用 7-Zip 完成。本文件保留用于后续在 Python
工作流中复用解压路径规划和日志约定。
"""

from __future__ import annotations

from pathlib import Path


def planned_extract_dir(zip_name: str, raw_root: str | Path) -> Path:
    """
    根据 zip 文件名规划解压目录。

    参数：
        zip_name: 原始压缩包文件名。
        raw_root: raw 数据根目录。

    返回：
        对应的解压目标目录。
    """
    name = zip_name.lower()
    root = Path(raw_root)
    if name == "code.zip":
        return root / "Code"
    if name == "label.zip":
        return root / "Label"
    if name.startswith("octa_3mm"):
        return root / "OCTA_3mm"
    if name.startswith("octa_6mm"):
        return root / "OCTA_6mm"
    return root / "Unknown"
