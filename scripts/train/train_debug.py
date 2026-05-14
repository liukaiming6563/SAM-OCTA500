"""训练流程调试入口。当前只验证训练器初始化，不启动正式训练。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from sam_octa500.training.trainer import Trainer


def main() -> None:
    """读取实验配置并初始化训练器。"""
    parser = argparse.ArgumentParser(description="初始化训练调试流程")
    parser.add_argument("--config", default="configs/experiment/exp_debug.yaml", help="实验配置路径")
    args = parser.parse_args()
    trainer = Trainer(args.config)
    trainer.prepare_dirs()
    print(f"训练调试目录已准备: {trainer.output_root}")


if __name__ == "__main__":
    main()
