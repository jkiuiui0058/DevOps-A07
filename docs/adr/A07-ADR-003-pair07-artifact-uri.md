# A07-ADR-003：pair07 产物 URI 语法

- 状态：已接受；实现事项由 PAIR07:ADR-001 最终确认
- 日期：2026-09-21

## 背景

A07 通过逻辑 URI 在 Job 输出中引用依赖图、错误报告和日志，避免直接嵌入大体积产物。

## 决策

产物 URI 使用以下语法：

```text
artifact://pair07/<job>/<file>
```

其中 `pair07` 固定，`<job>` 使用生产任务短名，完整任务编号由产物元数据的 `producer_job_id` 保存。详细字段约束见 [Artifact URI 约定](../contracts/artifact-uri.md)。

读取方式、治理和权限已由 [PAIR07:ADR-001](PAIR07-ADR-001-artifact-governance-and-error-domains.md) 确认为 HTTP 主入口、平台统一 GC、终态后保留 30 天且引用存在时不得删除、pair 内只读互访。

## 决策边界

本 ADR 仅定义 A07 的 URI 语法；双方共同约束以 PAIR07:ADR-001 为准。
