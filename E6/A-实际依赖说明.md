# A01/A02：实际依赖分析与 before 证据核对

参考实现来源：本仓库导入的 `A-buildchecker/` 教学参考实现（见 `E6/TASKS.md:7–16`），不是本人从零实现。个人贡献是机制分析、独立测试及真实证据核对。

**当前状态：A01/A02 已完成本次源码快照的静态分析及 before 真实证据核对。** 正式已提交版本与最终集成重验仍待完成，不代表整个 E6 已验收。采集阶段未执行 after/A04、未重建镜像、未提交 Git；现已获准在个人分支 e6/a 本地提交，提交 SHA 由本次提交生成，不在文档中自引用。源码行号按已核对版本引用；以下 `fullcheck.py` 指 `A-buildchecker/services/buildchecker/buildchecker/fullcheck.py`。完整路径、固定镜像 ID、文件哈希及版本边界见 [A-云端证据索引.md](A-云端证据索引.md)。

## 1. A01：从 trace 还原进程，再归到 recipe job

| 环节 | 代码位置 | 通俗解释 |
|---|---|---|
| 读取每个进程 | `fullcheck.py:92–102` | 只接收文件名完整匹配 `t.数字` 的条目，从文件名提取 PID，逐个解析事件；没有这类文件就报不支持。 |
| 还原父子关系 | `fullcheck.py:103–116` | 父进程的 `clone/clone3/fork/vfork` 返回值大于 0 时，该返回值就是子 PID。失败调用不建立关系；父子关系冲突、子 trace 缺失会报错，`CLONE_FS` 共享工作目录也不支持。 |
| 记录成功 exec | `fullcheck.py:112–120` | 只记录返回值为 0 的 `execve/execveat` 的可执行文件路径。按路径 basename 为 `make/gmake` 找 Make，要求恰好一个 Make PID，不支持递归 Make。失败的 exec 不能制造一个“Make 进程”。 |
| 找到 job | `fullcheck.py:131–151` | 沿父链上溯，找到 Make 的直接子进程，以它的 PID 作为 `job_pid`。它下面的编译器、汇编器等后代都归同一 job；Make 自身没有 job。父链成环会报错。 |
| 继承工作目录 | `fullcheck.py:144–169` | 从项目根目录开始遍历，成功 `chdir` 更新当前 cwd；在 fork 类事件发生的位置，把当时的 cwd 传给子进程，而不是用父进程最后的 cwd。成功 `fchdir` 暂不支持。 |
| 检查树完整性 | `fullcheck.py:210–215` | 必须只有一个根进程，且它就是 Make；不接受断开的进程树。 |

概念关系如下，**不是实测进程树，不使用虚构 PID**。实际环境可能有 shell 中间层、不同编译器程序或同一 PID 多次 exec，必须以 trace 为准。

```text
Make
├─ 编译 recipe 的直接子进程（可能是 shell 或 cc） ← 编译 job 的根
│  ├─ 编译器内部进程：成功 read-open main.c、config.h
│  └─ 汇编器进程：写出 main.o
└─ 链接 recipe 的直接子进程                     ← 另一个 job
   └─ 链接器进程：读取 main.o，写出 app
```

关键不是“谁叫 cc”，而是“谁属于同一个 Make 直接子进程的后代”。因此一个进程读源码、另一个兄弟进程写目标文件，也能合并到同一个 job。`main.o` **并未硬编码**：每个 job 收集读写后，从最终保留的输出确定目标名，再把该 job 的外部输入归给它（`fullcheck.py:216–228`）。无输出的 job 跳过，多于一个最终输出或多个 job 写同一目标则报不支持，不猜归属。

`processes.json` 的每项仅有 `pid`、`parent`、`executables`、`job_pid`（`fullcheck.py:231–234`）。其中 **`executables` 只是成功 exec 的可执行文件路径列表，不是完整 argv**。完整命令须回到原始 `execve/execveat` trace 的参数数组；若参数被截断，不能自行补全。父 PID 则须与父 trace 中成功派生子 PID 的事件相互核对。

## 2. A02：哪些文件访问算实际依赖

这里的“实际”是教学模型中的 **成功 read-open 观察**，不是证明文件已经读到字节，也不是所有配置下的完整语义依赖（`fullcheck.py:1–5`）。采集入口只跟踪 `%file,%process`（`fullcheck.py:374–378`），不能把成功 open 说成已验证 read 返回了数据。

