# L1–L3、Foundry、Harness 与 Map Notes 实际代码审计

审计时间：2026-10-23 UTC。游戏源码固定 `f50fe78630fd98339186349f4ea91d92540d6c5b`（`integration/four-lines-20261023`），从 GitHub 精确提交读取；未执行引擎或测试。本报告所有“有/检查”均为源码事实，不把已有磁盘证据改签为本轮通过。编辑器检出 `ccbb21eec9f4d92e46ab9a95d35abb664dc69189`，其模块库绑定的是游戏 `74d8a06b42cb2bc2c5023f1bfe1a4fbc4b163074`，两者必须区分。

## 结论

项目并不是缺少模块或验证。已经有可实例化的模块 Resource、真实站稳端口验收、连续真实 Motor 输入回放、分流随机数、版本化 Manifest、能力状态图离线验证。缺口在于：这些能力尚未形成统一的多入口/多出口 Macro Module → L4 Map 的运行数据契约。Foundry 连续路线、平原 inline 模块、森林 Dictionary 场所分别演进；离线设计 schema 很丰富，但不等于运行生成器已消费该 schema。

## 1. L1 Cell 与 L2 Module

`PlatformingModuleDefinition` (`scripts/generation/platforming_module_definition.gd:1–170`) 是明确的运行 Resource：

- 地形：`world_bounds`, `platforms`, `one_way_platform_indices`。
- 危险与动态物：`danger_bounds`, `surface_thorns`, `saws`, `ferries`。
- 路线：安全锚点 `anchors`、主 `main_route` 和 `branch_routes`（锚点索引），既能汇合也能结束于奖励袋。
- 端口：兼容 canonical 单 `entry_port/exit_port`，另有 `entry_ports/exit_ports` 数组；`get_entry_ports/get_exit_ports` (92–105) 回退到 canonical。
- 筛选：最少跳/弹、burst、最少跳高/距离/地速及最大射击冷却。

`is_valid` (34–89) 检查边界、端口 ID/位置、所有锚点实际站在支撑平台、危险/动态扫掠不侵入安全站点、索引和对象源 ID。`supports` (122–136) 只做配置/能力包络筛选，源码明确“不等于几何或物理路径证明”。`MovementCapabilityEnvelope` 是无碰撞解析近似。

L1 目前主要体现为上述矩形地形/刺面/锯轮/摆渡等 Definition，并没有单独、通用、版本化的 `Cell` 组合 schema。把这些稳定实体看作 L1 合理；不能声称“四层均已有独立运行类型”。

### 真实端口状态约束及边界

`PlatformingModulePort` (`scripts/generation/platforming_module_port.gd:4–16`) 保存 body-center 位置、方向、普通/反冲最大速度、最大射击冷却、最少剩余跳/弹、跳高/距离筛选。`supports` (21–25) 检查配置。

运行检查在 `PlatformingModule.port_accepts` (`scripts/generation/platforming_module.gd:116–133`)：必须 `is_on_floor()`；距端口 <=48wu；有限普通/反冲速度；`recoil_burst_remaining<=0`；真实 Controller 活跃；真实冷却与剩余跳/弹符合要求。它确实考虑部分真实状态，不能说“只按门坐标拼接”。但它是**站稳型端口**，不允许高速空中进入/下落入口/持续反冲交接；方向字段此函数未用于速度方向区间验收；没有钩索挂接/目标、精力区间、动态相位窗口等通用状态关系。

`RandomStageGenerator._compatible_geometry` (`random_stage_generator.gd:539–564`) 允许有意共享 dock 支撑，拒绝其他平台物理重叠、危险扫掠侵入对方平台/危险。不是仅测总包围盒，也不是全图稀疏不规则形状嵌入求解器。

## 2. L3 的实际形式与不统一处

### Foundry phrase / itinerary

`config/platforming_foundry.json:1–54` 有六类设计短语，各有体验/判断/依赖、两种模块序列、pressure 曲线，例如“升高后收束”“读节奏·搭乘·离船”。是手写候选模板，非自动任务语法。

