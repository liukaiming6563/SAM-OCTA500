"""
扫描 OCTA-500 raw 原始结构。

命令示例：
    python scripts/data_prepare/02_inspect_octa500.py --config configs/data/octa500_prepare.yaml

输入：
    配置文件中的 raw_root。

输出：
    manifest_raw.csv、raw_structure_report.json、inspect_log.txt，以及结构摘要文档。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from sam_octa500.data_prepare.inspect_utils import scan_raw_dataset, write_raw_outputs, write_structure_markdown
from sam_octa500.utils.config_utils import load_config
from sam_octa500.utils.log_utils import log_header, write_log
from sam_octa500.utils.path_utils import as_path, ensure_output_dirs


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(description="扫描 OCTA-500 raw 原始目录")
    parser.add_argument("--config", required=True, help="数据准备配置文件路径")
    return parser.parse_args()


def main() -> None:
    """主函数：读取配置、扫描 raw、写入 manifest、报告和文档。"""
    args = parse_args()
    config = load_config(args.config)
    ensure_output_dirs(config)
    log_path = as_path(config, "log_dir") / "inspect_log.txt"
    lines = log_header("02_inspect_octa500.py")
    rows, report = scan_raw_dataset(config)
    write_raw_outputs(config, rows, report)
    docs_path = write_structure_markdown(config, report)
    lines.extend(
        [
            f"raw_root: {config['raw_root']}",
            f"文件总数: {report['file_count']}",
            f"manifest: {as_path(config, 'manifest_dir') / 'manifest_raw.csv'}",
            f"report: {as_path(config, 'report_dir') / 'raw_structure_report.json'}",
            f"structure_doc: {docs_path}",
            "完成。",
        ]
    )
    write_log(log_path, lines)
    print(f"raw 扫描完成: {report['file_count']} files")


if __name__ == "__main__":
    main()
