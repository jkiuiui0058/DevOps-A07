# B：声明依赖、差集与修复审阅

## B01：声明图

`declaration_graph` 位于 `A-buildchecker/services/buildchecker/buildchecker/fullcheck.py:237-301`。它只解析 `make -p` 的 `# Files` 段，跳过注释、模式规则和 `# Not a target` 条目；通过 `shlex` 分词，区分普通与 order-only prerequisites，并展开 `.PHONY` 的普通前置条件。每条边保留 `source=make_database`、`artifact=make-db.txt`、行号及原始声明。

保存的修复前 `declared-graph.json` 中，`main.o` 声明依赖 `main.c`、`unused.h`，两者均锚定在 `make-db.txt:1053`：`main.o: main.c unused.h`。这正是 E5 人工检查的声明侧证据。

## B02：MD/RD 差集与证据

`analyze` 位于 `fullcheck.py:304-329`。对目标的实际依赖集合 `A` 和声明依赖集合 `D`：`MD=A-D` 生成 `MISSING`，携带成功读打开证据与目标写出证据；`RD=D-A` 生成 `REDUNDANT`，携带 Make 数据库声明锚点。仅项目内路径参与比较。

修复前报告 `trace_id=e6-0f5455e1175e4021b17f344190693539`，且状态为 `SUCCEEDED`、clean/build 均为 0。精确发现为：

| 类型 | target | dependency | 证据 |
| --- | --- | --- | --- |
| `MISSING` | `main.o` | `config.h` | 读取 `trace/t.14:579`（PID 14，`openat`）；写出 `trace/t.15:24`（PID 15，`openat`） |
| `REDUNDANT` | `main.o` | `unused.h` | 声明 `make-db.txt:1053`：`main.o: main.c unused.h` |

与 E5 人工结论 `MISSING(main.o, config.h)`、`REDUNDANT(main.o, unused.h)` 一致。`trace_id` 是一次完整报告的标识；边级证据才包含 `trace_file`、`line`、`pid`、`operation` 或 Make 数据库的 `artifact`、`line`、`declaration`。

## B03：隔离修复审阅

保存的前后 Makefile 差异仅为：

```diff
-main.o: main.c unused.h
+main.o: main.c config.h
```

`input_sha256` 对照显示仅 `Makefile` 变化；`main.c`、`config.h`、`unused.h` 的哈希保持不变。修复后声明锚点为 `make-db.txt:1045`，报告 `trace_id=e6-6e5943eb3d8e486b970fd01b9044c5e5`，状态 `SUCCEEDED`、findings 为空。自动校验结论为 `passed=true`、`before_findings=2`、`after_findings=0`、`changed_inputs=["Makefile"]`。

原始 fixture 未被改动；修复仅发生于隔离副本。完整运行证据由 C 的归档交付，本说明只引用已保存的报告、图和 trace 锚点。

## B04：新增测试

新增 `A-buildchecker/services/buildchecker/tests/test_e6_b.py`，使用独立的 Make/编译 trace 和 Make 数据库，覆盖已有测试未逐字段验证的证据契约：MD 必须保留读与写锚点，RD 必须保留 `make_database`、`make-db.txt`、行号和原始声明。课程导入的 `fullcheck.py` 未被作为个人从零实现申报。
