# ADR-003：pair07 产物 URI 语法

- 状态：URI 语法已记录，实现事项待 B07 联合确认
- 日期：2026-09-21

## 背景

A07 通过逻辑 URI 在 Job 输出中引用依赖图、错误报告和日志，避免直接嵌入大体积产物。

## 决策

产物 URI 使用以下语法：

```text
artifact://pair07/<job>/<file>
```

其中 `pair07` 固定，`<job>` 使用生产任务短名，完整任务编号由产物元数据的 `producer_job_id` 保存。详细字段约束见 [Artifact URI 约定](../contracts/artifact-uri.md)。

本 ADR 不选择本地目录、HTTP 服务或对象存储。

## 待联合确认

仅以下事项待 B07 联合确认：

- URI 到实际文件或下载机制的映射；
- 产物保留期限与清理责任；
- 读取产物的鉴权方式。
