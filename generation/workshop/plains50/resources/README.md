# 平原50：资源与射界方向的8个候选

这8个新版本使用移动、普通单跳和反冲，已通过原Godot工坊regular门槛并进入原候选库。四个配方各响应两种空间需求；其中三个沿用已有关系，新低射界关系仍待独立AI归组，不能将8版本当8个新家族。所有未验回程、接缝与整图仍为UNKNOWN，人工趣味/试玩/生产准入未获得。

|配方|两种实际空间需求|代表短片|代表状态|
|---|---|---|---|
|先东探射界、开门后向西折返|较窄岩屏+较远西出口；较宽岩屏+较近西出口|[MP4](sightline-i0/sightline-backtrack.mp4)|274帧全部字段exact|
|撤掉支撑桥、承诺进入下层|210宽/340深；230宽/220深|[MP4](trapdoor-i0/trapdoor-commit.mp4)|review-only，113帧中34处support_id差异，strict失败|
|两目标非交换顺序事务|280高接收岸；310高较远接收岸|[MP4](order-i0/ordered-target-transaction.mp4)|78帧全部字段exact|
|低射界开锁后回升落位|520高侧袋+500墙底；570高侧袋+540墙底|[MP4](lowray-overview-i0/low-ray-recoil-return.mp4)|98帧全部字段exact，实铃与入口/落点同屏|

代表片只绑定第一接口的精确版本，不替代第二接口录像。完整8版本、标准JSON/原库记录/输入/协议与校准留出见[清单](manifest.json)；每个Module只有2端口，本owner未提供分叉Module，根批次由其他方向交付三、四端口。

Harness实验共1190个实际案例，含全部失败/探针；另执行5次原生录像回放，其中1次strict失败保留原件。按配方累计382、218、234、352例，另PR-D03机制探针4例；均未超过每配方400例预算。八版本独立留出193/200目的有效且安全稳定，校准196/200；每个版本单独通过原门槛，未降低质量标准。它们不是人类通关率或全图可靠性。

## 来源、修订与未完成创意

- [四张完整设计卡](../../../../pcg/prototype/creative_batches/plains50_resources/design-cards-v1.json)保存玩家决定、因果、地貌、奖励、资源、失败/方向与反例。
- M10首版将“身体完全越过岩屏”当作必要性代理，误拒实际仍东探枪口射界的合理替代；第二版修正代理，并新增原地跳射/浅东移反例，完整重新校准和留出。原失败保存，未修改原regular门槛。
- 低射界首版低铃近垂直，早开也可成功，真实被反例拒绝。第二版低铃移到左侧制造实际遮挡；允许较早但仍真实下降后开锁回升的宽容解，不要求角色已低于出口或整个人体低于侧墙底。
- 原低射界镜头未覆盖真实接收铃，旧片保留在[原镜头目录](lowray-i0/manifest.json)。隔离展示场景只换Camera2D，让入口、实铃与侧袋同屏；[新片](lowray-overview-i0/manifest.json)重新严格逐帧通过，native trace与旧片字节一致，没有改物理或输入。
- PR-D03仍缺“同一世界3HP敌人供两奖励路线”的完整生成规则、连续资源成本与敌死后替代路线。四例仅验证原命中回充/有限HP，见[缺口回执](../../../../pcg/feedback/workshop/plains50-resources-D03-gap-v1.json)，不入库、不称已完成；本批低射界是另一个明确命名提案。

## 运行与复用

从仓库根、在原Godot环境已恢复时运行：

```sh
python3 -m pcg.prototype.creative_batches.plains50_resources.production_v1 produce --name fresh-resource-base --recipes trapdoor-commit ordered-target-transaction
python3 -m pcg.prototype.creative_batches.plains50_resources.sightline_v2 --name fresh-resource-sightline
python3 -m pcg.prototype.creative_batches.plains50_resources.lowray_v2 produce --name fresh-resource-lowray
python3 -m pcg.prototype.creative_batches.plains50_resources.reuse_v1 --name fresh-resource-retrieval
```

已有完整需求会优先从原磁盘库复用，生成调用0。要独立重做历史失败实验，使用新的worktree/输出名和已绑定规则，原目录拒绝覆盖。旧首版M10已知失败是历史回执，推荐的最终M10规则是sightline_v2。这里三次生产共覆盖四种配方；两条M10规则不是两种新家族。

手动试玩示例（`--case 0/1`选两种接口；R可重建实验，界面可切见证回放；重建只用于审阅，不算连续恢复证据）：

```sh
pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 --path "$PWD/pcg/prototype/godot" "$PWD/pcg/prototype/creative_batches/plains50_resources/main_lowray_overview_v1.tscn" -- --cases-json "$PWD/pcg/results/workshop-plains50-resources-lowray-production-v2/round-00/review_cases.json" --case 0
```

该示例只读实际发布case，不伪造动作或资源；用清单的`play_scene/source_run`可运行其余版本。[持久化复用回执](../../../../pcg/results/workshop-plains50-resources-reuse-v1/receipt.json)是新进程8/8精确检索，0新物理/0生成。原始9个结果目录列于清单，交根任务统一归档，包含失败、源码快照、输入与压缩轨迹。
