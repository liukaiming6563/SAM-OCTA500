"""
OCTA-500 raw 数据扫描工具。

输入：
    raw_root 下的 Code、Label、OCTA_3mm、OCTA_6mm 原始解压结果。

输出：
    1. manifest_raw.csv：逐文件记录相对路径、绝对路径、样本编号、视场、图像尺寸等。
    2. raw_structure_report.json：汇总文件数量、后缀分布、样本编号范围、尺寸分布等。
    3. docs/OCTA500_structure_summary.md：适合提交到仓库的结构摘要。

关键说明：
    raw 数据只读扫描，不修改、不移动、不覆盖原始文件。
"""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import re
from typing import Any

from sam_octa500.utils.config_utils import save_json
from sam_octa500.utils.file_utils import write_csv
from sam_octa500.utils.image_utils import IMAGE_SUFFIXES, get_image_info
from sam_octa500.utils.path_utils import as_path


KNOWN_LABELS = ["gt_faz", "gt_largevessel", "gt_capillary", "gt_artery", "gt_vein"]


def infer_sample_id(text: str) -> str:
    """
    从路径文本中推断样本编号。

    参数：
        text: 文件相对路径或文件名。

    返回：
        五位数字样本编号；无法识别时返回空字符串。
    """
    matches = re.findall(r"(?<!\d)(10\d{3})(?!\d)", text)
    return matches[0] if matches else ""


def infer_fov(relative_path: str, sample_id: str) -> str:
    """
    根据路径和样本编号推断视场。

    参数：
        relative_path: 相对 raw_root 的路径。
        sample_id: 五位样本编号。

    返回：
        3M、6M 或空字符串。
    """
    lower = relative_path.lower()
    if "octa_3mm" in lower or "3mm" in lower:
        return "3M"
    if "octa_6mm" in lower or "6mm" in lower:
        return "6M"
    if sample_id.isdigit():
        value = int(sample_id)
        if 10301 <= value <= 10500:
            return "3M"
        if 10001 <= value <= 10300:
            return "6M"
    return ""


def infer_label_type(relative_path: str) -> str:
    """
    从路径中识别标签类型。

    参数：
        relative_path: 文件相对路径。

    返回：
        标签关键词，例如 gt_faz；无法识别时返回空字符串。
    """
    lower = relative_path.lower().replace("-", "_")
    for label in KNOWN_LABELS:
        if label in lower:
            return label
    return ""


