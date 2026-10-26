# 平原30增量工坊（开发中）

当前标准目录：[8份新候选](manifest-progress-8-v2.json)，不是30份完成。原98份记录保持不变；本轮另有2份旧D04技术记录因设计反例暂扣，不计新内容目标。

| 内容 | 实际动作关系 | 当前视频 |
| --- | --- | --- |
| D05-1/2 | 空中同枪反冲并启动台，台接住第一次落脚，回枪后二跳到岸 | [首版](videos/D05-1-v1/bell-carrier-catch.mp4)；[启动后漏接、真实回A停台重试](videos/D05-1-moving-retry-v1/bell-carrier-catch.mp4) |
| C01-1/2 | 跳离旧桥，同枪撤A造B，落B真实恢复后继续 | [升层版](videos/C01-2-v1/paired-support-transfer-review-only.mp4)，review-only：235帧中2帧支持碰撞体ID顺序不同，严格比较未通过，未放宽 |
| D04-1/2（修订） | 去程同枪跨岸与停台；中位供直接回程，东位供远岸奖励接力 | [中位往返](videos/D04r2-1-return-v1/park-for-return-repaired.mp4)；[取奖完整往返](videos/D04r2-1-reward-return-v1/park-for-return-repaired.mp4) |
| C02-1/2 | 先过开着的A，在空中同枪反冲、关A开B，再过B到岸 | [首版](videos/C02-1-v1/serial-airlock-recoil.mp4)；困难失误后的连续恢复另在修，暂未签可靠恢复 |

每项各2份空间接口是适配证据，不算两种玩法。D03仍因空中命中的瞄准容错未达到原regular门槛而返工，不计候选。

D05与修订D04的上列影片均正常速度原生输入回放，逐帧比较通过。C01的真实原生片明确保留严格比较失败及全部差异：[审计](videos/C01-2-v1/strict-failure-audit-v1.json)。所有内容的人工趣味、实际试玩和生产批准仍UNKNOWN。

```sh
python3 -m pcg.prototype.creative_batches.plains50_catalog \
  --manifest generation/workshop/plains30-v1/manifest-progress-8-v2.json --list
python3 -m pcg.prototype.creative_batches.plains50_catalog \
  --manifest generation/workshop/plains30-v1/manifest-progress-8-v2.json --play D05-1
python3 -m pcg.prototype.creative_batches.plains50_catalog \
  --manifest generation/workshop/plains30-v1/manifest-progress-8-v2.json \
  --play D04-1 --route park-reward-and-descend
```

真实物理、原regular质量门槛、原CandidateLibrary和标准输出合同继续复用。当前方法与失败账本在 `pcg/creative-production/batch30/`；新双门Cell在 `pcg/prototype/creative_batches/batch30_cell/`，只有一开一关，并在关门会夹住玩家或敌人完整身体时拒绝整次切换。该Cell不自动证明单向路。

B可先按[首交接](../../../docs/l4-mapgen/plains30-first-handoff-v1.md)消费局部标准Module；任意进入状态、通用回程/接缝、变换和整图仍UNKNOWN。回程/恢复影片是精确同世界试件，不自动升级通用装配合同。

两份真实C01→D05连续试件、两份穿插冲突及准确可协商条件见[接缝交接](../../../pcg/prototype/creative_batches/batch30_seams/manifest-v1.json)。只原实体平移并集，无新增连接平台或资源恢复。接缝片同类支持ID差异仍是review-only，技术试件与视频精确状态分别记录。
