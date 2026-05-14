"""
processed 数据检查工具。

输入：
    processed/OCTA500_2D/{fov}/{task} 下的 images、masks 和 meta.csv。

输出：
    manifest_processed.csv、processed_check_report.json、processed_check_report.md。

检查内容：
    1. image 与 mask 数量是否一致。
    2. 文件名是否一一对应。
    3. 尺寸是否一致。
    4. image 是否为 RGB。
    5. mask 是否为单通道二值图，取值是否只包含 0 和 255。
    6. mask 是否全黑，并统计前景像素比例。
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from sam_octa500.utils.config_utils import save_json
from sam_octa500.utils.file_utils import write_csv
from sam_octa500.utils.image_utils import foreground_ratio
from sam_octa500.utils.path_utils import as_path, processed_task_dir


def check_processed_dataset(config: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """
    检查当前 processed 任务目录。

    参数：
        config: 数据准备配置。

    返回：
        (manifest_rows, report)。
    """
    task_dir = processed_task_dir(config)
    splits = ["train", "val", "test"]
    rows: list[dict[str, Any]] = []
    anomalies: list[dict[str, Any]] = []
    split_counts: dict[str, dict[str, int]] = {}
    ratios: list[float] = []

    for split in splits:
        image_dir = task_dir / split / "images"
        mask_dir = task_dir / split / "masks"
        image_files = sorted(image_dir.glob("*.png")) if image_dir.exists() else []
        mask_files = sorted(mask_dir.glob("*.png")) if mask_dir.exists() else []
        image_names = {p.name for p in image_files}
        mask_names = {p.name for p in mask_files}
        split_counts[split] = {"images": len(image_files), "masks": len(mask_files)}

        for name in sorted(image_names | mask_names):
            sample_id = Path(name).stem
            image_path = image_dir / name
            mask_path = mask_dir / name
            issue_list: list[str] = []
            image_width = image_height = mask_width = mask_height = ""
            image_mode = mask_mode = ""
            unique_values: list[int] = []
            ratio = 0.0

            if not image_path.exists():
                issue_list.append("缺失 image")
            if not mask_path.exists():
                issue_list.append("缺失 mask")
            if image_path.exists():
                with Image.open(image_path) as img:
                    image_width, image_height, image_mode = img.width, img.height, img.mode
                if image_mode != "RGB":
                    issue_list.append(f"image 模式不是 RGB: {image_mode}")
            if mask_path.exists():
                with Image.open(mask_path) as mask:
                    mask_width, mask_height, mask_mode = mask.width, mask.height, mask.mode
                    arr = np.array(mask.convert("L"))
                unique_values = sorted(int(v) for v in np.unique(arr).tolist())
                ratio = foreground_ratio(mask_path)
                ratios.append(ratio)
                if any(v not in {0, 255} for v in unique_values):
                    issue_list.append(f"mask 取值不是 0/255: {unique_values}")
                if ratio == 0:
                    issue_list.append("mask 全黑")
            if image_path.exists() and mask_path.exists() and (image_width != mask_width or image_height != mask_height):
                issue_list.append("image 与 mask 尺寸不一致")

            row = {
                "sample_id": sample_id,
                "fov": config["fov"],
                "task": config["task"],
                "split": split,
                "image_path": str(image_path) if image_path.exists() else "",
                "mask_path": str(mask_path) if mask_path.exists() else "",
                "image_width": image_width,
                "image_height": image_height,
                "mask_width": mask_width,
                "mask_height": mask_height,
                "image_mode": image_mode,
                "mask_mode": mask_mode,
                "mask_unique_values": "|".join(str(v) for v in unique_values),
                "foreground_ratio": f"{ratio:.8f}",
                "is_valid": "0" if issue_list else "1",
                "issues": "; ".join(issue_list),
            }
            rows.append(row)
            if issue_list:
                anomalies.append(row)

    split_sample_counter = Counter(row["split"] for row in rows if row["is_valid"] == "1")
    report = {
        "task_dir": str(task_dir),
        "fov": config["fov"],
        "task": config["task"],
        "split_file_counts": split_counts,
        "valid_sample_counts": dict(split_sample_counter),
        "total_rows": len(rows),
        "anomaly_count": len(anomalies),
        "anomalies": anomalies[:200],
        "foreground_ratio": {
            "min": min(ratios) if ratios else 0,
            "max": max(ratios) if ratios else 0,
            "mean": float(np.mean(ratios)) if ratios else 0,
        },
    }
    return rows, report


def write_check_outputs(config: dict[str, Any], rows: list[dict[str, Any]], report: dict[str, Any]) -> None:
    """
    写入 processed 检查结果。

    参数：
        config: 数据准备配置。
        rows: processed manifest 行。
        report: 检查报告。
    """
    manifest_path = as_path(config, "manifest_dir") / "manifest_processed.csv"
    report_json = as_path(config, "report_dir") / "processed_check_report.json"
    report_md = as_path(config, "report_dir") / "processed_check_report.md"
    fields = [
        "sample_id",
        "fov",
        "task",
        "split",
        "image_path",
        "mask_path",
        "image_width",
        "image_height",
        "mask_width",
        "mask_height",
        "image_mode",
        "mask_mode",
        "mask_unique_values",
        "foreground_ratio",
        "is_valid",
        "issues",
    ]
    write_csv(manifest_path, rows, fields)
    save_json(report, report_json)
    split_lines = "\n".join(
        f"- `{split}`: image {counts['images']}，mask {counts['masks']}"
        for split, counts in report["split_file_counts"].items()
    )
    text = f"""# Processed 数据检查报告

- 任务目录：`{report['task_dir']}`
- 当前任务：{report['fov']} + {report['task']}
- 检查样本行数：{report['total_rows']}
- 异常样本数：{report['anomaly_count']}
- 前景比例范围：{report['foreground_ratio']['min']:.8f} 至 {report['foreground_ratio']['max']:.8f}
- 前景比例均值：{report['foreground_ratio']['mean']:.8f}

## split 文件数量

{split_lines}
"""
    report_md.write_text(text, encoding="utf-8")
