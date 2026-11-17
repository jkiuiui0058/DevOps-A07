# E7 验证与 CI

E7 延续 A07 的 BuildChecker 轨道。成员 A/B/C 的分工见 [成员分工](成员分工.md).

分工为：A 独立完成本地全场景验证；B 独立完成 CI 接入到失败/恢复的完整闭环；C 独立完成判定测试与验收准备，最后收两份成品包并完成最终验收汇总。交付关系只有 **A → C、B → C**，A/B 不互相等待或接力。三人各自新增测试、运行并撰写自己的成稿。

## 本阶段目标

1. 每人新增一项有意义的测试，说明已有覆盖、自己的输入、预期与实际结果，保留个人提交。
2. 运行独立判定测试和完整八项 gate，核对重复性、修复结果及故障报告。
3. 在同一 GitHub 仓库完成正常 CI、分支保护、失败 PR 被拒绝合并、同一 PR 修复并合并的证据闭环。
4. 保存源码 SHA、镜像 ID、原始日志、运行记录与归档；状态按实际填写。

## 本仓库路径差异

- 本组持续使用 DevOps-A07 仓库，组件根目录为 `A-buildchecker/`，课程命令中的 `scripts/course.py` 在当前版本对应 `scripts/lab_cloud.py`。
- 随包 workflow 位于 `A-buildchecker/.github/workflows/e7-quality-gate.yml`，需要由 B 适配到仓库根目录 `.github/workflows/`。运行目录、Docker 构建上下文、扫描范围和 artifact 路径都必须核对，不能直接照搬组件独立仓库的相对路径。
- 当前组件未提供课程所述 `course-support/ci/`；由 B 对照教学实验包引入必要的保护配置与失败/恢复测试，注明来源。
- 真实构建和 gate 在 Linux 云主机个人克隆中执行，镜像显式指定个人标签；`work/` 被忽略，需要另行备份。

## 本地起步命令

在 Linux 个人克隆的 `A-buildchecker/` 目录执行，ROLE 按分工填写 a、b 或 c，输出目录每轮使用新名称：

```bash
ROLE=a
python3 -m unittest discover -s tests/e7 -v
ORACLE_CODE=$?
printf 'ORACLE_EXIT_CODE=%s\n' "$ORACLE_CODE"
python3 scripts/lab_cloud.py build --image "course1027-buildchecker:e7-$ROLE" --out work/e7-build-01 --build-timeout 3600
python3 scripts/lab_cloud.py gate --image "course1027-buildchecker:e7-$ROLE" --out work/e7-01
GATE_CODE=$?
printf 'E7_GATE_EXIT_CODE=%s\n' "$GATE_CODE"
python3 -m json.tool work/e7-01/gate/gate-result.json
cat work/e7-01/gate/results.csv
```

构建成功后再执行 gate。新增测试或服务修改后重新构建镜像。正式运行前记录已提交的源码 SHA、工作区状态、镜像标签与镜像 ID。基线独立判定为六项；新增后按实际数量记录，服务测试总数也以实际日志为准。
