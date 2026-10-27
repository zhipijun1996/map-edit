# N08 / N11 独立内容审查增补

本次只审三个精确版本：N08 `1685840df001…`，N11 W/W `1b61e4024681…`、E/E `c98366c7d7fb…`。延续[前27记录审查](curation-block27-v1.md)，文件名的30是已审版本并集，不是实时库总量；期间其他版本未自动获得本审结论。来源为当前独立Codex子代理，具体模型版本未暴露。未新增Godot调用、未改原报告/库/profile/全局预算审计。

**结论：N08保留为连续取奖与回程的技术样品，后移新创意主审队列；N11保留为原A4落唇刹车的一份代表加一份朝向适配。新增三版不增加独立玩法家族，不建议技术撤回或新增design_hold。**

实际看过五段影片的时序抽帧，包括799帧连续来回片；另读实际cases、动作程序、clean原始轨迹、held目的、反例与原父规则。视觉判断和轨迹证据分开，完整版本/SHA见[结构化报告](curation-block30-addendum-v1.json)。

**N08：空间返回成立，但创意辨识度偏弱。** 画面能读出上层去、下层回：去程三段相近的同向跳射，取16币、越柱到B；回来地面射access，上桥撤、下桥出现，落下后沿低桥走回A。低桥确有真实承载和回枪，同世界只取奖一次，没有重建或改钱包。这可以支持精确的双向高差奖励节点、持续机关状态与奖励事务复用。

作为新创意主角，它仍主要是已有接地反冲接力＋互斥支撑换路；回程换桥后较长步行，去程三次动作较相似。当前不具备已测的速度、动作数或风险收益优势。我建议把它留在“连续返回样品”，而不以更好玩/新家族作为主卖点。这是AI观感，不是用户对本版本的无聊反馈。

| 同一16币、实到B再返A | 低桥名义 | 原高路合法替代 |
| --- | ---: | ---: |
| 枪 / 跳 | 4 / 4 | 4 / 4 |
| B首次稳定帧 | 388 | 388 |
| A首次稳定帧 | 778 | 760 |
| 回程稳定点间隔 | 390 | 372 |
| raw帧数 | 799 | 781 |

低桥在这个已核raw比较中慢18帧，约0.30秒，不叫捷径或省动作。`780`是旧高路末帧索引，不是其raw帧数；应采用已核raw稳定A的778/760比较，避免混入索引与尾部等待。旧receipt/展示manifest中的779/391与本审实际读取的loop-clean-v2、full校准/held的778/390不一致；保留原摘要，但不把它当作另一份未找到的raw样本。原receipt不改。晚到低岸再射primary换桥也是合法较慢解；fresh B反走旧高路还可真实领取未取过的箱，不能伪设“已取奖”来排除收益。旧高路不因为缺“下桥”动作词而被判错。

N08标准Module仅A→B与fresh B→A；连续A→奖→B→A是独立fixture，在候选generation.source/validation中薄绑定为受限附证，不是新增Module、自环路线或通用状态返回。连续片单列，不算第三段单Module canonical影片。独立loop校准25/25、held25/25只覆盖冻结世界与策略，未签一般失误、外部状态、接缝或整图。

**N11：短动作核心清楚，WW/EE是适配。** 人物先走出厚岩外沿，身体完全低于岩唇再向外射击，止落并反向回袋领10币。raw中WW帧118为vx260→−1100、vy800→0；EE帧120为vx−260→1100、vy800→0，实际袋顶落脚帧141/146并回枪。不是只有中心点经过，24×36身体扫掠没有穿原岩。

它与已有A4“先跌出遮挡再反冲回唇下”的观察/决定相同，新增价值是同侧错位Block口W/W与E/E的真实覆盖。两片都很短、动作后果可见；适合作一个小动作节拍，不能把镜像或两个Port朝向算两种新玩法。EE针对其父几何真实镜像后独立重验，不继承WW证据。

WW held三档均通过全部样本；EE moderate11/12，其失败保留。两份原底岸1跳1枪到袋252/260帧是允许的较慢恢复替代，对名义1枪0跳157/161帧；不能以多跳而否认合法解，也不因此保证任意失误可恢复。B→A及实际Map联合赋值仍UNKNOWN。

| 已实际抽帧查看 | 原生比较范围 |
| --- | --- |
| [BN11-WW-v1](../../../generation/workshop/plains30-block-v1/videos/BN11-WW-v1/block128-underledge-brake-return.mp4) | 157帧，strict通过 |
| [BN11-EE-v1](../../../generation/workshop/plains30-block-v1/videos/BN11-EE-v1/block128-underledge-brake-return.mp4) | 161帧，strict通过 |
| [BN08-out-v1](../../../generation/workshop/plains30-block-v1/videos/BN08-out-v1/folded-reward-upper-out-lower-back-review-only.mp4) | 408帧，review-only；strict失败2处support_id差异 |
| [BN08-back-v1](../../../generation/workshop/plains30-block-v1/videos/BN08-back-v1/folded-reward-upper-out-lower-back-review-only.mp4) | 393帧，review-only；strict失败4处support_id差异 |
| [BN08-continuous-loop-v1](../../../generation/workshop/plains30-block-v1/videos/BN08-continuous-loop-v1/folded-reward-upper-out-lower-back-review-only.mp4) | 799帧，review-only；strict失败4处support_id差异 |

N08差异完整枚举在JSON内，分别为out帧56/57、back帧236/302/316/317、loop帧56/57/721/722；没有把support_id差异豁免成严格通过。未看过原高路的原生影片，其比较结论来自实际raw和同任务对照。

**人工视频认可、实际试玩、趣味批准、生产认可全部UNKNOWN。** 技术候选资格继续保留；如果后续要让N08承担新的返回选择创意，应先明确为什么选低路，并用实际差异验证，而非增加装饰、危险或强制开关词序。
