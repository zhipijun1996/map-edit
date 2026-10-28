# 平原批次001：AI去重后的人工视频审阅包

**32个版本 → 18个审阅组：18个主代表、6个有用适配、8个冗余变体。** 这是当前Codex子代理的归类，不是18个新家族、人类评分或生产批准。原库、技术状态及所有原件均保留。

每组先看一个代表；G06现有影片仅覆盖高路，低路影片尚缺，G03可展开看折返适配。其余适配默认折叠，不重复填满首轮队列。可直接在聊天按G编号反馈决定是否清楚、节奏/可读性、是否重复；无需填写评分表或亲自试玩。

## 主审阅队列

|组|代表：玩家要作的决定|已有视频原件|标准文档|代表版本|
|---|---|---|---|---|
|G01|有净空限制的定向反冲跨越：读上下净空与目标岸，选择起跳/射向使身体穿过通道。|[视频](../../../generation/workshop/v2/videos/thorn-slot.mp4)|[MapNote JSON](../../map_directed/library/candidates/c5825cd704759634c00a9277ce0f94c9948d70d6c8bfd2c09b55b73d3c1399a8/module.mapnote.json)|`c5825cd70475`|
|G02|下落过檐后反冲刹入凹槽：先落到悬檐下，再决定何时制动返向进入侧袋。|[视频](../../../generation/workshop/v2/videos/brake-under-ledge.mp4)|[MapNote JSON](../../map_directed/library/candidates/ca4aa8bdf05b7e5ac7e587aee258adf983c95b5c47e56c56e4ed88b914f4b547/module.mapnote.json)|`ca4aa8bdf05b`|
|G03|命中有限活敌恢复空中枪后续飞：把会攻击的敌人当真实补给机会，命中后决定第二枪的去向。|[视频](../../../generation/workshop/v2/videos/air-refund.mp4)|[MapNote JSON](../../map_directed/library/candidates/4aa99b6f4b965abdc989a217006a99a8239a734979d772e4faf59b77a2310bda/module.mapnote.json)|`4aa99b6f4b96`|
|G04|同枪开短门并穿门：把开锁射线与身体穿过短窗口的时机一起考虑。|[视频](../../../generation/workshop/v2/videos/timed-cache.mp4)|[MapNote JSON](../../map_directed/library/candidates/8c90c97e8fc15b43794c44d61bb64ed65be62df73b2c185be0285e94facc9a4a/module.mapnote.json)|`8c90c97e8fc1`|
|G05|射铃启动并主动追上移动落点：同枪释放台后主动截获，选择暂停/离台。|[视频](../../../generation/workshop/v2/videos/chase-landing.mp4)|[MapNote JSON](../../map_directed/library/candidates/26544bbf5c94d81a45bc1953800c97cbe0a62a42f0971aa1b0a59e67094972b0/module.mapnote.json)|`26544bbf5c94`|
|G06|唯一空中枪投资高奖励或低主路：观察高处收益和低处出口，为本次唯一空中枪选去向。|[高路](../../../generation/workshop/v2/videos/one-shot-two-routes.mp4)（低路影片尚缺）|[MapNote JSON](../../map_directed/library/candidates/e90dfa359fd066b3280e0bebdb0fca7735e210c5c66ab8467c896fdceb48bb13/module.mapnote.json)|`e90dfa359fd0`|
|G07|短门→刹袋→实体回程的连续探索组合：依次取两处奖励，再利用下降/跳台/反冲回原岸；也可查看漏接恢复。|[视频](../../../generation/workshop/macro-v1/videos/M01.mp4) **待查：review-only，严格比较失败**|[MapNote JSON](../../map_directed/library/candidates/167dcb6ec336cd7ff659febe66b44a3daabfe79922a9ddca5c041e62e28d114e/module.mapnote.json)|`167dcb6ec336`|
|G08|清除吸弹敌身以打开同线射界：先处理挡射线的敌人，再把下一发送到远铃。|[视频](../../../generation/workshop/creative20-v1/videos/M09.mp4)|[MapNote JSON](../../map_directed/library/candidates/0e52e3732ffbae67d01f6636592f765a9a145ef6fc85787fdd287e2000a90976/module.mapnote.json)|`0e52e3732ffb`|
|G09|离开出口方向取得射界再折返：先向目标反方向探身，打开永久门，再回到先前通路。|[视频](../../../generation/workshop/creative20-v1/videos/M10.mp4)|[MapNote JSON](../../map_directed/library/candidates/708a6dd6002a8db604e732f418d733eec70fb9c4e0055b5208e47ef31076a0a3/module.mapnote.json)|`708a6dd6002a`|
|G10|主动暴露让敌人攻击开门再离开弹线：保持视线使敌人提交攻击，再进入掩体通路；太早走和太晚等均有代价。|[视频](../../../generation/workshop/creative20-v1/videos/M07.mp4)|[MapNote JSON](../../map_directed/library/candidates/747d7f54552a19296df32b51ac2bd86a8cb6fbd91b06bd46d309348958437ae4/module.mapnote.json)|`747d7f54552a`|
|G11|推活敌占区，保留它维持远门：把敌人作为要保留的世界钥匙，取得持续开门支持后通过。|[视频](../../../generation/workshop/creative20-v1/videos/M11.mp4)|[MapNote JSON](../../map_directed/library/candidates/851be7661e7c931976999bad1aa9d819e7712142880d23c11394a381b67b7d37/module.mapnote.json)|`851be7661e7c`|
|G12|开脚下桥，承诺下降进入新通路：从有射界的位置撤除支撑，承诺下落；允许合理空中开桥。|[视频](../../../generation/workshop/creative20-v1/videos/M12.mp4) **待查：review-only，严格比较失败**|[MapNote JSON](../../map_directed/library/candidates/b4634207ffe04d75ab5fb4308714818158cc5b9e26f6c97c8340cf3752f5b3b4/module.mapnote.json)|`b4634207ffe0`|
|G13|击退敌身腾出真实安全落位：下落时处理挡住落点的敌体，以获得实际可站的身体空间。|[视频](../../../generation/workshop/creative20-v1/videos/M13.mp4)|[MapNote JSON](../../map_directed/library/candidates/d5fe842b15c1b85d978230799de0058e58c2f290258eaf5068e03352ed493607/module.mapnote.json)|`d5fe842b15c1`|
|G14|离开危险载台，在安全岸后重接同台：预测同一运行载台未来位置，暂离避险后再次截获。|[视频](../../../generation/workshop/creative20-v1/videos/M16.mp4)|[MapNote JSON](../../map_directed/library/candidates/d111648359a582cf23082401d12276881fa995b8b310970ca15ed15316ba091e/module.mapnote.json)|`d111648359a5`|
|G15|瞄准弹丸经过运动挡板后的射线窗口：根据挡板相位选发射时机，同时保留人体渡口的反冲机会。|[视频](../../../generation/workshop/creative20-v1/videos/M17.mp4)|[MapNote JSON](../../map_directed/library/candidates/de3f1cb2b2456022c4d4b0e3a884fa0b7ef6ae3bcc2e3ff02d09335bf061f577/module.mapnote.json)|`de3f1cb2b245`|
|G16|跟随危险释放的走廊并掉层避返程：进入刚释放的空间持续推进，在危险回返前离开其轨道。|[视频](../../../generation/workshop/creative20-v1/videos/M08.mp4)|[MapNote JSON](../../map_directed/library/candidates/e1aed107d2df1af781c1b3fdf8f2409d5d6093973ae967a186e2a8995484d888/module.mapnote.json)|`e1aed107d2df`|
|G17|共同可射目标的非交换顺序事务：识别两个同时可命中的目标，选择实际能推进世界状态的顺序。|[视频](../../../generation/workshop/creative20-v1/videos/M19.mp4)|[MapNote JSON](../../map_directed/library/candidates/35a76f5584c914dd5701edf175fffbaa89b28a19c8c072d6e711b52c620da659/module.mapnote.json)|`35a76f5584c9`|
|G18|同台先维持远门再释放作唯一移动支撑：在平台钥匙职责与运输职责间做交接：过门后放弃持续开门，取回载台。|[视频](../../../generation/workshop/creative20-v1/videos/M20.mp4)|[MapNote JSON](../../map_directed/library/candidates/b0a994d20b21700fbe3c3159f7bdda5467b19838d3adfb623058c116268413d0/module.mapnote.json)|`b0a994d20b21`|

