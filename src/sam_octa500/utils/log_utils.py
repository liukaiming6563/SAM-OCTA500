"""
日志工具。

数据准备脚本使用文本日志记录运行时间、输入输出、异常样本和安全跳过信息。
这些日志保存在本地数据目录，不提交到代码仓库。
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path


def write_log(log_path: str | Path, lines: list[str], mode: str = "w") -> None:
    """
    写入文本日志。

    参数：
        log_path: 日志文件路径。
        lines: 日志行列表。
        mode: 写入模式，默认覆盖本阶段日志；脚本会在内容中记录运行时间。
    """
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open(mode, encoding="utf-8") as f:
        for line in lines:
            f.write(f"{line}\n")


def log_header(script_name: str) -> list[str]:
    """
    生成日志头部。

    参数：
        script_name: 当前脚本名称。

    返回：
        日志行列表。
    """
    return [
        f"脚本: {script_name}",
        f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "-" * 80,
    ]
