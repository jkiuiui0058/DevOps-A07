# A07 使用 B07 校验记录

- A07 commit: `6fc9e7b6a3401eaa295946af57a736b48f238a08`
- B07 commit: `947e11e00fdb914a91a2139eb61df5038e2860ab`
- 校验来源：B07 `docs/contracts/validate.py`，直接加载 B07 工作树，不复制校验逻辑

- PASS valid docs/examples/full-check/request.json
- PASS valid docs/examples/full-check/accepted-response.json
- PASS valid docs/examples/full-check/succeeded-response.json
- PASS valid docs/examples/incremental-check/request.json
- PASS valid docs/examples/incremental-check/succeeded-response.json
- PASS rejected docs/examples/invalid/incremental-without-baseline.json

结果：`PASS`
