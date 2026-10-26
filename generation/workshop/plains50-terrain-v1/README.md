# 平原50：地貌组8个技术候选

只移动、普通单跳、反冲；4配方×2明确空间需求，8件均2port。2旧关系适配、1真实落地补枪组合、1下穿竖柱救回落点的子关系待AI归组；不称8新家族。原regular校准/留出不降低，人类观感/试玩/生产准入待审。

|样品|原生精确视频|标准JSON|独立留出 clean/mild/moderate|
|---|---|---|---|
|T01 窄道：较高接收岸|[MP4](videos/slot/thorn-slot.mp4)|[JSON](../../../pcg/map_directed/library/candidates/2a1efc95dcbb794926fd9e1d515b29f4cc7ee1a7936f96eb8d3e6178397a930d/module.mapnote.json)|1.00/1.00/0.75|
|T02 窄道：宽出口岸|[MP4](videos/slot-second/thorn-slot.mp4)|[JSON](../../../pcg/map_directed/library/candidates/c99a287ae8fc72dd79ca2b14a7f3584c2f0ee66d426c99b039900adaf0d5504e/module.mapnote.json)|1.00/1.00/0.75|
|T03 过檐刹入：短侧袋|[MP4](videos/brake/brake-under-ledge.mp4)|[JSON](../../../pcg/map_directed/library/candidates/d8c58bc54db2e649a9a24313f070be1d31cf177b54ca5e53316dd603255be625/module.mapnote.json)|1.00/1.00/1.00|
|T04 过檐刹入：深侧袋|[MP4](videos/brake-second/brake-under-ledge.mp4)|[JSON](../../../pcg/map_directed/library/candidates/027935f4f6f887d69854e1b4894bc77ce1436fdbb5a125fa635c74ec10afe857/module.mapnote.json)|1.00/1.00/1.00|
|T05 落地补枪：水平接力|[MP4](videos/relay/landing-reload-relay.mp4)|[JSON](../../../pcg/map_directed/library/candidates/79769580e6f6e55768697e01f0cec4df91c588de9a4990bbedd3b7b5b4fee8d7/module.mapnote.json)|1.00/1.00/0.75|
|T06 落地补枪：抬升接力|[MP4](videos/relay-second/landing-reload-relay.mp4)|[JSON](../../../pcg/map_directed/library/candidates/01c1569a6399b48d2b657b710181b9acd58eea9f583cc8f5b77be749034540a6/module.mapnote.json)|1.00/1.00/0.75|
|T07 柱底救回：低侧岸|[MP4](videos/column/under-column-escape.mp4)|[JSON](../../../pcg/map_directed/library/candidates/f678fdeefc8b2b6663b80249d10d110eb99386bca47a96b60c025034d9cea3ab/module.mapnote.json)|1.00/1.00/1.00|
|T08 柱底救回：宽转折|[MP4](videos/column-second/under-column-escape.mp4)|[JSON](../../../pcg/map_directed/library/candidates/0bdf37eeca235865474eef2d0b3440014edca4382ef1bbdc876fea8c0c6211f7/module.mapnote.json)|1.00/1.00/1.00|

正式生产832个真实案例，预探针40个，总872；8段原生1倍片996帧全字段严格比较通过，未放宽support_id或资源字段。独立新进程原WorkshopLibrary重检索8/8，生成/物理调用0；后录两片通过manifest-v2补齐，原manifest保留。

先前失败均保留：中途settle持续控制导致续接轴失效，改用显式零轴+实际落地恢复；pocket-reload-climb提案因入口可直达终岸而未生产；竖柱首版接收岸过高过远，第二几何修订后完整门槛通过。旧源、失败、原始轨迹见manifest列出的六个run根。

仅前向精确见证；回程、通用接缝、全图与任意进入状态保持UNKNOWN。底层保命地面不等于完整重试证明。

## 入口

从仓库根在无旧同名run的干净worktree执行（先恢复原Godot运行环境）：

```sh
python3 -m pcg.prototype.creative_batches.plains50_terrain.production_v1 --name terrain-adapt-new --recipes terrain-slot terrain-brake
python3 -m pcg.prototype.creative_batches.plains50_terrain.production_v2 --name terrain-relay-new --recipes landing-reload-relay
python3 -m pcg.prototype.creative_batches.plains50_terrain.production_v3 --name terrain-column-new --recipes under-column-escape
```

手动体验复用原场景，选择样品后点击“手动”：

```sh
pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 --path pcg/prototype/godot pcg/prototype/workshop/main.tscn -- --cases-json generation/workshop/plains50-terrain-v1/videos/slot/review_cases.json
```

替换`--cases-json`为任一影片目录的`review_cases.json`可切换样品。

[完整8件索引](manifest-v2.json) · [首次独立进程检索回执](manifest.json)