def scan_raw_dataset(config: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """
    扫描 raw 目录并生成逐文件 manifest 与统计报告。

    参数：
        config: 数据准备配置字典。

    返回：
        (manifest_rows, report)。
    """
    raw_root = as_path(config, "raw_root")
    rows: list[dict[str, Any]] = []
    suffix_counter: Counter[str] = Counter()
    size_counter: Counter[str] = Counter()
    label_counter: Counter[str] = Counter()
    sample_file_counter: Counter[str] = Counter()
    sample_ids_by_fov: dict[str, list[int]] = defaultdict(list)

    for path in sorted(raw_root.rglob("*")):
        if not path.is_file():
            continue
        relative_path = str(path.relative_to(raw_root))
        parts = path.relative_to(raw_root).parts
        top_folder = parts[0] if len(parts) > 0 else ""
        second_folder = parts[1] if len(parts) > 1 else ""
        suffix = path.suffix.lower()
        sample_id = infer_sample_id(relative_path)
        fov = infer_fov(relative_path, sample_id)
        info = {"width": "", "height": "", "image_mode": ""}
        if suffix in IMAGE_SUFFIXES:
            info = get_image_info(path)
            if info["width"] and info["height"]:
                size_counter[f"{info['width']}x{info['height']}|{info['image_mode']}"] += 1
        label_type = infer_label_type(relative_path)
        if label_type:
            label_counter[label_type] += 1
        if sample_id:
            sample_file_counter[sample_id] += 1
            if fov and int(sample_id) not in sample_ids_by_fov[fov]:
                sample_ids_by_fov[fov].append(int(sample_id))
        suffix_counter[suffix or "<none>"] += 1
        rows.append(
            {
                "relative_path": relative_path,
                "absolute_path": str(path),
                "top_folder": top_folder,
                "second_folder": second_folder,
                "suffix": suffix,
                "sample_id": sample_id,
                "fov": fov,
                "width": info["width"],
                "height": info["height"],
                "image_mode": info["image_mode"],
                "file_size_bytes": path.stat().st_size,
                "label_type": label_type,
            }
        )

    sample_ranges = {}
    for fov, values in sample_ids_by_fov.items():
        values_sorted = sorted(values)
        sample_ranges[fov] = {
            "min": values_sorted[0] if values_sorted else None,
            "max": values_sorted[-1] if values_sorted else None,
            "count": len(values_sorted),
        }
    report = {
        "raw_root": str(raw_root),
        "file_count": len(rows),
        "suffix_counts": dict(sorted(suffix_counter.items())),
        "sample_id_ranges": sample_ranges,
        "image_size_distribution": dict(size_counter.most_common()),
        "label_type_distribution": dict(sorted(label_counter.items())),
        "files_per_sample_summary": {
            "sample_count": len(sample_file_counter),
            "min": min(sample_file_counter.values()) if sample_file_counter else 0,
            "max": max(sample_file_counter.values()) if sample_file_counter else 0,
        },
        "files_per_sample": dict(sorted(sample_file_counter.items())),
    }
    return rows, report


def write_raw_outputs(config: dict[str, Any], rows: list[dict[str, Any]], report: dict[str, Any]) -> None:
    """
    写入 raw 扫描结果。

    参数：
        config: 数据准备配置字典。
        rows: manifest 行。
        report: 汇总报告。
    """
    manifest_path = as_path(config, "manifest_dir") / "manifest_raw.csv"
    report_path = as_path(config, "report_dir") / "raw_structure_report.json"
    fields = [
        "relative_path",
        "absolute_path",
        "top_folder",
        "second_folder",
        "suffix",
        "sample_id",
        "fov",
        "width",
        "height",
        "image_mode",
        "file_size_bytes",
        "label_type",
    ]
    write_csv(manifest_path, rows, fields)
    save_json(report, report_path)


def write_structure_markdown(config: dict[str, Any], report: dict[str, Any]) -> Path:
    """
    根据 raw 扫描报告生成结构摘要文档。

    参数：
        config: 数据准备配置字典。
        report: raw_structure_report.json 对应的统计字典。

    返回：
        写入的 Markdown 路径。
    """
    docs_path = as_path(config, "project_root") / "docs" / "OCTA500_structure_summary.md"
    suffix_lines = "\n".join(f"- `{k}`: {v}" for k, v in report["suffix_counts"].items())
    fov_lines = "\n".join(
        f"- `{k}`: 编号 {v['min']} 至 {v['max']}，识别样本数 {v['count']}"
        for k, v in sorted(report["sample_id_ranges"].items())
    )
    size_lines = "\n".join(f"- `{k}`: {v}" for k, v in list(report["image_size_distribution"].items())[:20])
    label_lines = "\n".join(f"- `{k}`: {v}" for k, v in report["label_type_distribution"].items())
    text = f"""# OCTA-500 原始结构摘要

本文件基于本地 raw 目录的实际扫描结果生成，只保留结构和统计摘要，不包含原始数据内容。

## 扫描范围

- raw 根目录：`{report['raw_root']}`
- 文件总数：{report['file_count']}
- 识别到的样本数：{report['files_per_sample_summary']['sample_count']}
- 每个样本文件数范围：{report['files_per_sample_summary']['min']} 至 {report['files_per_sample_summary']['max']}

## 后缀分布

{suffix_lines if suffix_lines else '- 未识别到文件'}

## 样本编号范围

{fov_lines if fov_lines else '- 未识别到样本编号'}

## 图像尺寸和模式分布

{size_lines if size_lines else '- 未识别到可由 Pillow 读取的图像文件'}

## 标签类型分布

{label_lines if label_lines else '- 未在路径中识别到标准标签关键词'}
"""
    docs_path.parent.mkdir(parents=True, exist_ok=True)
    docs_path.write_text(text, encoding="utf-8")
    return docs_path
