"""
数据说明文档生成工具。

本文件从本地数据目录中的 manifest、检查报告、可视化抽样列表和日志中提取
摘要，生成适合提交到代码仓库的 Markdown 文档。文档只包含结构、规则和统计
摘要，不包含原始数据或大量样本级路径。
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from sam_octa500.utils.config_utils import save_json
from sam_octa500.utils.file_utils import read_csv
from sam_octa500.utils.path_utils import as_path, processed_task_dir, resolve_zip_root


def _load_json(path: Path) -> dict[str, Any]:
    """读取 JSON 文件；不存在时返回空字典。"""
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _count_meta(meta_path: Path) -> dict[str, int]:
    """统计 meta.csv 中各 split 样本数。"""
    if not meta_path.exists():
        return {}
    counts = {"train": 0, "val": 0, "test": 0}
    for row in read_csv(meta_path):
        split = row.get("split", "")
        if split in counts:
            counts[split] += 1
    return counts


def _zip_list(zip_dir: Path) -> list[str]:
    """列出 zip 文件名。"""
    return [p.name for p in sorted(zip_dir.glob("*.zip"))]


def generate_documents(config: dict[str, Any]) -> dict[str, Any]:
    """
    生成 README 和 docs 文档。

    参数：
        config: 数据准备配置。

    返回：
        run_summary 字典，同时写入 outputs/reports/run_summary.json。
    """
    project_root = as_path(config, "project_root")
    report_dir = as_path(config, "report_dir")
    docs_dir = project_root / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    zip_dir, zip_note = resolve_zip_root(config)
    raw_report = _load_json(report_dir / "raw_structure_report.json")
    check_report = _load_json(report_dir / "processed_check_report.json")
    task_dir = processed_task_dir(config)
    meta_path = task_dir / "meta.csv"
    split_counts = _count_meta(meta_path)
    selected_path = as_path(config, "visualization_dir") / "processed_samples" / f"{config['fov']}_{config['task']}" / "selected_samples.csv"
    selected_count = len(read_csv(selected_path)) if selected_path.exists() else 0
    run_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    run_summary = {
        "run_time": run_time,
        "github_repo": config.get("github_repo", ""),
        "zip_directory_used": str(zip_dir),
        "zip_directory_note": zip_note,
        "raw_file_count": raw_report.get("file_count", 0),
        "raw_sample_ranges": raw_report.get("sample_id_ranges", {}),
        "processed_task": f"{config['fov']} + {config['task']}",
        "processed_task_dir": str(task_dir),
        "split_counts": split_counts,
        "anomaly_count": check_report.get("anomaly_count", 0),
        "visualization_sample_count": selected_count,
        "local_outputs": {
            "manifest_raw": str(as_path(config, "manifest_dir") / "manifest_raw.csv"),
            "manifest_processed": str(as_path(config, "manifest_dir") / "manifest_processed.csv"),
            "processed_check_report": str(report_dir / "processed_check_report.json"),
            "visualizations": str(selected_path.parent),
        },
    }
    save_json(run_summary, report_dir / "run_summary.json")

    zip_lines = "\n".join(f"- `{name}`" for name in _zip_list(zip_dir))
    split_lines = "\n".join(
        f"- `{fov}`: train {rules['train']}，val {rules['val']}，test {rules['test']}"
        for fov, rules in config["split_rules"].items()
    )
    count_lines = "\n".join(f"- `{k}`: {v}" for k, v in split_counts.items())
    suffix_lines = "\n".join(f"- `{k}`: {v}" for k, v in raw_report.get("suffix_counts", {}).items())
    label_lines = "\n".join(f"- `{k}`: {v}" for k, v in raw_report.get("label_type_distribution", {}).items())

    readme = f"""# SAM-OCTA500

## 项目目标

本项目用于构建 OCTA-500 数据集处理与医学图像分割研究工程，将本地原始数据整理为适合 PyTorch、SAM、MedSAM、SAM-OCTA 和 U-Net 使用的标准 image/mask 格式。

## GitHub 同步说明

- 代码、配置文件、脚本和 Markdown 文档保存在本仓库并同步到 GitHub。
- 原始 zip、raw 数据、processed 数据、manifest、日志、检查报告和可视化图片只保存在本地数据目录。
- 本地数据目录：`{config['data_root']}`
- 当前仓库地址：`{config['github_repo']}`

## 工程目录结构

- `configs/`: 数据、模型和实验配置。
- `scripts/data_prepare/`: OCTA-500 解压、扫描、转换、检查、可视化和文档生成脚本。
- `src/sam_octa500/`: 可复用数据处理、Dataset、模型占位、训练、推理和评估模块。
- `docs/`: 数据结构、处理流程、格式和运行摘要文档。
- `experiments/debug/`: 调试实验说明。

## 本地数据目录结构

