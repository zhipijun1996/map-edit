# 森林 Map 实际代码审计（只读）

审计基线：`integration/four-lines-20261023@f50fe78630fd98339186349f4ea91d92540d6c5b`。审计时间 2026-10-23。下文行号相对此提交。已读取实际 GDScript/Python 消费者与测试；本次审计没有运行 Godot，也没有把历史日志视为本轮通过。

## 0. 先纠正当前性

- **普通新建/调试森林默认 v15，v18 不是正式默认。** `scripts/generation/thorn_forest_region_generator.gd:20`：`CURRENT_DEPTH_LAYOUT := DEPTH_LAYOUT_BIBLE`，而 `DEPTH_LAYOUT_BIBLE` 为 `forest-bible-world-v15`。`DemoApp` 的 `_forest_layout_version` 从这里初始化（`scripts/demo/demo_app.gd:190`、258）；菜单专门请求才选择 v16/v17/v18（1694–1699）。
- v18 返回 `production_pool:false`、`admission:exploration_places_candidate_new_expansion_pending_native_art_and_playtest`（`thorn_forest_region_v2_v18.gd:12`、26），数据内部也保留 candidate 和 `not_complete_region`。这些字段不是“未接消费者”：它确实可经开发菜单进入真实 App；但不能称全面准入。
- `main@e9ab0e0743466b8983e34cc7de17bab1abf9d53a`（2026-10-22）与本基线的六份关键森林生成源码逐字一致：registry、v15、Bible layout、v18 network、v18 embedding、assembler。SHA256 对照见 `main-integration-comparison.json`。本结论不是只读 main 得出。
- `fix/forest-focus-and-interwoven-routes@71c29dfc03512ffcbac5578de1fe893de7f42794`（2026-10-19）相对 main 的 GitHub Compare 为 `behind / ahead_by:0 / behind_by:93`，即已经是 main 祖先，不能当未合入最新算法线。见 `compare.json`。

## 1. 实际入口与调用路径

```text
project.godot → scenes/demo/demo.tscn → DemoApp
  start_debug_region()/campaign 初始化
  → 森林 campaign.abilities.append(grapple) 与 traversal.grant(grapple)
  → DemoApp._load_stage() 创建 capability 字典
  → ThornForestRegionGenerator.generate()/generate_version()
  → v15.generate → v14.generate → v13.generate（真正检查 S2/H 能力）
  → v15._candidate → v14._candidate → v13._candidate → v12._candidate → v10._candidate
       v10 手工树洞/空地骨架+奖励/Boss
       v12 ForestVerticalExpedition.install
       v13 ForestInterwovenExpedition.install
       v14 ForestFruitRoutes.install
       v15 ForestBibleV2Layout.install
  → Dictionary manifest（areas/connections/routes/platforms/geometry_instances/...）
  → ThornForestRegionStage._ready()
  → ThornForestRegionAssembler.build(manifest,tuning)
  → StaticBody2D/CollisionShape2D、真实 GrappleAnchor/ForestFruitAnchor、门/捷径
  → Stage 加载真实 EnemyMotor 与 Boss 场景
  → DemoApp 实际控制、奖励与状态保存
```

精确入口：`demo_app.gd:265`、285 为当前森林真实 H 授予；415–416 把实际 `controller.traversal.hook_enabled`、campaign abilities、装备、内容版本传给 generator。`thorn_forest_region_generator.gd:44`–65 为版本分派。`thorn_forest_region_stage.gd:29`–39 校验绑定状态并 build；74 起实例化敌人；112 起选择/实例化 Boss。

## 2. 目前是什么算法

**默认 v15 是版本化、代码手写的空间/路线配方叠加系统，外加少量命名随机流选择，不是通用 Mission Graph Grammar、ASP 或任意图嵌入。**

