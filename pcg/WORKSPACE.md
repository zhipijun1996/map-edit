# 当前工作区：既有 Module 迁移

先读根 [MAP_FOUNDATION.md](../MAP_FOUNDATION.md)（规范）、[MAP_GENERATION_GUIDE.md](../MAP_GENERATION_GUIDE.md)（推荐）及 [迁移skill](../.agents/skills/pcg-module-migration/SKILL.md)。当前已授权执行：**先本仓库既有内容，再主游戏已有内容**，以最小必要修改迁移；新增Module暂停、旧Map生成器退役，本轮不实现新Map、不commit、不发布。

正式技术内容目录为根 `modules/`，回收为 `modules-recycle/`，失败/近似重复待审/证据缺口保留原处。完全重复须确定性等价和alias引用后归并；技术认证不等于人工趣味/试玩/生产批准。目标验证、回读、引用与可恢复归档检查完成后才归档原件。

复用原Godot Harness/资源/质量门槛；转换、metadata pass和旧录像不自动取得新认证。新CLI预期 `python3 -m pcg.migration` 的 audit/inspect/validate/promote/archive/build，先核实际已实现子命令、参数和覆盖，不按本文假定已可用。迁移状态若仍有旧顺序/旧计数，报告待同步，以实际证据为准。

## 以下为历史正文（完整保留，非当前执行指令）

以下“当前/最新”、旧入口、批次产量与Block不规则拥有格等描述均属历史上下文；不据此恢复生产或覆盖新地基。

**R2真实整图里程碑**：见 [woven-region-v1](../docs/l4-mapgen/woven-region-v1.md)。固定Seed由既有R2驱动19个不同尺寸Macro、27直接接缝；25条冻结整图策略（12独立输入扰动）及全部50声明方向通过。19版本入隔离候选库，热库全复用后13条整图复验通过；配对实测两条回程节省4.90/11.35秒。四段正常速度原生录像13,822帧精确一致。仍只有一张物理拓扑，内容与空间语法有限，非最终区域规模/人类趣味/生产准入；正式游戏未改。原件与失败见 woven-region-v1 归档。

# 关卡生成工作区

## 当前续作：24份Block候选与纯表现清晰版（2026-10-27）

[当前24份](../generation/workshop/plains30-block-v1/manifest-progress-24-v1.json)，原库132/平原114/生产0，最新原Map静态24版本42cases/41有序对。N16原规则两轮48probe+77full通过，held moderate11/12其余全过；离壁同成本更快同可靠，实际purpose不要求wall_contact，归旧反冲适配、0新族，恢复/返回仅各1clean附证。当前新N17十字分叉与N19折角气闸在实验，不计候选。

N14新readable表现只描出真实28×34铃靶、左右颜色/门标识及连线；两canonical重录244/245帧的native trace字节与原片相同。原case/doc/机关/碰撞/输入不改，manifest显式可选新scene，原scene/影片全保留。32条Module影片含20strict（5986重录帧，其中489为同case表现重录，独立原canonical片18条5497帧）及12review-only；不会将新表现计新Module/独立校准。N13旧51+repair29封0，名义修订screen有所改善但同世界回程不稳，未删目的或移门槛救过。闭包block-v12/v13保留失败；N16在v14。

## 当前续作：23份Block候选与原有玩法适配（2026-10-27）

[当前清单](../generation/workshop/plains30-block-v1/manifest-progress-23-v1.json)：原库131/平原优选113，生产0。N12原A5三口A→高B取12币或远低C，170完整案例两路cal/held各档全过，两原生139/234帧严格一致；第二需求实际负身体裕度拒绝。N14共同M落地回枪、越所选铃后反身命铃开高岸门，154完整案例通过原regular，held B moderate10/12、C11/12，其余全过；244/245帧原生严格一致。它们是有效接口/构图适配，不自动新增家族。

最新原Map静态兼容23版本41canonicalcases/40不同有序Port对，原862b的24实码绑定不变；新增两份各在新进程从原库精确复用、各6类完整冲突拒绝，累计23。Module影片29（17strict共5216物理帧、12review-only），独立接缝/连续片不混计。N12 full1源交接中止38+full2外部空气scope拒绝70+probe38+最终170共316；N14 probe54+full154共208。所有失败/冻结源由block-v10/v11保留，原游戏870与原98候选字节保持。

