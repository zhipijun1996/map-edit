# 区域网 R2：结构方向实验

这是 **新原型的抽象空间图**，不是 gunman-rush 的游戏截图，也不是最终可玩地图。与旧 A/B/C 的预算、成本单位不同，不可据此排名质量。详见 [修订报告](../../../../docs/l4-mapgen/region-exploration-revision.md)。

- `runs.json`：平原/森林各 Seed 0–19，共 40 份完整结构；失败字段与物理未验证状态保留。
- `summary.json`：批次计数及生成器/冻结复用组件源码 SHA-256。
- `reproduction-receipt.json`：另目录完整重跑 40 份，确定性摘要一致，逐份状态/方向/几何重新验证。
- `*-spatial.svg`：四个实际 Map Notes 布局 SVG，叠加生成后测得的两条初访路线。路线不是预制主线。
- `*-gallery.html` / `*-comparison.png`：同一实际布局的双 Seed 浏览器渲染。
- `browser-receipt.json`：本地 Chromium 实际查看器、筛选、数据集切换回执。

复现生成：`python3 experiments/l4-mapgen/region_network.py --seeds 20 --output /tmp/region-network-v2-rerun`。

本地查看：仓库根目录启动 `python3 -m http.server 8080`，打开 `/experiments/l4-mapgen/viewer.html?dataset=region-network-v2`。图库导出需要可选 Playwright/Chromium：`python3 experiments/l4-mapgen/capture_region_network.py`。
