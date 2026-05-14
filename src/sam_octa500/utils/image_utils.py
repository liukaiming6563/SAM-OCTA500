"""
图像读写工具。

本文件封装 Pillow 图像读取、尺寸检查、RGB 转换和二值 mask 规范化。
processed 数据要求 image 为 RGB PNG，mask 为单通道 PNG，二值任务像素只取
0 和 255。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image


IMAGE_SUFFIXES = {".png", ".bmp", ".jpg", ".jpeg", ".tif", ".tiff"}


def get_image_info(path: str | Path) -> dict[str, Any]:
    """
    获取图像基础信息。

    参数：
        path: 图像文件路径。

    返回：
        包含 width、height、mode 的字典；如果 Pillow 无法识别则返回空值。
    """
    try:
        with Image.open(path) as img:
            return {"width": img.width, "height": img.height, "image_mode": img.mode}
    except Exception:
        return {"width": "", "height": "", "image_mode": ""}


def save_rgb_png(source_path: str | Path, target_path: str | Path) -> tuple[int, int]:
    """
    将原始图像保存为 RGB PNG。

    参数：
        source_path: 原始 OCTA 图像路径。
        target_path: 输出 PNG 路径。

    返回：
        (width, height)。
    """
    target = Path(target_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source_path) as img:
        rgb = img.convert("RGB")
        rgb.save(target)
        return rgb.width, rgb.height


def save_binary_mask_png(source_path: str | Path, target_path: str | Path) -> tuple[int, int, list[int]]:
    """
    将原始标签保存为单通道二值 PNG。

    参数：
        source_path: 原始 mask 路径。
        target_path: 输出 mask 路径。

    返回：
        (width, height, unique_values)。unique_values 是转换后的像素取值列表。
    """
    target = Path(target_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source_path) as img:
        gray = img.convert("L")
        arr = np.array(gray)
        binary = np.where(arr > 0, 255, 0).astype(np.uint8)
        out = Image.fromarray(binary, mode="L")
        out.save(target)
        return out.width, out.height, sorted(int(v) for v in np.unique(binary).tolist())


def foreground_ratio(mask_path: str | Path) -> float:
    """
    计算二值 mask 前景比例。

    参数：
        mask_path: 单通道 mask 路径，推荐取值为 0 和 255。

    返回：
        前景像素数 / 总像素数。
    """
    with Image.open(mask_path) as img:
        arr = np.array(img.convert("L"))
    if arr.size == 0:
        return 0.0
    return float((arr > 0).sum() / arr.size)
