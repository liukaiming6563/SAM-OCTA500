"""
批量转换 OCTA-500 全部 2D 分割任务。

命令示例：
    python scripts/data_prepare/07_batch_convert_all_tasks.py --config configs/data/octa500_prepare.yaml

输入：
    manifest_raw.csv、raw 原始 OCTA(FULL) 图像和五类标签。

输出：
    processed/OCTA500_2D/{3M,6M}/{FAZ,LargeVessel,Capillary,Artery,Vein}
    outputs/reports/processed_all_tasks_summary.json
    outputs/logs/batch_convert_all_tasks_log.txt

关键说明：
    本脚本按任务逐一构造配置并调用已有转换、检查、可视化工具函数。
    如果某个任务目录已经有完整 meta.csv，且 image/mask 数量符合预期，则跳过转换，
    但仍会重新执行检查并保存任务级检查报告副本。
"""

from __future__ import annotations

import argparse
import copy
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from sam_octa500.data_prepare.check_utils import check_processed_dataset, write_check_outputs
from sam_octa500.data_prepare.convert_utils import parse_range, run_conversion
from sam_octa500.data_prepare.visualize_utils import visualize_processed_samples
from sam_octa500.utils.config_utils import load_config, save_json, snapshot_config
from sam_octa500.utils.file_utils import read_csv
from sam_octa500.utils.log_utils import log_header, write_log
from sam_octa500.utils.path_utils import as_path, ensure_output_dirs, processed_task_dir


TASKS = {
    "FAZ": ["gt_faz"],
    "LargeVessel": ["gt_largevessel"],
    "Capillary": ["gt_capillary"],
    "Artery": ["gt_artery"],
    "Vein": ["gt_vein"],
}


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(description="批量转换 OCTA-500 全部 2D 分割任务")
    parser.add_argument("--config", required=True, help="数据准备配置文件路径")
    return parser.parse_args()


def expected_count(config: dict[str, Any]) -> int:
    """
    根据 split 规则计算当前 fov 的期望样本数。

    参数：
        config: 当前任务配置。

    返回：
        train、val、test 三个区间的样本总数。
    """
    total = 0
    for range_text in config["split_rules"][str(config["fov"])].values():
        start, end = parse_range(range_text)
        total += end - start + 1
    return total


def task_is_complete(config: dict[str, Any]) -> bool:
    """
    判断任务是否已经转换完整。

    参数：
        config: 当前任务配置。

    返回：
        True 表示 meta.csv 存在且 image/mask 数量达到期望。
    """
    task_dir = processed_task_dir(config)
    meta_path = task_dir / "meta.csv"
    if not meta_path.exists():
        return False
    rows = read_csv(meta_path)
    image_count = sum(1 for p in task_dir.rglob("images/*.png") if p.is_file())
    mask_count = sum(1 for p in task_dir.rglob("masks/*.png") if p.is_file())
    n_expected = expected_count(config)
    return len(rows) == n_expected and image_count == n_expected and mask_count == n_expected


def copy_task_outputs(config: dict[str, Any]) -> dict[str, str]:
    """
    保存任务级检查文件副本，避免多个任务互相覆盖通用检查报告。

    参数：
        config: 当前任务配置。

    返回：
        任务级输出路径字典。
    """
    suffix = f"{config['fov']}_{config['task']}"
    manifest_dir = as_path(config, "manifest_dir")
    report_dir = as_path(config, "report_dir")
    outputs = {
        "manifest_processed": str(manifest_dir / f"manifest_processed_{suffix}.csv"),
        "check_report_json": str(report_dir / f"processed_check_report_{suffix}.json"),
        "check_report_md": str(report_dir / f"processed_check_report_{suffix}.md"),
    }
    shutil.copy2(manifest_dir / "manifest_processed.csv", outputs["manifest_processed"])
    shutil.copy2(report_dir / "processed_check_report.json", outputs["check_report_json"])
    shutil.copy2(report_dir / "processed_check_report.md", outputs["check_report_md"])
    return outputs


def make_task_config(base_config: dict[str, Any], fov: str, task: str) -> dict[str, Any]:
    """
    构造单个任务配置。

    参数：
        base_config: 原始配置。
        fov: 3M 或 6M。
        task: 分割任务名称。

    返回：
        当前任务配置副本。
    """
    cfg = copy.deepcopy(base_config)
    cfg["fov"] = fov
    cfg["task"] = task
    cfg["image_type"] = "FULL"
    cfg["input_keywords"] = ["octa(full)"]
    cfg["mask_keywords"] = TASKS[task]
    cfg["allow_overwrite"] = False
    return cfg


def main() -> None:
    """主函数：批量转换、检查、可视化并保存全任务摘要。"""
    args = parse_args()
    base_config = load_config(args.config)
    ensure_output_dirs(base_config)
    log_path = as_path(base_config, "log_dir") / "batch_convert_all_tasks_log.txt"
    lines = log_header("07_batch_convert_all_tasks.py")
    snapshot = snapshot_config(args.config, as_path(base_config, "config_snapshot_dir"), "batch_all_tasks")
    lines.append(f"配置快照: {snapshot}")

    summary_rows: list[dict[str, Any]] = []
    for fov in ["3M", "6M"]:
        for task in ["FAZ", "LargeVessel", "Capillary", "Artery", "Vein"]:
            cfg = make_task_config(base_config, fov, task)
            task_dir = processed_task_dir(cfg)
            lines.append(f"开始任务: {fov} + {task}")
            converted = False
            if task_is_complete(cfg):
                lines.append(f"跳过转换: {task_dir} 已完整存在。")
            else:
                meta_path, pair_logs, converted_count = run_conversion(cfg)
                converted = True
                lines.extend(pair_logs)
                lines.append(f"转换完成: {meta_path}, 样本数 {converted_count}")

            check_rows, check_report = check_processed_dataset(cfg)
            write_check_outputs(cfg, check_rows, check_report)
            copied_outputs = copy_task_outputs(cfg)
            vis_dir, selected_path, vis_count = visualize_processed_samples(cfg)
            split_counts = check_report.get("valid_sample_counts", {})
            summary_rows.append(
                {
                    "fov": fov,
                    "task": task,
                    "task_dir": str(task_dir),
                    "converted_this_run": converted,
                    "train": int(split_counts.get("train", 0)),
                    "val": int(split_counts.get("val", 0)),
                    "test": int(split_counts.get("test", 0)),
                    "total": int(sum(split_counts.values())),
                    "anomaly_count": int(check_report.get("anomaly_count", 0)),
                    "foreground_ratio": check_report.get("foreground_ratio", {}),
                    "visualization_dir": str(vis_dir),
                    "selected_samples": str(selected_path),
                    "visualization_count": vis_count,
                    **copied_outputs,
                }
            )
            lines.append(
                f"检查完成: {fov}+{task}, train={split_counts.get('train', 0)}, "
                f"val={split_counts.get('val', 0)}, test={split_counts.get('test', 0)}, "
                f"异常={check_report.get('anomaly_count', 0)}, 可视化={vis_count}"
            )

    summary = {
        "run_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "task_count": len(summary_rows),
        "tasks": summary_rows,
    }
    summary_path = as_path(base_config, "report_dir") / "processed_all_tasks_summary.json"
    save_json(summary, summary_path)
    lines.append(f"全任务摘要: {summary_path}")
    lines.append("完成。")
    write_log(log_path, lines)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
