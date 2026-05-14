"""
训练框架占位模块。

本文件规划后续训练流程所需的配置读取、随机种子、日志目录和 checkpoint
目录。当前阶段不启动正式训练。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sam_octa500.utils.config_utils import load_config
from sam_octa500.utils.seed_utils import set_random_seed


class Trainer:
    """
    训练器占位类。

    参数：
        experiment_config: 实验配置文件路径。
    """

    def __init__(self, experiment_config: str | Path) -> None:
        self.experiment_config_path = Path(experiment_config)
        self.config: dict[str, Any] = load_config(self.experiment_config_path)
        self.experiment_name = str(self.config.get("experiment_name", "debug"))
        self.random_seed = int(self.config.get("random_seed", 2026))
        set_random_seed(self.random_seed)
        self.output_root = Path("experiments") / self.experiment_name
        self.log_dir = self.output_root / "logs"
        self.checkpoint_dir = self.output_root / "checkpoints"

    def prepare_dirs(self) -> None:
        """创建训练日志和 checkpoint 目录。"""
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def fit(self) -> None:
        """训练入口占位；后续接入模型、DataLoader、loss 和优化器。"""
        self.prepare_dirs()
        raise NotImplementedError("训练流程尚未启用，请先完成数据准备和模型选择。")
