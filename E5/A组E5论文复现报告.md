# A07 组 A 轨道 E5 论文复现报告

## 1. 基本信息

|字段|内容|
|---|---|
|姓名|陈婉清|
|学号|241250082|
|小组/轨道|A07 / A（BuildChecker）|
|实验日期|2026-11-03|
|GitHub 仓库|`https://github.com/jkiuiui0058/DevOps-A07`|
|运行分支|`e5`|
|源码提交|`113712960b142b34bc226eb73e8a2a77a1c01f98`|
|镜像标签|`course1027-buildchecker:241250082`|
|镜像 ID|`sha256:09f5e03129702fd74d193212ec529ade0329e692c20ab83593a24db306c3169b`|
|镜像架构|`linux/amd64`|
|镜像内 Python|3.13.14|

云主机为 Ubuntu 24.04.4 LTS、x86_64、2 vCPU，Docker Server 29.1.3。环境自检显示约 1.7 GiB 可见内存，低于 E5--E7 脚本规定的 4 GiB 必需门槛；CPU 2 核和可用磁盘约 69.1 GiB 低于建议值但不低于必需值。该限制没有被隐藏：本次构建、15 项单元测试和 E5 采集均实际成功，但环境项仍保留为待助教确认。

## 2. 参考代码与本人修改

本次使用教学包提供的以下参考内容：

- `A-buildchecker/fixtures/md-rd/`：用于演示声明依赖与实际依赖不一致的输入项目；
- `A-buildchecker/scripts/lab_cloud.py`：云主机实验入口；
- `A-buildchecker/services/buildchecker/`：BuildChecker 服务与测试；
- 《E5 A 组：从原始构建记录解释 MD/RD》操作手册。

本人没有修改 `md-rd` 样例、跟踪逻辑或预期结果。由于服务器访问 Debian 官方软件源耗时过长，本人在提交 `1137129` 中仅修改服务 Dockerfile，将容器内 Debian 软件源替换为华为云镜像站；基础镜像 digest、安装的软件包、依赖锁文件和业务代码均保持不变。

完整手册使用 `scripts/course.py` 绑定个人镜像。本仓库保留 `A-buildchecker/` 子目录结构，因此本次直接调用等价的 `scripts/lab_cloud.py`，并显式传入个人镜像 `course1027-buildchecker:241250082`。实验核心命令、隔离方式和输出结构与手册一致。

## 3. 构建与基线测试

在正式分支对应源码上执行：

```bash
python3 scripts/lab_cloud.py build \
  --image course1027-buildchecker:241250082 \
  --out work/build-formal-02 \
  --build-timeout 3600
```

构建退出码为 0，镜像检查退出码为 0，服务单元测试退出码为 0。测试结果为：

```text
...............                                                          [100%]
15 passed in 0.04s
```

构建日志确认基础镜像固定为：

```text
python:3.13-slim@sha256:f82c96458eedc847b233e582eb31336f4954b39cae020b6dcf5b3ed0e5cbcd74
```

构建证据：

- `work/build-formal-02/build/command.json`
- `work/build-formal-02/build/exit-code.json`
- `work/build-formal-02/build/stderr.log`
- `work/build-formal-02/image/stdout.log`
- `work/build-formal-02/unit-tests/stdout.log`
- `work/build-formal-02/unit-tests/exit-code.json`

## 4. E5 输入与预期矛盾

输入项目包含 `main.c`、`config.h`、`unused.h` 和 `Makefile`：

```c
#include <stdio.h>
#include "config.h"
int main(void) { printf("%d\n", VALUE); return 0; }
```

`config.h` 定义 `VALUE=1`，因此编译器必须读取它。`unused.h` 只包含注释，没有被 `main.c` 包含。Makefile 却声明：

```makefile
main.o: main.c unused.h
	$(CC) -c main.c -o main.o
```

因此实验需要比较：

- 实际编译任务读取的项目文件；
- GNU Make 解析出的 `main.o` 声明依赖。

## 5. 原始证据采集

正式执行命令为：

```bash
python3 scripts/lab_cloud.py e5 \
  --image course1027-buildchecker:241250082 \
  --out work/e5-formal-01
```

脚本在无网络容器中复制样例并执行：

```bash
make clean
strace -ff -s 4096 -o trace/t -e trace=%file,%process \
  make -p app > make-db.txt 2> build-stderr.log
./app > program-output.txt
```

E5 执行退出码为 0，`build-stderr.log` 为空，程序输出为：

```text
1
```

采集元数据记录的 UTC 时间为 `2026-11-03T11:57:57.287793+00:00`，即北京时间 2026-11-03 19:57:57。

## 6. 声明依赖证据

`make-db.txt` 第 1061 行为：

```text
main.o: main.c unused.h
```

