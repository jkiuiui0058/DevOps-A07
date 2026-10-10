# A07 MD/RD 人工标准答案

分析范围只包含项目自己的源码头文件，排除 `stdio.h` 等系统头文件。

## MISSING: config.h

`main.c` 包含 `config.h`，但 Makefile 的 `main.o` 规则只声明了 `main.c unused.h`。
第一次构建后把 `config.h` 的 `BASE` 从 10 改为 12，再执行普通 `make`，Make 不会重建
`main.o`，程序仍输出 10；执行 `make clean && make` 后程序输出 12。这个行为证明
`config.h` 是实际依赖但未声明，Finding 类型为 `MISSING`。

## REDUNDANT: unused.h

Makefile 声明 `unused.h` 是 `main.o` 的依赖，但 `main.c` 没有包含它。先 clean build，
再把 `unused.h` 从 `UNUSED 0` 改为 `UNUSED 1` 并执行 `make --debug=b`，日志会显示
`main.o` 被重新构建，但程序输出仍为 10。这个行为证明 `unused.h` 是未使用的声明依赖，
Finding 类型为 `REDUNDANT`。

人工答案来源标记为 `INSTRUCTOR_ORACLE`，证据来自固定源码、Makefile 和本目录日志。