| 判定 | 代码位置 | 对分析结果的影响 |
|---|---|---|
| 只留项目内路径 | `fullcheck.py:60–65, 124–128, 169–171` | root 必须是绝对 Linux 路径；相对路径结合进程 cwd 规范化，再按根目录加 `/` 的边界过滤，并转成项目相对路径。根目录本身、项目外系统头文件、仅有相同前缀的旁边目录都不计入。这里是词法路径处理，不是完整符号链接解析；采集入口拒绝 fixture 内符号链接（`343–354`）。 |
| 失败访问不算 | `fullcheck.py:152–155` | 返回值小于 0 的事件跳过；例如探测头文件得到失败 open，不产生依赖。 |
| 只看支持的打开事件 | `fullcheck.py:164–186` | 处理 `open/openat/openat2/creat`；相对 `openat` 使用数字目录 FD 时明确报不支持，不猜路径。 |
| 路径句柄、目录不是输入 | `fullcheck.py:172–176` | 含 `O_PATH` 或 `O_DIRECTORY` 的打开直接排除。 |
| 写访问不当作读取 | `fullcheck.py:177–186` | `O_WRONLY/O_RDWR/O_CREAT/O_TRUNC` 任一出现即走写分支；即使是 `O_RDWR` 也不计为读依赖。只有不属于写访问且含 `O_RDONLY` 的成功打开才记入 reads。 |
| Make 读文件不算编译输入 | `fullcheck.py:178–181` | Make 自身读取 Makefile 等不属于 recipe 的源码输入；Make 自身写项目文件则报不支持。不能把“Make 读取 unused.h”直接当成“编译 main.o 依赖 unused.h”。 |
| 排除内部产物 | `fullcheck.py:182–207, 225–228` | 写过的文件加入 produced；rename 更新输出名并保留产物记录，unlink 移除最终输出。最终依赖剔除本 job 的所有 produced 和目标自身，避免临时产物被当外部输入。另一个 job 生成的 main.o 仍可成为链接 job 的输入。 |

每个输入路径保留首次收录的证据，字段为 `source`、`trace_file`、`line`、`pid`、`operation`（`fullcheck.py:156–157, 183–186`）。遇到 unfinished/resumed 系统调用时，解析器合并两行，但保留**起始行号**（`fullcheck.py:68–89`）。所以核对原始 trace 时可能需要连同 resumed 行一起看。

`analyze` 将目标及其依赖展开为边：`target`、`dependency`、`kind: ACTUAL_READ_OPEN`、`evidence`（`fullcheck.py:319–329`）。只有采集构建成功并完成分析后，`full_check` 才写出 `actual-graph.json`、`declared-graph.json` 和 `processes.json`（`fullcheck.py:378–387`）；本次生成的文件见第 4 节。

## 3. fixture 的静态预期，不是实测图

以下路径均在 `A-buildchecker/fixtures/md-rd/` 下：

- `Makefile:1, 4–7`：默认 `CC = cc`；编译命令为 `$(CC) -c main.c -o main.o`，但规则声明为 `main.o: main.c unused.h`。链接规则另行读取 main.o 生成 app。
- `main.c:1–3`：包含系统头 `stdio.h` 和项目头 `config.h`，使用 `VALUE`；没有包含 unused.h。
- `config.h:1`：定义 `VALUE`；`unused.h:1`：注释明确说明未被 main.c 包含。

由这些源码和模型可得：在预期构建配置下，main.o 的项目内实际输入应为 **main.c、config.h**；声明输入却是 **main.c、unused.h**。系统头 stdio.h 在项目外，不进入这张项目局部图。因此静态预期缺失声明为 `MISSING(main.o, config.h)`，冗余声明为 `REDUNDANT(main.o, unused.h)`；差集逻辑见 `fullcheck.py:304–318`。冗余结论也只限本次 job 和构建配置，不是断言文件永远无用。

**本节保留静态推导，与第 4 节的实测结果分开。** 不能把 Makefile 中的命令文本代替实际 exec argv。

## 4. 本次 before 实测核对

本地证据根为 `A-buildchecker/work/e6-a-cloud-20261106-111116/before/`，远端为 `/root/241098114/e6-env-20261106-025440/work/e6-20261106-111116-e7158c/`。以下 trace、图和数据库均相对此根的 `evidence/`。

`findings.json` 的 `status=SUCCEEDED`、`clean_exit_code=0`、`build_exit_code=0`；CLI 实际返回 **1**，与 `runner/exit-code.json` 一致，是发现问题，不是采集失败。恰好两条发现：`MISSING(main.o, config.h)`、`REDUNDANT(main.o, unused.h)`，无其他发现。trace_id 为 `e6-81f159597c624ef7b69724989827e739`。

项目 root 是容器中的 `/evidence/project`，不是宿主机源码根，也不是只读输入挂载 `/fixture`。`make-db.txt:69` 的 CURDIR 和 `trace/t.14:70,73` 的 getcwd 均确认该路径；Make 在两个 job 派生后才于 `t.12:70` 再次 chdir 至同一路径。

### 真实进程、父子关系与完整命令

所有成功 exec 的完整 argv 都保存在下表原始行中，未用 executables 列表代替。长链接命令的完整参数另见证据索引。

