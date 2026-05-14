"""评估指标调试入口。"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from sam_octa500.evaluation.metrics import compute_binary_metrics


def main() -> None:
    """使用一个小型二值数组验证指标函数。"""
    target = np.array([[1, 1, 0], [0, 1, 0]], dtype=np.uint8)
    pred = np.array([[1, 0, 0], [0, 1, 1]], dtype=np.uint8)
    metrics = compute_binary_metrics(pred, target)
    print(metrics)


if __name__ == "__main__":
    main()
