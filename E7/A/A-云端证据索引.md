# A01—A04 云端与交付证据索引

## C 整合入口与当前交付状态

发布前已 `fetch origin`：PR 基线 `origin/main` 为
`d18ef00e758c8a36f2cd3c5f8054f4f088378c11`，与运行源码父提交一致。
远端当时不存在 `e7-a` 分支；未 rebase、未覆盖他人分支。请 C 仍按 PR 最终基线做集成验收。

- 可直接拼接报告：[`A-本地验证报告.md`](A-本地验证报告.md)。
- 个人过程与职责：[`A-个人记录.md`](A-个人记录.md)。
- 验收 CSV：[`A-验收记录.csv`](A-验收记录.csv)，列与 E7/B 一致。
- 完整原包：[`evidence/E7-A-20261113T075315Z.tar.gz`](evidence/E7-A-20261113T075315Z.tar.gz)。
- 包外校验：[`evidence/PACKAGE.sha256`](evidence/PACKAGE.sha256)。
- 离线复验：仓库根执行 `python -B E7/A/verify_evidence.py`；
  实际输出及退出码见 [`09-delivery-verification.log`](09-delivery-verification.log)。

运行与资料核验、提交推送及个人 PR 交付已完成：
[PR #7](https://github.com/jkiuiui0058/DevOps-A07/pull/7)，作者账号 **ChipmunkYu**，`e7-a → main`。
C 可从 PR 直接取得交付包；PR 待 C 审阅与集成合并，不等于已合并。
不虚构 A 的 CI run ID，不用 B 结果代替 A 证据；最新 PR 检查以 GitHub 实际状态为准。

## 源码与镜像

- 源码提交：`e779b3130cd9b91eba4c6e54f4a6a85f5606b99c`。
- 提交内容：仅新增 `A-buildchecker/services/buildchecker/tests/test_e7_a.py`（33 行）。
- 源码来源：`git archive HEAD`；解包目录不是 Git 工作树；另有 `SOURCE_SHA` 标明来源。
- 归档 SHA256：`719b430cdf927dbe5258a245c82d2fab2cdb07a196575359eb7643d4dd5e2489`。
- 镜像：`e7-buildchecker:241098114-e7-20261113t075315z`。
- 镜像 ID：`sha256:9cf27a2cd2c894be2d913717aed1e441a06013ea49e4a04c2fe87db4c3c8ab03`。
- Docker 29.1.3；宿主 Python 3.12.3；镜像 Python 3.13.14、pytest 8.4.2、
  GCC 14.2、Make 4.4.1、strace 6.13、amd64。完整版本见原始 `toolchain/stdout.log`。
- 保留原 Dockerfile、带哈希依赖锁、构建完整日志、镜像 inspect 与源码逐文件哈希。
  基础镜像使用 Dockerfile 固定 digest，构建复用既有缓存，未调整镜像源或安装宿主依赖。

## 命令与真实退出码

工作目录均为隔离归档的 `A-buildchecker/`。完整 argv 见 `06-cloud-verification.json`，
真实测试 stdout/stderr 见 `08-cloud-tests.log`；构建原始日志也已包含在本目录交付包中。

| 操作 | 命令概要 | 退出码 | 结果 |
| --- | --- | --- | --- |
| 构建 | `docker build --progress=plain -f services/buildchecker/Dockerfile -t <上述个人标签> .` | 0 | 成功 |
| A01 | 镜像内 `python3 -m unittest discover -s tests -p test_e7_a.py -v` | 0 | 1 项通过 |
| 服务回归 | 镜像内 `pytest -v` | 0 | 21 项通过 |
| 独立判定 | `python3 -B -m unittest discover -s tests/e7 -v` | 0 | 6 项通过 |
| 完整 gate | `python3 -B scripts/run_e7_a_gate.py --image <上述个人标签> --out <全新证据目录>` | 0 | 8 项全部通过 |

单独的 A01/服务测试容器使用 `--network none --cpus 2 --memory 1g --pids-limit 256`。
完整 gate 原样使用公共脚本，自带 `--network none`，未擅自为该脚本添加资源参数；
因此不能声称八项 gate 也显式受上述全部资源参数限制。
开始前重新检查：活动容器 0、低负载、约 1.2 GiB 可用内存、69 GiB 磁盘空闲。
运行采用 `nohup` 后台收集；结束后活动容器仍为 0，未清理或停止其他人的容器。

## 八项判定

| case | CLI/测试退出码 | detector 状态 | 判定 |
| --- | --- | --- | --- |
| unit-tests | 0 | 不适用 | PASS，21 passed |
| original-1 | 1 | SUCCEEDED | PASS，精确 MD/RD |
| original-2 | 1 | SUCCEEDED | PASS，精确 MD/RD |
| original-3 | 1 | SUCCEEDED | PASS，精确 MD/RD |
| fixed | 0 | SUCCEEDED | PASS，无发现 |
| build-failed | 1 | FAILED / CHECK_FAILED | PASS，真实 Make 退出码 2 |
| unsupported | 1 | FAILED / UNSUPPORTED | PASS，构建退出码 0，拒绝多输出 |
| timeout | 1 | TIMED_OUT / TIMEOUT | PASS，1 秒超时并杀死进程组 |

超时报告不包含 `build_exit_code`；不能伪造为某个正常构建退出码。
build-failed 原始 stderr 明确为 `config.h: No such file or directory`，
随后 `make: *** [Makefile:7: main.o] Error 1`，不是镜像下载或环境故障。

## 输入与重要证据锚点

原始 fixture 前后逐文件 SHA256 相同，三次 original 的 `input_sha256` 全部一致。
fixed 文件集合不变，仅 Makefile hash 不同；内容仅将
`main.o: main.c unused.h` 改为 `main.o: main.c config.h`。
原 Makefile 为 CRLF，Linux 公共脚本文本重写同时归一为 LF；上述“仅替换”指按行文本差异，
不是声称只改动了依赖字符串的字节。唯一变化文件确为 Makefile，原始字节保留在交付包中。
`gate-result.json` 与 `results.csv` 的全部 8 行逐字段一致。

三次 original 均各有自己的真实 `evidence/trace/` 与 `make-db.txt`。
本次各容器 PID 从同样的命名空间序列开始，因此三次恰好具有相同 PID/行号，
不能只凭 PID 当成同一份采集。trace_id 分别为：

- original-1：`e6-ebd613ef134c43e0b0501ab0bf07bed5`
- original-2：`e6-f91147972ad148a298e2aa4e506113f1`
- original-3：`e6-76b7296adf884097ab9b3cbc1e053b48`

每次均核对如下精确发现与锚点（相对各自的 `gate/original-N/evidence/`）：

| 发现 | 锚点 | 原始内容 |
| --- | --- | --- |
| MISSING `main.o → config.h`，读 | `trace/t.14:579`，PID 14 | `openat(AT_FDCWD, "config.h", O_RDONLY\|O_NOCTTY) = 4` |
| 同一 MD，写 | `trace/t.15:23`，PID 15 | `openat(AT_FDCWD, "main.o", O_RDWR\|O_CREAT\|O_TRUNC, 0666) = 3` |
| REDUNDANT `main.o → unused.h` | `make-db.txt:1053` | `main.o: main.c unused.h` |

`processes.json` 显示 Make PID 12，recipe job/cc PID 13，
cc1 PID 14 与 as PID 15 均归属 job 13；各 PID 与 trace 文件、操作、行号逐项匹配。
完整三次摘录见 `07-trace-anchors.json`。
REDUNDANT 只表示在本次构建配置的该 recipe job 中未观测到读打开，不等于所有配置均不需要。
A01 是合成 trace 单元测试；上述 MD/RD 与故障 gate 才是真实构建采集，不混淆二者。

## 仓库外原始备份与完整性

备份目录：`D:\study\SE\DevOps\个人证据备份\E7-A-20261113T075315Z\`。

- 压缩包：`E7-A-20261113T075315Z.tar.gz`，412880 字节。
- 包 SHA256：`e800d08aa1bc6227e6d92dfe050778e1aafbfde1f81a9977cb9fa9e516777c84`。
- 包外 `PACKAGE.sha256` 与云端生成值、本地重新计算值一致。
- 包内与包外 `SHA256SUMS.json` 一致；解包后 259 个文件逐个核验通过。
- `raw/` 为已校验解包内容；`download-verification.json` 为本地核验结果。
- `raw/evidence/gate/` 保留每项 command、stdout/stderr、findings、trace、项目副本、
  Make 数据库、图、processes、JSON 与 CSV；`raw/evidence/` 还保留构建、环境、锁文件和哈希。
- 包内包含源码归档、`SOURCE_SHA`、一次性收集/核验脚本及后台日志，可审计来源和判定过程。

早期本地 Windows 平台限制保留于历史日志；本次 Linux 服务回归已真实通过对应测试。
仓库外原始备份保留不动；本轮扫描通过后，同一原包已复制到仓库相对路径
`E7/A/evidence/E7-A-20261113T075315Z.tar.gz`，供 C 使用，不再只依赖个人绝对路径。
包 SHA256 和原包相同，未脱敏重打包，未修改原始 trace 或构建日志。

## 交付包安全扫描与可复验性

检查覆盖外包及内嵌 `source.tar`，共 805 个普通文件；259 个原包清单文件逐项 hash 通过。
未发现认证文件名、私钥头、常见真实令牌、IPv4 地址或可执行 SSH/SCP 连接命令。
宽泛 SSH/SCP 词语搜索有 7 处，人工查看均为历史说明/提示文本，不是连接命令；
无须以脱敏为由篡改原始证据。未复制任何认证地址或私钥内容到报告。
该扫描为明确规则及人工核对，不宣称能够发现所有未知秘密格式。

`06-cloud-verification.json` 是之前的结果摘要，不能独立重算包内证据；
因此本轮补一个标准库脚本 `verify_evidence.py`，不解包、不联网、不运行采集脚本，
读取 tar/json/csv/hash，重新核验来源、259 文件、扫描、8 行、三次输入、fixed、故障与锚点。
该脚本不是新的检测器或公共 gate，不替代实际运行日志。
发布前 `git diff --cached --check` 发现 Windows 包装日志的 CR/CRCRLF 被判为行尾空白，
故仅将 `01`—`04`、`09` 文本日志换行归一为 LF，未更改命令、输出文本、时长或退出码。
云端原始证据包及其内部 trace/构建日志完全未动，包 SHA256 不变。
本轮核验退出 0；无未解决运行阻碍。个人提交、推送与 PR 交付已完成，待 C 审阅/集成验收及合并。
`05`、`06`、`08` 中的授权等待、未 push/PR 字段均为采集当时的历史记录，不表示当前发布状态。
