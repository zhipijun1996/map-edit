# 平原 Module：Block128 生产批次

当前[24份标准候选](manifest-progress-24-v1.json)，原库132版、平原优选114版；不是30份Block完成，也不是24种全新玩法。此前8份局部候选仍保留原资格，没有自动转为Block版本。当前Map合同来源为`research/l4-map-generator@862b736`，见[源码绑定与交接](../../../docs/l4-mapgen/plains30-block-handoff-v1.md)。

| 内容 | 包围尺寸/拥有格 | 实际玩法与影片 |
| --- | --- | --- |
| C02-1/2 空中气闸 | 1408×896，47/46格 | 空中同枪反冲、关身后门开前门；[下沉出口](videos/BC02-1-v2/block128-serial-airlock-review-only.mp4)，严格录像比较未过，供观感 |
| C01-1/2 换脚桥 | 1792×1024/76格；1408×1024/61格 | 同枪撤旧桥造新桥，真实落桥回枪再出发；[升层版](videos/BC01-2-v2/paired-support-transfer-review-only.mp4)，严格录像比较未过，供观感 |
| C05-1 三口移动站 | 1536×1280，94格 | 同一乘行选择点：[早离台回折到西上岸](videos/BC05-near-v1/block128-moving-station-choice.mp4)或[继续乘行、换门去东上岸](videos/BC05-far-v1/block128-moving-station-choice.mp4)，351/341帧严格比较均通过 |
| D05-1/2 风铃台追接 | 见标准清单，均Block128 | 跳起左下击挂载铃，同枪反冲+启动台、台接住第一次落脚，回枪后二跳到岸；[325帧严格比较通过](videos/BD05-1-v1/block128-bell-carrier-catch.mp4) |
| C07-1 关墙刹车袋 | 见标准清单 | 同枪开前门/关后墙，以真实新墙接触刹住反冲，再落袋回枪；[246帧及原Motor接触逐帧一致](videos/BC07-1-v1/block128-new-wall-collision-brake.mp4) |
| C10-1 条件纠错侧洞 | 896×1280 | [正常主路189帧严格一致](videos/BC10-main-v1/block128-retained-shot-recovery.mp4)；[失误入洞、真实返新A重试507帧](videos/BC10-retry-v1/block128-retained-shot-recovery-review-only.mp4)，后者1帧support_id不同，仅供观感 |
| N04-1 四口升层选择 | 1280×1024，80格 | 同一门先开孔让人上穿、再关闭成为落脚/回枪面，再择左右高岸；[A→B](videos/BN04-A-B-v1/timed-gate-return-catch-review-only.mp4)、[A→C](videos/BN04-A-C-v1/timed-gate-return-catch-review-only.mp4)，仅support_id差异，review-only |
| N04-2 三口非对称选择 | 1280×1024 | 左高岸需再跳射、右低岸只需离台跳；[右侧分支](videos/BN04-low-C-v2/timed-gate-return-catch-review-only.mp4)，371帧/1帧support_id差异 |
| A1-1/2 尖刺空槽双向 | 1280×896，39/44格 | 真实身体穿刺槽，宝箱可见；[正向124帧](videos/BA1-forward-v1/block128-human-A1-bidirectional.mp4)、[另一空间反向146帧](videos/BA1-return-v1/block128-human-A1-bidirectional.mp4)，严格逐帧一致 |
| A2-1 主动追台/逆向冷台 | 1408×768 | [正向6秒节选](review-excerpts-v1/BA2-forward-v1-excerpt.mp4)、[反向6秒节选](review-excerpts-v1/BA2-return-v1-excerpt.mp4)，字幕明确省略抵达后的验收停留；两段完整1000帧严格片另存 |
| A3-1/2 短时风铃门双向 | 1408×896 | [空间一](videos/BA3-forward-v1/block128-human-A3-bidirectional.mp4)、[空间二](videos/BA3-forward-2-v1/block128-human-A3-bidirectional.mp4)，各157帧严格一致；实际0.55/0.65s窗，不是单帧操作 |
| N06 三口中庭双翼 | 1280×1152 | 共同M落地回枪后，[保留左桥向西上](videos/BN06-left-v1/central-two-wing-bridge-choice-review-only.mp4)或[击铃换成右桥向东上](videos/BN06-right-v1/central-two-wing-bridge-choice-review-only.mp4)，每支真实落桥恢复后登岸 |
| N06 四口中庭双翼 | 1280×1152 | 新东低入口D；[D→西上B](videos/BN06-four-D-B-v2/central-two-wing-bridge-choice-review-only.mp4)、[D→东上C](videos/BN06-four-D-C-v1/central-two-wing-bridge-choice-review-only.mp4)，实际A/D→B/C四方向全部原regular通过，其余8对UNKNOWN |