N12两条取高奖后到C的真实1枪1跳解因B外邻19身体帧/20扫掠帧而不能认证内部通路，guarded分类只标外部依赖UNKNOWN、不加owned/放宽名义身体；原56反例重判仅2条变scope。N14其他4方向、四口、恢复/接缝UNKNOWN。N13停车screen中等2/6不通过，0候选/held；N16贴壁必要性被真实离壁等成本更快策略推翻，暂作旧定向反冲适配研究，不计新族。人工趣味/试玩/生产分别UNKNOWN。

## 当前续作：21份Block技术候选（2026-10-27）

原持久库新增N08回廊1份、N11下落刹车W/W与E/E两接口，合21份Block候选，129原库/111平原优选（发布清单与新进程检索回执随后绑定）。N08双向157完整案例、另同世界取16币往返50案例均过原regular；同任务配对对照下回比原上回约0.3秒慢，明确是另一返程选择，不是捷径或新家族。N11两空间154完整案例，E/E moderate11/12，其余全过。N10恢复mod5/12失败，0候选/0held；原失败不可删恢复要求救过。全部人工观感/试玩/生产准入UNKNOWN。

最新Map头仍为862b实码；候选37个canonical directed cases含同一A→B的不同策略，不等于37个独立有序端口对。新Card v3给N11–15五个具体接口提案；N12/N13在隔离路径实施，N15明确缺Cell，不悄换普通门。执行protocol-v5/v6仍每案2规则/80probe/full1600/全谱系24000，max2可变配方作者；前一源冻结后可并行下个设计，原库full入库由root串行。budget-audit-v1保存13归档实际逐输入预算截止，不将旧统计冒充实时最终余额。

## 最新：18份Block候选与862b实码（2026-10-27）

当前[18份](../generation/workshop/plains30-block-v1/manifest-progress-18-v1.json)，126原库/108平原优选/生产0；含N06真正三/四口共同M选择，A1/A3两空间双向、A2一空间双向。最新Map862b源码24文件在map-constraint-source-v3，Block128/JS/面中心规则不变；原validator新增boundary_gates覆盖，Map已有真实22 Macro接口样图。新Module自有条件门/同Module同高支撑并集适配皆新版本需整图证据。18份33方向仅静态兼容原证据，旧源身份不改。

原produce_v3新增原consumer字段预检/可选薄export；原record_block_v1读取持久化scene，严格比较不改。21条Module视频以当前manifest逐SHA绑定；A2两个完整1000帧保留，另明确6秒节选省验收尾段。N06 80探针谱系含失败后新几何修订，独立四口70probe+336full均留原件。N03新Cell8真实对照，但安全地面反向355连续支撑否决玩法，54总支出/0Module；不凑数。原件v6/v7/v8；独立AI增补curation-block27-v1覆盖25active/11审阅组，不是新家族数。

## 最新续作：13份Block候选与6c实际Map规则（2026-10-27）

最新Map已核`6c864ae6423b6409990564371aca34a322b66253`实际19文件（`creative-production/batch30/map-constraint-source-v2/`），不只README。Block128策略/JS合同未变；真实图联合求解必须精确port数、满足请求全部有向对，UNKNOWN反向不可顶替。奖励预算重绑产生新语义版本，须B真实重验。`produce_v3`默认预注册protocol-v2，并在物理前执行原Godot语法/原Block/counter绑定预检；不建第二物理或Map生成器。

当前[13份Block候选](../generation/workshop/plains30-block-v1/manifest-progress-13-v2.json)：此前9份＋N04四口/非对称三口各1＋A1两空间双向2。原库121，平原优选103，生产0；13份新进程原持久库复用，0生成/物理调用。13条Module影片，1722帧原严格比较通过，其他support_id差异完整保留review-only。版本/适配不等于新家族，人类趣味/试玩/生产仍UNKNOWN。

双N04真实零补路接缝90案例含原失败，cal25/25、held23/25原regular通过；836帧影片4support_id差异不改strict。A1另两次同世界往返只各clean，不推断通用状态/拼装。N02双台80probe+52/124full后高路moderate1/12，0候选/无held，不凑数。C10独立AI复核为条件纠错恢复扩展，初纠错前曾真实回枪，不能宣称一路保留唯一空中资源。新原件归档`content-workshop-plains30-block-v5`，旧源码/失败不覆盖。

