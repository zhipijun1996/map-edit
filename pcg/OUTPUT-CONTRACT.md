# 当前输出规范入口：Foundation 迁移

以根 [MAP_FOUNDATION.md](../MAP_FOUNDATION.md)为强制模型，[MAP_GENERATION_GUIDE.md](../MAP_GENERATION_GUIDE.md)为推荐，执行 [Module迁移skill](../.agents/skills/pcg-module-migration/SKILL.md)。当前先迁移本仓库既有Module，再主游戏；新增生产暂停、旧Map生成器退役，不实现新Map。

目标交付须明确：基础模板/版本及来源SHA、完整正整数W×H Block矩形（默认128像素可配置）、矩形外边BoundaryBlock外侧边中心Port、AIR/ROCK/ONE_WAY_PLATFORM与初始INPUT/OUTPUT/INOUT、N×N含自环/每格多Route、必要能力/动作/位移/难度/时长/资源/初态/动作接口/实证、允许镜像、部分连接的认证封口及实际有效Route集合。ROCK仅左右；AIR底边无INPUT/INOUT进入；顶部AIR OUTPUT无合法同类底边INPUT，不能作必接上出口。镜像同base，权限不交换、矩阵不转置；封口真阻断而非少量伤害，不破坏保留Route。规划不能删真实额外Route。

这些是语义要求，不声明旧 `generationContract`、schema、Python/JS或迁移工具已经支持。旧Map Notes文件保留来源兼容；新字段/适配要以实际共享实现与真实证据为准，不新造平行几何、库或物理。未来在线仅静态能力/初始权限，不传播HP/速度/资源/机关步骤。

根 `modules/`是技术合格可复用迁移内容；`modules-recycle/`保存事实已确认的重复非代表/明确排除项；近似待审、缺口、失败原处保留。先验证目标、回读/引用/可恢复归档，再归档原件；技术、AI、人评、试玩和生产认可分开。不commit、不发布。

## 以下为历史输出合同（原文保留，不覆盖当前模型）

下文不规则占用、N×(N−1)、自环不允许、在线状态传递、旧生产入口等均属旧系统资料；不能继续作为新迁移准入规则。其历史物理身份保留，不改标签为Foundation通过。

# Module / Macro 输出契约 v1

## 当前 Map 接口增量（2026-10-27）

新内容还需遵守[Graph + Block + Module契约](../docs/l4-mapgen/graph-block-module-contract-v1.md)和`map_directed/block_grid/plains-policy.json`。当前已校准Block为128，Module预留轮廓以连通Block表示，包围尺寸为Block倍数，内部碰撞/机关不按Block缩放。所有Port位于所拥有cell的真实边界中心；`ground64/v1`锚点、向内staging位置和身体中心+14px分别记录。旧局部通过不自动获得Block资格。

执行入口为`prototype/creative_batches/batch30_runtime/produce_v3.py`，复用原物理/质量/候选库；先调用上游原Python/JS校验，再进行Godot实验。完整实体、双门第二门、移动铃接收器的全行程和实际身体扫掠必须入所有权；未知敌人全行为范围仍返回缺口。改岸体/开口/机关或动作后重新绑定版本和证据。Map不补平台或重置资源。

适用于后续公开交付的生成内容；搜索算法、动作策略、物理参数和质量筛选不变。主生产入口`prototype/plains/produce.py`与`prototype/factory/core/producer.py`在结束时自动调用`contract.export`，输出`modules/`。输出失败会报错，不降级为可拼装模块。适配器遇到未映射的多端口、支路、奖励区或新机关会明确拒绝，要求补齐映射或直接提供完整Map Notes契约，不能静默丢弃。历史raw case、Godot输入和档案是研究证据，不是地图拼装接口；不回写或重标历史结论。