**G07限制：** 原影片真实完成取宝回程，但已有严格比较记录因`support_id`顺序不同而失败。本包只把它作为连续探索/恢复的观感片，列入人工待查；不称全字段exact，不用影片替代技术证明。该组组合G02/G04，新增动作家族数为0。

**G12限制：** M12原生片有32处`support_id`差异，严格比较失败，仅作观感审阅。G06两个已有索引实际指向同一高路片，不能充当高/低两路；本包只排一次高路，低路视频保持缺口。

**平原兼容不等于反冲示教：** G10/G16发布策略没有射击；G08/G09/G11/G12/G13主要是射击改变世界，G17主要教目标顺序。它们可服务平原节奏、探索、战斗和组合，不冒充基础反冲课。

<details>
<summary>展开6个有用适配（仍属原组，不增加家族）</summary>

|组|版本与用途|已有视频|标准文档|
|---|---|---|---|
|G02|`671c68bdd229`：有明确lip246/pocket466/x115需求与P4独立证据；有用性来自需求匹配，不是坐标更换本身。|[原件](../../results/workshop-plains-method-media-v1/P4/brake-under-ledge.mp4)|[MapNote JSON](../../map_directed/library/candidates/671c68bdd229e6e8a00f53907cf749a9a44769704b9f2c03f842b04e0cbed26b/module.mapnote.json)|
|G03|`7c06b9a528bb`：命中回充后第二枪改为折返入口上方，改变出口方向与后续接口；仍为air-refund子接口，值得附一段对照视频。|[原件](../../results/workshop-production-media-v1/T01/air-refund.mp4)|[MapNote JSON](../../map_directed/library/candidates/7c06b9a528bb98997869a603c3e8454253e8119112e54c57acdb86a287b9a66f/module.mapnote.json)|
|G02|`9c2b5f3c7424`：有明确lip250/pocket453/x100需求与P3独立证据；保持过檐后刹入同一决定。|[原件](../../results/workshop-plains-method-media-v1/P3/brake-under-ledge.mp4)|[MapNote JSON](../../map_directed/library/candidates/9c2b5f3c74249c2be731653de04c85d039aa1bb306eaccc2eb83f95f753491f1/module.mapnote.json)|
|G01|`aa4aa60a36d6`：有冻结需求front505/top438与P2独立证据；作为另一具体需求的交付接口保留，而非以距离增加家族。|[原件](../../results/workshop-plains-method-media-v1/P2/thorn-slot.mp4)|[MapNote JSON](../../map_directed/library/candidates/aa4aa60a36d6d93d4eed0bb03d8be85b6c70579f19e65b453093364c3eef99d9/module.mapnote.json)|
|G05|`d65bc5715ce9`：原Map需求有100高差、无奖励通行职责和特定空间预算；标准合同/反例独立，保留为通行适配。|[原件](../../../generation/workshop/map-carrier-rework-v3/chase-landing.mp4)|[MapNote JSON](../../map_directed/library/candidates/d65bc5715ce9ec73bfe8f6b88ee17381519d97484528b3e98f9e9147cb9d1884/module.mapnote.json)|
|G01|`fad73947ee6c`：有冻结需求front475/top430与P1独立标准/视频证据，承担适配工单；保留接口，不当新玩法。|[原件](../../results/workshop-plains-method-media-v1/P1/thorn-slot.mp4)|[MapNote JSON](../../map_directed/library/candidates/fad73947ee6c41eb643dd746b7dc680039dfc038159d22ffbe5a6da35bcaa2bf/module.mapnote.json)|

