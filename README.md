# ASC26 ICON 代表性正式子集证据

本目录保存 ICON `ape_from_spinup` 的部署、输入校验、编译、旧 62 天部分运行归档，以及最终 19 模拟日代表性正式子集的可复核证据。

## 正式代表性子集

- 时段：1979-07-01T00:00:00 至 1979-07-20T00:00:00（19 模拟日）
- MPI：32 进程，其中 30 个计算进程、2 个异步 I/O 进程
- 步数：92520，PT1M
- 墙钟时间：28:26:43
- 平均 CPU：3191%
- 最大 RSS：358844 KiB
- 模型状态：`finish.status=OK`
- 输出：2D 与 3D 两个 netCDF-4 文件均可读，`time=19`，逐日记录覆盖 1979-07-02 至 1979-07-20

外层运行脚本的最终退出码为 1，原因是模型已经正常结束并写完 NetCDF 后，脚本仍尝试复制未生成的可选 restart `ape_from_spinup_restart_atm_19790720T000000Z.nc`。本提交不把 wrapper 的 exit=1 隐藏或改写为 0；模型完成证据与后处理告警分别记录。

## 证据目录

`representative_19d_19790701_19790720/` 包含主日志、运行脚本、namelist、模型状态、资源统计、NetCDF 头信息与时间轴、输入/二进制 SHA256 和服务器归档清单。大型 NetCDF 原文件未复制进轻量提交包，但服务器归档曾以硬链接保留并生成完整哈希。

旧 62 天任务只作为 `superseded_full62d_partial` 的部分运行证据引用，未声称完整覆盖 62 天。

## 关键输入真实性

网格、臭氧、温室气体、restart attributes/patch 与 ICON 二进制的 SHA256 见 `representative_19d_19790701_19790720/config/INPUT_AND_BINARY_SHA256.txt`。所有 NetCDF 均经过 `ncdump` 可读性检查，不以空文件或伪造数据替代。
