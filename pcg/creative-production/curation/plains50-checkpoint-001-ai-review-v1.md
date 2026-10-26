# 平原50：首个批次AI审查检查点

实际核查 **23个新增技术候选版本 → 12个审阅组**：12个代表、11个有用适配。当前都为2端口；这不是50完成或12个新家族。

本检查点复用原verified_document/gate，对每版本核对文档/案例/证据SHA、原regular校准和独立留出门槛、固定发布策略与几何、每实例至少18条绑定反例。没有运行新物理或观看视频，视频队列待正式录制后绑定。

|组|玩家决定|与旧库关系|代表|
|---|---|---|---|
|P50-G01|读上下净空和目标岸，选择起跳/射向让完整身体穿过空腔。|G01；existing_relationship_demand_adaptation|[2a1efc95dcbb](../../map_directed/library/candidates/2a1efc95dcbb794926fd9e1d515b29f4cc7ee1a7936f96eb8d3e6178397a930d/module.mapnote.json)|
|P50-G02|先落到悬檐下，再选制动时机与返向落点。|G02；existing_relationship_demand_adaptation|[027935f4f6f8](../../map_directed/library/candidates/027935f4f6f887d69854e1b4894bc77ce1436fdbb5a125fa635c74ec10afe857/module.mapnote.json)|
|P50-G03|处理挡住远铃的吸弹敌体，再射击世界目标。|G08；existing_relationship_demand_adaptation|[2e69026fb65a](../../map_directed/library/candidates/2e69026fb65a79c09aa2b0ac25d2bac5161087107dc9605dd861a79ef06d3c0f/module.mapnote.json)|
|P50-G04|保留视线使敌人提交攻击，再从危险线脱离穿短门。|G10；existing_relationship_demand_adaptation|[47a74c8bf948](../../map_directed/library/candidates/47a74c8bf9487f1fd05592152dd78e93312ff9785b9f229ae1aa7909e9dc8618/module.mapnote.json)|
|P50-G05|推动并保留敌人在感应区，利用远门而不射杀钥匙。|G11；existing_relationship_demand_adaptation|[610b9bbe8efe](../../map_directed/library/candidates/610b9bbe8efe8cb0d3eb2b169f2b4be33cf0f543b9a4cbf227788295176802fa/module.mapnote.json)|
|P50-G06|射击启台后主动截获，选择暂停和离台时机。|G05；existing_relationship_demand_adaptation|[bfb0e2996b1a](../../map_directed/library/candidates/bfb0e2996b1a898f933de777ca6f4fb8f05d4a04e591a6d2b939469e1619f469/module.mapnote.json)|
|P50-G07|预测载台运行，在避险岸暂离后重新截获。|G14；existing_relationship_demand_adaptation|[a1af6569a708](../../map_directed/library/candidates/a1af6569a708c5bae497eb50853abc6a488b993b802d75bd9597cae9769e3d06/module.mapnote.json)|
|P50-G08|按运动挡板相位选弹丸发射时机及反冲落点。|G15；existing_relationship_demand_adaptation|[7acc4cdfa042](../../map_directed/library/candidates/7acc4cdfa042dedb338ace59d782444bf4a2fa12fccd88397e8bd42c1c489a51/module.mapnote.json)|
|P50-G09|先向西向出口的反方向探身，开永久门后回西。|G09；existing_relationship_demand_adaptation|[577021d1f4e0](../../map_directed/library/candidates/577021d1f4e0cbc095633b1d9961cd7ddfe638f0b4ee7bc3852b0981c758e992/module.mapnote.json)|
|P50-G10|从能看铃处主动撤桥，接受下降到新路线。|G12；existing_relationship_demand_adaptation|[6d96e4e0357c](../../map_directed/library/candidates/6d96e4e0357cce34df80c8af7af83bf71b82b6e32bfe4245b73b1370e619446e/module.mapnote.json)|
|P50-G11|辨识两个同时可射目标的正确提交次序。|G17；existing_relationship_demand_adaptation|[c039ba158429](../../map_directed/library/candidates/c039ba1584292368b14ab7c033d27f1ccd3830f6c56018d522cfb545995cddd2/module.mapnote.json)|
|P50-G12|坠到可射界后向前射铃，同时反冲回身后短门袋。|G02,G04；coupled_composition_under_review|[615eeddd3116](../../map_directed/library/candidates/615eeddd311680917d6696d0a9c37a29edc6ca84050b54fa247aa316023deb78/module.mapnote.json)|

需求由模型编写，不冒称任务B实际调用或独立盲空间泛化。两接口适配保留需求覆盖价值，不增加玩法家族。G12为刹车+短门的耦合组合待审；发布单枪证据成立，不证明所有扰动都必须同枪。G09修订的是过强射界代理条件，原regular门槛未改。

[逐版本去向与审查边界](plains50-checkpoint-001-ai-review-v1.json) · [实际原件/门槛完整性核查](plains50-checkpoint-001-integrity-v1.json)

原库与历史原件保留；本轮没有技术撤回或生产批准。后续达到50后另写最终AI审阅版本，不覆盖本检查点。
