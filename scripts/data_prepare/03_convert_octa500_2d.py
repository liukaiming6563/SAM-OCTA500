"""
将 OCTA-500 raw 数据转换为 2D image/mask 格式。

命令示例：
    python scripts/data_prepare/03_convert_octa500_2d.py --config configs/data/octa500_prepare.yaml

输入：
    manifest_raw.csv 和 raw 原始文件。

输出：
    processed/OCTA500_2D/{fov}/{task} 目录和 meta.csv。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from sam_octa500.data_prepare.convert_utils import run_conversion
from sam_octa500.utils.config_utils import load_config, snapshot_config
from sam_octa500.utils.log_utils import log_header, write_log
from sam_octa500.utils.path_utils import as_path, ensure_output_dirs, processed_task_dir


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(description="转换 OCTA-500 为 2D image/mask 格式")
    parser.add_argument("--config", required=True, help="数据准备配置文件路径")
    return parser.parse_args()


def main() -> None:
    """主函数：读取配置、保存配置快照、执行转换并记录日志。"""
    args = parse_args()
    config = load_config(args.config)
    ensure_output_dirs(config)
    log_path = as_path(config, "log_dir") / "convert_log.txt"
    lines = log_header("03_convert_octa500_2d.py")
    snapshot = snapshot_config(args.config, as_path(config, "config_snapshot_dir"), "convert")
    lines.append(f"配置快照: {snapshot}")
    meta_path, pair_logs, converted_count = run_conversion(config)
    lines.extend(pair_logs)
    lines.extend(
        [
            f"转换任务: {config['fov']} + {config['task']}",
            f"输出目录: {processed_task_dir(config)}",
            f"meta.csv: {meta_path}",
            f"转换样本数: {converted_count}",
            "完成。",
        ]
    )
    write_log(log_path, lines)
    print(f"转换完成: {converted_count} samples")


if __name__ == "__main__":
    main()
