# B：CI 证据索引

所有链接均为 GitHub 的真实运行记录；下载的 artifact 放在 `E7/B/evidence/ci-runs/`。

| 阶段 | PR / SHA | 实际结果 | 运行证据 | 本地归档 |
|---|---|---|---|---|
| 正常 main | PR #5，merge commit `13ac0aa39e5c29157fec6251f4c7bc027b4624c5` | SUCCESS | https://github.com/jkiuiui0058/DevOps-A07/actions/runs/43385151022 | 待下载 |
| 同一 PR 故意错误期望 | PR #6，`630bdf95ee0bf586559bc76bffc4b56eab8183f0` | FAILURE；服务单元测试退出 1，gate 总体失败 | https://github.com/jkiuiui0058/DevOps-A07/actions/runs/43385279812 | `failure-43385279812/` |
| 同一 PR 恢复正确期望 | PR #6，待本次提交推送 | PENDING | PENDING | PENDING |

## 保护规则权限核验

GitHub API 的仓库权限返回：`push=true`、`admin=false`。查询 `main` 分支保护规则返回 404，说明当前身份无法读取/配置该管理员资源。真实 GitHub Actions App ID 为 `15368`（slug `github-actions`）。因此本记录不把“策略拒绝合并”写成已完成；PR #6 在失败时保持 OPEN 且 `mergeStateStatus=UNSTABLE`，其状态快照为 `failure-43385279812/pr-status.json`。
