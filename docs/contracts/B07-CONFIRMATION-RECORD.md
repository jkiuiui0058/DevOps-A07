# B07 ERROR_REPORT 确认记录

## 已确认内容

B07 的 MDFixer 消费 `MISSING`，忽略 `REDUNDANT`。每条 `MISSING` 必须包含：

- `type`、`target`、`dependency`；
- 40 位完整小写十六进制 `commit`；
- `position.file` 与 `position.line`；
- `detector`，取值仅为 `BUILDCHECKER`、`ECHECKER`、`INSTRUCTOR_ORACLE`。

MDFixer 消费前必须确认 finding 的 `commit` 与 REPAIR 输入的 `repository.commit` 完全一致。

上述结构由 [`finding.schema.json`](finding.schema.json) 和 [`error-report.schema.json`](error-report.schema.json) 约束；[`examples/error-report.json`](../examples/error-report.json) 是最终交换样例，不在本文件重复 JSON。

## 范围说明

`REDUNDANT` 的下游用途不在当前 E2 修复范围内。“忽略 `REDUNDANT`”仅描述本阶段 MDFixer 的消费边界，不构成新的未协商策略。完整责任边界见 [A07 与 B07 对接约定](B07-INTEGRATION.md)。
