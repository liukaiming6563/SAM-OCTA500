"""
processed 数据可视化工具。

每个抽样样本生成一张横向拼接图：
    左侧：RGB image
    中间：单通道 mask
    右侧：mask 以红色半透明方式叠加到 image

抽样使用固定 random_seed，并保存 selected_samples.csv，保证可复现。
"""

from __future__ import annotations

import random
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from sam_octa500.utils.file_utils import read_csv, write_csv
from sam_octa500.utils.path_utils import as_path


def make_overlay(image: Image.Image, mask: Image.Image, alpha: float = 0.45) -> Image.Image:
    """
    生成 mask 叠加图。

    参数：
        image: RGB 图像，尺寸 [W, H]。
        mask: 单通道 mask，前景像素大于 0。
        alpha: 红色前景的透明度。

    返回：
        RGB overlay 图像。
    """
    rgb = np.array(image.convert("RGB")).astype(np.float32)
    mask_arr = np.array(mask.convert("L")) > 0
    red = np.zeros_like(rgb)
    red[..., 0] = 255
    out = rgb.copy()
    out[mask_arr] = (1 - alpha) * rgb[mask_arr] + alpha * red[mask_arr]
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), mode="RGB")


def visualize_processed_samples(config: dict[str, Any]) -> tuple[Path, Path, int]:
    """
    固定随机种子抽样并生成 processed 可视化图。

    参数：
        config: 数据准备配置。

    返回：
        (可视化目录, selected_samples.csv 路径, 样本数量)。
    """
    seed = int(config["random_seed"])
    num_samples = int(config["visualize_num_samples"])
    manifest_path = as_path(config, "manifest_dir") / "manifest_processed.csv"
    rows = [row for row in read_csv(manifest_path) if row.get("is_valid") == "1"]
    rng = random.Random(seed)
    selected = rng.sample(rows, min(num_samples, len(rows))) if rows else []
    output_dir = as_path(config, "visualization_dir") / "processed_samples" / f"{config['fov']}_{config['task']}"
    output_dir.mkdir(parents=True, exist_ok=True)

    selected_rows: list[dict[str, str]] = []
    for row in selected:
        image_path = Path(row["image_path"])
        mask_path = Path(row["mask_path"])
        with Image.open(image_path) as image, Image.open(mask_path) as mask:
            image_rgb = image.convert("RGB")
            mask_rgb = mask.convert("L").convert("RGB")
            overlay = make_overlay(image_rgb, mask)
            width, height = image_rgb.width, image_rgb.height
            canvas = Image.new("RGB", (width * 3, height), "white")
            canvas.paste(image_rgb, (0, 0))
            canvas.paste(mask_rgb, (width, 0))
            canvas.paste(overlay, (width * 2, 0))
            out_name = f"{row['sample_id']}_{row['split']}_{config['task']}.png"
            out_path = output_dir / out_name
            canvas.save(out_path)
        selected_rows.append(
            {
                "sample_id": row["sample_id"],
                "split": row["split"],
                "task": str(config["task"]),
                "image_path": row["image_path"],
                "mask_path": row["mask_path"],
                "visualization_path": str(out_path),
            }
        )

    selected_path = output_dir / "selected_samples.csv"
    write_csv(
        selected_path,
        selected_rows,
        ["sample_id", "split", "task", "image_path", "mask_path", "visualization_path"],
    )
    return output_dir, selected_path, len(selected_rows)
