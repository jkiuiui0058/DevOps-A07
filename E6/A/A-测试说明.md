# A03：双 recipe job 隔离测试说明

## 来源与新增贡献

生产代码来自仓库导入的 `A-buildchecker/` 教学参考实现，不是个人从零实现。本次个人新增 `A-buildchecker/services/buildchecker/tests/test_e6_a.py` 和本文；不修改生产源码、不增加依赖、不复用或导入其他 TestCase 的 helper，避免隐式重复收集测试。

写入前已阅读 `buildchecker/fullcheck.py` 和 `tests/test_fullcheck.py`（均相对服务目录）。已有 `test_fullcheck.py:22–38` 覆盖**一个** job 内兄弟进程读写合并；`40–90` 行还覆盖失败访问、路径范围、cwd、内部产物和异常 trace。新增点是**同一个 Make 下两个独立编译 job 的隔离及精确证据归属**，针对 `fullcheck.py:131–151, 216–234` 的 job 分组和输出逻辑。

## 输入和预期

只有一个 unittest 测试方法，使用 `tempfile.TemporaryDirectory` 写独立合成的 `t.PID` 文本，再直接调用 `execution_graph`；不启动 Make、编译器或 strace。

下表 PID **全部为测试构造值，不是云端实测证据**。合成 Make PID 为 10，直接派生两个 job；每个 job 再派生一个读取进程和一个写出进程。

| 目标 | job_pid | 完整 job 进程列表 | 精确依赖集合 | 输入 evidence（PID / 文件 / 行） |
|---|---|---|---|---|
| a.o | 11 | 11、12、13 | a.c、a.h | a.c：12 / t.12 / 2；a.h：12 / t.12 / 3 |
| b.o | 21 | 21、22、23 | b.c、b.h | b.c：22 / t.22 / 2；b.h：22 / t.22 / 3 |

断言目标集合恰为 `{a.o, b.o}`，分别核对依赖精确集合、job_pid、完整 processes 列表、依赖 evidence 的精确元组集合，并核对输出证据和完整进程摘要的父子/job 归属集合。这样不只检查“包含某条依赖”，也会拒绝两个 job 串线或多出输入。预期正常执行时报告 1 个测试成功、`OK`、退出码 0；实际离线结果见下方“当前状态”和日志。

## 后续执行与留证

环境就绪后，在 `A-buildchecker/services/buildchecker/` 目录执行：

```bash
python3 -m unittest discover -s tests -p test_e6_a.py -v
```

标准 unittest TestCase 也可被 pytest 收集；若环境已有 pytest，可使用 `python3 -m pytest tests/test_e6_a.py -v`，无需为本测试新增依赖。

建议在 Linux Bash 用以下方式保留标准输出、标准错误及退出码；日志名应每次换新，避免覆盖旧证据：

```bash
set -o pipefail
python3 -m unittest discover -s tests -p test_e6_a.py -v 2>&1 | tee e6-a-unittest.log
test_exit=$?
printf 'TEST_EXIT_CODE=%s\n' "$test_exit" | tee -a e6-a-unittest.log
```

执行时同时记录日期、Python 版本、源码版本及实际命令，并保留完整日志。独立合成测试即使通过，也不能代替 A01/A02 的真实 trace 与实际图核对。

## 当前状态

最初编写阶段仅完成代码与静态检查，未执行测试。现获用户允许，协调者已在本地服务目录执行上述 unittest discover 命令，工具显示成功，原始输出为 `Ran 1 test in 0.021s`、`OK`，即本地离线单元测试 1 项通过。

早期本地记录保存在 `E6/A-离线测试日志.txt`，由实际工具输出转存，并非自动重定向日志。上方 tee 命令只是留证建议，不是该次实际执行方式。

随后获准在云端固定镜像 `sha256:65e8007d888e74e3d8bfe059f96fbb4e589cae284e4cd674afcbd76abd3b23e3` 执行单项验证，实际命令为：

```bash
docker run --rm --network none sha256:65e8007d888e74e3d8bfe059f96fbb4e589cae284e4cd674afcbd76abd3b23e3 pytest tests/test_e6_a.py -v
```

结果为 `collected 1 item`、`1 passed in 0.02s`，退出码 **0**，stderr 为空。镜像内 pytest 配置自带 `-q`，所以输出显示文件及通过标记，不据此编造更详细的测试名称日志；该文件只有一个测试方法。

远端日志目录为 `/root/241098114/e6-env-20261106-025440/work/e6-a03-20261106-111116/`，完整复制到本地 `A-buildchecker/work/e6-a-cloud-20261106-111116/a03/`。`command.txt` 保存命令，`stdout.log:5–9` 保存收集及通过结果，`stderr.log` 保存标准错误，`exit-code.txt:1` 保存 0。本次日志使用实际重定向保存，不是早期工具输出转存。源码、镜像和本地测试文件的 SHA256 均为 `979169aa38d5efcfff0114f80bf3dee1cde100ae621027acf3b4f78e24ff8318`，版本边界见 [A-云端证据索引.md](A-云端证据索引.md)。

**A03 的运行验证已完成，现已获准在个人分支 e6/a 本地提交，提交 SHA 由本次提交生成，不在文档中自引用；仍不整体标 DONE。** 采集阶段同时完成 A01/A02 的 before 真实证据核对，未运行 after/A04、未重建镜像、未提交 Git。正式已提交版本及最终集成重验仍待完成。

## 个人提交关联复检

上述提交待生成的描述属于历史阶段；个人贡献现已提交为 `39f8c328e6d3ccd6e9e149468b17bb4a8b9702ce`，分支 `e6/a`。新增测试在提交/工作树/云源码/镜像中原始字节一致，其余 15 个相关文件仅 CRLF/LF 有别；严格仅替换 CRLF→LF 后内容逐字节一致。这里关联的是该限定行尾映射下的已提交逻辑，**不是提交原始字节运行证明，也不是最终集成验收**。

使用上述相同固定镜像再次执行 `docker run --rm --network none <固定镜像ID> pytest tests/test_e6_a.py -v`，结果 `collected 1 item`、`1 passed in 0.02s`，实际退出码 **0**。新日志在远端 `/root/241098114/e6-env-20261106-025440/work/e6-a-personal-39f8c328-5db6d4f1/a03/`，本地为 `A-buildchecker/work/e6-a-commit-39f8c328-229d0f61/personal-recheck-ea6309c3/run/a03/`；其中 `stdout.log:5–9` 为单项结果，`exit-code.json` 为 0，`command.json` 保存完整命令。

同轮全新 before 为远端 `work/e6-20261106-113348-785abc/`（相对云根），已核对 SUCCEEDED、clean/build 0、CLI 1 和精确两条预期发现。本地完整新证据、行尾边界及 40 个复制文件哈希校验见 [A-云端证据索引.md](A-云端证据索引.md) 第 5 节。旧单项日志和旧详细 PID 核对仍归属于各自旧采集目录，不被替换。

A01–A03 个人工作已完成，包括测试、机制与真实证据核对及贡献 SHA。本次未运行 after/A04、未改测试/生产源码或 fixture、未构建镜像、未再次提交或推送；本节与索引的追加修改留在工作区。C 的后续最终集成验收不属于本次个人待办。