## 最新Map接口：Block128内容生产（2026-10-27）

先读[Block交接](../docs/l4-mapgen/plains30-block-handoff-v1.md)与`creative-production/batch30/map-constraint-source-v1/source-index.json`：已核对Map分支a685fae实际policy/校验器/适配器/请求，而非只读README。新入口`batch30_runtime.produce_v3`强制原Block预检、原Engine/regular/候选库；128倍数尺寸、真实边界中心Port和内部staging分开。旧8份局部候选不自动升级。

当前[9份Block候选](../generation/workshop/plains30-block-v1/manifest-progress-9-v1.json)：气闸2、换脚桥2、真正三口移动站1、风铃台追接2、新墙刹车1、侧洞纠错1；原库117/平原优选99。成功生产运行1038真实案例含失败，六配方均过原校准及独立留出。C05两路线+D05/C07/C10主路共1452帧严格比较通过；C01/C02各3帧、C10恢复1帧support_id差异为review-only，严格失败未改。C02真实消费B exp1_0无奖励请求，其余为明确派生需求。Block适配不算新家族，人工/生产批准UNKNOWN。

C06两规则79probe+152full均保留，高路moderate7/12未过.65，整接口0新候选/held未跑。低路额外一枪跨入口外空气的分类记录UNKNOWN，不放宽名义完整身体。D04端口外邻高柱与双唇回程冲突返回needs_design；D05新恢复虽到奖但身体越外邻，未签恢复。气闸边界v2仍11/13，未签接缝。不要以保留恢复岸或clean成功继承旧保证。

原件恢复`content-workshop-plains30-block-v1/v2/v3`、旧未准入研究`content-workshop-plains30-prototypes-v1`；按精确results前缀取用，不覆盖新源。网页Block校验与Pages文件复制已由PR #6发布，公网字节已核对；候选索引继续从content/task-a-workshop读取。

## 当前执行：修订核心优先，新增30平原Module（2026-10-26）

当前8/30新增候选：D05追接、C01换脚桥、D04修订停台、C02空中气闸各两份需求，见`generation/workshop/plains30-v1/manifest-progress-8-v2.json`与README。总库98→108含旧D04另2份有效技术记录但因更省取奖绕法设计暂扣，不计8；原J06/J03四版暂扣不变。D03两次full各1498案例未达原regular，不计候选；当前r3真实perch缩短第二射距，协议v8先注册。C03/C04在开发，不能当库存。人工观感/试玩/生产准入UNKNOWN。

双门Cell最终`batch30_cell/runner_v3.gd`+`main_v3.tscn`：117Harness+3native=120，恰一开一关、玩家/敌人完整身体防夹，原弹丸/资源/生命周期。原话、12设计卡、预算与失败在`creative-production/batch30/`。D04r2四完整回程另320case通过；D05两类所选恢复过cal/held，992是含失败谱系成本。两套真实C01→D05连续试件保留原实体精确并集，163实际运行，不新增Module/不签通用装配。C01视频2帧support_id及接缝片同类差异strict失败，明确review-only；其他已发布核心片严格核对通过。

统一`batch30_runtime/produce_v2.py`复用原`plains50_ports.produce_v2`/evaluate/produce/store；gateB和移动铃由隔离输出adapter映射，canonical exporter支持2口显式有向路线。无新物理/候选库/Map生成器。核心原件含失败在`content-workshop-plains30-core-v1/v2`、C02在`content-workshop-plains30-c02-v1`；按需`restore_archive.py NAME --extract --prefix results/精确run/`，不要覆盖新工作源。空间整理见storage-eviction-v1与snapshot-storage-dedup-v1：字节核验归档副本/冻结快照重复存储已释放，完整压缩raw和归档保留。

## 当前优先：先修清D03/D04取舍与漏洞，保留用户D05改案（2026-10-26）

