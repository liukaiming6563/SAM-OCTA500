"""
分割模型占位模块。

本文件只提供后续模型接入的接口形状，不实现正式 SAM 结构。后续可在保持
forward(image) 输入输出约定的基础上替换为 SAM、MedSAM、SAM-OCTA 或 U-Net。
"""

from __future__ import annotations

try:
    import torch
    from torch import nn
except Exception:
    torch = None  # type: ignore
    nn = None  # type: ignore


if nn is not None:

    class PlaceholderSegmentationModel(nn.Module):
        """
        极简分割占位模型。

        输入：
            image: Tensor，形状 [N, 3, H, W]。

        输出：
            logits: Tensor，形状 [N, 1, H, W]。
        """

        def __init__(self, input_channels: int = 3, num_classes: int = 1) -> None:
            super().__init__()
            self.net = nn.Conv2d(input_channels, num_classes, kernel_size=1)

        def forward(self, image):  # type: ignore[no-untyped-def]
            """执行前向传播。"""
            return self.net(image)

else:

    class PlaceholderSegmentationModel:
        """未安装 PyTorch 时的接口占位类。"""

        def __init__(self, input_channels: int = 3, num_classes: int = 1) -> None:
            self.input_channels = input_channels
            self.num_classes = num_classes

        def __call__(self, image):  # type: ignore[no-untyped-def]
            raise RuntimeError("当前环境未安装 PyTorch，无法执行模型前向传播。")
