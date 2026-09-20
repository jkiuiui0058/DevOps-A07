# 错误码

MD/RD 是正常完成的检测结果，应写入 `ERROR_REPORT`，不能写入 `job.error`。只有任务未能正常完成时才使用以下错误码。

| 错误码 | 含义 | 建议处理 |
| --- | --- | --- |
| `REQ_1001` | 请求不符合 Schema | 修正字段后重新提交 |
| `REQ_1002` | 不支持的任务类型 | 使用契约定义的 `job_type` |
| `BASELINE_2001` | 增量请求缺少 baseline | 先运行全量检测或提供基线 |
| `BASELINE_2002` | baseline commit 与 base commit 不一致 | 使用对应提交的历史图 |
| `BASELINE_2003` | 构建配置不一致 | 使用相同 `configuration_id` 重新生成基线 |
| `ARTIFACT_2004` | 产物不可读取或完整性校验失败 | 检查 URI、权限和 SHA-256 |
| `ENV_3001` | Docker 镜像不可用 | 由环境提供方修正镜像引用 |
| `EXEC_4001` | 构建失败 | 检查构建日志和命令 |
| `EXEC_4002` | 执行超时 | 调整时间限制或构建配置 |
| `TRACE_4003` | 无法采集构建跟踪 | 检查容器权限和跟踪工具 |
| `ANALYSIS_5001` | 分析器执行失败 | 检查分析日志 |
| `ANALYSIS_5002` | GNU Make 数据库解析失败 | 检查 Make 版本和输出 |
