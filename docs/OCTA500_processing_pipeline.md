# OCTA-500 数据处理流程

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
- 输出：`processed/OCTA500_2D/3M/FAZ` 和 `meta.csv`。
- 当前配置使用 `input_keywords=['octa(full)']`，因为 raw 扫描显示单独使用 `full` 会同时匹配 `OCT(FULL)` 和 `OCTA(FULL)`。

4. 检查 processed：`scripts/data_prepare/04_check_processed_octa500.py`
   - 输入：processed 任务目录。
   - 输出：`manifest_processed.csv`、`processed_check_report.json`、`processed_check_report.md`。

5. 可视化：`scripts/data_prepare/05_visualize_processed_octa500.py`
   - 输入：`manifest_processed.csv`。
   - 输出：`outputs/visualizations/processed_samples/3M_FAZ`。

6. 生成文档：`scripts/data_prepare/06_generate_dataset_docs.py`
   - 输入：manifest、检查报告、抽样列表和日志。
   - 输出：README 和 docs 下的 Markdown 文档。

## 本地保存与仓库同步

- 本地数据目录保存所有数据和运行结果：`D:\study\project\Data\DataSet\OCTA500`
- 仓库同步代码、配置和 Markdown 文档。
- 不提交 zip、图片、CSV、日志、模型权重或中间数据。

## 常见问题

- 如果 zip 不在配置的 `zip_root`，脚本会回退检查 `data_root`，并在日志中记录。
- 如果目标文件已存在且 `allow_overwrite=false`，转换脚本会报错，避免静默覆盖。
- 如果关键词匹配不到 image 或 mask，应先查看 `manifest_raw.csv`，再调整 `input_keywords` 或 `mask_keywords`。
