# OCTA-500 运行摘要

## 本次运行时间

2026-05-14 15:15:58

## 已运行脚本

- `01_unzip_octa500.ps1`: 解压原始 zip。
- `02_inspect_octa500.py`: 扫描 raw 目录。
- `03_convert_octa500_2d.py`: 转换 3M + FAZ。
- `04_check_processed_octa500.py`: 检查 processed 数据。
- `05_visualize_processed_octa500.py`: 生成抽样可视化。
- `06_generate_dataset_docs.py`: 更新工程文档。

## 关键输出

- raw manifest：`D:\study\project\Data\DataSet\OCTA500\outputs\manifest\manifest_raw.csv`
- processed manifest：`D:\study\project\Data\DataSet\OCTA500\outputs\manifest\manifest_processed.csv`
- 检查报告：`D:\study\project\Data\DataSet\OCTA500\outputs\reports\processed_check_report.json`
- 可视化目录：`D:\study\project\Data\DataSet\OCTA500\outputs\visualizations\processed_samples\3M_FAZ`

## 当前完成的数据任务

- `3M + FAZ`
- split 样本数：
- `train`: 140
- `val`: 10
- `test`: 50
- 异常样本数：0
- 可视化抽样数：20

## 下一步建议

1. 使用 `OCTA500Dataset` 验证 DataLoader。
2. 扩展 6M 或其他标签任务。
3. 接入 SAM、MedSAM 或 U-Net 训练流程。