- `raw/`: 解压后的只读原始数据。
- `processed/OCTA500_2D/`: 转换后的 image/mask 数据。
- `outputs/manifest/`: 本地 manifest。
- `outputs/logs/`: 本地运行日志。
- `outputs/reports/`: 本地检查报告。
- `outputs/visualizations/`: 本地抽样可视化图。

## 环境安装

```bash
pip install -r requirements.txt
```

## 数据处理流程

```powershell
powershell -ExecutionPolicy Bypass -File scripts/data_prepare/01_unzip_octa500.ps1 -Config configs/data/octa500_prepare.yaml
python scripts/data_prepare/02_inspect_octa500.py --config configs/data/octa500_prepare.yaml
python scripts/data_prepare/03_convert_octa500_2d.py --config configs/data/octa500_prepare.yaml
python scripts/data_prepare/04_check_processed_octa500.py --config configs/data/octa500_prepare.yaml
python scripts/data_prepare/05_visualize_processed_octa500.py --config configs/data/octa500_prepare.yaml
python scripts/data_prepare/06_generate_dataset_docs.py --config configs/data/octa500_prepare.yaml
```

## 已完成任务

- 当前转换任务：{config['fov']} + {config['task']}，图像类型 {config['image_type']}。
- split 样本数：
{count_lines if count_lines else '- 尚未生成 meta.csv'}
- processed 检查异常样本数：{run_summary['anomaly_count']}
- 可视化抽样数：{selected_count}

## 后续模型开发计划

后续可在 `src/sam_octa500/datasets` 中扩展数据增强，在 `models` 中接入 SAM 或其他分割网络，在 `training`、`inference` 和 `evaluation` 中补充完整实验流程。
"""
    (project_root / "README.md").write_text(readme, encoding="utf-8")

    dataset_doc = f"""# OCTA-500 数据集说明

## 数据集简介

OCTA-500 是面向光学相干断层扫描血管成像的医学图像数据集，本工程将其整理为二维 image/mask 分割格式。

## 3M 和 6M

- `3M`: 3 mm 视场，本配置默认处理该视场。
- `6M`: 6 mm 视场，可通过修改配置中的 `fov` 扩展处理。

## 原始 zip 文件列表

实际 zip 读取目录：`{zip_dir}`

{zip_lines if zip_lines else '- 未找到 zip 文件'}

说明：{zip_note}

## raw 结构

- raw 根目录：`{config['raw_root']}`
- 文件总数：{raw_report.get('file_count', 0)}
- 后缀分布：
{suffix_lines if suffix_lines else '- 尚无扫描结果'}

## 图像和标签含义

- `OCTA(FULL)`: 全层 OCTA 投影图。
- `OCTA(ILM_OPL)`: ILM 到 OPL 层范围的 OCTA 投影图。
- `OCTA(OPL_BM)`: OPL 到 BM 层范围的 OCTA 投影图。
- `GT_FAZ`: 黄斑中心凹无血管区标签。
- `GT_LargeVessel`: 大血管标签。
- `GT_Capillary`: 毛细血管标签。
- `GT_Artery`: 动脉标签。
- `GT_Vein`: 静脉标签。

## 标签分布

{label_lines if label_lines else '- 尚未在路径中识别到标准标签关键词'}

## 当前已转换任务

- `{config['fov']} + {config['task']}`
- processed 目录：`{task_dir}`
- mask 取值规范：二值任务只允许 `0` 和 `255`。

## train/val/test 划分规则

{split_lines}

## 数据检查结果摘要

- 异常样本数：{run_summary['anomaly_count']}
- 前景比例均值：{check_report.get('foreground_ratio', {}).get('mean', 0):.8f}

## PyTorch Dataset 读取方式

`src/sam_octa500/datasets/octa500_dataset.py` 提供 `OCTA500Dataset`。样本返回 image、mask、sample_id 和路径信息，其中 image 形状为 `[3, H, W]`，mask 形状为 `[1, H, W]`。

## 模型训练建议

建议先使用 `{config['fov']} + {config['task']}` 进行调试，确认读取、增强、loss 和指标计算稳定后，再扩展到 6M 或其他标签任务。
"""
    (docs_dir / "OCTA500_dataset_description.md").write_text(dataset_doc, encoding="utf-8")

    pipeline_doc = f"""# OCTA-500 数据处理流程

## 完整流程

1. 解压：`scripts/data_prepare/01_unzip_octa500.ps1`
   - 输入：原始 zip。
   - 输出：`raw/Code`、`raw/Label`、`raw/OCTA_3mm`、`raw/OCTA_6mm`。
   - 检查：查看 `outputs/logs/unzip_log.txt`。

2. 扫描 raw：`scripts/data_prepare/02_inspect_octa500.py`
   - 输入：`raw/`。
   - 输出：`outputs/manifest/manifest_raw.csv`、`outputs/reports/raw_structure_report.json`。
   - 同步文档：`docs/OCTA500_structure_summary.md`。

