# E6 C：集成验收记录

包内路径提示：下文沿用 Git 仓库中的 `E6/work/...` 和云端 `A-buildchecker/work/...` 原始记录；在本提交包中，C 的同名完整证据目录位于上一级 `../work/...`。本文中的原始路径是来源说明，不是包内相对链接。

状态：集成运行与报告校验通过；正式证据已下载至本地 `E6/work/`。C 的 PR #4 已合入 main；阶段压缩包与包外 SHA256 待完成。

## 版本与构建

| 项目 | 本次实际结果 |
|---|---|
| C 分支 | `e6/c` |
| 实际构建的集成源码提交 | `a8d0fb37c2e8c79f6fc1037c15ba5101383ffcce`（基于 A/B 已合并的 `a9672a6`，包含 C 的 clean 失败测试） |
| 后续 C 文档提交 | `6c9d74002f638aa4a50e7187f3198ca1ceea3012`；该提交晚于镜像构建，不应写作构建源码 SHA |
| A 的 PR | [#2](https://github.com/jkiuiui0058/DevOps-A07/pull/2)，合并提交 `b794358b6c89596f3c12cdc4fa835070879465a8` |
| B 的 PR | [#3](https://github.com/jkiuiui0058/DevOps-A07/pull/3)，合并提交 `a9672a6bdbad959103fc73c9c82a7f31a5996b70` |
| C 的 PR | [#4](https://github.com/jkiuiui0058/DevOps-A07/pull/4)，合并提交 `846d8ccd2d1335d5484c80216da9c8a0ed793b44` |
| 个人镜像标签 | `course1027-buildchecker:241250082` |
| 完整镜像 ID | `sha256:92f77bd045fe08ed5a77b4092d5cf08edc1901cc059142ae0f8f52a778e36ad6` |
| 镜像构建 | 退出 0；云端 `A-buildchecker/work/e6-c-integrated-build-01/build.log`，本地备份 `E6/work/e6-c-integrated-build-01/build.log` |
| 服务测试 | 18 passed；退出 0（云端终端输出已核对，本地 `E6/work/` 未见单独保存的完整测试日志） |

华为云 Docker Hub 镜像代理获取 `docker/dockerfile:1` 时返回 500，Docker Hub 直连超时。正式构建使用云端 `A-buildchecker/work/e6-c-integrated-build-01/Dockerfile`（本地备份于 `E6/work/e6-c-integrated-build-01/Dockerfile`），从原 Dockerfile 仅去掉首行 `# syntax=docker/dockerfile:1`；构建上下文仍为 `A-buildchecker/`。该临时副本及完整构建日志须随证据归档，不能将此轮记作未经变更的原 Dockerfile 直接构建。

## 自动检测、修复与复检

| 项目 | 修复前 | 修复后 |
|---|---|---|
| 云端证据目录 | `A-buildchecker/work/e6-c-integrated-before-01/` | `A-buildchecker/work/e6-c-integrated-after-01/` |
| 本地证据备份 | `E6/work/e6-c-integrated-before-01/` | `E6/work/e6-c-integrated-after-01/` |
| 报告状态 | `SUCCEEDED` | `SUCCEEDED` |
| clean/build 退出码 | 0 / 0 | 0 / 0 |
| runner CLI 退出码 | 1（发现问题） | 0 |
| 发现 | `MISSING(main.o, config.h)`、`REDUNDANT(main.o, unused.h)` | 空数组 |
| trace_id | `e6-17ca9477500f4c96bb4c48d0d7347fd7` | `e6-49f9153f1d9348b2ac14164457b5cef3` |
| Makefile SHA-256 | `fd1dcd76a0bd9678351a1503941a5a875351455d4a6879e76af0af0b6c64772f` | `128069c949b0239e3377f320d51498c2b37a317c602d8755d573a283e1f400ae` |

两份报告中 `config.h`、`main.c`、`unused.h` 的输入 SHA-256 分别相同。对本地备份重跑 `verify_e6_evidence.py` 输出 `passed=true`、修复前 2 条、修复后 0 条、`changed_inputs=["Makefile"]`，退出 0。该脚本校验已保存的报告，不独立复验原始 trace；本地已核对 `trace/t.15:579` 成功打开 `config.h`，以及 `make-db.txt:1053` 声明 `main.o: main.c unused.h`。完整原始 trace、Make 数据库、两张图和进程文件均已在本地证据目录中。

修复前 `MISSING` 证据锚点为 `trace/t.15:579` 与 `trace/t.16:23`；`REDUNDANT` 的声明锚点为 `make-db.txt:1053`。这些行号只对应上述本次 trace_id，不能混用 E5 的行号。

## C 的个人测试

`test_failed_clean_preserves_failed_report` 验证 clean 失败时报告为 `FAILED`、错误码为 `CHECK_FAILED`、保留 `findings.json` 和 clean 日志。测试中 recipe 的 shell 退出 7，GNU Make 自身退出 2，报告记录的是 Make 的退出码。集成镜像中的服务测试共 18 项通过。

A 的贡献提交为 `39f8c32`、`b4dd4ef`，Git 作者为 `ChipmunkYu <3380077139@qq.com>`；B 的贡献提交为 `7f6396e`、`795678e`，Git 作者为 `241250005 <241250005@smail.nju.edu.cn>`。GitHub 上两个 PR 的创建者均显示 `jkiuiui0058`，与贡献提交的作者不同.

## 待完成的交付核对

- [x] 将集成构建日志、临时 Dockerfile、before/after 完整目录下载至 `E6/work/`；本地重新运行报告校验通过。
- [x] 确认本地存在原始 trace、Make 数据库、实际图、声明图、进程文件；核对本次缺失依赖的成功读取与冗余依赖的 Make 声明锚点。
- [x] 记录完整集成源码 SHA、C 文档提交、A/B PR 与 Git 提交作者。
- [x] 核对现有 `work/`：构建日志、before/after 的 runner stdout/stderr、命令与退出码、报告、两图、processes、trace、Make 数据库均已保存。先前终端展示的 18 项 pytest 输出、verify 输出和 Makefile diff 没有单独日志文件；报告已引用其实际结果及现有 JSON，独立日志不是 E6 手册的硬性额外要求。
- [ ] 检查归档包内容，生成包外 SHA256；在独立最终提交说明记录 PR #4、合并提交与归档对应关系，不为追记自身最终提交反复开 PR。
- [ ] 打包前检查证据目录完整性和敏感信息，并生成归档包。
