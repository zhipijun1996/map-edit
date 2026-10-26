# 平原新关系组：8个技术候选 / 4种配方

仅移动、普通单跳和反冲。8个新版本均经原regular校准和独立留出，入原CandidateLibrary；新进程8/8精确检索，8个错误空间需求拒绝，生成/物理调用0。四个配方按组合与适配审阅，不自动计为四个新家族。

|编号|内容|留出 clean / mild / moderate|标准Module|
|---|---|---|---|
|PN01|开侧门的一枪也是刹车|1/1 / 12/12 / 8/12|[JSON](modules/generated-a8f918f1ee9e8e682a919cdbb67ba2015fcfe075d54e5f25147fbe04dd156d2a.mapnote.json) / [SVG](modules/generated-a8f918f1ee9e8e682a919cdbb67ba2015fcfe075d54e5f25147fbe04dd156d2a.svg)|
|PN02|开侧门的一枪也是刹车|1/1 / 12/12 / 8/12|[JSON](modules/generated-c22d42efc9ea6697d034027772059c79463d79c3300fc1443c9e901f569da584.mapnote.json) / [SVG](modules/generated-c22d42efc9ea6697d034027772059c79463d79c3300fc1443c9e901f569da584.svg)|
|PN03|补给把你推离目标|12/12 / 12/12 / 11/12|[JSON](modules/generated-50e2a028167348a222df2ca54f4a9dd7ee5c3459e220c4bf6c83f3b4e162f6d7.mapnote.json) / [SVG](modules/generated-50e2a028167348a222df2ca54f4a9dd7ee5c3459e220c4bf6c83f3b4e162f6d7.svg)|
|PN04|把回充枪投给高处短门|12/12 / 12/12 / 11/12|[JSON](modules/generated-8f09302dc2ddb3e7b0a0c017a76edbbbc562c952f229bc4004addfba95f72da5.mapnote.json) / [SVG](modules/generated-8f09302dc2ddb3e7b0a0c017a76edbbbc562c952f229bc4004addfba95f72da5.svg)|
|PN05|把回充枪投给高处短门|12/12 / 12/12 / 10/12|[JSON](modules/generated-31d28456edaabba80edc83924f947490c675fad1583205a42a8a35b8573123a8.mapnote.json) / [SVG](modules/generated-31d28456edaabba80edc83924f947490c675fad1583205a42a8a35b8573123a8.svg)|
|PN06|补给把你推离目标|12/12 / 12/12 / 11/12|[JSON](modules/generated-5591634498e52e8f64bdc9a75dd1bfc9b09f8b1949a9ab3bf0b7fb565501847b.mapnote.json) / [SVG](modules/generated-5591634498e52e8f64bdc9a75dd1bfc9b09f8b1949a9ab3bf0b7fb565501847b.svg)|
|PN07|先备第一铃，再跃短门|1/1 / 12/12 / 12/12|[JSON](modules/generated-3ba90515a0c369b4bb77ee94e16b91c8d14578f5bfac7ef0d68c34ade36adff3.mapnote.json) / [SVG](modules/generated-3ba90515a0c369b4bb77ee94e16b91c8d14578f5bfac7ef0d68c34ade36adff3.svg)|
|PN08|先备第一铃，再跃短门|1/1 / 12/12 / 11/12|[JSON](modules/generated-d8c1b91b68ca06223f7bac2ba11a928bb8c8e3f5de00cb1b054ffa724e84bbfb.mapnote.json) / [SVG](modules/generated-d8c1b91b68ca06223f7bac2ba11a928bb8c8e3f5de00cb1b054ffa724e84bbfb.svg)|

4个代表短片均为正常1倍原生回放，379帧逐字段精确比较通过。代表片只证明自己的精确版本，其余空间版本以各自物理证据为准。

- [开侧门并刹入](videos/brake-gate/brake-gate-catch.mp4)
- [回充却反退，再转回](videos/adverse-refund/adverse-refund-reversal.mp4)
- [把回充枪投给短门](videos/refill-gate/refill-short-gate.mp4)
- [先备第一铃，再跃短门](videos/prepared-sequence/prepared-air-sequence.mp4)

补充反例发现：刹门接口0允许先开门，再另枪空中刹入；所以同枪双作用只描述发布见证，不能声称必要。该组按G02+G04适配/组合审阅。D02/D04/D05和中台落地折返的失败全部保留，不换标题算通过。

实验总计1066例原Godot，交付8版的独立留出230/244目的/无伤稳定。自动策略统计不转换为人类难度或趣味评分。所有反向与任意进入状态/全图拼装仍UNKNOWN。

复用/查看命令（仓库根）：

```sh
python3 -m pcg.prototype.creative_batches.plains50_new_relations.reuse_v1 --out /tmp/plains50-new-retrieval-fresh.json
python3 -m pcg.prototype.creative_batches.plains50_catalog --manifest generation/workshop/plains50-new-relations/catalog-entries-v1.json --list
```

本组采用原工坊可玩场景；序列门两个版本必须用绑定的sequence_main_v1.tscn，不能用普通场景漏掉二号铃。实际可玩入口由上面的标准catalog选择；不重写玩家或Map。

- [交付清单/两接口需求](manifest.json)
- [完整成本与来源回执](receipt-v1.json)
- [新进程检索](fresh-process-retrieval-v1.json)
- [已发现的可分开准备策略](brake-decoupling-adjudication-v1.json)