所有尺寸为128倍数；拥有格四邻接连通，可不规则。不生成外框，内部地形不缩放。SVG与可玩消费者显示Block轮廓、真实边界中心锚点和内部身体站位。Port锚点不是出生点：ground64地面在anchorY+32，人物中心在anchorY+14，本轮水平dock还向内24px。

C05是真正去向选择，不是额外安全口。A是低处西口，B是上方西口，C是高处东口；同一世界初态下分别验证A→B/A→C，其他四个方向UNKNOWN。它是新Block地貌规则，超出旧终岸±32适配域，因此重新校准；原型与旧版通过结论没有挪用。

十三组成功生产运行共2797次真实Godot案例，含全部失败与精确反例。C02、C01、D05各两份及C05/C10的两条路线、C07一路均过原regular校准和独立留出。C05的动态世界clean/mild/moderate各12次，留出两路线各36/36；D05两接口留出各clean12/12、mild12/12、moderate11/12；C01/C02静态世界clean各1次，mild/moderate各12次。它们仅为有限程序策略资格，不是人工成功率。

C01/C02两个review-only影片各有3帧`support_id`接触体顺序差异，完整差异见其`review-only-manifest.json`和`strict-failure-audit-v1.json`；位置、输入、资源、机关、奖励字段一致。原严格比较仍失败，没有放宽。C05两片、D05、C07、C10主路共加上A1双向270帧，加上A3两片314帧、A2两片2000帧，再加N11两片318帧，共4354帧是严格比较通过的正常60fps原生连续输入回放，末尾约1秒冻结结果画面。

## 运行与检索

```sh
python3 pcg/tools/restore_archive.py godot-runtime-v1 --extract
python3 pcg/tools/restore_archive.py content-workshop-plains30-block-v1 --extract \
  --prefix results/workshop-batch30-blockc05-full-v1/
python3 -m pcg.prototype.creative_batches.plains50_catalog \
  --manifest generation/workshop/plains30-block-v1/manifest-progress-24-v1.json --list
python3 -m pcg.prototype.creative_batches.plains50_catalog \
  --manifest generation/workshop/plains30-block-v1/manifest-progress-24-v1.json \
  --play C05-1 --route far
```

默认进入手动试玩；加`--replay`为程序见证。复现生产使用`batch30_runtime.produce_v3`和新run名；固定协议在`pcg/creative-production/batch30/protocol-map-block-v4.json`。原CandidateLibrary持久化检索见[前13份跨进程复用](retrieval-v3/receipt.json)及[新增4份](retrieval-v4/receipt.json)、[第18份](retrieval-v5/receipt.json)及[新增3份](retrieval-v6/receipt.json)，生成与物理调用均0；C05新增记录同样来自原磁盘库。

## 请求、失败与待做

C02实际消费最新B的`block-demand/exp1_0`，按其`rewards:[]`移除奖励并重验。C01/C05只响应明确的Task A派生需求，保留自己的宝箱，不能冒充B的无奖励或junction请求。标准清单保留完整请求、回应及逐方向关系。未知输入状态、反向、跨边界、Map奖励预算与整图不自动满足。

C06坠井选层的新Block规则尚未入库：高路完整校准moderate7/12，低于原.65门槛，整份三口拒绝，独立留出未运行。已用完两次几何修订，不靠改名补数量。第一轮曾把低路多付一枪、身体向入口外越2.89px误当机制反例；新分类保留了外部空间依赖UNKNOWN，严格名义身体检查未改，最终仍因真实瞄准容错不足拒绝。