- `thorn_forest_region_v2_v10.gd:29`–106：`forest_topology`、`forest_ecology` 两条流；2 个骨架分支映射为两图共4个 family；cache_route、enemy_mix、map2 cavity_direction、root_entry、west_reward 等有限选择。核心树洞固定 offset `(600,600)`，真实空间与图同步手写。
- `forest_vertical_expedition.gd:46`–54：七个实际 macro/action 几何实例、坐标和次序写在 `placements` 常量数组，只有 canopy crossing 由 H-H / R-H 等有限选择变化。不是每个 seed 任意生长七段新结构。
- `forest_interwoven_expedition.gd:48`–100：加入 grounded lesson、inner/upper 两支、deep-root 回环；seed 的一个 bit 选择 fast/growth 推荐先走哪支。图中两支都存在；**改变推荐 itinerary 不能直接计为世界拓扑新变化**。另外西奖条件确实改变探索顺序及部分连接。
- `forest_bible_v2_layout.gd:13`–43：一个 bit 在 outer-root east mouth 与 inner-root lower mouth 之间选择真正不同出口；加入 backbranch 奖励、双窗织网遭遇、发现物和奖励开捷径；地图/Boss仍依托既有大树空间。
- `v15.generate/validate`（`thorn_forest_region_v2_v15.gd:12`–41）会重新构造候选并比较 canonical data 与 hash；这是可复现/拒绝篡改机制，不是“对任意生成图证明可解”。

**v18 是新增探索场所的固定前缀+有限次序/形态变体实验。**

- `forest_exploration_network.gd:18`–52：在 v15 完整基线上拆除旧 Boss sector，固定 C 出口后增加 double_window、seven 场所；再放有两种次序的 fallen / Z，map2 额外插入 backbranch。
- 95–147：同 root seed 派生跨两图共享次序流，map2 反转 fallen/Z次序；场所各 variant 0/1。该变化比单纯贴图/平移更实质，但总体仍是 **chained choice places，非全面网状探索生成器**。源码 contract 自己也如此标注（89）。
- 210–230：以已放源支撑右缘+80wu 确定下个入口，Y 对齐实际端口，追加实际 jump_gap。没有全局回溯、SAT/CP、碰撞占用搜索或循环闭合求解。
- 457–489：Boss 用实际 arena factory 重新安置到新场所后端，非只移动图节点标签。

## 3. 逻辑拓扑和二维布局是否分离

有**可辨识的数据层**，但没有完整的独立生成阶段/契约：

- 图：`areas`（id/position/role）、`connections`（id/a/b/kind/path/steps/condition/支撑引用）、`routes`（命名 edge itinerary）。
- 空间：`platforms`、`dangers`、`hook_anchors`、`geometry_instances`、world_bounds、boss_geometry。
- 不过两者由同一 `install()` 按硬编码坐标同步写；Mission 的目标依赖没有独立 IR。边经常本身携带全部操作程序和世界坐标，替换二维布局会牵动图。
- v18 `forest_exploration_place_embedding.gd:6`–93 独立地负责局部几何平移和ID映射，是有用的雏形；它不解空间约束，只把已选且已知适配的模板放到指定 origin。
- v18 topology signature（network:232–240）是排序后的有向 `a,b,condition` 关系 hash；保留稳定语义ID，不能消除图同构，也不评“有效循环”。v15签名还继承包括 spawn 的旧签名（v10:515），有把空间/标签变化计入多样性的边界。

## 4. 分支、回环、锁、奖励、Boss

