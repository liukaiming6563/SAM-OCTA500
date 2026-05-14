"""
二值分割评估指标。

输入说明：
    pred 和 target 可以是 NumPy 数组或 PyTorch Tensor。
    支持形状 [H, W]、[1, H, W]、[N, 1, H, W]。
    输入取值可以是 0/1、0/255 或概率值；函数内部使用 threshold 转为二值。
"""

from __future__ import annotations

from typing import Any

import numpy as np


def _to_numpy_binary(x: Any, threshold: float = 0.5) -> np.ndarray:
    """
    将输入转换为 NumPy 二值数组。

    参数：
        x: NumPy 数组或 PyTorch Tensor。
        threshold: 二值化阈值。若最大值大于 1，则先按 255 尺度归一化判断。

    返回：
        bool 数组，True 表示前景。
    """
    if hasattr(x, "detach"):
        x = x.detach().cpu().numpy()
    arr = np.asarray(x)
    if arr.size == 0:
        return arr.astype(bool)
    if arr.max() > 1:
        return arr > 127
    return arr > threshold


def dice_score(pred: Any, target: Any, threshold: float = 0.5, eps: float = 1e-7) -> float:
    """计算 Dice，输入 mask 支持 [H, W] 或批量形状，返回 0 到 1。"""
    p = _to_numpy_binary(pred, threshold)
    t = _to_numpy_binary(target, threshold)
    inter = np.logical_and(p, t).sum()
    denom = p.sum() + t.sum()
    return float((2 * inter + eps) / (denom + eps))


def iou_score(pred: Any, target: Any, threshold: float = 0.5, eps: float = 1e-7) -> float:
    """计算 IoU，输入 mask 支持 0/1、0/255 或概率值。"""
    p = _to_numpy_binary(pred, threshold)
    t = _to_numpy_binary(target, threshold)
    inter = np.logical_and(p, t).sum()
    union = np.logical_or(p, t).sum()
    return float((inter + eps) / (union + eps))


def precision_score(pred: Any, target: Any, threshold: float = 0.5, eps: float = 1e-7) -> float:
    """计算 Precision，表示预测前景中真实前景所占比例。"""
    p = _to_numpy_binary(pred, threshold)
    t = _to_numpy_binary(target, threshold)
    tp = np.logical_and(p, t).sum()
    fp = np.logical_and(p, np.logical_not(t)).sum()
    return float((tp + eps) / (tp + fp + eps))


def recall_score(pred: Any, target: Any, threshold: float = 0.5, eps: float = 1e-7) -> float:
    """计算 Recall，表示真实前景被预测出的比例。"""
    p = _to_numpy_binary(pred, threshold)
    t = _to_numpy_binary(target, threshold)
    tp = np.logical_and(p, t).sum()
    fn = np.logical_and(np.logical_not(p), t).sum()
    return float((tp + eps) / (tp + fn + eps))


def f1_score(pred: Any, target: Any, threshold: float = 0.5, eps: float = 1e-7) -> float:
    """计算 F1；对于二值分割，与 Dice 在定义上等价。"""
    precision = precision_score(pred, target, threshold, eps)
    recall = recall_score(pred, target, threshold, eps)
    return float((2 * precision * recall + eps) / (precision + recall + eps))


def accuracy_score(pred: Any, target: Any, threshold: float = 0.5) -> float:
    """计算像素级 Accuracy，表示前景和背景预测正确的比例。"""
    p = _to_numpy_binary(pred, threshold)
    t = _to_numpy_binary(target, threshold)
    if p.size == 0:
        return 0.0
    return float((p == t).sum() / p.size)


def compute_binary_metrics(pred: Any, target: Any, threshold: float = 0.5) -> dict[str, float]:
    """一次性计算 Dice、IoU、Precision、Recall、F1 和 Accuracy。"""
    return {
        "dice": dice_score(pred, target, threshold),
        "iou": iou_score(pred, target, threshold),
        "precision": precision_score(pred, target, threshold),
        "recall": recall_score(pred, target, threshold),
        "f1": f1_score(pred, target, threshold),
        "accuracy": accuracy_score(pred, target, threshold),
    }