最新用户要求原话见`feedback/workshop/idea-sources/human-d03-d04-clarify-and-repair/v1.json`；[D03/D04修订](../docs/l4-mapgen/d03-d04-design-repair-v2.md)将玩家取舍与软锁/免费改位等方案漏洞分开。当前是设计逻辑修订，几何/真实物理仍NOT_RUN，不得当作已完成Module。D05最新用户改案为`human-d05-bell-carrier-catch`：跳起左下击铃，人物右上反冲、平台右移接人，再起跳到岸；先原型验证核心关系，不能替换成普通等台。此前J06/J03仍因无聊暂扣。

## 当前反馈：J06/J03无聊，停止作为优选创意（2026-10-26）

用户原话见`feedback/workshop/junction-boring-observation-v1.json`，明确否决这两种实现。四版本保留技术证据，优选平原86→82、总库98不变；重新生成视图须应用profile.design_holds，不能由旧发布清单重新选中。见[复盘](../docs/l4-mapgen/junction-design-regression-v1.md)。原五案D02—D05的具体动作/后果耦合应成为选案依据；先建立可玩核心与地貌构图，再适配端口/尺寸。此轮无新Module或物理实验，不擅自将问题替换为增加射击/危险数量。

## 历史：真实多口路口实现（2026-10-26）

已完成J06双岸会合风口与J03交织双桥各两种空间接口，4新候选入原库（94→98；平原82→86）。24路线原regular校准/独立留出各600/600；2精确等面积接缝试件102/102，通用seam仍UNKNOWN。6段正常速度原生视频2267帧严格一致；20有条件path/16UNKNOWN，不宣称单向已证。J03旧observer误标合法落地buffer造成的5次错误反例拒绝保持原件，以隔离分类解释后重验接口0；原物理/Harness/门槛不改。见[交付](../generation/workshop/junctions-v1/README.md)、[报告](../docs/l4-mapgen/junction-modules-v1.md)、`creative-production/junction-implementation-cycle-v1.json`。`prototype/creative_batches/junctions/`复用原多口调度/WorkshopEngine/原库；query_v1提供精确需求检索及具体冲突。环岛/任意进入状态/通用拼装/B整图未完成，人工趣味和生产准入仍待评。恢复归档content-workshop-junctions-v1后可复跑全部新原件。

## 前轮：多口的空间选择与创意先行（2026-10-26）

用户认可上一批实现总体，同时指出多口像强加安全口；现在优先构思能服务后续地图分叉的局部空间节点，允许部分单向。环岛只是例子，不默认开始实现或批量生成。执行 [pcg-multiport-junction](../.agents/skills/pcg-multiport-junction/SKILL.md)。逐字来源/解释见`feedback/workshop/multiport-spatial-choice-feedback-v1.json`；15份现有多口的设计审查在`creative-production/curation/multiport-junction-audit-v1.json`，原技术记录不改。先读不同空间创意`creative-production/junction-ideas-v1.json`，原平台只支持两点往返，真正圆轨迹需新Cell。旧“从A有2/3出口”是当批数量/技术条件，不是新路口设计准则；UNKNOWN反向不算已证单向。此次仅审查、skill和概念输出，物理/新候选/生产准入均不增加。

## 最新交付：新增50平原Module，含7三口/4四口（2026-10-26）

见 [报告](../docs/l4-mapgen/plains50-v1.md)、[50件清单/21组审阅/运行命令](../generation/workshop/plains50-v1/README.md)。原库44→94，平原候选32→82；新增39双口/7三口/4四口，69路线逐路过原regular，所有3/4口分别有2/3真实出口。21审阅组+29有效适配不等于50新家族。8623 Harness案例含失败/接缝；留出1969/2022，未编造人类成功率。新进程原库复用、55多口矛盾需求拒绝与两零增面积接缝试件均有回执。新的平原视图`plains_workshop/catalog_v2.py`、统一手玩/回放`creative_batches/plains50_catalog.py`。归档`content-workshop-plains50-v1`保存全部新raw；旧记录不覆盖。先读最终AI审查与本批失败，D02/D03/D04/D05完整设计仍有缺口。网页当前索引包含所有94版本并能按端口筛选；main已通过PR #5发布（54d0cfc），真实公网更新94/平原82/四口4和31主审影片字节核对通过，回执`generation/workshop/plains50-v1/publication-v1.json`。人工/生产批准仍待真实反馈。共享物理/质量门槛/候选库框架未改。

