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
- 平台共享错误码前缀为 `ENV_*`、`EXEC_*`，新增编码须双方确认；`ANALYSIS_*` 归 A07，可由 A07 扩展。消费者必须原样记录并容忍未知错误码。
- Artifact URI 使用 `artifact://<pair>/<job>/<file>`。A07/B07 使用 `pair07` 作为 pair 段。
- Artifact 通过 `GET /v1/artifacts/{pair}/{job}/{file}` 读取；pair 内只读互访，跨 pair 返回 403。
- `sha256` 使用 64 位小写十六进制；下载响应通过 `X-Artifact-Sha256` 提供校验值。
- 产物由平台统一 GC，Job 终态后保留 30 天；仍被任一 Job 引用的产物不得删除。

## 公共 Schema 版本同步

- 当前 `schema_version` 保持精确常量 `1.0`，不改为可静默接受不同小版本的范围匹配。
- 任何公共 Schema 变更都必须先由发起方创建 backlog 或 ADR 条目，经 A07/B07 确认后再合入。
- 变更发起方负责递增 `schema_version`，并在同一提交中更新全部相关样例；双方必须同步该版本后才视为契约完成。

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

## DRAFT → FULL_CHECK 字段映射

FULL_CHECK 的输入由完整 DRAFT Job 生成，而不只读取 `output`。映射方必须先确认 DRAFT 为 `SUCCEEDED`、`error` 为 `null`，并沿用同一 `trace_id`。

| FULL_CHECK 字段 | DRAFT 来源 | 映射规则 |
| --- | --- | --- |
| `input.repository` | `input.repository` | 原样传递仓库 URL 和完整 commit |
| `input.commit` | `input.repository.commit` | 原样传递，并与 `repository.commit` 保持一致 |
| `input.environment.image` | `output.image_ref` | 使用 DRAFT 成功构建并验证的镜像引用 |
| `input.environment.project_root` | `input.build.workdir` | 使用镜像内构建工作目录；示例为 `/app` |
| `input.build.build_command` | `input.build.command` | 原样传递 DRAFT 实际采用的构建命令 |
| `input.build.verify_command` | `input.verify.command` | 原样传递 DRAFT 的验证命令 |
| `input.build.clean_command` | A07 FULL_CHECK 配置 | DRAFT 没有对应字段；由 A07 针对项目明确提供，禁止从 `final_build` 推断 |
| `input.build.timeout_seconds` | `input.time_limit` | 使用 DRAFT 时间上限，或由 A07 显式收紧；不得超过平台上限 |
| `input.configuration_id` | A07 检测配置 | 由 A07 明确指定，用于区分编译器、参数和检测模式 |
| `input.idempotency_key` | A07 创建 FULL_CHECK 时生成 | 不复用 DRAFT 的幂等键 |

`output.dockerfile`、`output.rounds`、`output.final_build` 和 `output.final_verify` 用于审计 DRAFT 过程，不直接复制到 FULL_CHECK 输入。若 `output.image_ref`、`input.build.workdir`、构建命令或验证命令缺失，平台不得创建 FULL_CHECK。

## 决策记录命名

- A07 单方决策使用 `A07-ADR-NNN`；B07 单方决策使用 `B07-ADR-NNNN`；共同决策使用 `PAIR07-ADR-NNN`。
- 跨组引用必须携带组名前缀，例如 `A07:ADR-002`、`B07:ADR-0002`。
- J1–J3 的共同结论记录于 [`PAIR07-ADR-001`](../adr/PAIR07-ADR-001-artifact-governance-and-error-domains.md)。
