# E5：BuildChecker 论文复现

本目录保存 A07 组 A 轨道在 E5 阶段的复现说明、人工分析和验收记录。实验在华为云服务器的个人分支 `e5` 上完成，正式源码提交为 `113712960b142b34bc226eb73e8a2a77a1c01f98`。

## 当前结果

|项目|结果|
|---|---|
|服务镜像构建|PASS，退出码 0|
|服务单元测试|PASS，`15 passed in 0.04s`|
|E5 原始证据采集|PASS，退出码 0|
|程序输出|`1`|
|Make 声明|`main.o: main.c unused.h`|
|实际编译读取|`main.c`、`config.h`|
|缺失依赖 MD|`main.o -> config.h`|
|冗余依赖 RD|`main.o -> unused.h`|

详细过程和证据索引见 [A组E5论文复现报告.md](./A组E5论文复现报告.md)。

## 证据位置

服务器原始目录为：

```text
/root/241250082/DevOps-A07/A-buildchecker/work/build-formal-02
/root/241250082/DevOps-A07/A-buildchecker/work/e5-formal-01
```

下载后的本地备份位于：

```text
E5/work/build-formal-02
E5/work/e5-formal-01
```

`work/` 按仓库规则被 Git 忽略，完整 trace、Make 数据库、二进制和日志不进入 Git 历史；最终通过课程归档包提交。Git 中保留本说明、人工结论、源码修改与证据索引。

## 提交记录

|项目|内容|
|---|---|
|GitHub PR|[PR #1](https://github.com/jkiuiui0058/DevOps-A07/pull/1)，已合并|
|PR 最终提交|`445528d4d08ab9949b8d74475e1fa2ead84e3b86`|
|合并提交|`3b43c97591ef57d66fd1e6fc2ae8b9fb33090c9a`|
|作业归档|`A07-E5.zip`|
|SHA256|`278d7d9c71c2742a4f5941f936f1f42d2cbbf5ec503def30591218a7f71dfbff`|

本次提交范围仅为 E5。
