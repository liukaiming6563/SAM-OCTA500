"""
检查 OCTA-500 processed 数据质量。

命令示例：
    python scripts/data_prepare/04_check_processed_octa500.py --config configs/data/octa500_prepare.yaml

输入：
    processed/OCTA500_2D/{fov}/{task}。

输出：
    manifest_processed.csv、processed_check_report.json、processed_check_report.md。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from sam_octa500.data_prepare.check_utils import check_processed_dataset, write_check_outputs
from sam_octa500.utils.config_utils import load_config
from sam_octa500.utils.log_utils import log_header, write_log
from sam_octa500.utils.path_utils import as_path, ensure_output_dirs


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(description="检查 OCTA-500 processed 数据")
    parser.add_argument("--config", required=True, help="数据准备配置文件路径")
    return parser.parse_args()


def main() -> None:
    """主函数：执行 processed 检查并写入报告。"""
    args = parse_args()
    config = load_config(args.config)
    ensure_output_dirs(config)
    log_path = as_path(config, "log_dir") / "check_log.txt"
    lines = log_header("04_check_processed_octa500.py")
    rows, report = check_processed_dataset(config)
    write_check_outputs(config, rows, report)
    lines.extend(
        [
            f"检查任务: {config['fov']} + {config['task']}",
            f"检查行数: {report['total_rows']}",
            f"异常样本数: {report['anomaly_count']}",
            f"manifest: {as_path(config, 'manifest_dir') / 'manifest_processed.csv'}",
            f"report: {as_path(config, 'report_dir') / 'processed_check_report.json'}",
            "完成。",
        ]
    )
    write_log(log_path, lines)
    print(f"检查完成: anomalies={report['anomaly_count']}")


if __name__ == "__main__":
    main()
