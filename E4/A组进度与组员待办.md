# E4 A 组进度与组员待办

更新时间：2026-10-20

## 组长已完成

- 华为云服务器已安装并验证 Docker、Docker Compose、Buildx、Git、Make、Python 3。
- 安全组仅需开放 SSH 端口；不要开放 Docker API 的 2375/2376 端口。
- A 组 BuildChecker 模板已放到服务器并完成试跑。
- 根据助教“2 GB 内存即可”的配置要求，将 `scripts/doctor.py` 的最低可见内存从 3.5 GiB 调整为 1.5 GiB。2 GB 实例在 Linux 中显示约 1.7 GiB，属于正常现象。
- Docker 镜像构建时 Debian 官方源下载过慢，已改用华为云 Debian 镜像源；依赖名称和版本策略未改变。
- 学号 `241098114` 的个人克隆和仓库级 Git 身份已配置。

## 当前状态

- `make doctor` 已通过，`problems` 为空。
- Docker 镜像构建成功，单元测试结果为 `3 passed`。
- 冒烟测试 `passed: true`，密钥扫描未发现问题。
- 组长试跑证据目录：`work/20261020-200434/`。
- 每位组员仍需在自己的目录独立运行，不能共用组长的证据代替个人复现。

## 每位组员仍需完成

1. 在自己的学号目录克隆本组仓库，不要共用其他人的工作目录。
2. 在自己的仓库内设置 Git 身份（不要使用 `--global`）：

   ```bash
   git config user.name "自己的学号"
   git config user.email "自己的学号@localhost"
   ```

3. 进入 `E4/E4实验包/A-buildchecker`，依次运行：

   ```bash
   make doctor
   make all
   ```

4. 保留各自 `work/<时间>/` 下的 `env.json`、`build.log`、`test.log`、`smoke.json` 和 `secret-scan.txt`。
5. 与其他组员核对 Git 提交号和测试结论一致。

## 变更记录

- 2026-10-20：`doctor.py` 最低内存由 3.5 GiB 改为 1.5 GiB，以兼容课程要求购买的 2 GB 云实例；容器运行上限仍保持 1 GiB，未修改其他资源或安全限制。
- 2026-10-20：Dockerfile 中 Debian 软件源改为华为云镜像源，解决官方源下载速度过慢的问题。
- 2026-10-20：学号 `241098114` 完成首次 `make all`，环境自检、构建、3 项测试、冒烟测试和密钥扫描均通过。
