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

详细过程见 [A组E5论文复现报告.md](./A组E5论文复现报告.md)，逐项状态见 [E5验收记录.md](./E5验收记录.md) 和 [验收记录.csv](./验收记录.csv)。

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

## 后续事项

- 在最终归档后补充归档文件名和 SHA256。
- 创建或合并 PR 后补充 PR URL。
- E6、E7 和 CI 项目在相应阶段继续填写，目前不提前标记为通过。