G03折返适配改变了命中续枪后的出口方向，值得与前进代表对照；G05适配承担原100高差无奖励通行需求。P1–P4对应四个明确空间工单，保留的是需求覆盖价值，不是“距离不同所以新玩法”。

</details>

<details>
<summary>展开8个折叠的冗余变体（原库不删除，可按精确需求重新启用）</summary>

|组|版本|本轮折叠理由|原文档|
|---|---|---|---|
|G07|`04a93aeaf9d4`|与代表同样短门→两箱→刹袋→实体回程，四有向路线与连续世界语义相同；接缝/坐标偏移未新增探索决定，首轮折叠。|[MapNote JSON](../../map_directed/library/candidates/04a93aeaf9d4c19f132097e52e97faecda0da4b15b35539ee4be69598ca03c58/module.mapnote.json)|
|G03|`16ac1de2691c`|已由7c06保留折返子接口；本版同样命中后转回，差别为接收坐标/高差，首轮无需第二个折返视频。|[MapNote JSON](../../map_directed/library/candidates/16ac1de2691c91b7622413e4838b63d6d0f361963f58c73164119ecc7d529906/module.mapnote.json)|
|G02|`21029b907d05`|与代表同样下落过檐→一枪返向→凹槽领奖；不同凹槽高度未新增状态或回程职责，首轮折叠。|[MapNote JSON](../../map_directed/library/candidates/21029b907d05a8cc45163abf0dfc3abe7a5e6d34ce7fa76b7327cfaa77d55001/module.mapnote.json)|
|G03|`3c1c61652792`|前向命中回充→续飞与代表同一动作因果和资源来源；更高远岸未新增决定，首轮折叠。|[MapNote JSON](../../map_directed/library/candidates/3c1c616527925c9cad825e6e15afeb69649423733ee7d5fa3a57e6de2c7133d3/module.mapnote.json)|
|G04|`490a5f1478c3`|同一枪开短门并推进的判断不变；门距/0.65秒窗口是参数适配，当前未有独立需求驱动，首轮折叠。|[MapNote JSON](../../map_directed/library/candidates/490a5f1478c34f1040d2c01dfdb2e7ad3fc09dc7bd3b7a70641ff6a0f37280ad/module.mapnote.json)|
|G05|`6b9d2d9858db`|同样启动→截获→暂停/离台，运行模式和资源相同；较长轨道/时间无新增取舍或已绑定需求，首轮折叠。|[MapNote JSON](../../map_directed/library/candidates/6b9d2d9858dbb646b119182e597096264618d7e907588f6ee63ac99545016b63/module.mapnote.json)|
|G01|`89cc9ca617c8`|与代表保持同一净空判断、单枪资源、奖励职责及单向关系；仅较高接收岸/尺度变化，未找到独立调用需求，首轮视频不重复排。|[MapNote JSON](../../map_directed/library/candidates/89cc9ca617c8ebb042a28569c3eed5468c3afad843d9964cde1c19b46e855d2e/module.mapnote.json)|
|G06|`8e0ad37d208f`|保留同一个高奖励/低主路二选一及两条有向关系；高低落点变化未新增资源/世界状态取舍，首轮折叠。|[MapNote JSON](../../map_directed/library/candidates/8e0ad37d208f3f69a020c44fd746a90f14ce46727d6e561b627af7eaea1423ce/module.mapnote.json)|

