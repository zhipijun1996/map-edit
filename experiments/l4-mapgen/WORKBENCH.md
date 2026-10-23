# Map Notes L4研究台

任务 MAPGEN-RESEARCH-01 的管理中心在本仓库。主游戏是外部固定版本输入，不修改它的正式流程。当前状态为研究组件可用、正式地图替换/真实新图物理/玩家认可未验证。

完整交付从 [研究报告](../../docs/l4-mapgen/report.md) 开始；[架构与统一接口](../../docs/l4-mapgen/architecture.md)、[算法运行说明](README.md) 分别描述后续设计与当前代码边界。

从仓库根目录：

```bash
python3 -m pip install -r experiments/l4-mapgen/requirements.txt
npm run check
npm run check:mapgen
python3 experiments/l4-mapgen/check_artifacts.py
python3 -m http.server 8080
```

打开 `http://localhost:8080/experiments/l4-mapgen/viewer.html`。工作台只读，含三阶段SVG、同Seed对照、失败原因、下载与真实旧游戏基线录像。当前在线Map Notes尚未部署这些文件；Pages工作流已补打包路径，合入/部署仍需独立执行，不以本地网页冒称上线。

复现完整240样本（新目录，避免覆盖保留证据）：

```bash
python3 experiments/l4-mapgen/mapgen.py benchmark --seeds 30 --out /tmp/l4-mapgen-rerun --embedding-attempts 8
```

主程序默认写 `runs.json`；已交付数据为了viewer固定入口命名为 `results/benchmark.json`，**字节与原批次runs.json相同**。240份完整Manifest在该聚合文件中，不再重复提交逐文件版本。`check_artifacts.py` 按原序列化重建并核全部240个hash、源码/目录及原测试日志；需要原目录布局时：

```bash
python3 experiments/l4-mapgen/check_artifacts.py --unpack /tmp/l4-original-manifests
```

`results/provenance.json` 保留原批次路径和当时说明文件hash；`source-manifest.json` 绑定最终组件包。批次后只补充README限制说明、未改变核心源码/catalog/tests；两份README hash差异明确保留。`results/packaging-receipt.json` 说明聚合映射与最终文件。较早失败/中断目录存于 `failure_evidence/earlier-failed-and-interrupted-runs.tar.gz`，不作为最终成功证据。

真实内容相关工具：

```bash
python3 experiments/l4-mapgen/content_inventory.py --game /path/to/pinned-game --output /tmp/content-inventory.json
python3 experiments/l4-mapgen/check_real_catalog.py --inventory experiments/l4-mapgen/results/content-inventory.json --runs experiments/l4-mapgen/results/benchmark.json --output /tmp/real-port-probe.json
python3 experiments/l4-mapgen/validate_with_game.py --game /path/to/pinned-game --expected-commit f50fe78630fd98339186349f4ea91d92540d6c5b --runs experiments/l4-mapgen/results/benchmark.json --output /tmp/game-validator.json
```

前两个是资料/必要条件检查，不给模块准入；第三个实际调用游戏已有设计validator，但投影仍是设计声明，不是物理。真实生成与Motor结果见 [Godot输入说明](godot/README.md)、`results/motor/receipt.json`。

最小CI只跑当前Map Notes校验、21个Map组件/内容测试、原始证据hash和JS语法，不运行240完整搜索或游戏全部物理矩阵。Chromium可选本地检查：启动服务后 `python3 experiments/l4-mapgen/browser_check.py`，需要Playwright与Chromium；它不伪造游戏测试。