第 1074、1078 和 1080 行的 Make 自动变量也包含 `main.c unused.h`。`trace/t.14:46` 显示 Make 对 `unused.h` 做了 `newfstatat` 存在性检查；但后续编译器进程没有打开或读取 `unused.h` 的内容。这里将 Make 的元数据检查与编译任务的实际内容读取区分开。

声明依赖集合为：

```text
D(main.o) = {main.c, unused.h}
```

## 7. 实际读取及进程归属

进程链可以从同一次 trace 中还原：

|进程/证据|行为|归属说明|
|---|---|---|
|`t.14:1`|`execve("/usr/bin/make", ["make", "-p", "app"], ...)`|Make 主进程|
|`t.14:55`|Make 创建 PID 15|启动 `main.o` 的编译 recipe|
|`t.15:1`|`cc -c main.c -o main.o`|目标明确为 `main.o`|
|`t.15:64`|cc 创建 PID 16|启动编译器前端 `cc1`|
|`t.16:1`|`cc1 ... main.c ...`|处理 `main.c` 的编译器前端|
|`t.16:67`|成功打开 `main.c`，返回 fd 3|实际读取项目源文件|
|`t.16:580`|成功打开 `config.h`，返回 fd 4|实际读取项目头文件|
|`t.15:84`|cc 创建 PID 17|启动汇编器|
|`t.17:5`|成功执行 `/usr/bin/as ... -o main.o`|生成 `main.o`|
|`t.17:23`|以创建/截断方式打开 `main.o`|写入目标文件|
|`t.14:66`、`t.18:1`|Make 创建 PID 18，执行 `cc main.o -o app`|进入 `app` 链接任务|
|`t.20:82-83`|链接器读取 `main.o`|`app` 对 `main.o` 的实际依赖|

由 `cc -c main.c -o main.o` 的命令边界以及其子进程关系，可将 PID 16 对 `config.h` 的成功读取归属于 `main.o` 编译任务，而不是链接任务。

实际项目依赖集合为：

```text
A(main.o) = {main.c, config.h}
```

## 8. MD/RD 人工结论

定义：

```text
MD = 实际依赖集合 - 声明依赖集合
RD = 声明依赖集合 - 实际依赖集合
```

得到：

|目标|实际读取的项目依赖|Make 声明|结论|
|---|---|---|---|
|`main.o`|`main.c`、`config.h`|`main.c`、`unused.h`|MD：`config.h`；RD：`unused.h`|
|`app`|`main.o`|`main.o`|一致|

精确错误集合为：

```text
MD(main.o, config.h)
RD(main.o, unused.h)
```

## 9. 与论文原型及完整实现的差异

本次为教学缩小实验，范围限制为单个 GNU Make 进程、单个编译任务和单个最终输出。实际读取只统计项目根目录内文件，系统头文件不进入 MD/RD 集合；RD 也只表示在本次构建配置和执行路径下未被编译任务读取，不能直接推广到其他条件编译配置。

E5 阶段采用人工对照 trace 与 Make 数据库得出结论，尚未在本阶段展示 E6 自动生成的实际图、声明图和 `findings.json`。自动检测、隔离修复和复检属于 E6 验收范围。

## 10. 证据索引

下表路径相对于下载后的 `E5/` 目录；服务器原始路径位于 `A-buildchecker/work/`。`work/` 被 Git 忽略，完整内容进入最终归档包。

|检查项|证据路径|结果|
|---|---|---|
|构建命令与退出码|`work/build-formal-02/build/command.json`、`exit-code.json`|退出 0|
|镜像详情|`work/build-formal-02/image/stdout.log`|镜像 ID 与架构已记录|
|单元测试|`work/build-formal-02/unit-tests/stdout.log`|15 passed|
|E5 调用信息|`work/e5-formal-01/invocation.json`|轨道 A、个人镜像|
|E5 完整命令|`work/e5-formal-01/runner/command.json`|无网络、启用 SYS_PTRACE|
|E5 退出码|`work/e5-formal-01/runner/exit-code.json`|退出 0|
|输入副本|`work/e5-formal-01/evidence/`|四个输入文件完整|
|程序输出|`work/e5-formal-01/evidence/program-output.txt`|1|
|Make 声明|`work/e5-formal-01/evidence/make-db.txt:1061`|`main.o: main.c unused.h`|
|实际读取|`work/e5-formal-01/evidence/trace/t.16:580`|成功打开 `config.h`|
|源码版本|`work/e5-formal-01/source-commit.txt`|`1137129...`|
|镜像版本|`work/e5-formal-01/image-id.txt`|`sha256:09f5e...`|

## 11. 未完成项

- 最终证据归档文件名与 SHA256 尚待填写；
- PR URL 和合并提交尚待创建后填写；
