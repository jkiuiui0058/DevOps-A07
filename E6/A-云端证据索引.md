# E6 A01–A03 云端快照证据索引

教学检测器来自仓库导入参考实现；个人贡献为依赖机制分析、独立双 job 测试及证据核对。采集阶段使用已建镜像，未改生产源码、未重建、未提交 Git，未执行 after/A04。现已获准在个人分支 e6/a 本地提交这批测试与说明，不推送。

## 1. 位置与版本边界

| 项目 | 实际值 |
|---|---|
| 云端内容根（即本地 A-buildchecker 对应层，不再套一层目录） | `/root/241098114/e6-env-20261106-025440/` |
| before 远端目录 | 上述根下 `work/e6-20261106-111116-e7158c/` |
| A03 远端目录 | 上述根下 `work/e6-a03-20261106-111116/` |
| 本地完整副本根 | `D:\study\SE\DevOps\DevOps-A07\A-buildchecker\work\e6-a-cloud-20261106-111116\` |
| 本地 before / A03 | 副本根下 `before/` / `a03/` |
| 快照清单副本 | 副本根下 `SOURCE_SNAPSHOT.json` |
| 固定镜像 ID | `sha256:65e8007d888e74e3d8bfe059f96fbb4e589cae284e4cd674afcbd76abd3b23e3` |
| 快照记录的基线 HEAD | `3b43c97591ef57d66fd1e6fc2ae8b9fb33090c9a` |

云目录不是 Git 仓库，无法从那里核实 HEAD/工作区状态。`SOURCE_SNAPSHOT.json` 明确是环境构建用本地工作区快照，其 `entry_status` 记录新增测试当时未跟踪。**基线 HEAD 不是个人贡献提交 SHA，也不证明整个快照已提交。** 本次只验证该快照，正式已提交版本及最终集成后仍须重验。

已核实本地、云源码和镜像内关键文件 SHA256 一致：

| 文件（相对服务目录） | SHA256 |
|---|---|
| `buildchecker/fullcheck.py` | `a40b7bbf3f66756ee14b2bcbf838ee80dea137616623692de6ab2d025a59756f` |
| `tests/test_e6_a.py` | `979169aa38d5efcfff0114f80bf3dee1cde100ae621027acf3b4f78e24ff8318` |

旧环境构建的 `16 passed in 0.06s` 位于云根下 `work/e6-env-build-20261106-025546/unit-tests/stdout.log`；该目录还保留 build/image 记录。本次不以旧的总数代替 A03 单项日志。

## 2. 本次命令与结果

before 在云端内容根执行，未指定 out，入口自动选择全新目录：

```bash
python3 scripts/lab_cloud.py e6 --image sha256:65e8007d888e74e3d8bfe059f96fbb4e589cae284e4cd674afcbd76abd3b23e3
```

实际 CLI 退出码为 **1**。`before/cli-exit-code.txt:1` 是将当时 SSH 工具显示的退出码事后补记为文本，非声称原命令自动重定向；`before/runner/exit-code.json` 同样为 1。报告 `status=SUCCEEDED`，clean/build 均为 0，精确两条发现为 `MISSING(main.o,config.h)`、`REDUNDANT(main.o,unused.h)`。本轮没有 after 报告。

A03 使用同一固定镜像，`docker run --rm --network none ... pytest tests/test_e6_a.py -v`，未挂载源码，不重建、不联网、不改全局设置，保留镜像默认用户/工作目录。实际命令全文在 `a03/command.txt:1`；`a03/stdout.log:5–9` 为单项通过，`a03/exit-code.txt:1` 为 0，stderr 为空。

## 3. 可复查证据

下列 before 路径均相对本地 `before/`（远端同构）：

| 证据 | 复查用途 |
|---|---|
| `invocation.json`、`runner/command.json` | 固定镜像、入口及实际 Docker 参数；网络 none、SYS_PTRACE、只读 fixture 挂载 |
| `evidence/findings.json`、`runner/exit-code.json` | 成功状态、两条发现及构建/CLI 返回值 |
| `fixture/`、`evidence/project/` | 实际输入副本及构建输出，原始 fixture 未修复 |
| `evidence/processes.json:2–57` | PID 12 根；编译 job 13（13/14/15）；链接 job 16（16/17/18） |
| `evidence/actual-graph.json:2–37` | app→main.o、main.o→config.h、main.o→main.c 三条边 |
| `evidence/make-db.txt:69,601,1053` | root 为 `/evidence/project`；app 与 main.o 的声明 |
| `evidence/trace/t.12` 至 `t.18` | 全部原始 trace；完整 argv、父子关系和访问事件 |
| `evidence/clean.log`、`clean-stderr.log`、`build-stderr.log` | clean/build 配套日志 |

详细 PID、父 PID、job、exec/clone 行号和输入输出证据见 [A-实际依赖说明.md](A-实际依赖说明.md) 第 4 节。`t.17:1` 与 `t.18:1` 是完整未截断的长链接 argv，不是 processes.json 的 executables。为便于复查，下面完整列出两者共用的参数尾部；PID 17 的 argv[0] 为 `/usr/libexec/gcc/x86_64-linux-gnu/14/collect2`，PID 18 为 `/usr/bin/ld`，其余参数相同，均成功返回 0：

```text
-plugin /usr/libexec/gcc/x86_64-linux-gnu/14/liblto_plugin.so -plugin-opt=/usr/libexec/gcc/x86_64-linux-gnu/14/lto-wrapper -plugin-opt=-fresolution=/tmp/cc1r4rqP.res -plugin-opt=-pass-through=-lgcc -plugin-opt=-pass-through=-lgcc_s -plugin-opt=-pass-through=-lc -plugin-opt=-pass-through=-lgcc -plugin-opt=-pass-through=-lgcc_s --build-id --eh-frame-hdr -m elf_x86_64 --hash-style=gnu --as-needed -dynamic-linker /lib64/ld-linux-x86-64.so.2 -pie -o app /usr/lib/gcc/x86_64-linux-gnu/14/../../../x86_64-linux-gnu/Scrt1.o /usr/lib/gcc/x86_64-linux-gnu/14/../../../x86_64-linux-gnu/crti.o /usr/lib/gcc/x86_64-linux-gnu/14/crtbeginS.o -L/usr/lib/gcc/x86_64-linux-gnu/14 -L/usr/lib/gcc/x86_64-linux-gnu/14/../../../x86_64-linux-gnu -L/usr/lib/gcc/x86_64-linux-gnu/14/../../../../lib -L/lib/x86_64-linux-gnu -L/lib/../lib -L/usr/lib/x86_64-linux-gnu -L/usr/lib/../lib -L/usr/lib/gcc/x86_64-linux-gnu/14/../../.. main.o -lgcc --push-state --as-needed -lgcc_s --pop-state -lc -lgcc --push-state --as-needed -lgcc_s --pop-state /usr/lib/gcc/x86_64-linux-gnu/14/crtendS.o /usr/lib/gcc/x86_64-linux-gnu/14/../../../x86_64-linux-gnu/crtn.o
```

全部 before 目录和 A03 日志通过 SCP 完整复制到上述本地专属新目录，未覆盖既有目录；复制前已用 `git check-ignore` 确认目标受忽略，复制后再次确认 before 和 a03 路径均受忽略，原始日志未加入 Git。另复制快照清单以保留来源信息。已对照远端与本地以下关键文件哈希一致（不是声称所有文件都逐一校验）：

| 本地副本内文件 | SHA256 |
|---|---|
| `before/evidence/findings.json` | `a64d4bbd461447264a81bf52e18fb9cd7566cef965d0e99044ae56f5375f9aa8` |
| `before/evidence/actual-graph.json` | `6bd6c0050e6399f8803fe896c0678a716101a2b92b93de7519879a1059fb8780` |
| `a03/stdout.log` | `c70be00492d875e7bf3361ab7f5b4645759c56df4438d4f8fa3d43f2890c79b4` |

## 4. 完成边界

- A01/A02：已完成本次快照的真实 before 证据核对。
- A03：已完成云端单项运行验证；个人贡献提交已获授权，SHA 由本次提交生成，不在文档中自引用，尚不整体验收。
- 采集阶段未执行 after/A04，未修改 TASKS.md、生产源码或测试源码，未提交 Git。正式已提交版本、最终集成重验及整个 E6 验收仍待完成。
