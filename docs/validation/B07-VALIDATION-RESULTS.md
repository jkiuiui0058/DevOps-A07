# A07 使用 B07 校验记录

- A07 commit: `52e0dd14fd36c21505174ce6fb87bfd61ac3b433`
- B07 commit: `822083fb0c52d16c9a077b5ebc15e72a9af885cf`
- 校验来源：B07 `docs/contracts/validate.py`，直接加载 B07 工作树，不复制校验逻辑

- PASS valid docs/examples/full-check/request.json
- PASS valid docs/examples/full-check/accepted-response.json
- PASS valid docs/examples/full-check/succeeded-response.json
- PASS valid docs/examples/incremental-check/request.json
- PASS valid docs/examples/incremental-check/succeeded-response.json
- PASS rejected docs/examples/invalid/incremental-without-baseline.json

结果：`PASS`
