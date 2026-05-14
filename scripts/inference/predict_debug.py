"""推理流程调试入口。当前只验证 Predictor 接口初始化。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from sam_octa500.inference.predictor import Predictor


def main() -> None:
    """初始化推理器占位对象。"""
    parser = argparse.ArgumentParser(description="初始化推理调试流程")
    parser.add_argument("--checkpoint", default=None, help="可选 checkpoint 路径")
    args = parser.parse_args()
    predictor = Predictor(args.checkpoint)
    print(f"推理器已初始化，device={predictor.device}")


if __name__ == "__main__":
    main()
