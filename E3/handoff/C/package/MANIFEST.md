# 本地提交清单

## 应纳入最终压缩包

- `E2/contracts/`
- `E2/examples/`
- `E2/docs/adr/`
- `scripts/validate_contracts.py`
- `scripts/validate_against_b07.py`
- `E3/README.md`
- `E3/分工/`
- `E3/handoff/A/`
- `E3/handoff/B/`
- `E3/handoff/C/`

## 关键入口

- A 复现：`E3/handoff/A/README.md`
- B 复现：`E3/handoff/B/README.md`
- C 复现：`E3/handoff/C/README.md`
- 验证结论：`E3/handoff/C/验证结果.md`
- 失败记录：`E3/handoff/C/失败记录.md`
- B07 确认材料：`E3/handoff/C/B07确认材料.md`
- 云端待办：`E3/handoff/C/package/CLOUD-REPLAY-PENDING.md`

## 不应纳入

- SSH 私钥、Token、密码和 Docker 登录凭据。
- Docker Desktop 本地配置。
- Docker 镜像缓存和容器文件系统导出。
- 未说明来源的临时文件。
- 个人主目录和绝对路径配置。

## 提交前检查

- JSON 文件可以解析。
- `scripts/validate_contracts.py` 返回 0。
- WSL、Docker 和统一输出的 `SHA256SUMS` 校验通过。
- B07 状态如实写为“待确认”或“已确认”。
- 云端状态如实写为“待资源下发”或“已复验”。
