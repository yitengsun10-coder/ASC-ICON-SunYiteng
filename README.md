# ASC26 ICON 工程优化与 19 模拟日代表性正式子集

- 学生：孙逸腾（240810010427）
- 题目：Group Competition / ICON
- 官方仓库：https://github.com/ASC-Competition/ASC26-icon
- 最终范围：1979-07-01T00:00:00 至 1979-07-20T00:00:00，共 19 模拟日
- 并行配置：32 MPI（30 个计算进程 + 2 个异步 I/O 进程）
- 模型状态：`finish.status=OK`，92520 步，最终模型时间 1979-07-20T00:00:00

这是轻量工程证据仓库，包含构建、输入校验、运行、结果解析、旧 62 天部分运行归档和最终 19 日子集的可复核材料。大型输入和 NetCDF 输出不上传，但其头信息、时间轴、尺寸与 SHA-256 均保留。

## 重要范围声明

本次结果是明确标注的 **19 模拟日代表性正式子集**，不是完整 62 天结果。旧任务只运行到 1656 个 PT1M 步长，保存在 [`partial_1656_steps/`](partial_1656_steps/) 作为排错历史，不能与最终 19 日子集拼接或冒充完整运行。

最终模型正常结束并写完两个 NetCDF；外层 wrapper 返回 1，是因为结束后复制一个未生成的可选 restart 文件失败。仓库保留该退出码并单独解释，不把它改写成 0。

## 一分钟验收

```bash
python tools/verify_evidence.py
python validate_inputs.py --help
python parse_results.py --help
```

三个命令均只依赖 Python 标准库。第一条核对已归档的最终状态、模型时间、NetCDF 维度/时间轴、MPI 数和 wrapper 告警；后两条验证工程工具的终端入口。

## 构建环境

- Ubuntu 22.04
- GCC/GFortran 11.4
- OpenMPI 4.1.2
- NetCDF-C 4.8.1 / NetCDF-Fortran 4.5.4
- CPU 可执行文件约 99,988,616 bytes

环境和构建日志位于 [`environment.log`](environment.log)、[`configure_final.log`](configure_final.log)、[`build_retry.log`](build_retry.log) 和相应 `*_resource.log`。

## 安装和编译

ICON 仓库使用 Git LFS：

```bash
git lfs install
git clone https://github.com/ASC-Competition/ASC26-icon.git
bash install.sh "$PWD/ASC26-icon/icon-model" "$PWD/build-icon-gcc"
```

[`install.sh`](install.sh) 固定 GCC/GFortran 11，安装 MPI、NetCDF/HDF5、eccodes、fyaml 等依赖，并处理 CDI 生成步骤。实际编译输出和失败重试均保留，避免只展示最终成功日志。

## 输入校验

运行前必须提供真实的 R02B04 网格、臭氧、历史温室气体和 restart 文件。禁止用空文件或伪造 NetCDF 绕过：

```bash
python validate_inputs.py /absolute/path/to/normalized_inputs \
  --json reproduced/input_manifest.json
```

校验器检查存在性、非零大小、SHA-256，并在系统存在 `ncdump` 时验证 NetCDF 类型。失败返回码为 2，批处理不会启动 MPI。

## 工程改进与优化

1. [`install.sh`](install.sh)：可重复的依赖、Git LFS、submodule 和 CPU 构建流程。
2. [`validate_inputs.py`](validate_inputs.py)：付费长跑前 fail-fast 输入校验，防止无效 MPI 作业。
3. [`run_all.sh`](run_all.sh)：MPI 数扫描、绑定、逐次日志、墙钟时间和状态采集。
4. [`parse_results.py`](parse_results.py)：把批量 TSV 和日志解析为机器可读 JSON，排除缺少成功标记的运行。
5. 正式子集采用 32 MPI，并使用 ICON 自带的 30 compute + 2 asynchronous I/O 布局，降低同步 I/O 对计算进程的阻塞。

示例批量命令：

```bash
SOURCE_ROOT="$PWD/ASC26-icon" \
BUILD_DIR="$PWD/build-icon-gcc" \
INPUT_ROOT="$PWD/normalized_inputs" \
RESULT_ROOT="$PWD/reproduced" \
MPI_LIST="1 2 4 8 16" \
bash run_all.sh
```

## 正式子集结果

| 指标 | 值 | 证据 |
|---|---:|---|
| 模拟范围 | 19 天 | [`subset_19d_SCOPE.txt`](representative_19d_19790701_19790720/logs/subset_19d_SCOPE.txt) |
| PT1M 步数 | 92520 | [`VALIDATION.txt`](representative_19d_19790701_19790720/validation/VALIDATION.txt) |
| MPI | 32 | 同上 |
| 墙钟时间 | 28:26:43 | [`subset_19d_formal.resource`](representative_19d_19790701_19790720/logs/subset_19d_formal.resource) |
| 平均 CPU | 3191% | 同上 |
| 最大 RSS | 358844 KiB | 同上 |
| 2D/3D NetCDF 时间维 | 各 19 | [`2D header`](representative_19d_19790701_19790720/validation/netcdf_2d_header.txt)、[`3D header`](representative_19d_19790701_19790720/validation/netcdf_3d_header.txt) |
| 最终模型状态 | OK | [`finish.status`](representative_19d_19790701_19790720/config/finish.status) |

主模型日志为 [`ape_from_spinup.run.00031486.log`](representative_19d_19790701_19790720/logs/ape_from_spinup.run.00031486.log)。输入、ICON 二进制和归档文件哈希分别位于 [`INPUT_AND_BINARY_SHA256.txt`](representative_19d_19790701_19790720/config/INPUT_AND_BINARY_SHA256.txt) 与 [`SHA256SUMS.txt`](representative_19d_19790701_19790720/SHA256SUMS.txt)。
