# OCTA-500 数据集说明

## 数据集简介

OCTA-500 是面向光学相干断层扫描血管成像的医学图像数据集，本工程将其整理为二维 image/mask 分割格式。

## 3M 和 6M

- `3M`: 3 mm 视场，本配置默认处理该视场。
- `6M`: 6 mm 视场，可通过修改配置中的 `fov` 扩展处理。

## 原始 zip 文件列表

实际 zip 读取目录：`D:\study\project\Data\DataSet\OCTA500`

- `Code.zip`
- `Label.zip`
- `OCTA_3mm_part1.zip`
- `OCTA_3mm_part2.zip`
- `OCTA_3mm_part3.zip`
- `OCTA_6mm_part1.zip`
- `OCTA_6mm_part2.zip`
- `OCTA_6mm_part3.zip`
- `OCTA_6mm_part4.zip`
- `OCTA_6mm_part5.zip`
- `OCTA_6mm_part6.zip`
- `OCTA_6mm_part7.zip`
- `OCTA_6mm_part8.zip`

说明：配置中的 zip_root 不存在或无 zip 文件，实际使用 data_root 下的 zip 文件。

## raw 结构

- raw 根目录：`D:\study\project\Data\DataSet\OCTA500\raw`
- 文件总数：368645
- 后缀分布：
- `.bmp`: 367600
- `.mat`: 1000
- `.py`: 22
- `.pyc`: 21
- `.xlsx`: 2

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

- `gt_artery`: 500
- `gt_capillary`: 500
- `gt_faz`: 1000
- `gt_largevessel`: 500
- `gt_vein`: 500

## 当前已转换任务

- `3M + FAZ`
- processed 目录：`D:\study\project\Data\DataSet\OCTA500\processed\OCTA500_2D\3M\FAZ`
- mask 取值规范：二值任务只允许 `0` 和 `255`。

## train/val/test 划分规则

- `3M`: train 10301-10440，val 10441-10450，test 10451-10500
- `6M`: train 10001-10180，val 10181-10200，test 10201-10300

## 数据检查结果摘要

- 异常样本数：0
- 前景比例均值：0.04005605

## PyTorch Dataset 读取方式

`src/sam_octa500/datasets/octa500_dataset.py` 提供 `OCTA500Dataset`。样本返回 image、mask、sample_id 和路径信息，其中 image 形状为 `[3, H, W]`，mask 形状为 `[1, H, W]`。

## 模型训练建议

建议先使用 `3M + FAZ` 进行调试，确认读取、增强、loss 和指标计算稳定后，再扩展到 6M 或其他标签任务。
