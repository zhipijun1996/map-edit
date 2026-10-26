# 平原机械内容：8件候选与真实三端口分流

本owner交付7个双端口Module和1个三端口Module；四种旧动作关系的空间/接口适配，不宣称8种新家族。仅移动、普通单跳和反冲；没有新能力或物理替代。技术候选已进入原共享库，人工观感/试玩/生产认可均未推断。

|样品|端口|标准文档|已有影片|版本|
|---|---|---|---|---|
|追台后登上窄岸 / 接口1|2|[标准JSON](../../../pcg/map_directed/library/candidates/bfb0e2996b1a898f933de777ca6f4fb8f05d4a04e591a6d2b939469e1619f469/module.mapnote.json)|[代表影片](../plains50-machinery-v1/videos/chase/chase-landing.mp4)|`bfb0e2996b1a`|
|追台后登上窄岸 / 接口2|2|[标准JSON](../../../pcg/map_directed/library/candidates/bf2761ddec8c00c3ba67ca5493f71ad02cb0873c9cfd42deb679083de3013bfc/module.mapnote.json)|[代表影片](../plains50-machinery-v1/videos/chase/chase-landing.mp4)|`bf2761ddec8c`|
|在避险岛换乘同台 / 接口1|2|[标准JSON](../../../pcg/map_directed/library/candidates/a1af6569a708c5bae497eb50853abc6a488b993b802d75bd9597cae9769e3d06/module.mapnote.json)|[代表影片](../plains50-machinery-v1/videos/evacuate/evacuate-rejoin.mp4)|`a1af6569a708`|
|穿过移动挡板的射击窗口 / 接口1|2|[标准JSON](../../../pcg/map_directed/library/candidates/7acc4cdfa042dedb338ace59d782444bf4a2fa12fccd88397e8bd42c1c489a51/module.mapnote.json)|[代表影片](../plains50-machinery-v1/videos/ray/moving-ray-window.mp4)|`7acc4cdfa042`|
|穿过移动挡板的射击窗口 / 接口2|2|[标准JSON](../../../pcg/map_directed/library/candidates/33a31084073ef8a2fa5c04a10fc18964ef40caaacb1945eece09475879b1bf52/module.mapnote.json)|[代表影片](../plains50-machinery-v1/videos/ray/moving-ray-window.mp4)|`33a31084073e`|
|先守门再运人的载台 / 接口1|2|[标准JSON](../../../pcg/map_directed/library/candidates/dbb99f259703c1910659c2bb1d5a58b008824cf77f95f708c0d8ca118893518f/module.mapnote.json)|[代表影片](../plains50-machinery-v1/videos/dual/carrier-dual-service.mp4)|`dbb99f259703`|
|先守门再运人的载台 / 接口2|2|[标准JSON](../../../pcg/map_directed/library/candidates/23510fdcf52daa7193868c711655b90f79a7c443673ad2d35d00fee2c90f39f0/module.mapnote.json)|[代表影片](../plains50-machinery-v1/videos/dual/carrier-dual-service.mp4)|`23510fdcf52d`|
|追台取宝或下层通行 / 3口|3|[标准JSON](../../../pcg/map_directed/library/candidates/a8b3f205807da9b0bc08d76ffa3c62fbfb99033bf0abe941c6e371a41754f8e6/module.mapnote.json)|[分流影片](../plains50-machinery-v1/videos/branch-reward/chase-landing.mp4) / [分流影片](../plains50-machinery-v1/videos/branch-safe/chase-landing.mp4)|`a8b3f205807d`|

代表影片覆盖4关系及三端口两条路线，共6片、2115帧原strict全字段/事件精确一致；正常1倍速度。不同具体版本不能由代表影片互相冒充，精确case/版本绑定见[manifest](manifest.json)。本owner只额外抽看了射窗影片2秒处一帧，不声称逐片观感审核。

三端口A→B是需要两次空中击铃并真实承载的取宝路，A→C是有意允许无射击/0金币的低风险通行。共6有序对，仅这两条path；其余4条UNKNOWN，没有推断入口出口互换。52个反例中24条低路同目标替代操作被正常接受，没有被误判为高路绕法。两路原完整校准72/72和独立留出72/72目的通过。

全交付实际物理1267例，含所有失败；8个入库版本的9条路线独立留出目的 313/324。射窗两个接口moderate各8/12，仅刚过原65%门槛，不能称高容错或人类难度认可。宽低避险岛v1 moderate7/12失败、协商宽岛v2 mild10/12失败，未继续第三版。额外上升侧洞两源码轮共16探针仍未过，未校准/留出/入库；已持久化失败，未用点子填数。

从原共享候选库在新进程重检索全部8版本（零生成/零物理）：

```sh
python3 -m pcg.prototype.creative_batches.plains50_machinery.delivery_v2 --query-only
```

[磁盘检索回执](disk-retrieval.json)绑定全部精确需求。各样品`scene`和`play_cases_json`在manifest内，原Godot场景提供Replay/Manual/Retry。原始物理/冻结源码位于`pcg/results/workshop-plains50-machinery-*`八个批次目录，由根任务统一归档；没有覆盖旧批次。

完整复现实验应通过原`production_loop.run` API指定新的隔离`library_root`，原规则CLI的历史固定名称须在新输出目录运行。原loop对“两接口仅一件命中”的混合复用存在边界，已有候选库不要直接重跑四配方历史CLI；当前交付提供准确的零生成检索入口。新物理和进场/回程/接缝适配必须重新绑定与验证。
