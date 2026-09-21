# E2 Backlog

负责人先使用姓名或 GitHub ID 占位，完成后补充提交 SHA 或 PR 链接。

| ID | 工作项 | 负责人 | 产物 | 验收条件 | 状态 |
| --- | --- | --- | --- | --- | --- |
| E2-01 | 与 B07 确认配对信息 | 待认领 | `contracts/B07-INTEGRATION.md` | 双方仓库与契约责任边界明确 | DONE |
| E2-02 | 确认统一 Job 字段 | A07负责人 | `task.schema.json` | 两类 A 组任务均可表达 | DONE |
| E2-03 | 完善全量检测样例 | A07负责人 | `examples/full-check/` | 请求、受理响应和结果响应可解释 | DONE |
| E2-04 | 完善增量检测样例 | A07负责人 | `examples/incremental-check/` | 缺 baseline 时被拒绝 | DONE |
| E2-05 | 定义 MD/RD 报告 | 待认领 | `finding.schema.json`、`error-report.schema.json` | MISSING 含 position，MDFixer 能定位声明 | DONE |
| E2-06 | 确认 Artifact URI 实现 | A07/B07 | ADR 或契约更新 | B07 能实际读取一份 A07 产物 | BLOCKED |
| E2-07 | 校验有效与无效样例 | A07负责人 | `scripts/validate_against_b07.py`、`validation/B07-VALIDATION-RESULTS.md` | 有效样例通过，反例失败 | DONE |
| E2-08 | 确认错误码和失败行为 | A07/B07 | `error-codes.md` | 共享三类错误码已对齐，A07 扩展码待确认 | DOING |
| E2-09 | 记录架构决策 | 待认领 | `adr/` | 异步任务模型已与 B07 对齐 | DONE |
| E2-10 | 补全 AI 使用与个人贡献 | 全体成员 | 过程记录 | 建议、人工判断、验证和提交可追溯 | TODO |

## E3 准备

- 选择一个可稳定构建的 GNU Make/CMake 项目。
- 准备 C0、C1、C2 三个连续提交。
- 在 C1 或 C2 中注入可验证的 MD/RD。
- 与 B07 确认 Docker 镜像中的构建命令和进程跟踪权限。
