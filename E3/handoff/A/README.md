# E3 Role A：固定版本的 MD/RD 基线

本目录是 A07 在 E3 中交给 C 的独立 GNU Make/C 复现材料。它与
`E3/handoff/B/` 使用同一类最小项目思路，但拥有独立的源码副本和 Git 历史，
不会修改 B 的 C0/C1/C2 实验。

## 目录

```text
A/
├── Dockerfile
├── README.md
├── metadata.json
├── repository.bundle
├── run-experiments.sh
├── source/
│   ├── LICENSE
│   ├── Makefile
│   ├── config.h
│   ├── main.c
│   └── unused.h
├── oracle/
│   ├── expected-findings.json
│   └── reasoning.md
├── logs/
│   ├── baseline.log
│   ├── md-incremental.log
│   ├── md-clean.log
│   ├── rd-incremental.log
│   └── replay.log
└── evidence/
    └── makefile-numbered.txt
```

## 固定版本与来源

- 项目来源：A07 为课程 E3 创建的最小 GNU Make/C 教学样例。
- 独立 fixture commit：见 `metadata.json` 的 `fixture_bundle_commit`。
- A07 固定仓库 commit：见 `metadata.json` 的 `fixed_parent_commit`。
- 许可证：`source/LICENSE`。项目没有第三方源代码依赖。
- 分析范围：只分析项目自己的 `config.h` 和 `unused.h`，排除 `stdio.h` 等系统头文件。

## 构建命令

```text
make clean
make
./app
```

`make` 生成 `main.o` 和 `app`，`./app` 输出当前 `BASE` 值。

## 复现实验

直接在本机运行：

```bash
./run-experiments.sh
```

使用统一 Ubuntu 环境运行：

```bash
docker build -t e3-a-md-rd .
docker run --rm e3-a-md-rd
```

脚本在临时目录中复制 `source/`，不会修改提交中的固定源码。脚本在修改 `unused.h`
前等待 1 秒，避免文件系统时间精度导致 GNU Make 看不到时间变化。

## 预期行为

| 场景 | 操作 | 预期输出 | 结论 |
| --- | --- | ---: | --- |
| 基线 | `make clean && make && ./app` | `10` | 初始构建 |
| MD 增量 | 把 `config.h` 的 `BASE` 改为 `12`，执行 `make` | `10` | `config.h` 实际被包含但未声明，复用旧目标 |
| MD clean | 在同一修改后执行 `make clean && make` | `12` | clean build 读取了新头文件 |
| RD 增量 | clean build 后把 `unused.h` 的 `UNUSED` 改为 `1`，执行 `make --debug=b` | `10` | `main.o` 被重新构建，但 `unused.h` 未被 `main.c` 使用 |

## 人工标准答案

`oracle/expected-findings.json` 遵循 E2 的 Finding/ERROR_REPORT 结构：

- `MISSING`：`main.o` 实际需要 `config.h`，Makefile 的声明中缺少它。
- `REDUNDANT`：Makefile 声明 `unused.h`，但 `main.c` 没有包含它。
- `detector` 使用 `INSTRUCTOR_ORACLE`，因为这些是固定实验的人工标准答案。
- 两条 finding 都定位到 Makefile 第 13 行，并关联固定 A07 commit。

`oracle/reasoning.md` 说明了每条 finding 的判断依据，`logs/` 保存了实际命令和输出。

## 交给 C 的验收点

C 可以按 README 重跑脚本，核对：

1. 修改 `config.h` 后普通构建输出仍为 `10`，clean build 输出变为 `12`。
2. 修改 `unused.h` 后日志出现 `Prerequisite 'unused.h' is newer than target 'main.o'`，并重新执行编译命令。
3. `oracle/expected-findings.json` 中的 target、dependency、位置和 commit 能在源码与日志中找到。
4. `repository.bundle` 可以恢复独立 fixture 历史。
