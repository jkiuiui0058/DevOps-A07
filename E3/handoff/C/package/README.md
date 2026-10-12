# A07 E3 本地交付包

本目录汇总 E3 在学校云资源下发前可以完成的交付内容。WSL、A/B 独立 Docker 和 C 统一 Docker 均已验证通过。

## 当前可交付

- A 的 MD/RD 固定项目、人工答案和复现说明。
- B 的 C0/C1/C2 bundle、真实 SHA 和复现说明。
- C 的 WSL、Docker、统一环境及 `strace` 证据。
- E2 契约及其本地校验结果。
- 使用真实项目版本填写的 E3 FULL_CHECK、INCREMENTAL_CHECK 请求样例。
- 提供给 B07 的可消费性确认材料。

## 尚待补充

- 学校云服务器上的同镜像复验。
- B07 的明确确认回复。

这两项当前均标为待完成，不影响本地基线、契约样例和复现材料提交，也不得写成已完成。

## 真实样例说明

`examples/` 中的文件用于表达真实 E3 输入和人工预期：

- `full-check/request.json`：A 的固定 MD/RD 项目。
- `incremental-check/c0-to-c1-request.json`：C0 到 C1 的新增 include 与 MD。
- `incremental-check/c1-to-c2-request.json`：C1 到 C2 的编译命令变化。
- `error-report.json`：A 的人工 Oracle，不是 BuildChecker 实际运行结果。

请求中的 Artifact URI 是按照 E2 规则预留的交接位置。尚未由实际服务生成的 Artifact 不应描述为已经存在。
