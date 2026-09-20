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

## 约定

1. Job 响应只保存产物元数据和 URI，大日志及依赖图不直接放入响应。
2. 每个 URI 必须能由 A/B 配对组约定的解析器或下载接口读取。
3. 产物应记录 `producer_job_id`、媒体类型、完整 commit 和 `configuration_id`。
4. 跨机器传输时建议附带 SHA-256。
5. URI 到实际文件或下载地址的映射方式仍需与 B07 组确认。
6. A07/B07 使用 `pair07` 作为 `<pair>`；`<job>` 使用生产任务的短名，完整任务编号保存在 `producer_job_id`。

## 待确认

- 本地共享目录、HTTP 下载接口或对象存储三者选择哪一种。
- 产物保留时间和清理责任。
- B 组是否需要鉴权信息。