这里的“冗余”仅指首轮人工审阅不重复排片，不能推断该精确接口对任何未来空间请求都无用。部分折叠版本未找到自己的精确视频索引，代表片只解释共享决定，不作为那些版本的录像证据。

</details>

## 反馈与暂扣边界

D01被用户判为新提案冗余，降低的是重复提案优先级，**不使G01等已有基础反冲内容失效**。D02–D05仅有设计正向反馈，本批不计为已实现产物；用户对旧20项的整体正向视频观感不扩写为逐版本批准。每个版本`human_approval=UNKNOWN`、`production_admitted=false`。

原双台转乘`331f331fdce3…`已被输入catalog排除，不属于本次32项。其`pacing_held`来自root模型看37.45秒原速影片后的节奏判断，不是人类差评、物理失败或技术撤回。

## 实际阅读范围与证据

本次实际读取输入catalog、32份标准合同、32份统一库record、19份额外原库record，以及22份case源文件中这32版本绑定的40条发布路线case；比较控制计划、人物/机关/敌人、端口与有向路线。还读取了已有视频manifest、源绑定/轨迹索引并核对文件SHA。**没有打开观看视频，没有新增逐帧轨迹审查、没有回放或运行物理。**

所有18组代表均有已有影片索引。Macro的review-only/strict失败原样可见；6个折叠版本没有在所读索引中定位自己的影片，不拿相同标题的视频顶替。本轮只使用已有文件链接，未新增上传或声称做过公网核验。

- [32版本逐项去向与完整SHA证据](plains-batch-001-ai-review-v1.json)
- [输入catalog](../../../generation/workshop/plains-recoil-v1/catalog.json)
- [本轮人工原话](../../feedback/workshop/idea-sources/human-plains-batch-production/v1.json)
- [设计反馈范围](../../feedback/workshop/plains-five-design-feedback-v1.json)
- [批次skill协议](../../../.agents/skills/pcg-creative-producer/references/batch-production-v1.md)

JSON中的`representative`表示供人工先看的样品；所有归类仍是模型裁定。旧review-v8、selected20及原库未修改，也未发起技术撤回。
