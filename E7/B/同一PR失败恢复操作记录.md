# B：同一 PR 的失败、恢复与合并操作记录

本记录用于完成 B03。失败演示使用同一 PR 中一条故意写错的测试期望；不触发工作流手工失败开关，也不修改真实检测算法。

## 前置条件

- `main` 已有一次真实的 `e7-a-quality-gate` 成功运行。
- `main` 对 `e7-a-quality-gate` 设置为必需检查，strict=true、enforce_admins=true、审批人数 0，并保存真实 Actions App ID 与规则 JSON。

## 失败—恢复闭环

1. 从最新 `main` 建立 `e7-b-pr-recovery`，只把 `A-buildchecker/services/buildchecker/tests/test_e7_b.py` 的版本断言临时改为：

   ```python
   self.assertEqual(VERSION, "1")
   ```

2. 创建 PR，保存失败 run URL、run ID、触发 SHA、失败测试输出、PR 的 `OPEN/BLOCKED` 状态，以及普通合并被策略拒绝时的非零退出码。
3. 在**同一 PR 分支**将断言恢复为 `"0.2.0-teaching"`，推送后确认最新 SHA 的 `e7-a-quality-gate` 通过并下载 artifact。
4. 常规合并 PR，保存 `MERGED` 状态、merge commit SHA 与 `mergedAt`。

不得使用管理员绕过、直接推 main 或手工 `fail_demo` 代替上述过程。
