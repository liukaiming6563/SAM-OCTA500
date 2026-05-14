"""
OCTA-500 processed 数据集读取模块。

输入目录格式：
    processed/OCTA500_2D/{fov}/{task}/{split}/images/{sample_id}.png
    processed/OCTA500_2D/{fov}/{task}/{split}/masks/{sample_id}.png

返回字段：
    image: 默认形状 [3, H, W]，float32，取值范围 [0, 1]。
    mask: 默认形状 [1, H, W]，float32，取值范围 {0, 1}。
    sample_id: 五位样本编号。
    image_path / mask_path: 本地文件路径字符串。

说明：
    如果环境安装了 PyTorch，本类可直接用于 torch.utils.data.DataLoader；
    如果未安装 PyTorch，仍可通过 __len__ 和 __getitem__ 返回 NumPy 数据。
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Any

import numpy as np
from PIL import Image

try:
    from torch.utils.data import Dataset
    import torch
except Exception:
    Dataset = object  # type: ignore
    torch = None  # type: ignore


class OCTA500Dataset(Dataset):
    """
    OCTA-500 二维分割数据集。

    参数：
        root_dir: processed/OCTA500_2D 根目录或具体任务目录。
        fov: 视场名称，例如 3M 或 6M。
        task: 标签任务，例如 FAZ。
        split: train、val 或 test。
        transform: 可选联合变换函数，输入和输出均为字典。
        return_torch: 是否返回 torch.Tensor；如果 PyTorch 不可用则自动返回 NumPy。
    """

    def __init__(
        self,
        root_dir: str | Path,
        fov: str = "3M",
        task: str = "FAZ",
        split: str = "train",
        transform: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
        return_torch: bool = True,
    ) -> None:
        self.root_dir = Path(root_dir)
        if (self.root_dir / fov / task).exists():
            self.task_dir = self.root_dir / fov / task
        else:
            self.task_dir = self.root_dir
        self.fov = fov
        self.task = task
        self.split = split
        self.transform = transform
        self.return_torch = return_torch and torch is not None
        self.image_dir = self.task_dir / split / "images"
        self.mask_dir = self.task_dir / split / "masks"
        self.image_paths = sorted(self.image_dir.glob("*.png"))
        self.sample_ids = [p.stem for p in self.image_paths if (self.mask_dir / p.name).exists()]

    def __len__(self) -> int:
        """返回当前 split 的样本数量。"""
        return len(self.sample_ids)

    def _load_image(self, path: Path) -> np.ndarray:
        """
        读取 RGB image。

        参数：
            path: PNG 图像路径。

        返回：
            NumPy 数组，形状 [3, H, W]，float32，取值范围 [0, 1]。
        """
        with Image.open(path) as img:
            arr = np.array(img.convert("RGB"), dtype=np.float32) / 255.0
        return np.transpose(arr, (2, 0, 1))

    def _load_mask(self, path: Path) -> np.ndarray:
        """
        读取二值 mask。

        参数：
            path: PNG mask 路径。

        返回：
            NumPy 数组，形状 [1, H, W]，float32，取值范围 {0, 1}。
        """
        with Image.open(path) as img:
            arr = np.array(img.convert("L"), dtype=np.float32)
        arr = (arr > 0).astype(np.float32)
        return arr[None, ...]

    def __getitem__(self, index: int) -> dict[str, Any]:
        """读取单个样本并返回 image、mask、sample_id 和路径信息。"""
        sample_id = self.sample_ids[index]
        image_path = self.image_dir / f"{sample_id}.png"
        mask_path = self.mask_dir / f"{sample_id}.png"
        sample: dict[str, Any] = {
            "image": self._load_image(image_path),
            "mask": self._load_mask(mask_path),
            "sample_id": sample_id,
            "image_path": str(image_path),
            "mask_path": str(mask_path),
        }
        if self.transform is not None:
            sample = self.transform(sample)
        if self.return_torch:
            sample["image"] = torch.from_numpy(sample["image"]).float()
            sample["mask"] = torch.from_numpy(sample["mask"]).float()
        return sample
