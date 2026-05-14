<#
OCTA-500 原始压缩包解压脚本。

输入：
  - 配置文件中的 zip_root；如果该目录不存在或无 zip 文件，则安全回退到 data_root。

输出：
  - raw\Code
  - raw\Label
  - raw\OCTA_3mm
  - raw\OCTA_6mm
  - outputs\logs\unzip_log.txt

安全策略：
  - 不删除、不移动、不修改原始 zip。
  - 使用 7-Zip 的 -aos 参数跳过已存在文件，避免静默覆盖 raw 数据。
  - raw 目录已有内容时记录日志，继续以“跳过已存在文件”的方式补齐解压。
#>

param(
    [string]$Config = "configs\data\octa500_prepare.yaml",
    [string]$Password = ""
)

function Read-SimpleConfig {
    param([string]$Path)
    $dict = @{}
    foreach ($line in Get-Content -LiteralPath $Path -Encoding UTF8) {
        $trimmed = $line.Trim()
        if ($trimmed.Length -eq 0 -or $trimmed.StartsWith("#")) {
            continue
        }
        if ($line.StartsWith(" ") -or -not $trimmed.Contains(":")) {
            continue
        }
        $parts = $trimmed.Split(":", 2)
        $key = $parts[0].Trim()
        $value = $parts[1].Trim()
        if ($value.Length -gt 0) {
            $dict[$key] = $value.Trim('"').Trim("'")
        }
    }
    return $dict
}

function Find-SevenZip {
    $cmd = Get-Command 7z -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }
    $candidates = @(
        "C:\Program Files\7-Zip\7z.exe",
        "C:\Program Files (x86)\7-Zip\7z.exe",
        "C:\Program Files\NVIDIA Corporation\NVIDIA app\7z.exe",
        "C:\Program Files\AMD\CIM\Bin64\7z.exe",
        "C:\Program Files\AMD\CNext\CNext\7z.exe"
    )
    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate) {
            return $candidate
        }
    }
    throw "未找到 7-Zip 可执行文件。"
}

function Get-TargetDir {
    param([string]$ZipName, [string]$RawRoot)
    $lower = $ZipName.ToLower()
    if ($lower -eq "code.zip") {
        return Join-Path $RawRoot "Code"
    }
    if ($lower -eq "label.zip") {
        return Join-Path $RawRoot "Label"
    }
    if ($lower.StartsWith("octa_3mm")) {
        return Join-Path $RawRoot "OCTA_3mm"
    }
    if ($lower.StartsWith("octa_6mm")) {
        return Join-Path $RawRoot "OCTA_6mm"
    }
    return Join-Path $RawRoot "Unknown"
}

$configPath = Resolve-Path -LiteralPath $Config
$cfg = Read-SimpleConfig -Path $configPath
$dataRoot = $cfg["data_root"]
$zipRoot = $cfg["zip_root"]
$rawRoot = $cfg["raw_root"]
$logDir = $cfg["log_dir"]
$logPath = Join-Path $logDir "unzip_log.txt"

New-Item -ItemType Directory -Force -Path $logDir | Out-Null
New-Item -ItemType Directory -Force -Path $rawRoot | Out-Null

$lines = New-Object System.Collections.Generic.List[string]
$lines.Add("脚本: 01_unzip_octa500.ps1")
$lines.Add("运行时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')")
$lines.Add("配置文件: $configPath")
$lines.Add("原始 zip_root: $zipRoot")
if ($Password.Length -gt 0) {
    $lines.Add("密码状态: 已通过命令行参数提供。")
} else {
    $lines.Add("密码状态: 未提供；如果 zip 加密，7-Zip 会返回错误，脚本不会记录密码。")
}

if ((Test-Path -LiteralPath $zipRoot) -and ((Get-ChildItem -LiteralPath $zipRoot -Filter *.zip -File -ErrorAction SilentlyContinue).Count -gt 0)) {
    $actualZipRoot = $zipRoot
    $lines.Add("实际 zip 目录: $actualZipRoot")
} elseif ((Test-Path -LiteralPath $dataRoot) -and ((Get-ChildItem -LiteralPath $dataRoot -Filter *.zip -File -ErrorAction SilentlyContinue).Count -gt 0)) {
    $actualZipRoot = $dataRoot
    $lines.Add("实际 zip 目录: $actualZipRoot")
    $lines.Add("说明: 配置中的 zip_root 不存在或无 zip 文件，本次使用 data_root 下的 zip 文件。")
} else {
    $lines.Add("错误: 未找到 zip 文件。")
    $lines | Set-Content -LiteralPath $logPath -Encoding UTF8
    throw "未找到 OCTA-500 zip 文件。"
}

$sevenZip = Find-SevenZip
$lines.Add("7-Zip: $sevenZip")
$archives = Get-ChildItem -LiteralPath $actualZipRoot -Filter *.zip -File | Sort-Object Name

foreach ($archive in $archives) {
    $targetDir = Get-TargetDir -ZipName $archive.Name -RawRoot $rawRoot
    New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
    $existingCount = (Get-ChildItem -LiteralPath $targetDir -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count
    if ($existingCount -gt 0) {
        $lines.Add("目标目录已有文件，使用 -aos 跳过已存在文件: $targetDir, 已有文件数 $existingCount")
    }
    $lines.Add("开始解压: $($archive.FullName) -> $targetDir")
    $arguments = @("x", $archive.FullName, "-o$targetDir", "-aos", "-y", "-p$Password")
    $process = Start-Process -FilePath $sevenZip -ArgumentList $arguments -Wait -NoNewWindow -PassThru
    $lines.Add("解压完成: $($archive.Name), exit_code=$($process.ExitCode)")
    if ($process.ExitCode -ne 0) {
        $lines.Add("错误: 解压失败 $($archive.Name)")
        $lines | Set-Content -LiteralPath $logPath -Encoding UTF8
        throw "解压失败: $($archive.Name)"
    }
}

$rawCount = (Get-ChildItem -LiteralPath $rawRoot -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count
$lines.Add("raw 文件总数: $rawCount")
$lines.Add("完成。")
$lines | Set-Content -LiteralPath $logPath -Encoding UTF8
Write-Host "解压流程完成，日志: $logPath"