[阅读模块图与下载JSON](https://zhipijun1996.github.io/map-edit/generation/contracts/plains-v1/) · [交付清单](../generation/contracts/plains-v1/manifest.json)

## 复用的数据格式

**Module和Macro均沿用`gunman-rush-level-sketch/v1`，仅增加`generationContract`字段。** 没有另造第二种Module格式。

- `id/title/objects/canvas/source/intent`继续沿用Map Notes。平台、危险、轨道、怪物、机关、路线等真实几何只存在于`objects`；新字段通过ID引用，不另存一套平台数组。
- `capabilityRequirements`沿用`capabilities.js`的`version/status/allOf/anyOfGroups/note`。`unspecified/partial`都不等于条件满足；测试中提供某能力，不自动证明它是最低必要能力。
- `difficulty`沿用`difficulty.js`的`gunman-rush/module-difficulty/v1`，1～10或`score:null`。本批全部未评分，自动化扰动通过率不换算人类难度。
- 正式接入沿用`source.integration`，区分true、false、null。新研究候选明确false；有录像不等于已接正式流程。
- `manifest.json`仅是文件、版本、SHA和接口拒绝原因的索引，不是另一份Module几何格式，也不自动加入现有177个参考模块库。

`generationContract.version=1`。未知新增字段统一写字符串`"UNKNOWN"`；能力/难度/接入状态仍沿用其既有“不完整/空值”约定。未知不是false、无条件、零消耗、资源恢复或验证成功。

## 身份、版本和来源

`id`为稳定内容身份（当前源candidate UID），不会因审阅编号改变。`contentVersion`为SHA-256语义版本，覆盖ID、几何、能力/难度、坐标系、端口、有向关系、状态合同、组成与生成来源。排序对象键不改变版本；任意相应内容改变，旧证据不可继续授权。

显示标题、说明、更新时间、独立证据记录、静态回执及SVG文件路径不参与语义哈希，避免自引用。交付清单另有完整JSON和SVG的字节SHA。证据自身还要绑定内容版本及原输入/输出哈希，不能仅信任嵌入的`pass`。

- `seed`显式`{status,value,reason}`。真实使用随机种子时声明`known`；当前平原动作探针是确定性参数枚举，写`not_used/null`；缺失来源写`UNKNOWN`。**不把holdout种子冒充生成种子。**
- `generation.parameters`记录家族、动作参数、构造依据及可用的生产参数。factory另输出完整`generation_parameters.json`。
- `generation.source`绑定源case、源Module SHA、运行目录、物理游戏提交和源清单SHA。`source.commit`是原生产逻辑的工作树基线；实际导出器文件版本另由`export-source.json`文件SHA明确记录，不用基线提交冒充未提交实现的精确身份。
- `designStatus`是设计声明；`staticChecks`是结构/几何检查；`validations[kind=physics]`是真实物理的指定覆盖；`source.integration`是正式接入。四者互不替代。

## 空间

`canvas.units`与`space.units`均为`godot_world_unit`，位置精度`exact`，局部原点明确为`[0,0]`，x向右、y向下。保留原局部负坐标，不为显示平移物理坐标。

`space.bounds`是已知对象、动态已知范围及已观测身体扫掠的外接框，`boundsCoverage`明确完整性。**有未知攻击/动作范围时，这个框不是完整安全占用证明。** 模块可大小不同、长宽比不同，多个分离实体/空腔/圆形机关组成不规则空间，不要求填满矩形外框。

- `occupancy.objectIds/regions`：实体与保留空间。通过对象ID保留真实尺寸、形状、旋转和宿主引用。
- `actorBody`：原角色RectangleShape2D的24×36世界单位及源文件SHA；不是美术图片尺寸。
- `actionClearance`：独立的动作空间。当前仅存真实输入见证的身体扫掠，`partial/recorded_policy_body_sweep`。不是平台碰撞AABB，也不是所有动作/进入状态的净空证明。
- `dynamicEnvelopes`：齿轮使用原`origin ± abs(travel) ± radius`全活动范围；移动平台使用完整行程加真实尺寸；怪物完整AI/攻击/弹道范围尚未界定时为UNKNOWN，不把初始碰撞盒当全部活动范围。
- `seams`：明确关联Port ID、局部接缝区域及允许重叠类型。当前UNKNOWN，不能因靠边自动连接。
- `transforms`：每项列出平移、缩放、旋转、镜像和对应验证记录。当前通用变换均UNKNOWN，包括任意平移；没有向地图拼装开放镜像、缩放或旋转。具体组件的几何放置，不等于该变换已通过动作验证。

## 端口与有向关系

每个`ports[]`包含：

|字段|含义|
|---|---|
|`id/objectId`|稳定Port ID、真实标记对象引用|
|`position/connection`|局部连接点、允许连接范围及其证据状态|
|`support`|真实支撑对象ID和面，或UNKNOWN|
|`normal`|几何朝向，不是玩家速度、移动方向或双向通行声明|
|`motion.ingress/egress`|分别声明进入/离开的方向和模式，未知时各自UNKNOWN|
|`preconditions.ingress/egress`|分别声明进入/离开的能力、装备、资源与状态条件|
|`seamIds/routeRoles`|显式接缝引用、具体路线中的入口/出口角色|

同一Port可在不同路线兼任入口和出口，不靠复制端口名虚构更多物理连接口。当前入口/出口标记只是已有见证的两个真实位置，连接范围仍UNKNOWN。

`relations`必须覆盖**全部不同端口的有序对**，N个端口就是N×(N−1)条（自环由单独路线/状态表达，不默认生成）。`path/no_path/UNKNOWN`分别表示声明的通路、不通及未知；`path`还必须引用方向相符的路线及其条件，不能凭字段存在获得拼装资格。

每条`routes[]`有`from/to/role/pathObjectId`，角色支持`main/reward/return/recovery/shortcut`。各路线独立保留能力格式、难度格式与资源压力，不把主路评分复制为奖励/返回路线评分。关系UNKNOWN时，即使存在预期路线，也不能交给拼装器当通路。

## 状态传递、回程及解锁

`route.transfer.requires → ensures`分别为进入要求和离开保证，包含以下显式字段：

```text
capabilityRequirements, equipment, grounded,
velocity.x/y, remainingJumps, airShots,
stamina, health, shotCooldown, traversalState,
mechanisms, phase, recoveryConditions
```

已知数值范围用`[min,max]`；动作次数为非负整数，不能少字段后默认0。地面状态只接受true/false/UNKNOWN。能力与装备、机关与相位也必须显式描述；某项UNKNOWN时不能作为状态满足证明。

当前旧轨迹**第一帧在执行输入之后**，不是进入快照。因此进入状态保持UNKNOWN。最后稳定帧的落地、速度、剩余次数、精力与机关状态写入物理记录的`observedExit`，**不自动提升为对任意进入状态的离开保证**。

`return.status/routeId/conditions`明确能否返回及反向路线。声明yes必须引用方向相反的真实路线；拼装准入还检查返回所需能力/机关是否由本次离开状态满足，以及反向独立物理证据。不能借未来奖励或未来开门状态证明回程。

不能确认回程或明确单向时，`onward.target/requiredState/status`必须描述后续通行或安全恢复目标。未验证目标保留UNKNOWN，不能自动填“落地回满”。

`unlocks`声明真实触发Cell、触发条件、状态变化及`before/after`各自的端口对、方向、条件和通行结论。当前钟的门碰撞在开启时失效，持续1.6秒，并按原逻辑安全关闭；不是永久奖励捷径。击钟见证不证明初始开门状态下所有走法、反向或捷径可用，因此这两组关系仍UNKNOWN。

## Macro一致性

`composition.components`列出稳定实例ID、Module ID、精确内容版本与放置变换；`connections`逐条列出内部端口连接、方向、传递与验证状态；`exports`将每个Macro外部端口映射到实际组件端口。

检查器核对：组件版本、变换后的所有几何、外部端口真实位置和对象、每条路线的组件路线/连接步骤是否连续。重复别名不能制造额外物理端口。新增独立Cell必须在`composition.cells`引用实际对象和内容版本；不能藏入无来源的碰撞实体。

当前组合工具支持显式平移的几何实例，其他组件变换拒绝推断。示例Macro有2个Module、4个真实外部端口及12个明确有序关系；内部连接和所有Macro通路均UNKNOWN。它是契约表达与检查示例，**不是新生成的可通关Macro**，不继承部件物理通过结论。

## 物理证据及拼装准入

每条验证记录绑定`contentVersion/routeId/from/to`、能力配置和装备、进入状态、验证方法、覆盖范围、结果、失败原因、未验证项、原case SHA、输入/输出/源绑定文件SHA。

本批3个Module复用`plains-production-v1/v2`的旧真实见证，明确标记`historical_actual_godot_forward_replay`。原holdout统计作为父参数化候选的采样上下文附带；不冒充所有相位都验证了当前导出的固定实例。反向、通用摆放、完整进入状态、完整净空均未验证，Macro整体物理UNKNOWN。

`assemblyInterface(document, context)`是唯一的接口准入函数，**默认拒绝**，返回逐项原因。需要：

1. 当前内容哈希有效，结构/真实几何引用合法；选定方向为有条件的已声明path。
2. 对应进入/离开端口的支撑、连接范围、接缝、方向/运动模式及前置状态已知且验证。不要求无关的反方向也已验证。
3. 占用、动作净空、动态范围和指定变换已验证，状态要求与离开保证明确，能力配置符合路线。
4. 有本端口对、本进入状态和运动方式的独立物理记录；调用方通过`verifyEvidence`从可信证据库核验原件，并用`acceptCoverage`明确接受此次覆盖。不能只信输入JSON里自填的pass。
5. 使用者显式提供`entryState/entryMotion/capabilityConfiguration/transformId`，回程或安全后续符合实际获得的离开状态；Macro还需可信组件解析及内部连接。

即使某接口准入通过，仍不替代具体摆放的碰撞/净空重叠检查、两模块之间的接缝实测或整图验证。当前公开4个候选的自动拼装接口均关闭；人工可看图、编辑、反馈，不会被默默加入正式库。

## 工具、检查和实际交付

```sh
# 已有原Godot runtime与归档按WORKSPACE.md恢复后：
python3 -m pcg.contract.export \
  --cases pcg/results/plains-production-v1/review_cases.json \
  --run pcg/results/plains-production-v1 --out pcg/results/contract-new-export
# 后续正常生产会自动输出 modules/：
cd pcg
python3 -m prototype.plains.produce --name new-run --calibration plains-calibration-v3 --holdout-seed 94007211
# 根目录检查：
node tools/contract-tests/check-contract.mjs
node tools/check-module-contracts.mjs
npm run check
```

核心代码：`module-contract.js`（版本/结构/准入）、`module-contract-render.js`（同版本SVG）、`pcg/contract/export.py`（原输入输出哈希核验）、`tools/export-module-contracts.mjs`（既有Map Notes格式映射）、`tools/compose-module-contract.mjs`（明确Macro候选）。Map Notes导入保留生成内容ID；信息面板区分当前与已改动版本，编辑后旧证据不能授权新几何。

32项初始合同测试后补充方向独立性、未映射多端口/支路不得静默丢弃，共34项合同测试；正向准入单元测试用明确标注的mock证据，不是物理实验。另复查原factory26项、平原9项及编辑器回归。模块图/SVG与JSON逐字节清单核验，浏览器导入/修改失效另有回执。

新物理批`plains-contract-production-v1`在首批12个输出后因Godot退出资源ERROR被拒；v2使用**同一seed93007211与原选择规则**做基础设施重试，首批接受、第二批退出ERROR后停止。错误原样保留，没有修改物理、退出检查或再抽幸运种子；本次没有新的完整通关批次可报告，也未把这些不完整运行当生产通过。交付使用既有3个Module的有界证据来验证输出适配，不重新盖章。

版本化归档`module-contract-v1`保留本轮适配过程、失败日志、两次不完整物理运行及源快照。它与此前真实平原/原角色归档共同复现；公开Module JSON和SVG在`generation/contracts/plains-v1`。
