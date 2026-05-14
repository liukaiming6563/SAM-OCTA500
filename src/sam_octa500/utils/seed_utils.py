"""
随机种子工具。

数据抽样和后续训练应固定随机种子，保证转换、检查和可视化结果可复现。
"""

from __future__ import annotations

import os
import random

import numpy as np


def set_random_seed(seed: int) -> None:
    """
    设置 Python、NumPy 和可选 PyTorch 随机种子。

    参数：
        seed: 随机种子整数。
    """
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    try:
        import torch

        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    except Exception:
        pass
