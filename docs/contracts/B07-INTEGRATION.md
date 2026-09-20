# A07 与 B07 对接约定

配对仓库：[Cedar-bog/DevOps-B07](https://github.com/Cedar-bog/DevOps-B07)。本文件记录 2026-09-20 对 B07 `main` 分支契约的对齐结果。

## 责任边界

| 内容 | 责任方 |
| --- | --- |
| 四类任务公共 Job 外壳 | A07/B07 共同确认，B07 当前提供统一 Schema 初稿 |
| `FULL_CHECK`、`INCREMENTAL_CHECK` 专有输入 | A07 |
| 完整 `ERROR_REPORT` 结构 | A07 |
| `DRAFT`、`REPAIR` 专有输入输出 | B07 |
| Artifact URI、状态与公共错误码 | A07/B07 共同确认 |

## 已对齐内容

- 状态使用 `QUEUED`、`RUNNING`、`SUCCEEDED`、`FAILED`、`TIMED_OUT`、`CANCELLED`。
- `job_id` 采用 `job-*`，`trace_id` 采用 `trace-*`。
- 创建请求不携带 `job_id`；服务端返回 HTTP 202 后生成 `job_id`。
- 创建请求携带 `idempotency_key`，同一键的重复提交不得创建重复任务。
- MD/RD 写入 `output` 的 `ERROR_REPORT`，不会使正常完成的检测任务变成 `FAILED`。
- 共享系统错误码至少包括 `ENV_3002`、`EXEC_4002`、`ANALYSIS_5001`。
- Artifact URI 使用 `artifact://<pair>/<job>/<file>`。A07/B07 使用 `pair07` 作为 pair 段。
- `sha256` 使用 64 位小写十六进制，跨组传递时建议提供。

## MDFixer 对 ERROR_REPORT 的最低要求

B07 只消费 `MISSING`，忽略 `REDUNDANT`。每条 `MISSING` 必须提供：

- `type`、`target`、`dependency`、完整小写 commit SHA；
- `position.file` 与 `position.line`，可选 `position.declaration`；
- `detector` 使用 `BUILDCHECKER`、`ECHECKER` 或 `INSTRUCTOR_ORACLE`。

MDFixer 消费前必须验证 finding 的 commit 与 REPAIR 输入的 `repository.commit` 完全一致。

## 创建请求与 Job 资源

B07 的统一 `task.schema.json` 描述持久化后的完整 Job，因此要求 `job_id`、`status`、`execution` 等字段。A07 的创建请求样例只描述 POST 请求体，不携带服务端字段。双方联调时按以下两层处理：

1. POST 请求：`trace_id`、`job_type`、`input.idempotency_key` 和服务专有输入。
2. Job 查询结果：补全 `job_id`、`status`、`execution`、`output` 和 `error`。

## 尚待联合确认

- `artifact://` 到实际文件或 HTTP 下载地址的解析器实现。
- 产物保留期限和清理责任。
- A07 专有错误码是否加入 B07 的共享枚举。
- 公共 Schema 最终存放在哪个仓库，以及如何同步版本。
