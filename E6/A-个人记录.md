# E6 A04：个人 before / after / verify 复现记录

## 1. 贡献与完成范围

本仓库 `A-buildchecker/` 是导入的教学参考实现，不是本人从零实现。个人贡献包括实际依赖机制分析、独立双 recipe job 隔离测试、进程/图边证据核对，以及本次个人复现与留证。

**A04 的本次个人复现闭环已完成**：复用个人提交关联 before，在隔离副本修复后运行 after，再校验报告并完整保存证据。这不表示整个 E6 完成，也不是 C 的最终集成验收。本次文档阶段没有重跑实验、修改源码/原始 fixture、构建镜像、提交或推送。

## 2. 版本与可追溯边界

| 项目 | 已核实值 |
|---|---|
| 个人贡献完整提交 SHA（来自本地 Git） | `39f8c328e6d3ccd6e9e149468b17bb4a8b9702ce` |
| 个人分支 | `e6/a` |
| 已建镜像标签 | `course1027-buildchecker:241098114` |
| 本次实际固定使用的镜像 ID | `sha256:65e8007d888e74e3d8bfe059f96fbb4e589cae284e4cd674afcbd76abd3b23e3` |
| 云端内容根 | `/root/241098114/e6-env-20261106-025440` |
| 快照清单中的基线 SHA（非个人贡献 SHA） | `3b43c97591ef57d66fd1e6fc2ae8b9fb33090c9a` |

云目录**不是 Git 仓库**，不能说它具有上述 HEAD。版本关联来自本地提交内容与云源码/镜像文件的比较：16 个相关路径中，15 项原始字节仅 CRLF/LF 不同，新增 `test_e6_a.py` 原始字节一致。严格只在内存执行 `bytes.replace(b'\r\n', b'\n')` 后，所有可映射文件内容一致；没有剥除空白或重新编码。

诊断位于本地 `A-buildchecker/work/e6-a-commit-39f8c328-229d0f61/` 的 `version.json`、`result.json`、`line-ending-analysis.json`；前两份保留最初原始哈希不匹配而停止的历史，不应误读为后来诊断失败。A04 manifest 保留该映射，并在运行前重新确认 16 路径云源码/镜像哈希、镜像 ID 和既有 before 未漂移（`preflight_no_drift=true`）。verify 脚本也核对了提交/云源码的限定行尾转换内容一致。

**这些证据只支持上述行尾映射下的个人复现，不是“正式提交原始字节完全一致构建”的证明。** 标签可能变化，复查以固定 ID 为准；不为记录 SHA 再制造一次提交。

## 3. 证据位置与日志索引

以下远端相对路径均以第 2 节云根为起点：

| 证据 | 远端位置 |
|---|---|
| 复用的提交关联 before | `work/e6-20261106-113348-785abc/` |
| 全新 after（默认自动 out） | `work/e6-20261106-131948-acd780/` |
| A04 命令、verify、diff、manifest | `work/e6-a04-personal-652dcfa8/` |
| before 原始 CLI 日志及版本记录 | `work/e6-a-personal-39f8c328-5db6d4f1/` |

