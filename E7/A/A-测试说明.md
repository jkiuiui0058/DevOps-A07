# A01 测试说明

> 当前状态：A01 正式源码已提交，A02/A03 云端完整验证与回传已完成。
> A04 报告及证据已提交推送，个人 [PR #7](https://github.com/jkiuiui0058/DevOps-A07/pull/7)
> 已由 `ChipmunkYu` 创建，待 C 审阅与集成合并，不等于已合并。
> 下文早期 Windows ERROR、诊断与 PENDING 为历史过程；最终结果见文末及
> `A-云端证据索引.md`，不将历史失败改写成通过。

## 目的与覆盖缺口

验证两个独立 recipe jobs 写同一 target 时，`execution_graph` 必须抛出
`Unsupported`，不能合并依赖、覆盖前一个 job 或猜测归属。
已阅读 `fullcheck.py`、服务现有测试及 E7 gate 判定测试：
`test_e6_a` 是两个 jobs 写不同 targets；`test_fullcheck` 的多输出测试是
一个 job 写两个 outputs；现有测试均未覆盖此次边界。
实现已有同 target 拒绝分支，本次不修改实现或公共脚本。

## 输入与预期

新增且仅新增一个 unittest 测试：
`TestE7A.test_two_recipe_jobs_writing_same_target_fail_instead_of_merging`。
合成 trace 中 Make PID 10 直接创建独立 jobs 11、21；分别读取 `a.c`、`b.c`，
每个 job 均只有一个最终输出，且都写 `shared.o`。
调用 `execution_graph(folder, "/course/project")`，预期异常类型为 `Unsupported`，
消息精确匹配 `Multiple jobs write the same target: shared.o`。
如果静默合并、覆盖或误入单 job 多输出拒绝分支，测试必须失败。

## 历史阶段一：本地执行与实际结果（2026-11-13，源码提交前）

环境：Windows，Python 3.11.9；子进程设置 `PYTHONPATH=.`、
`PYTHONDONTWRITEBYTECODE=1`，不安装依赖、不生成仓库内字节码。
通过 Python `subprocess.run` 分别运行并独立记录退出码；日志保存完整 stdout、
stderr、工作目录、命令及 Python 版本，不以日志采集脚本自身退出码代替测试退出码。

前三项工作目录为 `A-buildchecker/services/buildchecker`：

| 命令 | 实际结果 | 退出码 | 原始日志 |
| --- | --- | --- | --- |
| `python -m unittest discover -s tests -p test_e7_a.py -v` | 1 项通过；确认拒绝同 target 的独立 jobs | 0 | `01-new-test.log` |
| `python -m unittest discover -s tests -p test_fullcheck.py -v` | 13 项运行，12 项通过、1 项 ERROR；不是全通过 | 1 | `02-fullcheck-regression.log` |
| `python -m unittest discover -s tests -p test_e6_a.py -v` | 1 项通过 | 0 | `03-e6-a-regression.log` |

独立判定测试工作目录为 `A-buildchecker`：

| 命令 | 实际结果 | 退出码 | 原始日志 |
| --- | --- | --- | --- |
| `python -m unittest discover -s tests/e7 -v` | 6 项通过；仅判定逻辑，不代表完整 gate 成功 | 0 | `04-e7-independent.log` |

相邻 fullcheck 回归中的 `test_failed_clean_preserves_failed_report` 在 Windows
调用 `full_check` 时触发已有 Linux 平台限制：
`ValueError: Full collection requires Linux; offline analyze is portable`。
当时保留该真实 ERROR，未跳过、未改动既有测试或实现；当时 Linux 复验待执行，
随后已在正式 Linux 服务回归中通过，见最终结果。

## 历史阶段一/二：证据边界与当时阻碍（源码提交前）

所有 PID 和 syscall 均为人工合成，仅验证离线分析边界，**不等于真实构建证据**。
前次本地执行时 Docker 不可用；本次云端只读诊断已确认远程 Docker 可用，
但尚未构建或运行测试：镜像验证 **PENDING**；镜像内测试及完整 gate **PENDING**。
未引用 B 方证据充作 A 方结果，未安装依赖，未修改 Git 配置，未 commit/push。

## 历史阶段二：A02/A03 云端诊断与授权等待（2026-11-13，07:42 UTC 起）

2026-11-13 的只读诊断见 `05-cloud-diagnostic.log`（连接与认证信息未写入报告）。
远程 Docker client/server 29.1.3 可用，活动容器为 0；2 CPU、约 1.7 GiB 内存、
约 69 GiB 空闲磁盘，诊断时负载低。个人目录可写。
远程个人克隆仍为旧 `main`，SHA 为
`a2d9d3a2a4b2af062a11d1cc5406510ab3c5b8b8`，存在未跟踪 `E4/`，
且缺少根下 `A-buildchecker/`。未更新、切换、清理或覆盖该克隆。

本地 `e7-a` HEAD 基线为 `d18ef00e758c8a36f2cd3c5f8054f4f088378c11`，
新增 `test_e7_a.py` 尚未提交，其 SHA256 为
`8bc8301b76a902bd315617d48fe4e7567bed14f1cfc1fb3e10811bb4ac518eb4`。
该 HEAD **不包含 A01 测试**，不得当作已提交的 A01 源码版本。

结论：远程具备开展运行的初步条件，但应在个人目录另建唯一时间戳目录，
使用独立源码副本、个人唯一镜像标签和全新证据目录，不能直接使用旧克隆。
本轮按要求停在诊断阶段，未上传源码、未构建未提交版本、未启动容器。
正式证据是否必须对应包含 A01 的已提交 SHA，以及是否授权本地提交，等待确认；
commit/push/PR 均未获授权，均未执行。
Linux 测试、镜像构建、完整八项 gate、内容一致性核对、原始证据回传和备份 SHA256
均仍为 **PENDING**，不以本次环境诊断替代这些结果。

## A01/A02/A03 最终运行结果（2026-11-13）

用户授权提交后，仅 stage 并提交新增测试，正式源码提交为
`e779b3130cd9b91eba4c6e54f4a6a85f5606b99c`。
身份核对：Git 用户名与 GitHub 当前登录均为 `ChipmunkYu`；未更改配置。
源码提交未包含 `E7/A/` 的诊断或 PENDING 说明；运行阶段当时未 push、未创建 PR。

以该已提交 HEAD 的 `git archive` 在个人全新时间戳目录解包，
不伪装 Git 工作树，不接触旧克隆；归档检查未含个人笔记、`.git`、`.ssh`、
真实 `.env`、PEM 或 KEY 文件。Dockerfile 与 gate 脚本不依赖 Git 工作树，
直接构建及调用原脚本，没有修改 Dockerfile、实现或公共脚本。

云端构建、新增测试（1 项）、全部服务测试（21 项）、独立判定（6 项）及
完整 gate 均退出 0。Linux 已实际运行并通过先前 Windows 受限的 fullcheck 测试。
完整 gate 的 8 项均符合预期：三个 original 的 CLI 退出 1 是检出问题后的正确门禁结果；
fixed 退出 0；build-failed、unsupported、timeout 分别正确拒绝。
真实 gate 的 unsupported 是单 job 多输出，与 A01 的合成同 target 冲突测试互补，
不能声称它是 A01 场景的真实构建复现。

原始 fixture 运行前后 hash 相同；三次 original 的全部输入 hash 相同；
fixed 仅 Makefile 变化，精确替换 `unused.h` 为 `config.h`，无发现；
该替换为按行文本比较，公共脚本同时将 Makefile 的 CRLF 归一为 LF，未改其他文件。
MD/RD 精确边及各自 trace/声明锚点已逐行核对；JSON/CSV 8 行一致。
原始证据已回传仓库外并完成包及 259 个文件的 SHA256 核验，详细位置与引用见索引。
该阶段验证与回传无未解决阻碍；当时按用户要求将 push/PR 留到报告整合后，现已完成个人 PR 交付。

## A04 可交付归档（2026-11-13，真实运行之后）

报告、个人记录、对齐 B 列的验收 CSV 及同一原始证据包已放入 `E7/A/`。
原包经递归扫描与逐文件校验通过，可由 C 通过仓库相对路径获取；详见
`A-云端证据索引.md` 与 `A-本地验证报告.md`。最终授权后已提交推送并创建
[PR #7](https://github.com/jkiuiui0058/DevOps-A07/pull/7)，作者账号 `ChipmunkYu`。
A04 提交与 PR 交付完成，待 C 审阅和最终集成验收；未自动合并，不能说成已合并。