- 真实已有分支/汇合/单向下落：树腹M、外冠E、内根D、外根R，及 S/C 树洞；`v10._core_edges():185` 起；`_single_tree():226` 起组装 `macro_loops`。
- v13 树内/树外支路与 grounded recovery/deep-root ascent 是真实不同运动段，并有落点支撑/资源恢复要求；不是只有叶子奖励房。
- v15 backbranch 奖励从一侧进、另一侧出；奖励的 accepted claim 才打开物理 shortcut blocker（`forest_bible_v2_layout.gd:119`–141，`thorn_forest_region_assembler.gd:147`–167）。普通长回程保留。门状态进入 `region_state.opened`，claim本身有幂等来源ID。
- 森林主能力条件是当前入口已授予 H；v13能力门限制 `[grapple]`、拒绝 wall/double jump/武器演化等未授予能力（`thorn_forest_region_v2_v13.gd:14`–19）。不应把它解释为运行时搜索/生成多种能力解锁顺序。
- 藤门由实际 `hook_kick` 且命中指定合法 anchor 打开（assembler:135–145）；抽象图边仍可能 `condition:"open"`、`kind:"gate_hook"`，说明动作锁语义散布在边kind和runtime，不是统一布尔条件模型。
- 奖励数额/资源二选一、approach_route/return_route、claim_before_edge 都有实际消费者；reward placement大多为特定手工位置，未由通用风险收益约束求解。
- v10 `_route`（476–489）是未加权 BFS，跳过非目标 cache，但**没有评估 condition、能力/资源/开关状态**。它生成推荐行程，不是整个状态空间可解性证明。v15新shortcut不会自动被这段通用 BFS 正确建模，只由专用手写route和runtime处理。

## 5. Module / Macro Module 与运动端口

- 森林当前多数 Module 是工厂返回 Dictionary，不是统一 Resource 接口；如 `ForestExplorationModules.build()`（`forest_exploration_modules.gd:28`–64）返回平台、挂点、危害、spawn/goal、entry/exit_support、steps/routes、action_program、requires、risk_reward、admission。
- `ForestExplorationPlaces.build()`（places:21–31）只对两个 card 真正实现 factory；catalogue里 `proposed_only` 卡不能当可放置内容。另 fallen/backbranch 用各自 factory。
- 宏几何实例已存 factory/version/local_geometry/translation/platform_id_map/anchor_id_map/danger_indices（embedding:40–42 等），足以做追溯、真实几何比对、可复现回放，是可沿用的数据资产。
- 场所 port 含 position/support_id/role；embedding 转为 area/point/support（46–57）。route 会映射支撑ID、起跳点、落点、path/action_program（59–92），部分边增加 entry/landing_support、hook_wait、first_hook_delay、hang frames。**这已比四向门更接近实际平台连接。**
- 但没有统一 `entry_state → exit_state` transfer relation，也没有普遍的速度/朝向区间、剩余空中跳/枪/Htoken、精力、相位集合或不确定性包络约束。现有手写 action_program 和真实 driver 会顾及它们，不能说生成器已在组合时通用求解。
- 放置变换主要是平移，未见对不规则宏模块任意方向/镜像/旋转及高空高速端口的通用适配验证。v18按实际支撑水平/高度对齐和80wu缝隙拼接是专项规则。

## 6. 当前“可通关验证”究竟覆盖什么

### Runtime validate

- v15 canonical regenerate+hash、Bible.validate 主要检查语言/危险宿主、唯一ID、敌人掉落身份、发现物引用和命名route连续性（Bible:210–240；v15:34–41）。
- v18 Network.validate（506–528）检查Bible/source contract、requires H、非正式池、Boss geometry.ok、unique IDs、命名route a→b连续、支撑引用存在；随后v18.validate同样重生成比较（v18:38–44）。
- **未见全状态 `(area,abilities,opened,resource/velocity/phase)` reachable-set 检查，更未见对所有可达状态的“仍能达到目标/安全锚点”反向求解；不能据此证明全图无softlock。** canonical比较可拒绝重算hash后的篡改，不证明原候选设计质量。

### 离线真实 Godot

