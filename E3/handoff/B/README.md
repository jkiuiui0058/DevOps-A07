# E3 Role B：C0/C1/C2 增量构建基线

本目录用于验证两类增量构建问题：C1 遗漏头文件依赖导致的 Missing Dependency（MD），以及 C2 编译参数变化没有触发重新编译。

## Docker 环境

在本目录执行 `docker build -t e3-b-lab .`，然后执行 `docker run --rm -it e3-b-lab`。进入容器后工作目录为 `/work`，其中包含 GNU Make、GCC 和 Git。

## Git 版本

`C0` 是基线；`C1` 新增 `feature.h`，但 Makefile 漏写该依赖；`C2` 新增 `-DMODE=7` 编译参数。

查看历史：`git log --oneline --decorate --all`。查看标签：`git tag --list`。切换 tag 时出现 `detached HEAD` 提示是正常的。

## C0：正确基线

执行：`git checkout C0`、`make clean`、`make`、`./app`。

预期输出：`10`。C0 中 `BASE=10`，未指定 `MODE` 时默认为 `0`，所以结果是 `10 + 0 = 10`。

## C1：遗漏头文件依赖

C1 在 `main.c` 中新增 `#include "feature.h"`，计算 `BASE + FEATURE + MODE = 10 + 2 + 0 = 12`。

执行 `git checkout C1`、`make clean`、`make`、`./app`，预期输出 `12`。

C1 的 Makefile 仍然只有 `main.o: main.c config.h`，没有声明 `feature.h`，因此存在 MD。

复现 MD：先执行 `make clean` 和 `make`；然后执行 `sed -i 's/FEATURE 2/FEATURE 3/' feature.h`、`make`、`./app`。预期仍输出 `12`，但正确结果应为 `13`，因为 `main.o` 没有因 `feature.h` 变化而重新编译。

实验后执行 `git restore feature.h` 恢复文件。

## C2：编译参数变化未触发重编译

C2 在 Makefile 中加入 `CFLAGS = -O0 -DMODE=7`。`-DMODE=7` 等价于编译时定义 `MODE=7`。

先执行 `git checkout C1`、`make clean`、`make`、`./app`，得到旧产物和输出 `12`。

然后执行 `git checkout C2`、`make`、`./app`，不要执行 clean，预期仍输出 `12`。Make 没有检测编译参数变化，继续使用旧的 `main.o`。

最后执行 `make clean`、`make`、`./app`，预期输出 `19`，因为 `10 + 2 + 7 = 19`。

## 预期结果

| 场景 | 构建方式 | 预期输出 | 说明 |
|---|---|---:|---|
| C0 | clean build | `10` | 正确基线 |
| C1 | clean build | `12` | 正确编译新功能 |
| C1 | 修改 `feature.h` 后增量构建 | `12` | 旧结果，存在 MD |
| C2 | C1 产物基础上的增量构建 | `12` | 编译参数变化未触发重编译 |
| C2 | clean build | `19` | 正确结果 |

## 交付检查

使用 `git status`、`git log --oneline --decorate --all`、`git diff C0 C1`、`git diff C1 C2` 检查仓库。使用 `git bundle verify repository.bundle` 检查历史备份。使用 `git clone repository.bundle e3-b-restored` 可恢复完整历史。

## 结论

C1 证明遗漏头文件依赖会导致增量构建复用过期目标文件；C2 证明只改变编译参数时，普通 GNU Make 可能不会自动重新编译。clean build 能得到正确结果，但不能替代增量构建依赖检查。
