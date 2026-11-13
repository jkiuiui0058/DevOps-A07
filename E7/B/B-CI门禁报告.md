# B：CI 门禁报告

负责人：B（241250005）  
轨道：A / BuildChecker

## 已完成的仓库内交付

- 新增 `A-buildchecker/services/buildchecker/tests/test_e7_b.py`，包括两项 CI 边界回归：拒绝把证据目录放在源 fixture 内、将检测器版本固定为可追溯的 CI 断言。
- 将 workflow 放在 GitHub Actions 可识别的根目录 `.github/workflows/e7-quality-gate.yml`，并适配实际项目目录 `A-buildchecker/`、镜像构建上下文、扫描范围和 artifact 路径。
- 工作流执行独立 Oracle、源码与历史扫描、镜像构建/扫描和完整八项 gate，所有结果均归档 `work/ci/` 14 天。
- 移除嵌套的旧 workflow 和 `fail_demo` 输入。失败演示只能在同一 PR 写入一条错误测试期望，不能以手工开关替代。

## 本地验证

服务测试 15 项通过（含本次新增 2 项），独立 Oracle 测试 7 项通过，Python 语法检查通过。CI 的完整容器验证由 GitHub Actions 运行并通过 artifact 留证。

## 云端闭环状态

| 项目 | 状态 | 证据 |
|---|---|---|
| B01：测试与 workflow 接入 | PASS | PR #5 与 Actions 检查 |
| B02：正常 main CI | PASS | run 43385151022（commit `13ac0aa`） |
| B03：同一 PR 失败与恢复 | PASS | PR #6 在错误期望下失败，恢复正确期望后 run 43385546575 成功 |
| B03：保护规则 | PENDING（权限不足） | 当前身份有 push、无 admin，不能配置或声称已配置保护规则 |
| B04：成品包 | PASS | normal、failure 和 recovery artifact 已下载并归档；合并记录见 PR #6 |

> 云端 URL、运行 ID、规则 JSON 和合并记录只在实际操作后填写，绝不以预期代替结果。