`FoundryCatalog.generate` (`scripts/generation/foundry_catalog.gd:89–112`) 生成 phrase manifest：`schema,id,template_id,variant,phase_index,capability_profile,seed,basis,engine,scope=development_only,nodes,hash`。每个 node 为 `{module_id,offset,phase_index}`，逐 canonical 出入口重合对接，先 `supports` 后 `_compatible_geometry`。

`FoundryCatalog.itinerary` (158–180) 组合多个 phrase，额外 `kind=itinerary,phrases,boundaries`，仍把子节点展开成线性序列；最多 6 phrases/24 parts，同一 capability_profile。它是可以工作的 L3 连续路线表示，却没有通用多出口外边界接口、内部状态转移关系、占用遮罩与回环闭合约束。不能将“macro_chain”模块 ID 或 itinerary 名称等同于成熟通用 Macro Module 类型。

磁盘当前 `resources/foundry/batch.json` 有 36 accepted phrases、18 itineraries、18 connection proofs，engine 字段为 `4.7.2-stable (official)`；这是已有批次文件事实，本轮未重跑，不判断其 basis 是否当前有效。

### 森林场所型 Macro

森林工厂另用 Dictionary。`ForestExplorationModules._base` (`forest_exploration_modules.gd:62–66`) 与 `ForestExplorationPlaces` 的 `_seven_bough_reveal` (27+) / `_z_descending_return` (247+) 含 `platforms,ports,routes,action_program,recovery,risk_reward,world_bounds,requires` 等。Places 有实际多端口、奖励/继续出口分离、失误出口与世界回程要求（places:133+,231,331+,410），并保留 `production_pool=false/native_verified=false`，不把工厂构建直接签物理准入。`_port` (523–524) 目前是 position/support_id/role/native_verified Dictionary，不直接使用完整 `PlatformingModulePort` 状态合同。

因此已经有“场所/复杂空间结构”内容，但 Resource 模块、Foundry itinerary、森林场所是三套不同的数据形状。L4 应通过适配器消费并逐步收敛，不复制三套生成器的所有细节，也不为统一名词先重写正式流程。

## 3. Foundry 实际验证了什么

调用路径：开发菜单 → `DemoApp.open_foundry` (`scripts/demo/demo_app.gd:1178+`) → `FoundryLab` → `FoundryCatalog.batch/valid` → `FoundryWorld.build` → `PlatformingModule`。

离线构建：`tools/foundry.py build` (28–71) → `tools/foundry_validate.gd` → 批次/回放 JSON。CLI `--promote` (178) 明确只安装开发 Foundry，绝不正式池。

`foundry_validate.gd` 的关键事实：

- `fixture/_create_fixture` (30–75)：真实 PlayerMotor 场景，仅首次定位到入口，之后不搬运；应用显式开发能力 profile。
- `tick` (77–113)：真实 `controller.physics_tick`，记录 Router 请求、位置、剩余弹；检查连续位移、全身矩形扫掠静态危险、锯轮相对运动扫掠和场景边界。
- `trace` (115–136)：每模块进入与退出调用真实 `port_accepts`，使用原输入驾驶，最后落地到达出口。
- `replay` (138–148)：从新 fixture 连续重放输入，最大位置偏差 <=0.05wu，检查安全与终点；实际开发 `FoundryRoutePlayer` (16–86) 回放仍进 Controller，不按记录坐标移动，运行容差 2wu。
- `_run` (155–216)：每候选最多四相位尝试，phase=[0,.25,.5,.75]；真实输入、JSON roundtrip、落盘后重放分别留证。
- (218–248)：另抽三种不同模板组成六条 itinerary，整条重新 trace/replay，不能只把单模块 PASS 相乘。

