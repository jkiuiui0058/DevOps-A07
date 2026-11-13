# C：测试与运行记录

## 贡献与新增覆盖

新增 `A-buildchecker/tests/e7/test_e7_c_boundary.py`。原六项独立判定未单独覆盖“错误集合正确，但同一发现被重复列出”的边界。新增测试先确认精确两条发现被接受，再重复添加其中一条，要求抛出 `Oracle mismatch`。完整错误集合不变，但数量不再精确，故必须拒绝。

输入为合成报告，不是真实构建 trace；本次没有修改检测算法。新增测试在根目录 workflow 的 unittest discover 中自动执行。

## 运行版本

| 项目 | 实际记录 |
|---|---|
| 分支 | e7-c |
| 运行源码 SHA | 04ddd8f9ca73342bad56412a0b54e81b70227d5f |
| 运行时工作区 | 干净，见 worktree-status.txt |
| 镜像标签 | course1027-buildchecker:e7-c |
| 镜像 ID | sha256:bc0561cdd10505386aaffe78043acda26593541d1f7818eb064946966fdf4d8c |
| Docker 客户端/服务端 | 29.1.3 / 29.1.3 |
| 运行平台 | linux/amd64 |
| 依赖锁文件 | A-buildchecker/requirements-dev.lock |
| 本地证据目录 | E7/C/evidence/ |

镜像和原始运行对应上述源码提交；之后写入文档或核验脚本的提交不是本次镜像源码版本。日志目录名用于标识运行，不单凭其推断时区。

## 实际结果

| 检查 | 结果 | 证据（相对 E7/C） |
|---|---|---|
| 本机原有判定 | 6 项通过，退出 0 | 01-baseline-oracle.log |
| 新增定向测试 | 1 项通过，退出 0 | 02-new-boundary.log |
| 本机完整判定 | 7 项通过，退出 0 | 03-all-oracle.log |
| 云端完整判定 | 7 项通过，退出 0 | evidence/oracle.log、oracle-exit.txt |
| 构建与服务测试 | 21 项通过，退出 0 | evidence/build-console.log、build-exit.txt |
| 完整 gate | 八项 passed=true，整体退出 0 | evidence/run/gate/、gate-exit.txt |
| 下载后离线核验 | 通过；JSON/CSV 一致、三次输入相同、fixed 仅 Makefile 变化 | 04-evidence-verification.json |

逐场景结果及原始文件保存在 `evidence/run/gate/<case>/`。服务测试的 21 项与宿主独立判定的 7 项属于不同测试入口，分别记录。

离线核验命令：`python E7/C/verify_evidence.py`。脚本复核下载文件及报告，不代表重新执行容器。`SHA256SUMS.json` 是下载后本地文件完整性基准，不是云端生成的签名或传输前清单。

## 补充收尾状态

C 的 PR #8 已合并；随后 PR #9 补做的实际策略拒绝日志已保存，退出 1，同一 PR 恢复并合并，最终 main CI 43428975185 成功。记录见 `e7-rejection/github-records.json`。新三阶段 artifact 与完整保护 JSON 已下载并通过 verify_closure.py 核验，结果见 05-closure-verification.json；最终归档见提交说明。

## 原运行范围与限制

- A 的代码及 B 的既有代码已包含在本次基线；当前通过结果是 C 分支验收，最终 main CI 已另行核对成功，原运行目录仍只对应上述 C 源码；新 CI artifact 已另行保存在 e7-rejection/，不覆盖本轮原始运行目录。
- B 的版本字符串断言失败/恢复已留证，旧报告当时缺少拦截证据；后续 PR #9 已补实际策略拒绝和恢复，完整规则 JSON 已保存并核验。
- 本地验证和门禁证据已汇总；收尾文档尚需通过个人分支正常 PR 提交，不宣称原论文全量基准通过。
