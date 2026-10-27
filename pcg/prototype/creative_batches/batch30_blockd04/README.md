# 修订 D04r2 的 Block 缺口

本目录先返回 `needs_design`，没有生成新Module或运行新Godot。只读取有效的 `batch30_d04r2.api_v1` / `park-for-return-repaired` 两版本；因中位无台取奖绕法暂扣的旧D04两版本明确排除。

原每份三Port提供A→B `park-middle-and-cross` 与A→C `park-reward-and-descend`。中段停台支持短直接回程；东段停台支持经B后真正乘原台接力到12币C岸。两份同世界A回程是独立验证试件，不是额外A口，也不签通用B→A。

最新Block合同要求真实拥有格子的外侧邻格不属于Module。朴素 `dy=-64` 可让三岸以−22/−22/+22px适配ground64；但B的E边界中心768之外那一格被原高柱实际占用。扩大拥有格子会把这个Port变成内部面，不能通过。

此外原B本质是被两种策略再次利用的内部岸：去C从右唇离开，中位回程从左唇离开。简单把任一唇改成Module外接口，也会把相应必要策略引入禁止拥有的外邻格。保留底岸并不让旧回程证据自动成立。这是当前地貌与控制的接口冲突，不是对所有未来新规则的不可行证明。

必须先设计独立B开口或新的内部绕行，并真实验证完整身体、停位收益、奖励反例及同世界回程。没有删中位策略来凑通过，也没有把原内部B点画成已可拼装的Port。

```sh
python3 -m pcg.prototype.creative_batches.batch30_blockd04.constraint_gap_v1 \
  --out pcg/results/workshop-fresh-blockd04-gap/request-response.json
```

`constraint-gap-v1.json`绑定来源、原两版本、方向、具体格子与可协商项。当前0新物理、0新候选；原局部候选仍保留原身份和证据。新的2规则/80probe预算尚未消耗，不把静态拒绝当完成。
