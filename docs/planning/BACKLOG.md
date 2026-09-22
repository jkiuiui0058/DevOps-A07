# E2 Backlog

| ID | 工作项 |产物 | 验收条件 | 状态 |
| --- | --- | --- | --- | --- |
| E2-01 | 与 B07 确认配对信息 | `contracts/B07-INTEGRATION.md` | 双方仓库与契约责任边界明确 | DONE |
| E2-02 | 确认统一 Job 字段 |`task.schema.json` | 两类 A 组任务均可表达 | DONE |
| E2-03 | 完善全量检测样例 |`examples/full-check/` | 请求、受理响应和结果响应可解释 | DONE |
| E2-04 | 完善增量检测样例 |`examples/incremental-check/` | 缺 baseline 时被拒绝 | DONE |
| E2-05 | 定义 MD/RD 报告 |`finding.schema.json`、`error-report.schema.json` | MISSING 含 position，MDFixer 能定位声明 | DONE |
| E2-06 | 确认 Artifact URI 读取与治理契约 | `adr/PAIR07-ADR-001-artifact-governance-and-error-domains.md` | PAIR07 ADR 已约定 HTTP 读取、保留期与权限；服务与 GC 实现留至 E12 | DONE |
| E2-07 | 校验有效与无效样例 |`scripts/validate_against_b07.py`、`validation/B07-VALIDATION-RESULTS.md` | 有效样例通过，反例失败 | DONE |
| E2-08 | 确认错误码和失败行为 |`error-codes.md` | 前缀归属和消费者容忍未知码已确认 | DONE |
| E2-09 | 记录架构决策 |`adr/` | 异步任务模型已与 B07 对齐 | DONE |
| E2-10 | 补全 AI 使用与个人贡献 |`AI_USAGE.md`、`contributions/E2贡献汇总.md` | 建议、人工判断、验证和提交可追溯 | DONE |

## E3 准备

- 选择一个可稳定构建的 GNU Make/CMake 项目。
- 准备 C0、C1、C2 三个连续提交。
- 在 C1 或 C2 中注入可验证的 MD/RD。
- 与 B07 确认 Docker 镜像中的构建命令和进程跟踪权限。
