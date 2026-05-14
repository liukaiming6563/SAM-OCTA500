# SAM-OCTA500

## 项目目标

本项目用于构建 OCTA-500 数据集处理与医学图像分割研究工程，将本地原始数据整理为适合 PyTorch、SAM、MedSAM、SAM-OCTA 和 U-Net 使用的标准 image/mask 格式。

## GitHub 同步说明

- 代码、配置文件、脚本和 Markdown 文档保存在本仓库并同步到 GitHub。
- 原始 zip、raw 数据、processed 数据、manifest、日志、检查报告和可视化图片只保存在本地数据目录。
- 本地数据目录：`D:\study\project\Data\DataSet\OCTA500`
- 当前仓库地址：`https://github.com/liukaiming6563/SAM-OCTA500`

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

- 当前转换任务：3M + FAZ，图像类型 FULL。
- split 样本数：
- `train`: 140
- `val`: 10
- `test`: 50
- processed 检查异常样本数：0
- 可视化抽样数：20

## 后续模型开发计划

后续可在 `src/sam_octa500/datasets` 中扩展数据增强，在 `models` 中接入 SAM 或其他分割网络，在 `training`、`inference` 和 `evaluation` 中补充完整实验流程。