## 当前续作：批次生产、AI去重、人工集中审核（2026-10-26）

执行 [批次方法](../docs/l4-mapgen/plains-batch-production-v1.md) 与 `.agents/skills/pcg-creative-producer/references/batch-production-v1.md`，续作账本 `creative-production/plains-campaign-v2.json`。每轮模型5张创意卡，缺规则/Cell就隔离实现，原Godot门槛通过后入原候选库；默认累计20个新增技术候选版本后AI按实际决策/因果分组，再给人工代表短视频。原库复用不算新增，适配不算新家族；重复仅折叠，不删除或当技术撤回。会话外不持续运行。最新反馈：D01被否决为已有基础反冲关系，停止作为新创意；D02-D05只有设计正向意见，未获试玩/生产批准。现有32平原版本做第一轮AI批次，D02进入有界实现；具体完成/失败必须读新cycle回执，计划数量不算完成。

首轮实际回执：`creative-production/plains-campaign-v2-cycle-001.json`。32版本AI分18审阅组、6适配、8折叠；18段不同代表影片有两段review-only，G06低路影片未找到。D02首版17真实案例发现岸上预停→静态跳台绕法，完整校准/留出NOT_RUN，新增入库0；先读`feedback/workshop/descending-carrier-prepark-v1.json`再修订。原库44版本保留。新失败原件用`content-workshop-plains-batch-v1`归档恢复。

## 当前优先：反冲平原与可持续配方（2026-10-26）

用户已整体正向评价新20项。见 [库现状与方法](../docs/l4-mapgen/plains-recoil-method-v1.md)、[平原视图](../generation/workshop/plains-recoil-v1/catalog.json)。共享库已归拢为44版本，平原优选32候选版本；新20里11项三能力兼容、9项高级能力留后，兼容项不全是反冲课。当前仅move/jump/shot_recoil；教学、练习、组合、奖励、同世界回程恢复分别验收。新方法首试两条旧规则×两新空间，4/4通过原门槛，新进程4/4复用0物理调用；不是方法稳定性或盲空间泛化通过。优先补安全首课和配方跨需求适应，接B现有平原流程，不继续按数量扩高级玩法。归档content-workshop-plains-method-v1提供新原件与旧15依赖闭包；旧20只需恢复results前缀，不覆盖当前源码。

## 大模型创意工坊：20种新动作关系（2026-10-25）

最新 [20种新玩法报告](../docs/l4-mapgen/content-workshop-creative20-v1.md) 与 [视频/标准Module目录](../generation/workshop/creative20-v1/README.md)。使用用户授权的当前Codex会话与子代理实际提出、实现和反驳创意，原生产循环执行参数搜索/真实Godot验证；[创意生产者skill](../.agents/skills/pcg-creative-producer/SKILL.md) 固定了可续作的方法。20种均为新关系，不计旧六家族、尺寸适配、普通电梯或Macro拆分；598/610独立留出安全稳定，沿用原regular门槛。新20原库入库及新进程检索，未编造在线API成功或无人值守服务。恢复 `content-workshop-creative20-v1` 后运行 `python3 -m pcg.prototype.creative_batches.catalog_v4 --list` / `--play 1`。人工趣味/试玩/生产准入待评，其他接口与B整图UNKNOWN。长等待双台转乘因模型视频节奏复审暂扣；撤桥下坠录像32处support_id差异严格失败，review-only，未放宽比较。

## 内容工坊续作：连续 Macro（2026-10-25）

最新 [双宝箱回程 Macro](../docs/l4-mapgen/content-workshop-macro-v1.md) 在原六家族之上交付两个三端口空间接口；4 份组成 Module 仅为版本依赖，不增加家族。450 条新留出中 444 条目的通过，原 regular 门槛不变；完整循环48/50，漏接恢复另26/26。原候选库磁盘重检索2/2，新增连接地形0。三段原生审阅录像有18帧支撑碰撞ID顺序差异，严格比较失败保持原件，不计全字段精确录像。v2已获用户整体正向视频反馈；新Macro观感、实际试玩、生产准入与B整图仍未完成。恢复 `content-workshop-macro-v1` 获取全部新源码/失败/轨迹。

## 任务 A 内容工坊入口（2026-10-25）

