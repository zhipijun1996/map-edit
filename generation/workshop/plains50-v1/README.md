# 平原50：模块、分叉与人工审阅

**新增50个技术候选：39双端口、7三端口、4四端口。** 全部只需移动、普通单跳和反冲；原库44→94，平原候选32→82。版本数不等于玩法家族数。AI按实际决定归为21个审阅组，另29个接口适配保留。尚无人类新批次观感/试玩/生产批准。

[完整标准Module清单](manifest.json) · [独立AI审查](https://github.com/zhipijun1996/map-edit/blob/content/task-a-workshop/pcg/creative-production/curation/plains50-final-ai-review-v1.md) · [11个多口精确检索与55个矛盾需求拒绝](fresh-process-multiport-retrieval-v1.json)

## 先看21组代表

下列都是所列版本的真实短片。20组有严格逐字段通过片；撤桥组仅review-only。可直接聊天按组或P编号反馈，无需评分表。未给第二接口借用代表片作为版本证据；15个适配没有自己的影片，独立AI包明确列出。

|审阅组 / Module|玩家判断|代表短片|
|---|---|---|
|P50-G01 / P47|读上下净空和目标岸，选择起跳/射向让完整身体穿过空腔。|[reward](../plains50-ports-v1/videos/plains50-thorn-branch-0-reward/thorn-slot.mp4) · [lower-exit](../plains50-ports-v1/videos/plains50-thorn-branch-0-lower-exit/thorn-slot.mp4)|
|P50-G02 / P43|先判遮挡底缘与可救落点，再选择何时制动返向或向侧岸救回。|[reward](../plains50-ports-v1/videos/plains50-brake-branch-1-reward/brake-under-ledge.mp4) · [lower-exit](../plains50-ports-v1/videos/plains50-brake-branch-1-lower-exit/brake-under-ledge.mp4) · [west-exit](../plains50-ports-v1/videos/plains50-brake-branch-1-west-exit/brake-under-ledge.mp4)|
|P50-G03 / P13|处理挡住远铃的吸弹敌体，再射击世界目标。|[main](../plains50-enemy-v1/videos/enemy-clear-sightline.mp4)|
|P50-G04 / P11|保留视线使敌人提交攻击，再从危险线脱离穿短门。|[main](../plains50-enemy-v1/videos/enemy-attack-relay.mp4)|
|P50-G05 / P17|推动并保留敌人在感应区，利用远门而不射杀钥匙。|[main](../plains50-enemy-v1/videos/enemy-sensor-hold.mp4)|
|P50-G06 / P44|射击启台后主动截获，选择暂停和离台时机。|[reward](../plains50-machinery-v1/videos/branch-reward/chase-landing.mp4) · [safe-lower-exit](../plains50-machinery-v1/videos/branch-safe/chase-landing.mp4)|
|P50-G07 / P19|预测载台运行，在避险岸暂离后重新截获。|[main](../plains50-machinery-v1/videos/evacuate/evacuate-rejoin.mp4)|
|P50-G08 / P24|按运动挡板相位选弹丸发射时机及反冲落点。|[main](../plains50-machinery-v1/videos/ray/moving-ray-window.mp4)|
|P50-G09 / P32|先向西向出口的反方向探身，开永久门后回西。|[main](../plains50/resources/sightline-i0/sightline-backtrack.mp4)|
|P50-G10 / P36|从能看铃处主动撤桥，接受下降到新路线。|[main（review-only）](../plains50/resources/trapdoor-i0/trapdoor-commit.mp4)|
|P50-G11 / P26|辨识两个同时可射目标的正确提交次序。|[main](../plains50/resources/order-i0/ordered-target-transaction.mp4)|
|P50-G12 / P22|下降取得射界后瞄准世界铃，利用同次反冲回侧袋或回升落稳。|[main](../plains50/resources/lowray-overview-i0/low-ray-recoil-return.mp4)|
|P50-G13 / P07|先利用停台维持远门，再放弃持续开门把同台取回作运输。|[main](../plains50-machinery-v1/videos/dual/carrier-dual-service.mp4)|
|P50-G14 / P15|下降前先处理挡住身体落点的敌人，选择真实可站空间。|[main](../plains50-enemy-v1/videos/enemy-displace-landing.mp4)|
|P50-G15 / P20|完成第一段后在中台落稳取得空中枪，再处理第二空腔。|[main](../plains50-terrain-v1/videos/relay/landing-reload-relay.mp4)|
|P50-G16 / P46|观察可见高处收益与低路出口，为同一空中枪选择分支。|[reward](../plains50-ports-v1/videos/plains50-investment-fork-1-reward/one-shot-two-routes.mp4) · [lower-exit](../plains50-ports-v1/videos/plains50-investment-fork-1-lower-exit/one-shot-two-routes.mp4) · [main](../plains50-ports-v1/videos/plains50-investment-fork-1-main/one-shot-two-routes.mp4)|
|P50-G17 / P30|先从真实命中获得第二枪，再兼顾高门打开与上升穿门。|[main](../plains50-new-relations/videos/refill-gate/refill-short-gate.mp4)|
|P50-G18 / P01|必须取命中资源时承受离岸反冲，再用所得枪反转运动。|[main](../plains50-new-relations/videos/adverse-refund/adverse-refund-reversal.mp4)|
|P50-G19 / P50|同时考虑弹丸到铃和身体过门时机，并选择高奖励或安全低路。|[reward](../plains50-ports-v1/videos/plains50-timed-branch-1-reward/timed-cache.mp4) · [lower-exit](../plains50-ports-v1/videos/plains50-timed-branch-1-lower-exit/timed-cache.mp4) · [east-lower-exit](../plains50-ports-v1/videos/plains50-timed-branch-1-east-lower-exit/timed-cache.mp4)|
|P50-G20 / P41|从有限活敌取得第二次空中枪，再选择继续去高岸或折返。|[reward](../plains50-ports-v1/videos/plains50-refund-retreat-fork-1-reward/air-refund.mp4) · [lower-exit](../plains50-ports-v1/videos/plains50-refund-retreat-fork-1-lower-exit/air-refund.mp4) · [turnback-reward](../plains50-ports-v1/videos/plains50-refund-retreat-fork-1-turnback-reward/air-refund.mp4)|
|P50-G21 / P28|先使两目标机关进入已准备状态，再选择开启短窗口并穿门的时机。|[main](../plains50-new-relations/videos/prepared-sequence/prepared-air-sequence.mp4)|

## 分叉样品

三口均从同一A口有两个已测出口，四口均有三个。所有奖励、敌人和机关初态完全共享；逐方向的完整声明在标准JSON。未验方向是UNKNOWN，不能自动互换入口出口。

|Module|接口|已验路线|标准JSON / 图|
|---|---|---|
|P40 命中回充登高或西侧撤离 · 3口 · 接口1|3口|A→B（reward）、A→C（lower-exit）、A→C（reward-rejoin）|[JSON](modules/generated-6e26234adb89a5e939a68343dfd21328011d35af34e07a26639757ac50e051c9.mapnote.json) · [SVG](modules/generated-6e26234adb89a5e939a68343dfd21328011d35af34e07a26639757ac50e051c9.svg)|
|P41 命中回充登高或西侧撤离 · 4口 · 接口2|4口|A→B（reward）、A→C（lower-exit）、A→D（turnback-reward）|[JSON](modules/generated-c972d86b61a33b2ef42dd32225e8539ea80a4191a44b0b0d0adb7113dab48621.mapnote.json) · [SVG](modules/generated-c972d86b61a33b2ef42dd32225e8539ea80a4191a44b0b0d0adb7113dab48621.svg)|
|P42 刹入侧袋与下层分流 · 3口 · 接口1|3口|A→B（reward）、A→C（lower-exit）、A→C（reward-rejoin）|[JSON](modules/generated-88ee048790d157eccaa32dced1de0fd9c95d11d6d24bc36ada8ea408632e8253.mapnote.json) · [SVG](modules/generated-88ee048790d157eccaa32dced1de0fd9c95d11d6d24bc36ada8ea408632e8253.svg)|
|P43 刹入侧袋与下层分流 · 4口 · 接口2|4口|A→B（reward）、A→C（lower-exit）、A→D（west-exit）|[JSON](modules/generated-442fc35fe7d3da35dfbaa9d2ca8e03380c64e553f5d13c8e8e9f802967a0a964.mapnote.json) · [SVG](modules/generated-442fc35fe7d3da35dfbaa9d2ca8e03380c64e553f5d13c8e8e9f802967a0a964.svg)|
|P44 追台取宝或下层通行 / 3口|3口|A→B（reward）、A→C（safe-lower-exit）|[JSON](modules/generated-f608e889e50720d179e97848d478aca0a69b5fa740f1d7ea2a04ddcdd02b141d.mapnote.json) · [SVG](modules/generated-f608e889e50720d179e97848d478aca0a69b5fa740f1d7ea2a04ddcdd02b141d.svg)|
|P45 单枪投资高奖或低路 · 3口 · 接口1|3口|A→B（reward）、A→C（main）、A→C（reward-rejoin）|[JSON](modules/generated-0a076beebb7a25ff247e6f5bd384ae2cb086da6fdf671cd2fc515823aa78075c.mapnote.json) · [SVG](modules/generated-0a076beebb7a25ff247e6f5bd384ae2cb086da6fdf671cd2fc515823aa78075c.svg)|
|P46 单枪投资高奖或低路 · 4口 · 接口2|4口|A→B（reward）、A→C（main）、A→D（lower-exit）|[JSON](modules/generated-7d6714311bc3a2bfdb32711c8fefc771e048028d9c3fe5d675feded7c346e1f0.mapnote.json) · [SVG](modules/generated-7d6714311bc3a2bfdb32711c8fefc771e048028d9c3fe5d675feded7c346e1f0.svg)|
|P47 尖刺窄道与低路分叉 · 3口 · 接口1|3口|A→B（reward）、A→C（lower-exit）|[JSON](modules/generated-6922690459755e84f0b1e744fa55f64660163f47702201d2101d12abccb359fe.mapnote.json) · [SVG](modules/generated-6922690459755e84f0b1e744fa55f64660163f47702201d2101d12abccb359fe.svg)|
|P48 尖刺窄道与低路分叉 · 3口 · 接口2|3口|A→B（reward）、A→C（lower-exit）|[JSON](modules/generated-79dac1564c3fbcf3472439ee1e6a6aeed2ce4da2657df009e72d283f52188fbb.mapnote.json) · [SVG](modules/generated-79dac1564c3fbcf3472439ee1e6a6aeed2ce4da2657df009e72d283f52188fbb.svg)|
|P49 短门取宝与下层分流 · 3口 · 接口1|3口|A→B（reward）、A→C（lower-exit）、A→C（reward-rejoin）|[JSON](modules/generated-a2106f386792452d7bad491afd663bd9aa4973d99416fba23efd2cdb3e747491.mapnote.json) · [SVG](modules/generated-a2106f386792452d7bad491afd663bd9aa4973d99416fba23efd2cdb3e747491.svg)|
|P50 短门取宝与下层分流 · 4口 · 接口2|4口|A→B（reward）、A→C（lower-exit）、A→D（east-lower-exit）|[JSON](modules/generated-3e14cdefdeb69f3d0ff9188efab8596aec16d9898bcd5c120910f9504f1e7a6c.mapnote.json) · [SVG](modules/generated-3e14cdefdeb69f3d0ff9188efab8596aec16d9898bcd5c120910f9504f1e7a6c.svg)|

全部50共69条已验路线，65个有条件有向通路、103个UNKNOWN关系。独立从源口新建场景的路线不等于继承其他路线出口状态；只有明确via_ports的连续取宝汇回保留同一角色/世界。

## 运行与复用

仓库根、恢复原Godot运行环境后：

```sh
python3 -m pcg.prototype.creative_batches.plains50_catalog --list
python3 -m pcg.prototype.creative_batches.plains50_catalog --play P01
python3 -m pcg.prototype.creative_batches.plains50_catalog --play P41 --route turnback-reward
python3 -m pcg.prototype.creative_batches.plains50_catalog --play P40 --route lower-exit --replay
```

三/四口必须选route；默认真实手玩，--replay是冻结输入回放。CLI逐SHA核对原库record/doc/case与scene，原case原样复制到新运行目录。每件specification可交原工坊检索/适配；当前只声明列明的有限需求域，域外明确冲突。

```sh
python3 -m pcg.prototype.creative_batches.plains_workshop.catalog_v2 --query demand.json
python3 pcg/tools/restore_archive.py content-workshop-plains50-v1 --extract
```

归档含52,807个文件、全部成功/失败/冻结源与原始物理输入输出，9片共94,175,431字节；ZIP SHA `05f800111244353ac2f8b2ada9f64801de2598ee47f9f723b8e38dadb0706d79`。旧库依赖按旧报告恢复；新实验应使用新目录/隔离原库参数，不覆盖已发布结果。

## 已验证的范围与保留的问题

- 所有版本通过原regular门槛；本批8,623个Harness案例包含失败、小筛、校准、独立留出及接缝试件。69交付路线的留出1969/2022目的通过，不能换算人类成功率。
- 11多口新进程精确检索11/11，错误端口、额外机关、资源重置、未验回程和高级能力共55个要求均明确拒绝；其他39件的原库新进程复用见各owner回执。
- [两份零新增碰撞面积接缝试件](../plains50/seams/README.md)共104实际案例，独立留出48/50，仍不升级原Module的通用接缝或整图资格。
- 刹门组合存在提前开门再刹入的合法解，不宣称同枪必要或新家族。东侧低路回充样品未过门槛，已停止；最终是重新验证的西侧出口需求。
- D02下降台、D03持续有限补给双路、D04留台回程、D05射移支撑及部分组合仍有明确缺口；本次50没有冒称完成这些完整设计。
- timed连续汇回片仅1帧normal_velocity/support_id差异，保持review-only；撤桥片也为review-only。原严格比较器未放宽。
- Map需求是本任务模型编写的接口工单，不声称来自B的实际调用或盲空间泛化。区域拓扑/布局/整图验收仍由B完成。

## 网页编辑器

打开 [关卡编辑器](https://zhipijun1996.github.io/map-edit/)，点“更新仓库Module”，内容范围选“反冲平原候选”，可按“3端口/4端口”筛选，打开可编辑副本。标准合同、原版本与证据保留；编辑后重新验证。
