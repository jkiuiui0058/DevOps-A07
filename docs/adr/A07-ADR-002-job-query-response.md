# A07-ADR-002：Job 查询返回完整持久化资源

- 状态：提议，待 B07 确认
- 日期：2026-09-21

## 背景

[A07:ADR-001](A07-ADR-001-asynchronous-job-api.md) 确定通过 `GET /v1/jobs/{job_id}` 查询任务。A07 的 [`task.schema.json`](../contracts/task.schema.json) 区分创建请求与持久化 Job，但 B07 当前的查询视图样例与 A07 成功响应仍有差异。

## 决策

`GET /v1/jobs/{job_id}` 返回完整持久化 Job：保留创建时的原始输入，并补全 `job_id`、`status`、`execution`、`output` 和 `error`。

- 成功任务的 `error` 为 `null`。
- MD/RD 是检测结果，写入 `output` 引用的 `ERROR_REPORT`；检测到 MD/RD 时 Job 仍为 `SUCCEEDED`。
- 字段含义及创建请求边界以 [`task.schema.json`](../contracts/task.schema.json) 和 [B07 对接约定](../contracts/B07-INTEGRATION.md) 为准。

## 样例索引

| 阶段 | 现有样例 | 字段对照 |
| --- | --- | --- |
| 创建请求 | [FULL_CHECK request](../examples/full-check/request.json)、[INCREMENTAL_CHECK request](../examples/incremental-check/request.json) | 携带 `schema_version`、`trace_id`、`job_type` 和原始 `input`，不携带服务端字段 |
| 已接受 | [FULL_CHECK accepted response](../examples/full-check/accepted-response.json) | 保留请求字段，并补全 `job_id`、`status`、`execution`、`output`、`error` |
| 查询成功 | [FULL_CHECK succeeded response](../examples/full-check/succeeded-response.json)、[INCREMENTAL_CHECK succeeded response](../examples/incremental-check/succeeded-response.json) | 保留原始 `input`，以 `status`、`execution`、`output`、`error` 表示最终结果 |

## 影响

客户端可用同一查询结果还原创建设定、检查执行状态并读取产物。该响应形态是 A07 提案，须在 B07 调整或确认查询视图样例后成为双方最终契约。
