# 整图效果截图 · 2026-10-24

来源：当前游戏 main@cd4989a68613e0b457cdfd5e252634dd57008505；Map 2。游戏输入未改。

实际Godot 4096×2304渲染，每张单独适应整图；HUD隐藏，角色回调冻结，未搬运角色。全图观察可能露出正常近景镜头外的背景边界。截图不作为通关证据，也不是新算法已实装证明。

同一组Seed 00/03/04用于三类图；为覆盖平原三骨架而选，不是随机统计样本。

| 区域 | Seed | family | 区域数 | 原始整图 |
|---|---|---|---:|---|
|plains|l4-baseline-00|linked_rings|20|[4096×2304](plains-00/whole-map.png)|
|plains|l4-baseline-03|crossroads|20|[4096×2304](plains-03/whole-map.png)|
|plains|l4-baseline-04|woven_layers|23|[4096×2304](plains-04/whole-map.png)|
|forest|l4-baseline-00|clearing_shared_edge|40|[4096×2304](forest-00/whole-map.png)|
|forest|l4-baseline-03|clearing_shared_edge|40|[4096×2304](forest-03/whole-map.png)|
|forest|l4-baseline-04|clearing_shared_node|41|[4096×2304](forest-04/whole-map.png)|
|forest-v18|l4-baseline-00|clearing_shared_edge|77|[4096×2304](forest-v18-00/whole-map.png)|
|forest-v18|l4-baseline-03|clearing_shared_edge|77|[4096×2304](forest-v18-03/whole-map.png)|
|forest-v18|l4-baseline-04|clearing_shared_node|78|[4096×2304](forest-v18-04/whole-map.png)|

plains为正式实装root-bell-v3；forest为默认v15；forest-v18为显式开发候选，未混作正式默认。

[本地图库](gallery.html)（HTTP打开）包含三张一组对照及新A/B/C实际生成的结构图。所有新算法图片均为合成mask/连接布局，物理未验证。

原图由Godot直接保存；对照长图只是Chromium把原图和标注排版，不改原图像素。report.json/每张receipt.json记录实际版本、Manifest、镜头、尺寸、哈希及无角色搬运。

静态截图显式使用Dummy音频；4K图封存后降为小视口再执行原1000ms音频退出检查，不扩预算。首轮音频驱动/4K清理失败日志保留在此次输入研究临时目录，最终9例日志均无引擎错误且退出0。

复现命令：

```bash
python3 experiments/l4-mapgen/godot/capture_whole_maps.py --game /path/to/pinned-game --output /tmp/fresh-whole-maps
python3 -m http.server 8090
# 后续图库构建需新目录位于该仓库experiments/l4-mapgen内，供HTTP读取。
python3 experiments/l4-mapgen/godot/build_whole_map_gallery.py --output experiments/l4-mapgen/results/whole-maps-20261024
```