这比普通几何筛选强很多，但只证明特定 profile、相位、方向、驾驶策略和初始站稳状态下的路线。不能外推所有进入速度、所有相位/资源、所有武器、任意新 L4 接缝、敌战/Boss/隐藏支路与返程。

`config/foundry_capabilities.json` 中 base/二跳/空中链是不同开发 profile；hook `implemented:false` 是工坊 profile 未接入，不代表正式森林没有 grapple。正式能力来源必须追 DemoApp 实际授予。

## 4. 已有离线设计合同与能力可达性

`tools/level_design_contracts.py:296–389` 已有严格的离线 `level_design_intent` schema：STATE 位置/速度区间与资源引用；BUILD 单装备；ACTION；PHRASE；CHALLENGE 的入口/出口/相位/恢复/设备；Room/Encounter/Scene；topology 节点 grants/return_policy 与有向边 requires/weapon_ids/role/challenge_ids。

`validate_design:543–599` 按 `(node,ability_set)` 对每种单武器 build 做状态空间搜索，能力为单调授予；有状态上限。检查 goal 可达、grant 可达/循环锁、排除 master 后仍有通关路、每个可达状态（非终点）可以返回入口。代码明确装备切换和消耗资源需要 Motor 证据。该 schema 的 evidence_boundary 全为 unverified；这是一套有价值的设计/验证工具，但不是正式 Runtime 生成器的 MissionGraph/Macro 合同。

`tools/level_design.py` 是离线 CLI，不是 Runtime director：capture (118+) 调真实 Godot 后保存源文件摘要/命令/退出码/日志/数据 hash，analyze (157+) 校验 receipt 并产生 REVIEW/REJECT。`level_design_analysis.py:73–77,184+` 明确现有平原 capture scope 为正式 Manifest+Assembler+射击机关，未实例化敌/Boss，不可把报告当完整战役通过。

`tests/level_design_trace.gd:10–26` 目前只支持默认能力，非默认请求直接拒绝；每帧记录的是 Router 请求，非“被玩法接受的动作”事件。新能力/武器实验必须扩展真实消费者再比较。

## 5. Harness 与 Skills 参与方式

`tools/harness.py` + `tools/harness/profiles.json` 是离线选择/执行/证据系统：124+ 启动检查、token、超时清理；631+ 调度；905+ CLI。当前清单 174 checks、16 profiles，docs=33、gameplay=127、full=142 项（源码数组数量，非本轮执行次数）。如 `level-design-contracts/analysis/routing` 为 Python 专项，`level-design-runtime` 调 `run_level_design_tests.py`，`level-design-golden` 调 Foundry experience。Skills 是设计/生产/评审流程指令，未发现游戏 Runtime 调用 Skill 或在线模型生成大地图。

`tools/run_plains_region_tests.py` 默认 15 套 current suites + baseline；27 条独立旧 v10 路线用 `--with-legacy-fixtures` 显式开启，缺完成标记/错误/超时拒绝。`tools/run_generated_consumer_tests.py` 保留共享模块/碰撞/生命周期消费者，文件头明确八小关 App 已退役。最小新实验应注册精准专项，不默认跑全部 127 项 gameplay；原相关正式守门不得删/降标。

## 6. 重复/并行生成链

- 正式两区大地图入口是 `DemoApp:410–461` 的 PlainsRegionGenerator / ThornForestRegionGenerator + 对应 Stage；实际森林版本由其默认/显式参数决定。
- `RandomStageGenerator` 是旧线性 seamless_port_chain (version 9)，仍被 Random Stage Preview (`scripts/demo/random_stage_preview.gd:138`) 使用，也被 Foundry/平原复用 definition/兼容几何函数；不宜直接删除。
- `GeneratedDemoStage` 仍保存旧几何链消费者，并由若干隔离平原候选继承/消费；`PlainsSetDressing` 在该类 `:83–86`，不能据此认定正式 PlainsRegionStage 使用它。
- `DemoApp:361–409` 另有 world_rebuild、regional_art、environment/place、spatial_golden 显式实验分支，均优先于正式 generated_plains 分支。实验并存是事实，不等于默认冲突；需要统一入口注册表与明确退休清单。
- 精确提交树中没有名为 `plains_room_grammar.gd` 的运行文件；文档中 RoomGrammar 属历史说明，不能凭 README 重新把它列为当前主链。

