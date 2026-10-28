# 多端口真实实现：风口分流与双廊换层

> 当前状态：用户已否决J06/J03，认为无聊且缺设计感。四份版本保留为技术试件，已从平原优选暂扣；下文是历史技术交付记录，不代表体验认可。[原话与版本绑定](../../pcg/feedback/workshop/junction-boring-observation-v1.json)。

本轮将前轮J06和J03变为4份可玩候选，各两种空间接口；原库94→98、平原82→86。[短视频、合同图、试玩和B接口](../../generation/workshop/junctions-v1/README.md)。其余四份创意仍是提案；环岛轨迹未开发。

J06使用静态高来岸、共同落点与向东逐级抬高的阶地。玩家落稳后仍能在同一状态下选西下通路或东升通路；B/C也能交换。两接口的真实共同前缀分别104/103帧，分流前角色静止落地、HP5、原精力100、一枪、无冷却。连续A→B→C另外保持同一世界验证。去掉奖励仍有三处外部继续开口。

J03用上下两层真实廊道与中庭开口组织四口。上层从A进入选择跨桥到B或下降到D；下层从C进入选择直行D或在中庭反冲升B。共用下廊的C/D有左右继续方向，不是两个恢复标记。上下层选择的真实共同前缀分别59/111帧与46/93帧，分歧时仍在同一几何与资源状态。A→D→B连续路线证明这条具体下降、返向、升层可以在不重建世界时执行；不推断任意返回。

## 实际实验

|部分|实际Godot案例|结果|
|---|---:|---|
|J06探针/修订/有限高岸反向搜索|176|名义与扰动通过；36条反向搜索未成功，仍UNKNOWN|
|J03探针与修订|136|首版4次升高不足；修订后132条探针通过|
|J06完整生产|800|两接口全部路线通过原regular|
|J03首次完整生产|716|窄高接口入库；宽接口被5次观测分类冲突拒绝，原件保留|
|J03宽接口分类修复后重验|533|同一几何/名义策略、原门槛、该接口尚未见过的holdout703；通过|
|两份精确接缝试件|102|校准与独立留出全部通过，原合同seams不升级|
|合计|2463|包含失败、反例和观测冲突，不作为内容数量或人类成功率|

最终24条路线的校准600/600、独立留出600/600，均按原regular质量门槛。静态clean每路1次，mild/moderate每路各12次。没有动态Cell，动态相位不适用；涉及射击的路线仍叠加真实时机/瞄准扰动。两种接口是适配证据，不是盲空间泛化或四种新玩法。

## 五个误判反例怎样处理

原Controller先执行`motor.step`，碰地后重置跳跃次数，再消费尚有效的跳跃缓冲。旧observer用该帧开始时的空中/已用跳数判断，于是在frame114把实际落在Platform2后的一次普通跳标成`air_jump`。五例真实能力均`maximum_jumps=1`、`double_enabled=false`；这类普通替代走法不使分叉失效。

未修改共享物理、Harness、原始计数或regular门槛。隔离解释器只识别单跳配置、前后落地状态、24×36身体完整支撑与实际速度签名；原raw仍保留`air_jumps=1`，解释结果单列。未识别的事件继续拒绝。五个原例与十个合成负对照检查通过；合成检查不是Godot实验。随后冻结新解释源码，仅重验尚未进入留出的宽接口，旧拒绝保持原件。

[源码和逐帧审计](../../pcg/prototype/creative_batches/junction_bridges/landing-buffer-audit-v1.json) · [隔离解释](../../pcg/prototype/creative_batches/junctions/landing_buffer_v1.py) · [原例检查](../../pcg/creative-production/junction-landing-buffer-check-v1.json) · [额外负对照](../../pcg/creative-production/junction-landing-buffer-check-v2.json)。这是观测修复，未把空间失败改名通过，也不宣称已修复共享observer。

## 可重复使用的入口

原多口调度仅增加可选配方/导出/固定protocol回调，旧默认不变；继续调用原WorkshopEngine、instantiate/evaluate、produce、标准合同和WorkshopLibrary。源码固定后执行搜索、反例、校准与留出，不另造验证器或候选库。新配方只有两种显式接口，范围外返回冲突，不替换成旧挑战房。

```sh
python3 -m pcg.prototype.creative_batches.junctions.produce_v1 --name fresh-windgap --rules pcg.prototype.creative_batches.junction_windgap.rules_v3
python3 -m pcg.prototype.creative_batches.junctions.produce_v1 --name fresh-bridges --rules pcg.prototype.creative_batches.junction_bridges.rules_v3
# 复现宽接口原分类冲突之后的精确修复重验：
python3 -m pcg.prototype.creative_batches.junctions.produce_v2 --name fresh-bridges-observation-recheck
```

上述命令用于复跑原实验；已有相同版本不可重复入库。正常复用走`query_v1`，不重新跑物理。完整原件从`content-workshop-junctions-v1`归档恢复。第一次生产命令会真实复现旧解释层的宽接口拒绝；不将该结果掩盖为全通过。新内容版本必须重新绑定证据，原库精确复用不能算新增。

没有取得人工趣味、操作手感、逐个难度评分或生产批准。独立模型审查只认定局部空间选择成立，六段视频通过严格回放比对。20个有条件path与16个UNKNOWN供B按实际摆放选择；不替代B整图、任意进入状态、通用变换或单向证明。