本地完整归档目录：
`D:\study\SE\DevOps\DevOps-A07\A-buildchecker\work\e6-a04-personal-7b1ce79c\`

下列路径相对此本地归档根：

| 路径 | 用途 |
|---|---|
| `before/`、`after/` | 完整输入副本、图、processes、findings、Make 数据库、原始 trace、构建输出与 runner 日志 |
| `run/after/` | 实际 after 命令、CLI stdout/stderr、退出码 |
| `run/verify/` | 实际校验命令、JSON stdout、stderr、退出码 |
| `run/diff/` | 原始 Makefile diff、命令、stderr、退出码 |
| `manifest.json`、`run/manifest.json` | 本地/远端版本记录，结果、输入哈希、未漂移及未改原件的断言 |
| `transfer-verification.json` | 75 个证据文件远端/本地 SHA256 逐项校验，全部 matches=true |

before 从既有本地完整副本复制成套，after 和日志通过 SCP 复制，全部与远端哈希比对；没有重跑 before 或覆盖旧输出。既有 A03 单项通过日志及 before CLI 的独立记录仍在 `A-buildchecker/work/e6-a-commit-39f8c328-229d0f61/personal-recheck-ea6309c3/`，索引见 [A-云端证据索引.md](A-云端证据索引.md)。详细进程核对见 [A-实际依赖说明.md](A-实际依赖说明.md)，其中早期 PID 表属于其明确注明的旧采集，不与本次目录混用。

## 4. 实际命令与退出码

命令均在云根执行。为易读，下列变量代表**实际命令中已展开的完整值**，不是声称当时按此整段脚本执行：

```bash
IMAGE=sha256:65e8007d888e74e3d8bfe059f96fbb4e589cae284e4cd674afcbd76abd3b23e3
BEFORE=/root/241098114/e6-env-20261106-025440/work/e6-20261106-113348-785abc
AFTER=/root/241098114/e6-env-20261106-025440/work/e6-20261106-131948-acd780
python3 scripts/lab_cloud.py e6 --image "$IMAGE"          # 既有 before
python3 scripts/lab_cloud.py e6 --fixed --image "$IMAGE"  # 本次 after
python3 scripts/verify_e6_evidence.py --before "$BEFORE/evidence/findings.json" --after "$AFTER/evidence/findings.json"
diff -u "$BEFORE/fixture/Makefile" "$AFTER/fixture/Makefile"
```

| 阶段 | CLI/工具退出码 | 报告 status | clean/build | findings |
|---|---|---|---|---|
| before | 1 | SUCCEEDED | 0 / 0 | 恰好 2 条 |
| after | 0 | SUCCEEDED | 0 / 0 | 空数组 |
| verify | 0 | JSON passed=true | 检查两份报告 | 2 → 0 |
| 原始 diff | 1 | 检出差异，正常 | 不适用 | 不适用 |

before 退出码 1 表示发现问题，不是采集失败：精确发现 `MISSING(main.o, config.h)`、`REDUNDANT(main.o, unused.h)`，与 E5 人工 MD/RD 结论一致；after 不再有发现。完整实际命令数组和退出码分别在 `run/{after,verify,diff}/{command.json,exit-code.json}`；before 返回值还可查 `before/runner/exit-code.json` 及既有 CLI 记录。

## 5. 修复与输入完整性

只修复 `--fixed` 创建的隔离副本。仅归一行尾后，内容差异为：

```diff
-main.o: main.c unused.h
+main.o: main.c config.h
```

**原始 diff 不是只改一行**：参考入口用文本读写 Makefile，将其 11 个 CRLF 全部改为 LF，因此 `run/diff/stdout.log` 显示 11 行移除/增加。manifest 如实记录 `makefile_raw_only_rule_replacement=false`、before_crlf=11、after_crlf=0；只有限定 CRLF→LF 后，才满足“其余内容不变，仅替换上述规则”（`makefile_only_expected_replacement=true`）。

完整输入文件集合相同，哈希变化只有 Makefile：before 为 `e02e8fa1beab535fa4e7d3d29d7f010f05d1c1c620d8c51f598b372ad3271aaf`，after 为 `128069c949b0239e3377f320d51498c2b37a317c602d8755d573a283e1f400ae`。main.c/config.h/unused.h 未变；云根原始 fixture 及完整 before 目录均核对未变（`original_fixture_and_before_unchanged=true`），未直接修复原始样例。

## 6. verify 实际 JSON 与交付说明

`run/verify/stdout.log` 原文为：

```json
{
  "passed": true,
  "before_findings": 2,
  "after_findings": 0,
  "changed_inputs": [
    "Makefile"
  ],
  "before_trace_id": "e6-9b84623993f34e919d51c49c5e1f9354",
  "after_trace_id": "e6-b29e2f7cc8c04e44994d3ed7bc166056",
  "scope": "Saved report assertions; raw traces are not independently revalidated"
}
```

该脚本核验已保存报告，不会重新运行实验，也不独立复核全部原始 trace，不能把 passed=true 扩大为所有原始证据均已人工复审。

交给 C 时，**work 被 Git 忽略，提交文档不会自动交付原始证据**：必须另交上述完整 before/after/run、manifest、传输校验，以及关联的行尾诊断与 A03 日志，不能只提供目录名。归档版本边界和个人/集成身份应一并保留。A04 到此完成本次个人复现记录；整个 E6 与最终集成版本验收仍由后续集成流程处理。