`prototype/workshop/` 在既有 PlainsEngine / CandidateLibrary 上增加六个因果玩法家族；每家族两种接口，另有既有 Map 100 高差需求的实际适配。**当前为 [content-workshop-v2](../docs/l4-mapgen/content-workshop-v2.md)**：旧 A2 静止登台绕法已撤回，库检索拒绝失效版本；新几何经过扩展反例与新留出。v1 原件保留。全部仍为未获人工观感/试玩/生产认可的候选。先交付 A1 的记录见 [任务 B 首次交接](../docs/l4-mapgen/task-a-first-handoff.md)。不包含 Map Director 或整图验收。

**内容驱动整图第一轮，尚未超过正式图趣味目标**：见 [content-routes-v1](../docs/l4-mapgen/content-routes-v1.md)。用户已否决上一轮“到处走”的观感，原话与版本绑定见 `feedback/woven-region-boring-v1.json`。保留19 Macro多环路骨架，15份父内容复用、4份需求适配；真实限时击铃反冲、敌人命中回充、尖刺净空与敌人死亡后的连续回程。21整图策略（8独立输入扰动）/50声明方向通过；19份热库复用后5整图复验。主线走路策略43.12%→39.03%，其他路线改善有限，不能据测试通过宣布整图更好玩。正式当前v12已重新5 Seed生成和1 live路线；生态、内容配方、地标、容错与流程仍领先。录像与三方对照在 `generation/maps/content-routes-review-v1`，全部失败/源/标准Module/候选记录恢复 `content-routes-v1`归档。人工认可0、生产准入关闭；下一步是内容配方/教学恢复/地貌共同驱动，不先扩大空地图。

**新增内容生态闭环**：见 [content-ecosystem-v1](../docs/l4-mapgen/content-ecosystem-v1.md)。`python3 -m pcg.map_directed.ecosystem.run --name fresh-ecosystem --batch` 复用既有 Director、CandidateLibrary、标准合同与真实 Harness，逐 Module 搜索/补缺/重新验整图/候选索引。固定批次生成调用 8/0/1，105 条连续整图策略通过（84 新相位），9 个候选版本；仍同一张八 Macro 双回环物理拓扑，不冒称多 Seed 探索多样性。16 个关系家族中7个仍为未实现提案；没有任意创意自主落地、生产准入或人工趣味批准。旧39 Macro压力样品仍不通过设计验收。恢复新 `content-ecosystem-v1` 获取全部失败/源/原始轨迹。

**真实整图阶段已接入，设计验收仍未通过**：见[阶段报告](../docs/l4-mapgen/full-region-spatial-stage-v1.md)。39 Macro / 55 接缝，核心90方向的12条连续巡回、两条进场和回程及12个独立相位样本已验证；6处奖励职责和16个奖励/捷径方向仍未完成，候选库拒绝入库。不能把这张薄楼板压力样品当新正式关卡。`region_scale.feedback`提供真实失败到现有端口列求解的有界反馈；`region_scale.materialize/verify`复用已有生成、标准输出和Harness。下一步是地貌/挑战先行的Macro与奖励补缺，目标并未降级。

**当前目标已升级为超过正式单图规模的完整平原**，见[目标与状态](../docs/l4-mapgen/full-region-goal-v1.md)和`map_directed/region_scale/protocol.json`。32核心探索地点、96–128 Module内容预算；不以重复/拆碎或扩大空白达标。原3个39–41地点蓝图中，Seed0已作39 Macro物理物化；另2个仍仅逻辑输出。当前设计验收未通过，不作为正式关卡交付。既有8 Module只作回归样品。人物/移动平台主要入口已改走正式安装器，`valley_complete.run --formal-style`可复现新样式验证；全游戏表现/战役迁移仍未完成。

最新完整风谷小区域：`python -m pcg.map_directed.valley_complete.run --name fresh-valley --mode full`。8个Module直接拼装，3宝箱/商人，新增空中停靠和敌人回充接力；正式native32px Tile。5整图路线、20新相位、216局部闭门策略和两个宝箱几何隔离，见[本轮报告](../docs/l4-mapgen/valley-complete-v1.md)。主游戏正式v12已另跑5 Seed及live Harness，不以旧v10代表最新状态。恢复`valley-complete-v1`归档取得完整新证据。仍是固定小区域，无Boss/战役和多Seed品质准入。