- `tools/run_forest_depth_region.py:1`–30、1612–1626：`--corpus` 固定10 root seeds×两图×fast/growth/high_return/change_mind，共80个真实App路线；引擎import90秒、每native240秒，选择路线总范围有界。`--matrix`是16条而非完整随机空间。
- `tests/forest_depth_region_trace.gd:72`–103 通过真实 DemoApp 创建森林，router提交动作；没有中途搬位置/补资源。runner输出scope明确 `formal_DemoApp_forest_v2_continuous_route_not_boss_fight`、`manual_motor_step:false`、`position_or_resource_injection:false`、`boss_fight_covered:false`（runner:27–34）。因此真实角色、敌人和门通过不等于Boss战、所有路线/相位/能力组合。
- v15 使用 `forest_depth_trace_strategy.gd`、`forest_bible_region_auto_trace.gd` 与 support 适配当前App/射击规则；当前单发免费与历史双发程序不同处有真实输入替代事件及资源账本校验。不能把历史动作原程序与新规则的替代程序混作相同实验。
- `tools/run_forest_bible_world_motor.py` 可执行 `bible_connection_journey` / `bible_backbranch_journey` 从真实正式spawn到camp的完整路线，验证claim打开实际shortcut（`tests/forest_bible_world_motor_runner.gd:20`–43）。这比仅局部支撑连通强，但仍是两种专用pilot。
- v18 `tools/run_forest_places_feedback.py:337`–360 设计清楚区分：20个世界结构/回放样本（非物理）；2变体×4条局部seven路；map1/2各一个 **formal-spawn normal journey**；reward/return/windows是 **initial fixture spawn only**，非完整前缀。library扩展还含5个fixture probes与8个局部probe（313–334）。这些输出的scope不可合并称“v18所有seed整图物理通过”。
- `tests/forest_places_world_runner.gd:22`–62 检查20世界JSON回放、重算hash的几何篡改拒绝、物理轮廓和完整有向图签名有差异，明确FUN/art/human time/device均未验证。
- 本审计只读代码，以上说明测试系统能验证的范围；没有声称本轮新鲜执行上述任何测试。新算法应复用这些pilot/账本，并针对新接缝、低资源、回程、单向边和死敌挂点做反例，而不是复制其PASS历史记录。

## 7. 重复系统与集成风险

- registry保留v1、v7、v9、v10、v11、v12、v13、v14、v15、v16、v17、v18；这是显式版本白名单/旧存档来源，不能简单全删。AGENTS最新要求当前Demo优先，旧兼容可延期，但需区分“删历史”与“停止新功能层层继承”。
- 当前默认 v15 的生产实际上不断重构v10底稿并叠加v12→v13→v14→v15修改；几何、路线、材料、能力、测试专用识别器散落多代；同一段既有 old producer又有被新层移除/改名的边。增加模板/新能力时，审计和重复构造成本增长。
- `generate()`在各wrapper先调用BASE.generate/validate，然后又 `_candidate()`从最底层重建并再次validate；生成成功不代表Runtime成本理想，需测量实际版本完整调用。不能只测最底层 `_candidate()`后称正式性能。
- v16/v17/v18与default v15并行保留开发入口；需要新的统一 L4实验入口明确算法/version/content snapshot，避免又增加一个正式generator registry分支后误称架构升级。
- 借鉴方向：保留已有macro几何实例/真实ports/动作轨迹；新增Mission/Exploration独立IR与状态空间validator；让空间求解器选择局部factory、验证几何/端口约束后再输出旧manifest可读的完整展开数据。仅用现有v18 `install(origin)`不能覆盖新系统全局布局。

## 8. 可操作的实验对照边界

1. 固定现有高质量factory和能力H快照，先比较逻辑图；不能因推荐行程变了就计拓扑变异。
2. 放置器声明只平移还是允许镜像、占用多矩形、端口唯一性和连接走廊；失败应返回constraint/retry预算，不偷偷删图边。
3. 能力布尔合法、所有可达状态仍可恢复、几何占用合法、单接缝真实Motor、完整路线真实Motor、人工趣味分别计pass/unknown。
4. 至少留“奖励后回到熟悉地标”“可见未达目标”“同一能力解锁不同顺序”“主线短/奖励深”职责；现有v18次序反转并不足以单独证明这些目标。
5. 用实际v15/v18 exporter+上述两类测试作基线；不把20世界结构样本当20张物理通关样本。

## 证据索引

完整源码按固定commit下载在此目录 scripts/、tests/、tools/，用于审计可复核；未改变游戏文件。`compare.json`、`main.json`、`fix.json`记录分支GitHub返回，`main-integration-comparison.json`记录六关键文件字节比较。完整链接模板：`https://github.com/zhipijun1996/gunman-rush/blob/f50fe78630fd98339186349f4ea91d92540d6c5b/<path>#L<line>`。