| PID | 父 PID | job_pid | 成功 exec 命令/完整 argv 位置 | exec 行 | 父进程成功派生行 |
|---|---|---|---|---|---|
| 12 | 无，根进程 | 无 | `make -p app`，可执行文件 `/usr/bin/make` | `t.12:1` | 无 |
| 13 | 12 | 13 | `cc -c main.c -o main.o`，可执行文件 `/usr/bin/cc` | `t.13:1` | `t.12:55` |
| 14 | 13 | 13 | `/usr/libexec/gcc/x86_64-linux-gnu/14/cc1 -quiet -imultiarch x86_64-linux-gnu main.c -quiet -dumpbase main.c -dumpbase-ext .c -mtune=generic -march=x86-64 -fasynchronous-unwind-tables -o /tmp/cc2VfXJs.s` | `t.14:1` | `t.13:64` |
| 15 | 13 | 13 | `as --64 -o main.o /tmp/cc2VfXJs.s`，可执行文件 `/usr/bin/as` | `t.15:5` | `t.13:84` |
| 16 | 12 | 16 | `cc main.o -o app`，可执行文件 `/usr/bin/cc` | `t.16:1` | `t.12:66` |
| 17 | 16 | 16 | `/usr/libexec/gcc/x86_64-linux-gnu/14/collect2`，完整 argv 见原始行及索引 | `t.17:1` | `t.16:129` |
| 18 | 17 | 16 | `/usr/bin/ld`，完整 argv 见原始行及索引 | `t.18:1` | `t.17:96` |

上述 exec 均返回 0，成功 clone 返回对应子 PID。`processes.json:2–57` 与表一致：编译 job 13 的 processes 为 `[13,14,15]`，链接 job 16 为 `[16,17,18]`。`t.15:1–4` 的 as 路径探测失败不计成功 exec；例如 `t.12:54` 的 clone3 返回 ENOSYS，也不能当作子进程。

### 图边与输入/输出证据

| 对象 | 实际图位置 | 原始事件 | 核对结果 |
|---|---|---|---|
| main.o → main.c | `actual-graph.json:26–37` | `t.14:67`：`openat(AT_FDCWD, "main.c", O_RDONLY\|O_NOCTTY) = 3` | job 13 的成功读打开，路径归一为 main.c |
| main.o → config.h | `actual-graph.json:14–25` | `t.14:579`：`openat(AT_FDCWD, "config.h", O_RDONLY\|O_NOCTTY) = 4` | job 13 的成功读打开，路径归一为 config.h |
| main.o 输出 | 缺失依赖发现的第二项 evidence | `t.15:23`：`openat(AT_FDCWD, "main.o", O_RDWR\|O_CREAT\|O_TRUNC, 0666) = 3` | 同一 job 的唯一项目内最终输出；不是 read 输入 |
| app → main.o | `actual-graph.json:2–13` | `t.18:82`：`openat(AT_FDCWD, "main.o", O_RDONLY) = 7` | 属于另一个 job 16，不反向混入编译 job |
| app 输出 | 链接 job | `t.18:71`：`openat(AT_FDCWD, "app", O_RDWR\|O_CREAT\|O_TRUNC, 0666) = 3` | 链接 job 的输出 |
| main.o → unused.h | 实际图无此边；声明来自 `make-db.txt:1053` | 编译 job 的 `t.13/t.14/t.15` 检索无 unused.h 访问；`t.12:46` 仅 Make 的 stat | 本次配置下未观察到编译输入，不宣称永远无用 |

- [x] 实际图恰好三条边，证据 PID、文件、行号和 operation 均与 trace 对应；main.o 的输入集合精确为 `{main.c, config.h}`，app 的为 `{main.o}`。
- [x] 读输入 PID 14、写目标 PID 15 经父链同属 job 13，链接输入 PID 18 属 job 16，无串线。
- [x] Make 读取 `Makefile`（`t.12:39`）未进入编译输入；目录打开 `t.12:38` 带 O_DIRECTORY，被过滤。
- [x] `t.14:108,114,120` 是失败的 stdio.h open；`t.14:125` 虽成功读开 `/usr/include/stdio.h`，但在项目外，不成为图边。
- [x] 汇编中间文件 `/tmp/cc2VfXJs.s` 的写/读/删除见 `t.13:60,113`、`t.14:72`、`t.15:24`，位于项目外，不列依赖。本次未用项目内临时产物或 O_PATH 事件证明对应分支，相关规则仍由静态分析说明。

核对中一次远端 grep 因 SSH 引号传递异常而超时，未改变采集结果；随后完整复制证据到本地，使用专用读取/检索工具完成上述核对，未因此重跑 before 或修改代码。

## 5. 已有测试只作静态旁证

已阅读 `A-buildchecker/services/buildchecker/tests/test_fullcheck.py`：其 `1, 22–31` 行说明并构造独立的微型系统调用文本，不是 fixture 实测记录。`33–38` 行覆盖兄弟进程读写合并；`40–53` 行覆盖失败 open、项目外路径、失败 exec/clone；`55–66` 行覆盖 fork 时 cwd 与内部产物；`68–90` 行覆盖多输出拒绝、数字目录 FD、unfinished 合并和子 trace 缺失。`100–105` 行用合成输入核对精确差集边。

这些现有测试的覆盖说明来自静态阅读，不把它们当成本次 fixture 实测。另行新增的 A03 测试及本次云端单项通过记录见 [A-测试说明.md](A-测试说明.md)。本次只完成 A01–A03 范围的快照验证，不包含 after/A04 或最终集成验收。
