# E7 A 本地与云端验证报告（供 C 整合）

## 1. 结论、版本与职责边界

2026-11-13 已完成 A01 测试、A02/A03 真实云端验证与证据回传，A04 报告与可交付包已整理。
**个人提交、推送与 PR 交付已完成，PR 待 C 审阅及集成合并，不等于已合并**。
PR：[#7](https://github.com/jkiuiui0058/DevOps-A07/pull/7)，作者账号 `ChipmunkYu`，
方向为 `e7-a → main`。创建前基线为 `d18ef00e758c8a36f2cd3c5f8054f4f088378c11`。
A 不负责 CI：本报告没有 A 的 CI run ID，不借用 B 的 CI 结果证明 A 运行通过。

| 项目 | 本次实际值 |
| --- | --- |
| 已提交源码 SHA | `e779b3130cd9b91eba4c6e54f4a6a85f5606b99c` |
| 源码提交内容 | 仅新增 `A-buildchecker/services/buildchecker/tests/test_e7_a.py`，33 行 |
| 运行源码 | 对上述 HEAD 执行 `git archive`，在个人全新目录解包；不是 Git 工作树 |
| 源码归档 SHA256 | `719b430cdf927dbe5258a245c82d2fab2cdb07a196575359eb7643d4dd5e2489` |
| 镜像标签 | `e7-buildchecker:241098114-e7-20261113t075315z` |
| 镜像 ID | `sha256:9cf27a2cd2c894be2d913717aed1e441a06013ea49e4a04c2fe87db4c3c8ab03` |
| 检测器版本 | `0.2.0-teaching` |
| 独立新增测试 / 全部服务 / 独立判定 | 1 / **21** / **6** 项通过，命令均退出 0 |
| 完整 gate | 8 项符合预期，驱动脚本退出 0 |

`full_check` 生成 trace_id 时固定使用 `e6-` 前缀，这是实现约定，不表示使用 E6 旧证据。
本报告由本次源码 SHA、镜像 ID、归档哈希及各自 trace_id 共同标识 E7 运行。

## 2. A01：新增测试的目的、输入、预期与实际

目的：锁定两个独立 recipe jobs 写同一 target 的归属歧义，必须显式拒绝，不能合并或覆盖。
`TestE7A.test_two_recipe_jobs_writing_same_target_fail_instead_of_merging` 构造三个临时合成 trace：
Make PID 10 分别 fork jobs 11、21，各读取 `a.c`、`b.c`，均成功写 `shared.o`。
每个 job 只有一个最终输出，故不会误用“单 job 多输出”分支满足测试。

预期调用 `execution_graph(folder, "/course/project")` 抛出 `Unsupported`，
消息精确匹配 `Multiple jobs write the same target: shared.o`。
本地 Windows 和本次 Linux 镜像中均 1 项通过、退出 0。
证据为包内 `evidence/a01/{command.json,stderr.log,exit.json}`。

非重复价值：已有 `test_e6_a` 验证两 jobs 写不同 targets 的隔离；
已有 `test_fullcheck` 的多输出测试验证一 job 写多个 outputs。
本测试专门覆盖已有实现中跨 job 的同 target 冲突保护，未新增检测算法或修改实现。
该输入为人工合成 syscall，只证明分析边界，不冒充真实构建证据。

## 3. A02：三次 original 的输入与精确结果

以下证据路径均相对交付包根目录；每次的独立目录为
`evidence/gate/original-N/`。原 fixture 运行前后哈希完全相同。

三次 `findings.json.input_sha256` 均逐项等于下表，未只比较文件名或 findings 数量：

| 文件 | original-1 SHA256 | original-2 / original-3 |
| --- | --- | --- |
| Makefile | `e02e8fa1beab535fa4e7d3d29d7f010f05d1c1c620d8c51f598b372ad3271aaf` | 两次均与左列完全相同 |
| config.h | `3e0a94208536b4647200d58d19ade2b8acd6cd8f7cb331533d74a0e4c16a4b10` | 两次均与左列完全相同 |
| main.c | `ffe2599619c674acdc5b33ee6735c20bfb4fc64783112be1637f23e42b672df4` | 两次均与左列完全相同 |
| unused.h | `dba8b0a5b7a490e05e30f0ddaf9c579a9d1b88f1383cf8305ed27f2d042119ec` | 两次均与左列完全相同 |

| case | 独立 trace_id | 精确 findings 集合 | clean/build/CLI |
| --- | --- | --- | --- |
| original-1 | `e6-ebd613ef134c43e0b0501ab0bf07bed5` | `{MISSING(main.o,config.h), REDUNDANT(main.o,unused.h)}` | 0 / 0 / 1 |
| original-2 | `e6-f91147972ad148a298e2aa4e506113f1` | 同一精确集合，恰好 2 项 | 0 / 0 / 1 |
| original-3 | `e6-76b7296adf884097ab9b3cbc1e053b48` | 同一精确集合，恰好 2 项 | 0 / 0 / 1 |

每次均具有下列逐行核对的锚点；路径相对各自 `original-N/evidence/`：

| case | MD 读输入 | MD 写输出 | RD Make 声明 |
| --- | --- | --- | --- |
| original-1 | `trace/t.14:579`，PID 14 | `trace/t.15:23`，PID 15 | `make-db.txt:1053` |
| original-2 | `trace/t.14:579`，PID 14 | `trace/t.15:23`，PID 15 | `make-db.txt:1053` |
| original-3 | `trace/t.14:579`，PID 14 | `trace/t.15:23`，PID 15 | `make-db.txt:1053` |

原始行分别是：
```text
openat(AT_FDCWD, "config.h", O_RDONLY|O_NOCTTY) = 4
openat(AT_FDCWD, "main.o", O_RDWR|O_CREAT|O_TRUNC, 0666) = 3
main.o: main.c unused.h
```

三次容器的 PID 数字相同，不代表同一次采集：目录和 trace_id 各自独立。
完整锚点结构见 `E7/A/07-trace-anchors.json` 及包内 `evidence/trace-anchors.json`。

## 4. fixed：仅修改声明后通过

`fixed` 的 trace_id 为 `e6-7191b9c094844e7ca7ff16b35638b00c`。
文件集合不变，仅 Makefile hash 从上述原值变为
`128069c949b0239e3377f320d51498c2b37a317c602d8755d573a283e1f400ae`；
其余三个文件逐字节哈希不变。按文本行比较的 diff 为：

```diff
-main.o: main.c unused.h
+main.o: main.c config.h
```

需准确说明字节差异：原归档 Makefile 使用 CRLF，公共脚本的 `read_text/write_text`
在 Linux 重写时同时归一为 LF；并非只有该依赖字符串的字节发生变化。
忽略换行编码后，唯一文本行变化是上述依赖修复，且唯一变化文件仍为 Makefile。
原始包不做换行修正，核验脚本按行验证该预期。

`evidence/gate/fixed/evidence/findings.json` 中 `clean_exit_code=0`、
`build_exit_code=0`、`status=SUCCEEDED`、`findings=[]`；CLI 退出 0。
证据保留修复后的 fixture、构建日志、actual/declared graph 和完整 trace。

## 5. A03：三种真实故障，不把环境错误充作注入结果

| case | 隔离 fixture 的输入改动 | 真实结果 | 包内原始锚点 |
| --- | --- | --- | --- |
| build-failed | 只删除 `config.h`；其余输入保持原 hash | clean=0，Make build=2，CLI=1；FAILED/CHECK_FAILED | `evidence/gate/build-failed/evidence/build-stderr.log:1-5`；`findings.json:35-37` |
| unsupported | Makefile 配方改为 `cp main.c one; cp main.c two`，clean 删除这两个输出 | clean=0，build=0，CLI=1；FAILED/UNSUPPORTED，多输出归属被拒绝 | `evidence/gate/unsupported/fixture/Makefile:1-5`；`evidence/findings.json:36-38` |
| timeout | Makefile 先 `sleep 10` 再复制 app；CLI 配置 `--timeout 1` | clean=0，CLI=1；TIMED_OUT/TIMEOUT；进程组被杀，无正常 build_exit_code | `evidence/gate/timeout/fixture/Makefile:1-6`；`evidence/trace/t.13:1`；`evidence/findings.json:36-38` |

build-failed stderr 第 1 行为 `main.c:2:10: fatal error: config.h: No such file or directory`，
第 5 行为 `make: *** [Makefile:7: main.o] Error 1`，Make 自身返回 2。
unsupported 错误为 `Recipe job 13 has multiple final outputs; needs a richer attribution model`。
timeout 的真实 trace 第 1 行成功执行 `/usr/bin/sleep`，参数为 `10`；
报告为 `Command exceeded 1s; process group was killed`（elapsed_ms=1006）。
不伪造 timeout 的正常构建退出码，也不把此 unsupported 场景说成 A01 的同 target 冲突。

## 6. 完整八项与独立判定

| case | CLI/测试退出码 | detector 状态 | 最终判定 |
| --- | --- | --- | --- |
| unit-tests | 0 | 不适用 | PASS，21 passed |
| original-1 | 1 | SUCCEEDED | PASS，发现精确问题后拒绝放行 |
| original-2 | 1 | SUCCEEDED | PASS，同上 |
| original-3 | 1 | SUCCEEDED | PASS，同上 |
| fixed | 0 | SUCCEEDED | PASS，无发现 |
| build-failed | 1 | FAILED/CHECK_FAILED | PASS，真实构建失败 |
| unsupported | 1 | FAILED/UNSUPPORTED | PASS，显式不支持 |
| timeout | 1 | TIMED_OUT/TIMEOUT | PASS，真实超时 |

公共驱动 `scripts/run_e7_a_gate.py` 整体退出 0，
`evidence/gate/gate-result.json` 中 `passed=true`；与 `results.csv` 的
8 行按 case、passed、exit_code、detector_status、trace_id、error 逐字段一致。
6 项独立判定覆盖精确错误的 CLI 门禁、空报告不得通过、fixed、失败构建、
显式 unsupported、timeout 退出码；独立命令退出 0，不能单独替代真实八项 gate。

## 7. 进程归属与路径过滤：用本次证据说明

复用 E6 已有教学实现 `fullcheck.py`，未重写机制：单 Make 进程的直接子进程为 recipe job，
其后代读写汇入该 job；每个 job 只允许一个最终输出，跨 jobs 同 target 必须 Unsupported。
本次 `original-1/evidence/processes.json` 显示：Make PID 12 → cc/job 13 →
cc1 PID 14 与 as PID 15；链接 job 16 的 collect2 PID 17 → ld PID 18。
因此 cc1 的 config.h 读打开与 as 的 main.o 写打开被归到同 job 13，而非混到链接 job。
`actual-graph.json` 精确保留 `main.o→main.c`、`main.o→config.h`、`app→main.o`。

路径经过 POSIX 规范化，只保留 `/evidence/project/` 内的项目相对路径；
失败 syscall 不作为依赖。Make 自己读取数据库输入不会算成编译依赖。
本次 `original-1/evidence/trace/t.14:125` 成功打开 `/usr/include/stdio.h`，
`:99` 成功打开 `/usr/include/stdc-predef.h`，两者在实际图中均被排除；
`:82` 的失败 openat 也不进入图。项目内 `main.c` 的成功读在 `:67`，
`config.h` 的成功读在 `:579`，都被保留。
这是 successful read-open 观测模型，不是字节读取证明；RD 也仅表示本次 job/配置未观测到读。

## 8. 来源、个人新增与环境限制

- 参考/复用：仓库已有 `fullcheck.py`、`test_e6_a.py`、`test_fullcheck.py`、
  `tests/e7/test_e7_a_gate.py`、`scripts/run_e7_a_gate.py`、Dockerfile 和依赖锁。
  本次直接调用公共 gate，没有重新实现其门禁，也未修改 B/C/workflow/保护规则。
- 个人新增：A01 一个测试；包内一次性 `run.py`/`package.py` 负责命令、退出码、
  哈希与备份核验，不改变检测算法；本轮报告、验收 CSV、交付包和离线核验脚本。
- 云端宿主：Linux、2 CPU、约 1.7 GiB 内存、无 swap、约 69 GiB 空闲磁盘；
  Docker 29.1.3，宿主 Python 3.12.3。镜像 Python 3.13.14、pytest 8.4.2、
  Make 4.4.1、strace 6.13；完整版本见包内 `evidence/toolchain/stdout.log`。
- A01/单独服务回归容器显式限制 2 CPU、1 GiB、256 PIDs、禁网。
  完整 gate 按原脚本禁网运行，未显式添加上述全部资源参数，不扩张这一结论。
- Windows 初次 fullcheck 13 项中 1 项受 Linux 限制而 ERROR；保留历史记录。
  后续 Linux 21 项实际通过已覆盖该测试。早期 PENDING 属于提交授权前的阶段，不是当前状态。
- 教学范围为单 Make、每 job 单最终输出、小型显式 oracle，不宣称覆盖完整论文 benchmark。

## 9. C 可直接获取的交付证据

无需访问个人电脑或云端：使用仓库相对路径
`E7/A/evidence/E7-A-20261113T075315Z.tar.gz` 与 `E7/A/evidence/PACKAGE.sha256`。
包为 412880 字节，SHA256：
`e800d08aa1bc6227e6d92dfe050778e1aafbfde1f81a9977cb9fa9e516777c84`。
该包与已回传原包逐字节一致，未重打包，未修改原 trace/构建日志。
包含 259 文件的哈希清单、原始证据、来源源码归档、命令、工具版本和采集脚本。

递归检查外包及内嵌 source.tar 共 805 个普通文件：认证文件名、令牌、私钥头、
IPv4 地址及可执行 SSH/SCP 连接命令模式均未命中。
宽泛 SSH/SCP 词语匹配的 7 处均是历史说明/错误提示文字，非真实连接命令；
未因这些文字擅改原始内容。扫描是规则与人工复核，不宣称能识别所有未知秘密类型。
可用标准库离线重复核验，无须 Docker、网络或解包：

```text
python -B E7/A/verify_evidence.py
```

本轮返回 0：包及 259 文件哈希、递归扫描、8 行一致、三次输入、fixed、
故障日志与行锚点核验通过。结果见 `E7/A/09-delivery-verification.log`。
交付包已随报告提交并推送至 `e7-a`，C 可直接从上述 PR 获取，不再依赖个人本机备份。
个人交付完成不表示 CI 或合并自动通过；请 C 核对 PR 最新检查与最终集成基线，不自动合并。
