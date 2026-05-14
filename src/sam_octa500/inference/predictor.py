"""
推理框架占位模块。

约定输入为 RGB 图像路径或 Tensor，输出为单通道分割概率图或二值 mask。
当前阶段不加载正式权重。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


class Predictor:
    """
    推理器占位类。

    参数：
        checkpoint_path: 模型权重路径，可为空。
        device: 推理设备名称。
    """

    def __init__(self, checkpoint_path: str | Path | None = None, device: str = "cpu") -> None:
        self.checkpoint_path = Path(checkpoint_path) if checkpoint_path else None
        self.device = device

    def predict(self, image: Any) -> Any:
        """
        单张图像推理入口。

        参数：
            image: RGB 图像路径、NumPy 数组或 Tensor。

        返回：
            后续实现中返回形状 [1, H, W] 或 [H, W] 的 mask。
        """
        raise NotImplementedError("推理流程尚未启用，请先接入正式模型。")
