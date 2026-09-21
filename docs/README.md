# E2 文档索引

本目录保存 A07 组在 E2 阶段的接口契约、设计决策和过程记录。

## 1. 接口契约 `contracts/`

- `task.schema.json`：统一异步任务模型，覆盖全量检测与增量检测。
- `artifact.schema.json`：依赖图、错误报告、日志等产物的引用格式。
- `finding.schema.json`：Missing Dependency 和 Redundant Dependency 的统一记录格式。
- `error-report.schema.json`：A07 输出、B07 MDFixer 消费的完整检测报告。
- `error-codes.md`：系统执行错误的编号和语义。
- `artifact-uri.md`：A/B 组交换文件时采用的 URI 约定。
- `B07-INTEGRATION.md`：与配对仓库现有契约的责任边界及差异处理。
- `B07-README-UPDATE.md`：已提供 A07 地址及 `pair07` 命名，供 B07 更新 README。

## 2. 交换样例 `examples/`

- `full-check/`：BuildChecker 全量检测请求和响应。
- `incremental-check/`：EChecker 增量检测请求和响应。
- `invalid/`：应被 Schema 或服务拒绝的反例。

样例中的仓库地址、提交 SHA 和产物 URI 均为占位内容，联调前由 A/B 配对组共同替换。

## 3. 设计决策 `adr/`

记录关键方案、选择理由、替代方案和代价。改变公共字段、状态或产物读取方式时，应新增或更新 ADR。

## 4. 计划与过程记录

- `planning/BACKLOG.md`：E2 工作项、负责人和验收条件。
- `AI_USAGE.md`：AI 建议、人工判断及验证记录。
- `contributions/README.md`：成员贡献和提交证据。

## E2 最小验收

1. 有效的全量与增量请求能够通过 Schema 校验。
2. 删除增量请求中的 `baseline` 后必须校验失败。
3. 未知 `job_type` 必须校验失败。
4. 检测到 MD/RD 时任务仍可为 `SUCCEEDED`。
5. B 组能够根据 Artifact URI 读取 A 组输出的报告。

可在仓库根目录运行无第三方依赖的关键字段检查：

```text
python scripts/validate_contracts.py
../E2-B07/.venv/bin/python scripts/validate_against_b07.py --b07-root ../E2-B07
```
