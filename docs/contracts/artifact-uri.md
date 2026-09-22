# Artifact URI 约定

## 格式

E2 暂定使用以下逻辑 URI：

```text
artifact://{pair_id}/{job_id}/{file_name}
```

示例：

```text
artifact://pair07/full01/error_report.json
```

## 读取入口

`artifact://pair07/<job>/<file>` 是稳定的逻辑标识。实际读取统一映射为：

```http
GET /v1/artifacts/{pair}/{job}/{file}
```

- `200 OK`：响应 `Content-Type: <media_type>`、`X-Artifact-Sha256: <sha256>`，body 为产物字节流；
- `404 Not Found`：产物不存在或已超过保留期；
- `403 Forbidden`：请求访问其他 pair 的产物。

HTTP 是主读取入口。共享目录仅允许作为部署内部的可选存储实现，不得成为跨组契约或要求消费者直接访问生产方存储。

## E2 读取样例（无需部署服务）

E2 通过以下契约样例证明 B07 能解释读取过程，不要求启动 HTTP 服务。给定 A07 Job 输出中的引用：

```json
{
  "type": "ERROR_REPORT",
  "uri": "artifact://pair07/full01/error_report.json",
  "media_type": "application/json",
  "producer_job_id": "job-full01",
  "sha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
}
```

B07 按以下步骤消费：

1. 校验 URI 的 pair 为 `pair07`，并解析出 `job=full01`、`file=error_report.json`。
2. 将 URI 映射为 `GET /v1/artifacts/pair07/full01/error_report.json`。
3. 预期服务返回 `200 OK`、`Content-Type: application/json` 和与元数据一致的 `X-Artifact-Sha256`。
4. 对响应字节计算 SHA-256；与响应头及引用元数据不一致时拒绝消费。
5. 按 `application/json` 解析，并使用 [`error-report.schema.json`](error-report.schema.json) 校验后交给 MDFixer；MDFixer 只消费 `MISSING`。

此样例只验证 URI 到请求及校验步骤的可解释性。HTTP 服务与平台 GC 在 E12 实现。

## 治理与权限

- 产物由平台统一 GC，不由 A07/B07 各自清理；
- Job 进入终态后保留 30 天；
- **只要仍有 Job 引用某个产物，该产物就不得删除**；引用不变式优先于 30 天期限；
- A07 与 B07 在 `pair07` 内只读互访，跨 pair 访问必须拒绝。

## 约定

1. Job 响应只保存产物元数据和 URI，大日志及依赖图不直接放入响应。
2. 每个 URI 必须能由 A/B 配对组约定的解析器或下载接口读取。
3. 产物应记录 `producer_job_id`、媒体类型、完整 commit 和 `configuration_id`。
4. HTTP 响应必须附带 `X-Artifact-Sha256`；产物元数据中的 `sha256` 用于读取后校验。
5. URI 到下载地址的映射、保留和权限以本文件上述规则为最终约定。
6. A07/B07 使用 `pair07` 作为 `<pair>`；`<job>` 使用生产任务的短名，完整任务编号保存在 `producer_job_id`。