从独立研究工作区 f5daecb 迁入，布局保留以便复现；`prototype` 是可执行程序。`REPORT.md`、`COMPOSABLE-REPORT.md`、`DYNAMIC-REPORT.md`、`FACTORY-REPORT.md` 为历史阶段报告；其旧路径/提交是当时的证据，不重新盖章。

主入口：`prototype/factory/core/producer.py`。真实动作语法→运动构造→双档案变异→独立扰动/反例→人类观感评审。当前不是运行中无限生成器、完整地图或已证明的趣味库。真人试玩/正式批准仍为0；上一轮R已有1条整体正向视频反馈，原话见feedback/plains-round2-positive-v1.json。

最新开放风谷样品：`python -m pcg.map_directed.open_valley.run --name fresh-open --mode full`。7个无默认外墙的地形Module，主线三次空中击铃反冲，奖励铃联动回程平台，见[样品报告](../docs/l4-mapgen/open-valley-recoil-v1.md)。标准文档、真实接缝和整图验证继续复用原工具；先恢复`open-valley-sample-v1`取得证据和输入。当前为确定性样品与有限策略验证，未签多Seed品质/人类趣味/生产准入。

最新直接拼接Map入口：`python3 -m pcg.map_directed.direct_join.run --name fresh-direct-map --mode full`。27个不同大小Module/39处零间隙接缝，Map新增地形0；实际整图见[直接拼接报告](../docs/l4-mapgen/direct-module-contact-v1.md)。旧r2_full导航填充版被用户否决，保留原件，不再作为当前交付。候选的通用关系和生产准入仍关闭，整图有限物理见证与人类趣味认可分开。恢复`direct-module-source-and-failures-v1`及`direct-module-run-payloads-v1`取得全部新失败、冻结源及大输入；结果和媒体清单按报告链接读取。

本轮旧批次、全部冻结源和三段原生trace在 `r2-full-source-and-failures-v1`，用 `python3 pcg/tools/restore_archive.py r2-full-source-and-failures-v1 --extract` 恢复；仅校验不加extract。大量原始cases/compiled/input JSON另用 `python3 pcg/tools/restore_archive.py r2-full-run-payloads-v1 --extract` 恢复，逐文件索引见results/r2-run-payloads-index-v1.json。简要结果、库入库/复用日志、压缩物理输出及新媒体直接保留。原生AVI可重建，不入库。

历史小motif入口：`python3 -m pcg.map_directed.run`，见[旧闭环报告](../docs/l4-mapgen/map-driven-library-v1.md)。用户已反馈范围过小、安全连接过长；旧原件保留。

本轮媒体/实际试玩来源与恢复：[PUBLICATION](../generation/maps/map-directed-loop-v1/PUBLICATION.json)。`map-directed-source-and-failures-v1` 归档含各阶段冻结源和首失败；直接结果以 `results/map-directed-final-v1` 为完整新库闭环、`results/map-directed-loop-v2` 为跨进程库复用及媒体源。当前正式游戏未修改；下一步是人工评审、缩短安全连接并扩展多motif，不能把技术通过写成区域设计完成。

## 恢复与运行

在仓库根执行：

```sh
python3 pcg/tools/restore_archive.py godot-runtime-v1 --extract
# 复跑历史失败轨迹实验时恢复这部分；完整旧数据仍在同一归档。
python3 pcg/tools/restore_archive.py research-results-v1 --extract --prefix results/factory-production-v1/
```

使用官方 Godot4.7.2 Standard，放到 `pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64`；官方ZIP SHA `cadd3204e728a35d3f13adb7fd0d7902636b79f6b95c40c265eb73b6c35329e4`，实际二进制SHA `8d106cbe6144c2dc7e881d61d2429c1a8a76e6b22ef48bd5e48dcf934953f71e`。引擎来自官方Godot release4.7.2，不重传二进制或缓存。

```sh
cd pcg
python3 -m pip install -r requirements.txt
toolchain/Godot_v4.7.2-stable_linux.x86_64 --headless --editor --path prototype/godot --quit
python3 -m prototype.factory.core.producer --name new-run --tier regular
python3 -m prototype.factory.compare_landing_repairs --name guided-new-run
python3 -m unittest discover -s prototype/factory/tests -v
```

