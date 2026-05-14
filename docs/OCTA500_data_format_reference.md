# OCTA-500 数据格式参考

## 原始数据格式摘要

- 文件总数：368645
- 后缀分布：
- `.bmp`: 367600
- `.mat`: 1000
- `.py`: 22
- `.pyc`: 21
- `.xlsx`: 2

## processed 数据格式摘要

当前任务目录：`D:\study\project\Data\DataSet\OCTA500\processed\OCTA500_2D\3M\FAZ`

```text
3M\FAZ
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

- `3M`: train 10301-10440，val 10441-10450，test 10451-10500
- `6M`: train 10001-10180，val 10181-10200，test 10201-10300

## mask 像素值规范

二值分割 mask 使用单通道 PNG，背景为 `0`，前景为 `255`。

## 当前 3M + FAZ 示例

- 当前转换任务：3M + FAZ
- split 样本数：
- `train`: 140
- `val`: 10
- `test`: 50

## 扩展方式

继续转换 6M 或 LargeVessel、Capillary、Artery、Vein 时，修改 `configs/data/octa500_prepare.yaml` 中的 `fov`、`task`、`image_type`、`input_keywords` 和 `mask_keywords`，然后重新运行转换、检查、可视化和文档脚本。