D04r2的原中间岸既供主路离开又供同世界回程使用，朴素Block端口外邻还被高柱占用。当前返回具体`needs_design`，没有删回程或扩掩码假通过。气闸镜像接收器边界试件的第二轮只有11/13，未签接缝。D05错枪重试实际到奖，但身体越出入口外邻，因而新版本恢复资格仍UNKNOWN；不能继承旧恢复结论。其余内容继续按新版本验证。C10初次全量实际已过校准/留出，但反例ID后缀未绑定原canonical而被原库正确拒绝；仅修注册ID后完整重跑，不修改地貌、策略、噪声或门槛。旧155次失败保留，重复相同留出不算额外独立条件。现入口在0物理调用时预检反例ID/原几何/Block所有权绑定。

源码、全部失败、留出和冻结快照归档为`content-workshop-plains30-block-v1`；D05另在`content-workshop-plains30-block-v2`；C07/C10在`content-workshop-plains30-block-v3`。旧未准入原型及失败由`content-workshop-plains30-prototypes-v1`保留。最新网页兼容补丁[PR #6](https://github.com/zhipijun1996/map-edit/pull/6)已部署，[公网字节回执](editor-compatibility-v1.json)记录校验；内容索引仍通过现有“更新本仓库模块”按钮获取。

技术候选、视频观感、实际试玩和生产批准分别记录；人工趣味/试玩/生产准入均UNKNOWN。

## 新增交接与诚实的体验分组

N04四口只验证A/D→B/C四个有向对，其他八对UNKNOWN；三口仅A→B/A→C，其他四对UNKNOWN。它不是额外安全口：同门开孔/关回承载后，再决定高岸去向。三口第二版本明确降低右岸、封原第四外口，只保留内部恢复岸，完整重验，不能仅改Port标签。

[真实双N04接缝](../../../pcg/prototype/creative_batches/batch30_blockn04_seam/handoff-v2.json)保留两源实体精确并集，同一人物、零补平台/资源，90实际案例含原控制失败，最终cal25/25、held23/25符合原regular。[836帧接缝影片](videos/BN04-seam-v1/exact-N04-block-continuity-review-only.mp4)有4帧support_id差异，原strict仍失败，额外两门观察836帧一致；不冒充单Module录像，不增加候选/家族数量。

A1四条方向全部原regular通过，另有两条clean同世界A→B→A，254/314tick，同一个宝箱事务/钱包8，没有重建人物或重复发奖。这两条连续试件尚无扰动资格。A1保留原8币只向真实Map r3提供金额/口映射提案；无奖励需求返回动机冲突，未知总预算不自动满足。

N02主动双台分叉经过80probe、两次full52+124，高路线最终moderate1/12，整接口0候选/held未跑。失败推动后续设计改变接收窗口/射线可见性，不改名或降低门槛。新N04/N02/A1及完整接缝原件均在`content-workshop-plains30-block-v5`，可按精确results前缀恢复。

独立模型审阅指出C10初次纠错射击前已经碰顶盖/真实回枪，因此它证明的是**有真实一枪时的开袋纠错、返A重试**，不能声称从初跳一路保留唯一空中资源。它归已有恢复关系的有效扩展，不计新家族；技术资格保持原用例范围。人工观感、试玩与生产批准仍分别UNKNOWN。

`manifest-progress-13-v1.json`保留为发布器诊断历史：其14条视频错误包含一条双N04接缝。当前v2严格按内容版本和精确case SHA双绑定，13条Module视频；接缝独立列出，不向单Module继承。

[独立AI审阅与8段首看队列](../../../pcg/creative-production/batch30/curation-block21-v1.md)覆盖旧local8+Block11+旧held2快照：19活跃版归8组、11适配；不含后来A1，不是全库家族总数。代表只解释对应版本，不能替代其他版本证据。

## 当前新增验证与方法修订

A2最终`api_v3`只输出一个双向空间，另一个返程扰动失败仍拒绝。两次完整物理之后的导出元数据失败共398案例保持原件；最终199完整案例过原regular且重检索，三次相同held不算三套独立条件。原Map UNKNOWN输入另存，具体本地relations/space/normals/基础move桥接显式编译；区域foldback没有被本地资格替代。原consumer字段现已在0物理调用预检，不能用缺字段消耗完整实验。

N06原周期52案例容错失败（M贴边、远铃敏感），新明确几何周期4clean+24noise，总谱系仍80封顶，旧失败不覆盖。仅扩大M左边与缩短枪线，在噪声前按真实完整身体落脚水平余量选c1，最小54.833px；154完整cal/held全过。独立四口是新的接口需求：M右侧扩大64、新D岸，70probe+336完整案例、4路线全部cal/held全过；不是给三口安全地板贴D。它是同一家族的有效空间适配。匿名support_id差异影片仍review-only，严格比较器不改。

N03新反向Cell的8个真实运动/承载对照成立，但Module总54次后发现地面射击可持续安全乘台355帧、同3枪少1跳到同奖口，直接推翻空中反转接回的风险假设。0 Module、无full；保Cell与原反例，不改名当成功。

A3地面预开+空中反冲是合法多一枪替代，可能比名义更快；底岸也是已验返程而非唯一解。同枪开门是可执行示范，不宣称所有解都必须如此。A2节选的[修正审计](review-excerpts-v1/manifest-v2.json)直接读原fired_commands，完整影片保持不变，不把节选计新录像证据。

最新Map源码862b的24文件、Git blob/字节SHA已核。Block128/JS/锚点公式未变，新增Module自有条件/单向边界门覆盖和同Module同高原支撑并集。改后新版本须真实Map验收，不自动给现有候选单向/整图资格；512高边界门也可能割到同面另一口。18版本33方向已用新原validator静态核对，0新物理、旧证据原身份保留。

原件新增`content-workshop-plains30-block-v6`（A2/A3含398元数据失败）、`v7`（N03与N06原失败/修订）、`v8`（独立四口）。独立AI[27技术记录增补](../../../pcg/creative-production/batch30/curation-block27-v1.md)覆盖截至Block17的25活跃版，11审阅组/14适配；四口为后续适配，不能借此增加新家族计数。所有新候选人工观感/试玩/生产均UNKNOWN。


## 新增三份：回廊与下落刹车

N08上行取16币、下行换桥返回：双向Module157完整案例通过；另同一人物/宝箱/世界A→B→A连续50案例通过，两者证据不互换。[完整连续片](videos/BN08-continuous-loop-v1/folded-reward-upper-out-lower-back-review-only.mp4)799帧有4处support_id差异，仅供观感；两段Module片408/393帧分别2/4处同类差异。旧高路返回仍是合法解，同任务配对对照下路约0.3秒更慢，不称捷径。它是连续取奖/回程技术样品，是否有趣待人工评审。

N11岩唇下刹回宝袋：[W/W 3.7秒](videos/BN11-WW-v1/block128-underledge-brake-return.mp4)、[E/E 3.77秒](videos/BN11-EE-v1/block128-underledge-brake-return.mp4)，157/161物理帧逐字段严格一致。两接口154完整案例通过原regular，E/E中等扰动11/12，其余全过；落底原岸保留，付费重试小样本不能替代通用恢复/返回。两种接口仍是一种旧A4动作关系的适配。

N10双铃遮挡恢复路线mod5/12未通过，0候选、留出未运行；80probe含3零帧拒绝及107full均保留。新闭合原件[归档v9](../../../pcg/archives/content-workshop-plains30-block-v9/manifest.json)含N08/N10/N11失败、冻结源与全部真实实验；26205工件逐SHA恢复检查通过。最新Map静态兼容为[21版本37策略/36有序对](../../../pcg/creative-production/batch30/latest-map-compatibility-v5.json)，静态检查不冒充新物理或整图证据。

独立AI[三版增补审查](../../../pcg/creative-production/batch30/curation-block30-addendum-v1.md)把N08后移创意展示队列、N11归旧A4代表/适配，没有撤回技术资格；逐raw纠正低回稳定帧778/旧高760、相差18帧，早期摘要779/391保留为未与raw一致的原声明，不混作另一套实验。


## 新增两个真实三口：N12 / N14

N12 一次空中资源选择近高奖岸或远低通路，A→B/A→C两路线同世界布局。两路1枪1跳，高路实际12币、低路0；[高岸3.4秒](videos/BN12-B-v1/one-shot-two-routes.mp4)及[远低岸4.98秒](videos/BN12-C-v1/one-shot-two-routes.mp4)，139/234帧原strict全字段一致。170完整案例cal/held各档全过，第二空间仍needs_design。高奖后再落低口的真实替代穿B外邻19身体/20扫掠帧，最大80.667px，Map若提供空气可能可重汇；不认证B→C、不强称永久二选一。见[AI逐raw审查](../../../pcg/creative-production/batch30/curation-block31-addendum-v1.md)。

N14 先真实落共同M回枪，选择左/右，跳到相应铃外侧再回身射击，同枪反冲朝选定高岸并打开它的原短时门。[左侧5.15秒](videos/BN14-B-v1/pass-receiver-turn-fork.mp4)、[右侧5.17秒](videos/BN14-C-v1/pass-receiver-turn-fork.mp4)，244/245帧strict全字段一致。原regular校准全通过，held B moderate10/12、C11/12，其余全通过；不称全扰动100%。另四方向、通用恢复、第四口与接缝UNKNOWN。名为over-top的两有限策略实际仍击中正确铃，是合法瞄准替代，不误报已证无越顶绕行。

新增两份各在原库新进程完整请求命中，分别[复用v7](retrieval-v7/receipt.json)、[复用v8](retrieval-v8/receipt.json)，每份6种变更冲突皆拒绝，累计23技术版本复用，0生成/新物理。新[静态兼容v7](../../../pcg/creative-production/batch30/latest-map-compatibility-v7.json)覆盖23版本41策略case/40有序对，不替代源物理、任意进入或整图。

原件闭包[block-v10](../../../pcg/archives/content-workshop-plains30-block-v10/manifest.json)为N12含全部316次失败/成功；[block-v11](../../../pcg/archives/content-workshop-plains30-block-v11/manifest.json)为N14共208次。与原v1..v9均保留，旧结果不覆盖。当前29条Module片中17strict共5216物理帧、12review-only；所有都是程序输入回放，非真人试玩或趣味批准。


## 当前24份：N16与N14靶标清晰版

N16 [斜射开高门5.77秒](videos/BN16-near-v1/wall-projection-unlock.mp4)281帧strict一致。48probe+77full，cal各档全过，held moderate11/12其余全过。贴壁时原碰撞确实去掉水平反冲，离壁方案也1枪1跳且更快/同等小样可靠，因此保留为基础反冲的具体地貌接口，不算新族、不强制碰墙。实际8币；失手回A再试、同世界返回仅各1clean，不签一般恢复/反向。

N14默认观感消费者改用明确绑定的[靶标表现配置](presentation-n14-readable-v1.json)：[左侧清晰版](videos/BN14-B-readable-v1/pass-receiver-turn-fork.mp4)、[右侧清晰版](videos/BN14-C-readable-v1/pass-receiver-turn-fork.mp4)。左右真28×34靶标以不同色框出、细线连对应门、门顶写标识。新旧两片的完整native trace字节相同，原case/文档/物理源都不变；旧scene/影片保留。该配置逐case SHA、版本、场景依赖和原严格录像绑定，不由一个自填implemented标志准入。

当前32条Module影片中20strict共5986重录帧，489帧是上述同case表现重录；独立原canonical片18条5497帧，其余12review-only。表现重录不增加Module、家族或独立校准/留出数量；实际原生调用另计预算。

N13停车方案原51与修订29共80probe后封为needs_design，0full/held/Module。近距离停枪+45度离台能更好保门，但返回原A仍不可靠，不能只保留较容易A→B删去目的。失败闭包[block-v12](../../../pcg/archives/content-workshop-plains30-block-v12/manifest.json)/[v13](../../../pcg/archives/content-workshop-plains30-block-v13/manifest.json)保留，N16原件在[v14](../../../pcg/archives/content-workshop-plains30-block-v14/manifest.json)。新[静态兼容v8](../../../pcg/creative-production/batch30/latest-map-compatibility-v8.json)覆盖24版本42case/41有序对；真人反馈、趣味和生产批准继续UNKNOWN。
