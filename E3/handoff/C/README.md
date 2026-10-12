# E3 Role C：统一复现与交付说明

本目录保存 C 对 A、B 交付材料的接收检查、WSL 预验证、Docker 正式复现、统一环境验证和后续 B07 确认材料。

## 当前结论

- A 的 MD/RD 基线已在 WSL Ubuntu 20.04 和独立 Ubuntu 24.04 Docker 镜像中复现。
- B 的 C0/C1/C2 基线已在 WSL Ubuntu 20.04 和独立 Ubuntu 24.04 Docker 镜像中复现。
- C 的统一 Ubuntu 24.04 镜像连续完成 A、B、E2 契约校验和 `strace` 原始证据采集，容器退出码为 `0`。
- WSL、独立 Docker 和统一 Docker 的关键程序输出一致。
- 云服务器复验和 B07 可消费性确认尚未完成，不能标记为已确认。

## 目录

```text
C/
├─ README.md
├─ 环境信息.md
├─ 验证结果.md
├─ 失败记录.md
├─ B07确认材料.md
├─ docker/
│  ├─ Dockerfile
│  └─ run-all.sh
└─ evidence/
   ├─ wsl/
   ├─ docker/
   └─ unified/
```

## 统一复现

在仓库根目录构建：

```bash
docker build \
  -f E3/handoff/C/docker/Dockerfile \
  -t a07-e3-unified:ubuntu24.04 \
  .
```

运行：

```bash
docker run \
  --name a07-e3-unified-run \
  --cap-add SYS_PTRACE \
  --security-opt seccomp=unconfined \
  a07-e3-unified:ubuntu24.04
```

容器中的 `/lab/output` 包含环境、MD/RD、C0/C1/C2、契约校验、系统调用跟踪和校验值。运行结束后可执行：

```bash
docker cp a07-e3-unified-run:/lab/output/. ./unified-output/
```

`SYS_PTRACE` 和放宽的 seccomp 配置只用于课程样例的 `strace` 采集，不应直接用于不受信任项目。

## 证据入口

- WSL 预验证：`evidence/wsl/`
- A、B 独立 Docker 验证：`evidence/docker/`
- C 统一 Docker 验证：`evidence/unified/`
- 统一运行的最终输出：`evidence/unified/output/`
- 首次统一运行失败证据：`evidence/unified/failed-output/`

最终提交前需完成云服务器复验、真实 E3 请求样例整理和 B07 可消费性确认。
