"""
生成 OCTA-500 processed 抽样可视化。

命令示例：
    python scripts/data_prepare/05_visualize_processed_octa500.py --config configs/data/octa500_prepare.yaml

输入：
    manifest_processed.csv。

输出：
    outputs/visualizations/processed_samples/{fov}_{task} 下的拼接图和 selected_samples.csv。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from sam_octa500.data_prepare.visualize_utils import visualize_processed_samples
from sam_octa500.utils.config_utils import load_config
from sam_octa500.utils.log_utils import log_header, write_log
from sam_octa500.utils.path_utils import as_path, ensure_output_dirs


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(description="可视化 OCTA-500 processed 样本")
    parser.add_argument("--config", required=True, help="数据准备配置文件路径")
    return parser.parse_args()


def main() -> None:
    """主函数：固定随机种子抽样并输出可视化图。"""
    args = parse_args()
    config = load_config(args.config)
    ensure_output_dirs(config)
    log_path = as_path(config, "log_dir") / "visualize_log.txt"
    lines = log_header("05_visualize_processed_octa500.py")
    output_dir, selected_path, count = visualize_processed_samples(config)
    lines.extend(
        [
            f"随机种子: {config['random_seed']}",
            f"抽样数量: {count}",
            f"可视化目录: {output_dir}",
            f"抽样列表: {selected_path}",
            "完成。",
        ]
    )
    write_log(log_path, lines)
    print(f"可视化完成: {count} samples")


if __name__ == "__main__":
    main()