Godot素材与真实脚本由 `godot-runtime-v1` 完整保存870原件；恢复时逐SHA检查，不覆盖已更改文件。原许可证和资产来源见 `prototype/godot/asset_licenses_provenance.json` / `source_provenance.json`，归档不改变许可。

`research-results-v1` 包含4318份旧原始结果，含失败、输入输出、源快照；`review-delivery-v1` 含364份审阅录像/证据。归档分片均在本仓库，不依赖预览仓库作为唯一存储；清单列出完整ZIP及每片SHA。解压目标为本目录。旧Web导出的基础PCK/官方JS-WASM仍保留原不可变链接，不重复搬运；可重建的`.godot`缓存、原生AVI中间件与官方引擎不列为归档资产。原工作区继续保留原件。

## 接下来的范围

先比较失败轨迹指导的接收面修复与固定随机参数变异；只有多个种子/家族证据支持时才提升为默认。接入Map Notes先做显式候选导出和证据绑定，不把库里的未知能力/未评分模块默认当可通关或低难度。

当前生成物理基线12f6cb0；编辑器177参考模块来自74d8a06，不能无条件复用技术回执。迁移不改这两份历史身份。生成器未直接接正式大地图和编辑器工程回写。

## 平原的新工作入口

当前优先平原：只移动、普通单跳、反冲，以实际判断/动作链为多样性目标。`prototype/plains/{pilot,calibrate,produce}.py`执行有界离线生成；`PLAINS-REPORT.md`记录3代表/6技术候选及全部失败、原件绑定和新留出。先恢复`plains-generation-v1`再复跑；新平原worker恢复正式角色枪口，不能将旧worker的射击数据混作同一绑定。`results/plains-review-v1/playlist.json`明确每段对应哪一批验证。当前人类观感/试玩/批准为0，下一轮扩大真实机关/敌人关系与替代策略，避免仅换尺寸批量计数。

## 后续交付格式

必须执行[OUTPUT-CONTRACT.md](OUTPUT-CONTRACT.md)。plains和factory主生产器自动输出`modules/*.mapnote.json`及同版本SVG；raw review_cases仅供研究/回放，不作为地图接口。格式为现有Map Notes+generationContract；能力、难度、source.integration继续沿用旧格式。空间、端口有向对、状态、Macro组成与未知项显式表达；`assemblyInterface`默认拒绝未验证关系。

## 平原连续挑战第二轮

最新见[PLAINS-REVIEW-ROUND2.md](PLAINS-REVIEW-ROUND2.md)：6技术候选/3代表，416次正式物理验证，额外30批360案例基础设施回归0错误。3段完整原生录像及841帧精确比对随generation/videos/plains-round2公开；人工观感/试玩/批准仍0。恢复plains-review-round2-v1可取得所有新失败、校准、原始轨迹、冻结源与录像。当前等待R01/R02/R03观感审核；齿轮等待必要性未证明，不再据此增加玩法计数；自动拼装仍关闭。

## 三端口最新入口

[PLAINS-THREE-PORT-REPORT.md](PLAINS-THREE-PORT-REPORT.md)：`prototype/plains/three_port.py`生成同几何A/B/C分支；`three_port_produce.py`完成校准/独立留出。2候选，每个6有向对/7路线，正式552次物理；742帧原生视频精确匹配。新T视频待评，奖励服务/通用回程保证/接缝/拼装仍未完成。恢复plains-three-port-v1可取得完整失败与源；不是14个Module，不将参数变体算新玩法。

## 审批修复 revision063–064

本轮12项原生可玩、23条固定方向，11项FULL v2通过；四载台三锯升降井仍未通过扰动，未授予独立资格。main规格同步提交`c04fca59`，完整交付见[README](../feedback/manual-review/implementation-results/revision-063-v1/README.md)。原始成功、失败和快照归档`approved-revision063-064-implementation-v1`含115817文件、19份分片；可用`python3 pcg/tools/restore_archive.py approved-revision063-064-implementation-v1 --verify-parts-only`核验，用`--extract`恢复。原游戏870保护文件未变。
