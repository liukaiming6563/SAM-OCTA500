"""
生成 OCTA-500 工程文档。

命令示例：
    python scripts/data_prepare/06_generate_dataset_docs.py --config configs/data/octa500_prepare.yaml

输入：
    manifest、检查报告、可视化抽样列表和日志。

输出：
    README.md、docs 下的 Markdown 文档和 outputs/reports/run_summary.json。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from sam_octa500.data_prepare.doc_utils import generate_documents
from sam_octa500.utils.config_utils import load_config
from sam_octa500.utils.log_utils import log_header, write_log
from sam_octa500.utils.path_utils import as_path, ensure_output_dirs


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(description="生成 OCTA-500 数据说明文档")
    parser.add_argument("--config", required=True, help="数据准备配置文件路径")
    return parser.parse_args()


def main() -> None:
    """主函数：根据实际运行产物生成可提交的 Markdown 文档。"""
    args = parse_args()
    config = load_config(args.config)
    ensure_output_dirs(config)
    log_path = as_path(config, "log_dir") / "docs_log.txt"
    lines = log_header("06_generate_dataset_docs.py")
    summary = generate_documents(config)
    lines.extend(
        [
            f"README: {as_path(config, 'project_root') / 'README.md'}",
            f"docs_dir: {as_path(config, 'project_root') / 'docs'}",
            f"run_summary: {as_path(config, 'report_dir') / 'run_summary.json'}",
            f"当前任务: {summary['processed_task']}",
            "完成。",
        ]
    )
    write_log(log_path, lines)
    print("文档生成完成")


if __name__ == "__main__":
    main()