3. 转换 2D：`scripts/data_prepare/03_convert_octa500_2d.py`
- 输入：`manifest_raw.csv`。
- 输出：`processed/OCTA500_2D/{config['fov']}/{config['task']}` 和 `meta.csv`。
- 当前配置使用 `input_keywords={config['input_keywords']}`，因为 raw 扫描显示单独使用 `full` 会同时匹配 `OCT(FULL)` 和 `OCTA(FULL)`。

4. 检查 processed：`scripts/data_prepare/04_check_processed_octa500.py`
   - 输入：processed 任务目录。
   - 输出：`manifest_processed.csv`、`processed_check_report.json`、`processed_check_report.md`。

5. 可视化：`scripts/data_prepare/05_visualize_processed_octa500.py`
   - 输入：`manifest_processed.csv`。
   - 输出：`outputs/visualizations/processed_samples/{config['fov']}_{config['task']}`。

6. 生成文档：`scripts/data_prepare/06_generate_dataset_docs.py`
   - 输入：manifest、检查报告、抽样列表和日志。
   - 输出：README 和 docs 下的 Markdown 文档。

## 本地保存与仓库同步

- 本地数据目录保存所有数据和运行结果：`{config['data_root']}`
- 仓库同步代码、配置和 Markdown 文档。
- 不提交 zip、图片、CSV、日志、模型权重或中间数据。

## 常见问题

- 如果 zip 不在配置的 `zip_root`，脚本会回退检查 `data_root`，并在日志中记录。
- 如果目标文件已存在且 `allow_overwrite=false`，转换脚本会报错，避免静默覆盖。
- 如果关键词匹配不到 image 或 mask，应先查看 `manifest_raw.csv`，再调整 `input_keywords` 或 `mask_keywords`。
"""
    (docs_dir / "OCTA500_processing_pipeline.md").write_text(pipeline_doc, encoding="utf-8")

    format_doc = f"""# OCTA-500 数据格式参考

## 原始数据格式摘要

- 文件总数：{raw_report.get('file_count', 0)}
- 后缀分布：
{suffix_lines if suffix_lines else '- 尚无扫描结果'}

## processed 数据格式摘要

当前任务目录：`{task_dir}`

```text
{config['fov']}\\{config['task']}
├── train
│   ├── images
│   └── masks
├── val
│   ├── images
│   └── masks
├── test
│   ├── images
│   └── masks
└── meta.csv
```

## 命名规则

- image：`sample_id.png`
- mask：`sample_id.png`
- `sample_id` 为五位数字编号。

## split 规则

{split_lines}

## mask 像素值规范

二值分割 mask 使用单通道 PNG，背景为 `0`，前景为 `255`。

## 当前 3M + FAZ 示例

- 当前转换任务：{config['fov']} + {config['task']}
- split 样本数：
{count_lines if count_lines else '- 尚未生成'}

## 扩展方式

继续转换 6M 或 LargeVessel、Capillary、Artery、Vein 时，修改 `configs/data/octa500_prepare.yaml` 中的 `fov`、`task`、`image_type`、`input_keywords` 和 `mask_keywords`，然后重新运行转换、检查、可视化和文档脚本。
"""
    (docs_dir / "OCTA500_data_format_reference.md").write_text(format_doc, encoding="utf-8")

    run_doc = f"""# OCTA-500 运行摘要

## 本次运行时间

{run_time}

## 已运行脚本

- `01_unzip_octa500.ps1`: 解压原始 zip。
- `02_inspect_octa500.py`: 扫描 raw 目录。
- `03_convert_octa500_2d.py`: 转换 {config['fov']} + {config['task']}。
- `04_check_processed_octa500.py`: 检查 processed 数据。
- `05_visualize_processed_octa500.py`: 生成抽样可视化。
- `06_generate_dataset_docs.py`: 更新工程文档。

## 关键输出

- raw manifest：`{run_summary['local_outputs']['manifest_raw']}`
- processed manifest：`{run_summary['local_outputs']['manifest_processed']}`
- 检查报告：`{run_summary['local_outputs']['processed_check_report']}`
- 可视化目录：`{run_summary['local_outputs']['visualizations']}`

## 当前完成的数据任务

- `{config['fov']} + {config['task']}`
- split 样本数：
{count_lines if count_lines else '- 尚未生成'}
- 异常样本数：{run_summary['anomaly_count']}
- 可视化抽样数：{selected_count}

## 下一步建议

1. 使用 `OCTA500Dataset` 验证 DataLoader。
2. 扩展 6M 或其他标签任务。
3. 接入 SAM、MedSAM 或 U-Net 训练流程。
"""
    (docs_dir / "OCTA500_run_summary.md").write_text(run_doc, encoding="utf-8")
    return run_summary
