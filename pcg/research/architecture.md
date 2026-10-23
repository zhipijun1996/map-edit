# 当前代码审计：生成、物理与 Map Notes

审计日期：2026-10-23。以下为代码读取结论，除单列的 Map Notes 检查外，不表示现有游戏全部回归已通过。

## 1. 冻结版本和范围

| 来源 | 本次读取提交 | 说明 |
| --- | --- | --- |
| gunman-rush 正式主线 | `e9ab0e0743466b8983e34cc7de17bab1abf9d53a` | main，2026-10-22；72个 `.tres` 模块 |
| gunman-rush 最新开发集成 | `12f6cb006d7119598e3235f4ca4f7323e4c9d092` | `integration/four-lines-20261023`，本次查到的当天集成分支，2026-10-23 11:20 UTC；72个 `.tres` 模块 |
| Map Notes 编辑器 | `ccbb21eec9f4d92e46ab9a95d35abb664dc69189` | map-edit/main，2026-10-22 |
| Map Notes 模块库游戏来源 | `74d8a06b42cb2bc2c5023f1bfe1a4fbc4b163074` | `library/source-commit.txt` / `coverage.json`；与上述两份游戏源码均非同一版本 |

可复核的38份开发集成源码原字节在 [audit/](audit/)，路径和 SHA-256 见 [audit/index.json](audit/index.json)。报告代码链接固定到提交，避免后续 main 漂移。此处“最新”指本次发现的开发集成分支，不能由分支名推断其他专题分支均已合入；该提交的 `docs/current_state.md` 自身仍记录最终 CI / main / 正式新 Web 未完成。