## 7. Map Notes 现状与直接可复用项

`model.js:3,25` schema 是独立 `gunman-rush-level-sketch/v1`；canvas 明记 sketch/approximate。对象包括平台、刺、机关、钩点、敌、入口/出口、奖励、轨道、安全锚点和 route。可手绘主/支/奖励/返回路径、预览预期运动、导出 PNG/工程；不运行游戏物理，也不自动写回游戏。

`model.js:28–53` 实现修改原模块/新增变体、baseline objects/abilities/difficulty 与 changeRequest；`applicationStatus=not_applied` 明确。`capabilities.js:4–27` 可直接复用 AND+多 OR 组和三态判断：不满足=false；完整已知=true；缺资料=null。不能把 unspecified/partial 空条件视为无限制。

实测读取 catalog（不执行游戏）：177 条参考=72资源模块+51森林工厂/变体+36 Foundry短语+18路线；**0 条具有统一1–10分，0条能力要求完整defined，138 partial/39 unspecified**。因此当前不适合按 score 当真值批量做地图难度优化。评分必须先人工/实测校准。

`tools/build_library.py:282–303` 将 phrase/itinerary 展开成编辑对象，保留偏移和相位，内部端口变小 seam marker；原回放只作为 provenance，网页不运行回放。`coverage:305–310` 明确不枚举无限 Seed 整图和 inline 接缝、不包含整图区额外敌/Boss。

`library-client.js:33–39` 核模块 hash；42–54 同时读两库 main，将目录和模块读取固定同一编辑器 SHA。更新按钮目前默认查询 main，不能自动发现未合入最新开发分支。

没有 Mission Graph/Exploration Graph 结构、整图 Manifest 导入、能力状态层/捷径开关可视化、质量/失败结果面板、算法×Seed 并排对照。第一步建议独立只读实验报告 HTML/SVG，并定义机器数据；后续在 Map Notes 添加只读 Map 视图，复用现有缩放/路线高亮/来源指纹，而不把 map JSON 塞进对象草图 schema。

两个项目根目录均未发现 LICENSE 文件（精确游戏tree+编辑器根）；不能推定全部项目内容可按MIT再分发，素材既有来源/许可应继续逐件保留。本研究复用项目内代码不引入外部复制授权结论。

## 8. 对 L4 统一接口的具体建议

1. 复用 `RunRandomStream` 的 sha256_counter_52_v1（独立 namespace/version）与既有 RunManifest/Stage state 分离；新实验另 version，不改变正式流消费次序。
2. 复用现有 Definition/Module 实例化；提供适配器把 Resource、Foundry itinerary、森林场所转为 L4 候选描述，声明内部端口转移、占用与保护空腔、多出口语义及准入证据，保留原始数据来源。
3. 新 Macro 契约应包含 `template_id/version/source_hash,footprint,ports,transitions,requirements,resource_transfer,phase_policy,recovery,role_tags,verification_refs`，不只用width/height与四方向门。端口状态至少分grounded/airborne/falling/hanging；不能把所有入口强制重置满资源。
4. Mission/Exploration 图引用同一节点/边ID，边条件采用三态能力合同及开关状态；基于旧离线状态验证器扩展有限状态检查，资源消耗/相位不伪装为单调能力。
5. Spatial Embedding 同时分配模板/端口/位置，回环闭合失败可回馈 grammar，须有限预算+结构化失败。所有边都显式有内容/接缝承担，不画出无物理实现的图线。
6. 首轮固定现有内容库与 profile，分别报告逻辑、空间、真实Motor、主观。Foundry单模块/路线通过只作候选条件，新地图接缝和连续回程必须再跑。

