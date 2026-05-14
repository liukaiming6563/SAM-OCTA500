"""
OCTA-500 2D image/mask 转换工具。

输入：
    manifest_raw.csv 和 raw 原始图像、标签。

输出：
    processed/OCTA500_2D/{fov}/{task}/{split}/images
    processed/OCTA500_2D/{fov}/{task}/{split}/masks
    processed/OCTA500_2D/{fov}/{task}/meta.csv

关键数据维度：
    image: RGB PNG，读取后形状为 [H, W, 3]。
    mask: 单通道二值 PNG，读取后形状为 [H, W]，像素值只允许 0 和 255。
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from sam_octa500.utils.file_utils import read_csv, write_csv
from sam_octa500.utils.image_utils import IMAGE_SUFFIXES, save_binary_mask_png, save_rgb_png
from sam_octa500.utils.path_utils import as_path, processed_task_dir


def parse_range(range_text: str) -> tuple[int, int]:
    """解析形如 10301-10440 的闭区间。"""
    left, right = str(range_text).split("-", 1)
    return int(left), int(right)


def split_for_sample(sample_id: str, config: dict[str, Any]) -> str:
    """
    根据配置中的编号范围确定 train/val/test。

    参数：
        sample_id: 五位样本编号。
        config: 数据准备配置，包含 split_rules。

    返回：
        split 名称；不在范围内时返回空字符串。
    """
    if not sample_id or not sample_id.isdigit():
        return ""
    value = int(sample_id)
    fov = str(config["fov"])
    for split, range_text in config["split_rules"][fov].items():
        start, end = parse_range(range_text)
        if start <= value <= end:
            return split
    return ""


def _contains_keywords(text: str, keywords: list[str]) -> bool:
    """判断路径文本是否包含任一关键词。"""
    lower = text.lower().replace("-", "_")
    return any(str(k).lower().replace("-", "_") in lower for k in keywords)


def _is_image_row(row: dict[str, str]) -> bool:
    """判断 manifest 行是否为可读取图像候选。"""
    return row.get("suffix", "").lower() in IMAGE_SUFFIXES


def build_pairs(config: dict[str, Any], manifest_rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[str]]:
    """
    从 raw manifest 中构建 image/mask 配对。

    参数：
        config: 数据准备配置。
        manifest_rows: manifest_raw.csv 行列表。

    返回：
        (pairs, logs)。pairs 中每行包含 sample_id、split、image_path、mask_path。
    """
    fov = str(config["fov"])
    input_keywords = [str(x) for x in config["input_keywords"]]
    mask_keywords = [str(x) for x in config["mask_keywords"]]
    images_by_sample: dict[str, list[dict[str, str]]] = defaultdict(list)
    masks_by_sample: dict[str, list[dict[str, str]]] = defaultdict(list)
    logs: list[str] = []

    for row in manifest_rows:
        sample_id = row.get("sample_id", "")
        if not sample_id or row.get("fov", "") != fov or not _is_image_row(row):
            continue
        rel = row.get("relative_path", "")
        top = row.get("top_folder", "").lower()
        if top.startswith("octa") and _contains_keywords(rel, input_keywords):
            images_by_sample[sample_id].append(row)
        if top == "label" and _contains_keywords(rel, mask_keywords):
            masks_by_sample[sample_id].append(row)

    expected_ids: list[str] = []
    for split, range_text in config["split_rules"][fov].items():
        start, end = parse_range(range_text)
        expected_ids.extend(str(v) for v in range(start, end + 1))

    pairs: list[dict[str, str]] = []
    for sample_id in expected_ids:
        split = split_for_sample(sample_id, config)
        image_candidates = sorted(images_by_sample.get(sample_id, []), key=lambda x: x["relative_path"])
        mask_candidates = sorted(masks_by_sample.get(sample_id, []), key=lambda x: x["relative_path"])
        if len(image_candidates) > 1:
            logs.append(f"样本 {sample_id} 存在多个 image 候选，按路径排序选第一个: {[x['relative_path'] for x in image_candidates]}")
        if len(mask_candidates) > 1:
            logs.append(f"样本 {sample_id} 存在多个 mask 候选，按路径排序选第一个: {[x['relative_path'] for x in mask_candidates]}")
        if not image_candidates or not mask_candidates:
            logs.append(f"样本 {sample_id} 缺失配对: image={len(image_candidates)}, mask={len(mask_candidates)}")
            continue
        pairs.append(
            {
                "sample_id": sample_id,
                "split": split,
                "image_path": image_candidates[0]["absolute_path"],
                "mask_path": mask_candidates[0]["absolute_path"],
                "image_relative_path": image_candidates[0]["relative_path"],
                "mask_relative_path": mask_candidates[0]["relative_path"],
            }
        )
    return pairs, logs


def convert_pairs(config: dict[str, Any], pairs: list[dict[str, str]]) -> list[dict[str, Any]]:
    """
    执行 RGB 图像和二值 mask 转换。

    参数：
        config: 数据准备配置。
        pairs: build_pairs 输出的配对列表。

    返回：
        meta.csv 行列表。
    """
    task_dir = processed_task_dir(config)
    allow_overwrite = bool(config.get("allow_overwrite", False))
    meta_rows: list[dict[str, Any]] = []

    for pair in pairs:
        sample_id = pair["sample_id"]
        split = pair["split"]
        image_out = task_dir / split / "images" / f"{sample_id}.png"
        mask_out = task_dir / split / "masks" / f"{sample_id}.png"
        if (image_out.exists() or mask_out.exists()) and not allow_overwrite:
            raise FileExistsError(f"转换目标已存在且不允许覆盖: {image_out} / {mask_out}")
        image_width, image_height = save_rgb_png(pair["image_path"], image_out)
        mask_width, mask_height, unique_values = save_binary_mask_png(pair["mask_path"], mask_out)
        if unique_values not in ([0], [255], [0, 255]):
            raise ValueError(f"mask 转换后取值异常: {mask_out}, {unique_values}")
        meta_rows.append(
            {
                "sample_id": sample_id,
                "fov": config["fov"],
                "task": config["task"],
                "split": split,
                "image_type": config["image_type"],
                "mask_type": config["task"],
                "original_image_path": pair["image_path"],
                "original_mask_path": pair["mask_path"],
                "output_image_path": str(image_out),
                "output_mask_path": str(mask_out),
                "image_width": image_width,
                "image_height": image_height,
                "mask_width": mask_width,
                "mask_height": mask_height,
            }
        )
    return meta_rows


def write_meta(config: dict[str, Any], meta_rows: list[dict[str, Any]]) -> Path:
    """
    写入转换后的 meta.csv。

    参数：
        config: 数据准备配置。
        meta_rows: 转换结果列表。

    返回：
        meta.csv 路径。
    """
    meta_path = processed_task_dir(config) / "meta.csv"
    fields = [
        "sample_id",
        "fov",
        "task",
        "split",
        "image_type",
        "mask_type",
        "original_image_path",
        "original_mask_path",
        "output_image_path",
        "output_mask_path",
        "image_width",
        "image_height",
        "mask_width",
        "mask_height",
    ]
    write_csv(meta_path, meta_rows, fields)
    return meta_path


def run_conversion(config: dict[str, Any]) -> tuple[Path, list[str], int]:
    """
    运行完整转换流程。

    参数：
        config: 数据准备配置。

    返回：
        (meta_csv_path, log_lines, converted_count)。
    """
    manifest_path = as_path(config, "manifest_dir") / "manifest_raw.csv"
    rows = read_csv(manifest_path)
    pairs, logs = build_pairs(config, rows)
    meta_rows = convert_pairs(config, pairs)
    meta_path = write_meta(config, meta_rows)
    return meta_path, logs, len(meta_rows)