**关键版本差异：main 的 `max_air_shots=2`，最新集成为1。** 最新默认只有一跳、一发；二段跳和钩索必须经能力授予。当前 `time_energy_v2.tres` 明确 `shooting_consumes_energy=false`，时间能量用于空中慢时。不可把旧双发耗能测试结果作为当前玩法证据。来源：[开发物理配置](https://github.com/zhipijun1996/gunman-rush/blob/12f6cb006d7119598e3235f4ca4f7323e4c9d092/config/player_tuning.json#L12)、[主线物理配置](https://github.com/zhipijun1996/gunman-rush/blob/e9ab0e0743466b8983e34cc7de17bab1abf9d53a/config/player_tuning.json#L12)、[当前时间能量资源](https://github.com/zhipijun1996/gunman-rush/blob/12f6cb006d7119598e3235f4ca4f7323e4c9d092/resources/player/demo_ui_01/time_energy_v2.tres)。

## 2. 正式运行调用链和实际算法

### 平原

`DemoApp._load_stage()` 的普通 `generated_plains` 分支调用 `PlainsRegionGenerator.generate()`；同一分支按地区改调森林，随后用 `PlainsRegionStage` / `ThornForestRegionStage`，并 `configure_generated()`。候选的 world_rebuild、regional_art、environment、spatial_golden 有独立前置开关，不能把它们的实验能力当成普通生成路径。Root Bell 内容则由 App 显式固定到已准入版本。来源：[demo_app.gd:410](https://github.com/zhipijun1996/gunman-rush/blob/12f6cb006d7119598e3235f4ca4f7323e4c9d092/scripts/demo/demo_app.gd#L410)。

普通算法为**人工拓扑族 + 有限语义路线 + 加权/均衡挑选人工动作配方 + 模块端口嵌入 + 条件/预算校验 + 有界失败回退**：

1. `FAMILIES=[woven_layers,linked_rings,crossroads]`，拓扑、内容、奖励各用独立随机流；最多4次尝试，再用固定已验证族回退。
2. `PlainsExplorationTopology.make()` 在三份人工 footprint 上选择15或18区域，变化层高，保留已定义的 short_technique / upper_discovery / creek_return 路线。
3. 生成器删除部分非桥边，约束连通、回环数、Boss接近点入度；设置背侧开启捷径、固定商人汇合点等。
4. `PlainsRouteRecipes.RECIPES` 为17个明确写出的动作配方，每个直接列 `.tres` 模块ID。`choose()` 按区域身份和目的过滤、优先较少使用并避免连续重复。然后按实际模块占地分配空间，不是纯等距矩形网格。
5. `PlainsRegionAssembler.build()` 将 `manifest.nodes` 的 Definition 实例化为正式 `PlatformingModule`，再安装支承地形与捷径墙。

代码：[生成入口/随机流/回退](https://github.com/zhipijun1996/gunman-rush/blob/12f6cb006d7119598e3235f4ca4f7323e4c9d092/scripts/generation/plains_region_generator.gd#L18)、[人工拓扑族](https://github.com/zhipijun1996/gunman-rush/blob/12f6cb006d7119598e3235f4ca4f7323e4c9d092/scripts/generation/plains_exploration_topology.gd#L5)、[动作配方](https://github.com/zhipijun1996/gunman-rush/blob/12f6cb006d7119598e3235f4ca4f7323e4c9d092/scripts/generation/plains_route_recipes.gd#L4)、[真实装配](https://github.com/zhipijun1996/gunman-rush/blob/12f6cb006d7119598e3235f4ca4f7323e4c9d092/scripts/generation/plains_region_assembler.gd#L10)。

`validate()` 校验图、能力筛选、唯一ID、机关计划、Manifest哈希，并重生相同候选比较。它本身**没有对每个新Seed调用Godot动作搜索**。验证同源重建可防篡改，却不能证明任意新几何可达。现有真实Motor专项测试是另一个环节。[validate:893](https://github.com/zhipijun1996/gunman-rush/blob/12f6cb006d7119598e3235f4ca4f7323e4c9d092/scripts/generation/plains_region_generator.gd#L893)。

### 森林

真实默认为 `thorn-forest-region-v2` + **`forest-bible-world-v15`**。`thorn_forest_region_generator.gd:18` 的 `CURRENT_DEPTH_LAYOUT=DEPTH_LAYOUT_BIBLE`；v16/v17/v18文件与注册条目存在，但不是无参数普通入口默认值。[版本注册](https://github.com/zhipijun1996/gunman-rush/blob/12f6cb006d7119598e3235f4ca4f7323e4c9d092/scripts/generation/thorn_forest_region_generator.gd#L18)。

V15调用V14生成基线，构造Manifest后 `ForestBibleV2Layout.install()` 追加根部连接、背枝、织网双窗、发现点、路线及捷径，最后重建场景结构/荆棘表面和边界。其局部几何和动作步骤大量为人工坐标：`_install_root_connection()` 内枚举各平台、takeoff/landing/support_id和两种出口；随机只挑部分分支、连接和内容变体。V15 `validate()` 通过类型、Manifest哈希、Bible结构验证，并重构相同候选做全数据相等比较。它是**版本化规则工厂与人工几何/动作程序的组合**，并非在线规划器从Cell自动发明钩索技巧。`native_verified=false`、`production_pool=false`也被明确保留，不能由生成成功擦掉。来源：[V15生成](https://github.com/zhipijun1996/gunman-rush/blob/12f6cb006d7119598e3235f4ca4f7323e4c9d092/scripts/generation/thorn_forest_region_v2_v15.gd#L12)、[布局安装](https://github.com/zhipijun1996/gunman-rush/blob/12f6cb006d7119598e3235f4ca4f7323e4c9d092/scripts/generation/forest_bible_v2_layout.gd#L13)。

这些实现已具备路线分叉/重汇合、能力条件、资源和回程消费者。缺口不是“没有图”，而是图和局部几何仍依赖人工目录，动作程序对新组合没有通用求解能力。

## 3. 四层在当前代码中的真实表示

| 目标层 | 现有数据 | 可以复用 | 尚缺能力 |
| --- | --- | --- | --- |
| Cell | `PlatformingModuleDefinition.platforms:Array[Rect2]`、one_way索引、surface_thorns、saws、ferries；森林为各类字典行 | 正式碰撞体、单向平台、刺面、动态物件Definition | 没有统一泛化Cell文法/动作affordance/参数域；拓扑中的`cells`是区域地址，不等于目标L1 Cell |
| Module | `PlatformingModuleDefinition` Resource；森林多个factory输出字典，含platforms/dangers/hook_anchors/steps | 真实实例化、稳定ID、局部边界、入口出口、能力筛选 | 尚未统一为动作契约+可求解参数几何；部分钩索表达在森林字典中、未纳入通用Module Resource |
| Macro Module | 平原`design_recipe.modules`、Foundry模板/phrase/itinerary、森林routes/connections/geometry_instances | 短语拼接和连续回放框架 | `macro_chain.tres`只是一个普通Definition资源，并非独立Macro类型；缺跨模块状态可达集合和自动节奏搜索 |
| Map | 各地区版本化Dictionary Manifest，areas/connections/nodes/rewards等；RunManifest管运行身份 | Seed/RNG流、哈希、预算、保存、正式装配 | 存在多个区域专用schema，通用空间嵌入和能力状态拓扑规划未统一 |

`PlatformingModulePort`以**身体中心**记录位置，限制普通速度/反冲速度/射击冷却和动作余量。当前多以站稳出入口为合同；若把每段都切成站稳港，容易破坏连续技巧的速度/相位衔接。新接口应允许带速度/资源/钩索状态区间的空中handoff，并继续检验完整身体净空。来源：[Definition](https://github.com/zhipijun1996/gunman-rush/blob/12f6cb006d7119598e3235f4ca4f7323e4c9d092/scripts/generation/platforming_module_definition.gd#L1)、[Port](https://github.com/zhipijun1996/gunman-rush/blob/12f6cb006d7119598e3235f4ca4f7323e4c9d092/scripts/generation/platforming_module_port.gd#L4)。

`MovementCapabilityEnvelope`明确只是无碰撞单跳筛选，未包含障碍、动态相位、连招和落地证明。它适合cheap rejection，不应升级成完整reachability oracle。[实现](https://github.com/zhipijun1996/gunman-rush/blob/12f6cb006d7119598e3235f4ca4f7323e4c9d092/scripts/generation/movement_capability_envelope.gd#L3)。

## 4. Foundry、Harness、Skills分工与差距

**Foundry** 当前是开发内容编排、真实Motor验收与回放交付工具。`config/platforming_foundry.json` 有6个模板、合计12个人工模块序列；`FoundryCatalog.generate()` 仅按template/variant选择已有`.tres`，按4个相位复制动态参数，检查端口几何，再序列化。`itinerary()`组合已合法phrase，最多24模块、6短语。`valid()`要求能从同一模板重生且全部数据相等，因而任意新几何无法直接通过此现有身份验证。`seed`写入身份并不自动扩大动作创造空间。[Catalog:89](https://github.com/zhipijun1996/gunman-rush/blob/12f6cb006d7119598e3235f4ca4f7323e4c9d092/scripts/generation/foundry_catalog.gd#L89)、[配置](https://github.com/zhipijun1996/gunman-rush/blob/12f6cb006d7119598e3235f4ca4f7323e4c9d092/config/platforming_foundry.json)。

`foundry_validate.gd`的优点是连续实际输入、真实Motor、完整身体危险扫掠、磁盘JSON重读后再回放、明确`awaiting_playtest`。但driver的`branch_module_driver.gd`按module_id分派已知专用走法，再回退到人工main_route；它并非任意地形的A*或MCTS规划器。[验收器:100](https://github.com/zhipijun1996/gunman-rush/blob/12f6cb006d7119598e3235f4ca4f7323e4c9d092/tools/foundry_validate.gd#L100)、[driver:25](https://github.com/zhipijun1996/gunman-rush/blob/12f6cb006d7119598e3235f4ca4f7323e4c9d092/tests/branch_module_driver.gd#L25)。

**Harness** (`tools/harness.py` + `tools/harness/profiles.json`) 是检查编排、版本/产物、超时/成功标记与证据归档体系；`level-design-*`、Foundry、正式地区各专项在此挂载。它不产生新的几何或控制策略，不会自动评价趣味性。应接入新生成器的真实候选/拒绝/轨迹指标，避免再增加一套冲突验收系统。

**Skills** 是人/agent的工作流程、合同、角色与审查要求。`level-module-creator`已要求实际Motor、资源/入口/出口/相位/负例，`challenge-choreographer`要求连续动作和恢复，`gameplay-reviewer`做独立反证。它们能提高工程纪律，不能替代运行时动作文法、几何求解器或搜索器。技能文档出现“动作链”不证明算法已能创造动作链。

另一个实际滞后：Foundry `hook` profile为 `implemented:false`，而正式TraversalAbility已经实现钩索。Foundry能力注册不是游戏能力权威，应以真实组件与授予入口为准。[配置](https://github.com/zhipijun1996/gunman-rush/blob/12f6cb006d7119598e3235f4ca4f7323e4c9d092/config/foundry_capabilities.json)、[实际钩索](https://github.com/zhipijun1996/gunman-rush/blob/12f6cb006d7119598e3235f4ca4f7323e4c9d092/scripts/player/traversal_ability.gd#L45)。

## 5. 真实物理实验接口

最小可复用链：`InputRouter.request_action()` → `PlayerController.physics_tick()` → Jump/Shoot/Traversal → **PlayerMotor.step()唯一move_and_slide** → 接触/落地/资源回执。

- `tools/foundry_validate.gd:33`的fixture只在出生时设置位置，关闭Controller自动物理与键鼠输入；每个`physics_frame`提交轴/动作，再`physics_tick(1/60)`。`tick:69`记录实际输入和位置、24×36身体静态危险扫掠、锯轮相对扫掠，适合改为独立候选验证服务。
- `FoundryRoutePlayer`回放输入而非设置pose；绑定basis、Manifest和引擎，适合回归重播。当前内部fixture与正式App测试要分栏；正式App还含能力授予、敌人、伤害、UI、保存和真实时钟。
- 钩索为cast/fly/pull/contact/kick/hang/retract等状态，实际shape cast查询可钩目标。`grant("grapple")`启用；二段跳`grant("double_jump")`设置实际容量下界。`resources/player/traversal.tres`的range为231wu。它不是摆绳物理，研究应采用本游戏的拉近/弹起/悬挂状态机，不照搬绳摆模型。
- 钩索接触、墙跳、真实空中命中可恢复动作；`restore_air_actions()`不能被生成器直接调用作验证捷径。基础一发下“连续反冲”必须有真实落地/命中/钩索恢复，或明确开发profile授权，不得静默设无限弹药。
- Router有100ms墙钟TTL及epoch/sequence；离线快进仍要在消费帧发新请求。大量并行Godot进程引起请求过期，不应被归为模块物理不可行。失焦、预算耗尽、探索未找到路线分别记证据，不能把搜索失败称证明无解。

源码：[Router:102](https://github.com/zhipijun1996/gunman-rush/blob/12f6cb006d7119598e3235f4ca4f7323e4c9d092/scripts/input/input_router.gd#L102)、[Controller:71](https://github.com/zhipijun1996/gunman-rush/blob/12f6cb006d7119598e3235f4ca4f7323e4c9d092/scripts/player/player_controller.gd#L71)、[Motor:30](https://github.com/zhipijun1996/gunman-rush/blob/12f6cb006d7119598e3235f4ca4f7323e4c9d092/scripts/player/player_motor.gd#L30)、[fixture/tick](https://github.com/zhipijun1996/gunman-rush/blob/12f6cb006d7119598e3235f4ca4f7323e4c9d092/tools/foundry_validate.gd#L33)、[Traversal状态](https://github.com/zhipijun1996/gunman-rush/blob/12f6cb006d7119598e3235f4ca4f7323e4c9d092/scripts/player/traversal_ability.gd#L58)。

引擎也须冻结：项目AGENTS要求4.7.2 Standard；环境初始`godot --version`为4.6.3。未经项目安装工具选择正确版本，不应把系统Godot测试声称为项目指定版本。

## 6. Map Notes兼容与可执行接入方案

现状是**游戏数据→编辑器草图的单向适配**，并非双向Runtime格式：

- `model.js:3` schema=`gunman-rush-level-sketch/v1`，对象为x/y/w/h/rotation、route.points[].action、tracks、targetId。`validateDocument()`仅检查结构/引用/有限数值。`progressAt()`是编辑器轨道预览，不运行Motor。
- `changeRequest()`保留 modify_existing/new_variant/new_module、baselineCommit、对象差异、能力条件、1–10人工难度。这些是很好的人机协作意图接口，但游戏未直接消费。
- `tools/build_library.py`从真实Godot提取的平台/刺面/动态物件/工厂数据映射成objects；`normalize_canvas()`平移后保留`source.editorTranslation`。回写必须逆变换，不能把编辑器坐标直接用于世界。
- 177份参考=72资源模块+51森林工厂结果+36 Foundry短语+18路线；总量不等于177个自动创造的Module。其来源固定到旧提交，更新源码必须重提取并重算消费者接入状态。能力字段保留`unspecified/partial/defined`，未知不是无需能力；难度`null`不是最低难度。

本次实际执行 `npm run check`，exit=0，覆盖177份文档、原资源保留、引用、能力AND/OR/不确定性、难度边界及消费者链失效回退；证据见[audit/map-edit-check.txt](audit/map-edit-check.txt)。该结果不包含游戏物理验证、真实浏览器交互或用户趣味评价。

建议分三步接入，不先强改编辑器核心：

1. **独立版本化候选IR**：`ChallengeSpec`记录动作意图、Cell参数域、完整能力/武器/资源/引擎/源码hash、entry/exit状态、分叉重汇合、禁止关系；`CandidateModule`记录求解后的准确世界几何、控制见证、验证收据和可见危险宿主。编辑器草图作为设计输入，游戏Definition/森林字典作为编译输出；schema不同显式转换。
2. **可回写适配器**：优先只支持terrain/platform/附着刺面/hookBounce/hookHang/entry/exit/reward及明确动作标签。逆editorTranslation，严校rotation、曲线轨道、复杂机关：无运行消费者必须报unsupported并保留需求，不能默默降级。修改原模块做baseCommit三方差异，输出补丁而非直接覆盖。
3. **候选评审界面**：点击生成请求本地/开发服务，返回若干QD不同格子的候选、实际动作轨迹、误差成功率、失败帧和真实Godot试玩链接。路线示意和执行轨迹视觉区分；“编辑后未验证/已验证源码版本/待人工试玩”状态明确。任何几何、机关、能力、物理、引擎变化使旧收据失效。保留人类评分/备注用于离线校准，不能把AI静态评分写成人类乐趣认可。

## 7. 可以保留与应该重设计的边界

保留：真实Motor与输入路由、能力状态机/合法恢复、碰撞/危险实体、随机流与版本身份、Manifest保存、正式装配、轨迹回放及原Harness正反例、Map Notes稳定对象ID和修改意图。

重设计：新动作/几何候选IR、动作前后条件文法、状态区间/相位兼容、通用可达性搜索、违反约束反馈、行为轨迹多样性档案、稳健性与删技能反例。Foundry可增加独立`generated_candidate` schema和身份构造器，不放宽旧Catalog.valid()让任意数据绕过。

质量证明最低标准：新几何并非预制Module拼接；在真实能力快照下有成功输入见证；删反冲/删钩索及替代路线消融证明机制发挥作用；噪声测试给操作容错；轨迹行为距离而非模块名/坐标hash给多样性；人类盲测仍为趣味性准入。成功一条见证只证明存在，不能证明没有更简单绕法；不存在见证只代表此预算/策略未找到。
