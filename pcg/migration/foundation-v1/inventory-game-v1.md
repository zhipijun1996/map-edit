# 主游戏来源盘点 v1

状态：只读盘点完成；尚未迁移、运行物理或认证任何主游戏 Module。详细逐文件来源、SHA256、Git blob SHA、旧目录的逐项账目和运行时 diff 见同目录 `inventory-game-v1.json`。

## 固定来源与覆盖边界

- 主游戏固定 main：`879b39eaa869be70cb799dedd1bb6ffc35e0b92f`，tree `8b005cbed42d580cd013fa24fca6377436cef00d`，提交时间 `2026-10-26T16:03:42Z`。本轮复查 main 仍是此版本，没有把后续版本混入。
- 读取方式：GitHub connector 的 main 引用、固定 ref 目录与文件 GET；本地文件只读，逐 Git blob 对照。没有 clone、下载完整游戏或在游戏目录运行 Godot。
- `/workspace/gunman-rush` 是无 `.git` 的下载副本。**整份本地副本版本 UNKNOWN**；只有与固定远端 blob 匹配的路径可以归属上述提交。JSON 每项区分 `remote_verified` 与 `UNKNOWN`。
- 本仓库旧来源：`74d8a06b42cb2bc2c5023f1bfe1a4fbc4b163074`，位于 `library/source/`；旧目录是 `library/catalog.json`、`library/coverage.json`。
- Harness 原来源：`12f6cb006d7119598e3235f4ca4f7323e4c9d092`，以 `pcg/prototype/godot/source_provenance.json` 的 870 项保护文件为准。
- 新约束依据：根目录 `MAP_FOUNDATION.md`（规范）与 `MAP_GENERATION_GUIDE.md`（建议）。读取时 SHA 保存在 JSON 的 `source_docs`，不以旧 README 代替。

## 177 条旧参考究竟是什么

| 类别 | 旧条目数 | 实际输入与含义 |
|---|---:|---|
| 通用与平原资源 | 72 | 72 份 `PlatformingModuleDefinition` `.tres`，通用 19、平原 53 |
| 森林工厂输出 | 51 | 12 个源码入口文件的有限求值结果，含数值变体 |
| Foundry phrase | 36 | 6 个组合模板的能力、参数、相位样本 |
| Foundry itinerary | 18 | 多 phrase 串联路线，属于复合内容 |
| 合计 | 177 | 参考条目数，不能作为基础模板或玩法家族总数 |

森林按「源码路径、方法、逻辑字符串参数」合并数值变体，得到 47 个**语法构造签名**。这不是 47 个已去重玩法或认证模板。明确重复的数值组包括 `seven_bough_reveal`、`z_descending_return`、fallen trunk 和 fruit crossing。`forest_exploration_modules` 已委托生成的三个 thorn corridor 也不能另加三次。

Foundry 的 6 个模板是 `height_then_precision`、`read_ride_release`、`short_long_rise`、`climb_change_height`、`resource_then_rhythm`、`precision_to_transfer`，各有两个既有资源序列。36 phrase 的 profile 分布是 base 24、double_jump 6、air_chain 6；18 itinerary 各 profile 6 条。名称、seed、相位、能力档或镜像不自动增加基础模板数。

旧 `integration` 中 development 82、unverified 70、formal 25，表示当时源码消费者接入状况。它们不等于本轮新地基认证、人工趣味认可或生产批准。

## 最新实际目录

| 范围 | 数量 | 与固定 main 的核对 |
|---|---:|---|
| `resources/generation/modules/*.tres` | 72 | 本地 72/72、旧 `library/source` 72/72 均与 main blob 相同；此目录无新增资源漏项 |
| `scenes/generation/modules/*.tscn` | 68 | 本地 68/68 匹配 main；旧快照只保存其中 17 份，已有 17 份均相同 |
| `scripts/generation/*` | 156 | 78 `.gd` + 78 UID；本地全部匹配 main，不是 156 个生成器 |
| 旧 generation `.gd` 快照 | 78 | 77 份与 main 相同；`plains_region_generator.gd` 已变化 |
| 本地 `resources/**/*.tres` | 155 | 完整本地路径与哈希清单；除已匹配范围，远端归属保持 UNKNOWN |
| 本地 `scenes/**/*.tscn` | 122 | 完整本地路径与哈希清单；除已匹配范围，远端归属保持 UNKNOWN |

四份资源没有同名包装场景：`plains_ferry_channel`、`plains_low_arch`、`plains_twin_gears`、`plains_windchime_rush`。资源仍可由消费者直接加载，不能因此称它们缺失或未实现。68 个包装场景均指向上述资源，没有额外 scene-only Module ID。

122 个场景的类别为 generation 68、bosses 8、enemies 8、world 7、player 1、demo 10、dev 9、style_exploration 10、test_levels 1。场景数量不是 Module 数量。

17 份 Boss `.tres` 中包含 HealthDefinition 5、WindkeeperDefinition 6（含两份 legacy）、ThornForestDefinition 2，以及 BossDefinition、BossDuelDefinition、ThornQueenCanopyDefinition、ThornQueenWeaveDefinition 各 1。8 个 Boss actor 场景与这些调参资源、场地工厂分别记账。`boss_approach`、`plains_boss_arena` 等资源只是场地地貌，不能代表完整 Boss 遭遇。

## 旧 177 未覆盖的实际来源

JSON 的 `procedural_source_inventory` 列出全部 78 个 generation `.gd` 的固定来源、哈希、公开方法及静态角色；`old_index_omissions` 列出以下可定位遗漏。没有执行工厂来编造输出数量。

| 来源 | 内容性质与遗漏 |
|---|---|
| `forest_ecology_geometry.gd::woven_crown` | 可定位的双平台、hook、双敌人局部原型，未被旧提取入口收录；源码仍标记待 native/formal-return 验证 |
| `forest_boss_arena_factory.gd` | `from_prep`、`queen_golden`、`queen_canopy_from_prep` 的 Boss 场地构造，依赖实际 Boss definition 与 prep |
| `forest_entry_rest_bay.gd::install` | 内联休息地貌和 first/second H 几何实例；休息点不计动作家族 |
| place embedding / fruit routes / exploration ecology | 区域中的路线、奖励、敌人安装规则；不是每个脚本一个基础模板 |
| `plains_environment_plan.gd` 与 `environment_grammar/lee_post_v1.json` | Polygon 环境候选，原始输入含 5 个 place、7 个实体多边形、1 个机关；不属于旧 72 份矩形资源 |
| `plains_place_plan.gd`、`plains_joint_recoil_plan.gd`、`plains_world_rebuild.gd` | JSON 与程序式地貌／动作构造；无有限输入域时，输出数量 UNKNOWN |
| `plains_route_recipes.gd` | 17 个组合 recipe，复用既有资源；不是新增 17 个独立基础 Module |
| `plains_region_generator.gd` | woven_layers / linked_rings / crossroads 等正式区域构造及内联连接、教程、奖励节点；旧索引不穷举 |
| `plains_root_bell_encounter_v2/v3.gd` | 实际遭遇与场地扩展；源码 production 标志不能替代新地基认证 |
| 历史 forest region/layout/expedition 系列 | 多个整区域版本，按整图构造规则记录，不拆成虚构的基础 Module |

`forest_exploration_places` 中 `l_backside_nook`、`fallen_trunk_two_faces` 只有 proposed-only catalogue 条目，没有可执行 build 地貌，因此不能算遗漏的已实现模块。

Foundry 最新 main 仍是 36 phrase + 18 itinerary，ID、36 份 phrase nodes、18 份 itinerary nodes 与旧批次相同；但 basis 从 `4739d409…` 变成 `dceae4cf…`，相关 manifest/replay 哈希也变了。不能用相同节点来沿用旧来源认证。当前 batch 自身为 `production_pool=false`、`awaiting_playtest`。

## 原始数据是否像素精确

可以取得精确输入，**不能把旧网页图层整体当作精确物理场景**。

- 177/177 保留 `source.original` 求值字典；72 `.tres` 的原始字节也已经与 main 对上，适合后续迁移从源码重新解码。
- 检查 72 个资源的 210 个平台：减去 `source.editorTranslation` 后，编辑对象矩形与原始字典 210/210 数值相同。此转换没有缩放，原 one-way indices 也有传入。
- 177/177 的 canvas 明确标记 `world_units_reference`、`positionPrecision=approximate`。森林缺位置的 action program 被插值到 spawn→goal；路线时长和移动物体相位是示意数据，不是实际轨迹或输入录像。
- 门铃、入口图标尺寸与真实碰撞体不同，例如编辑铃 30×40、真实 ShotLatch 28×34；入口图标 30×53、真实角色 24×36。危险物和缩略图也有代理画法。
- 迁移输入优先顺序应是固定版本 `.tres/.tscn/.gd/JSON` 及其真实消费者，之后才是保留的 original 字典；编辑图层用于参考。新 decoder、Cell 绑定和依赖应版本化，不能凭图层外观认证。

## 可最小迁移的第一批来源

以下都是依赖较小的静态几何，可以优先作为地基迁移试件；**不是已迁移或新玩法计数**。所有原平台像素坐标保存在 JSON，均无 saw/ferry/thorn/danger 组件。

| 原资源 | 原 world_bounds 尺寸 | 平台数 |
|---|---:|---:|
| `micro_board` | 240×360 | 1 |
| `micro_step` | 360×440 | 2 |
| `micro_drop` | 360×440 | 2 |
| `safe_hub` | 1280×720 | 1 |
| `plains_micro_stool` | 120×380 | 1 |
| `plains_long_meadow` | 1080×420 | 1 |
| `plains_meadow_gap` | 470×440 | 2 |
| `plains_terraces` | 850×600 | 3 |

72 份 `.tres` 的直接 ext_resource 并集只有五个脚本：`platforming_module_definition`、`platforming_module_port`、`platform_thorn_definition`、`module_saw_definition`、`module_moving_platform_definition`。这是数据类型依赖，**不是可玩依赖闭包**。

真实实例化还需 `platforming_module.gd`、原移动平台／锯组件、PlayerTuning/Traversal/能力资源，以及实际玩家、碰撞、武器、奖励和呈现消费者。另有 **9 个资源 ID 的风铃机关由 `config/plains_shot_latches.json` 与 planner 外部安装**；只复制 `.tres` 会丢掉它们的玩法。Boss/enemy 也可能由区域消费者添加。

已有 `tools/prepare_extraction.py` 可建立 data-only 求值项目，复用 19 个 generation 脚本、7 个支持文件和 72 个资源；本轮没有运行它，也不把它当可玩运行时。

原 `module_reflection.gd` 已按 source world_bounds 反射矩形、端口、方向、刺面、移动轨迹并保留 entry/exit 身份与别名处理，可作为迁移代码参考。镜像不转置，仍需新证据，不能继承旧方向通过结论。

## 当前游戏与 Harness 是否相同

**部分核心代码同源，完整运行时不同。**

对 Harness provenance 的 870 项逐项只读验 SHA：870/870 仍符合其原记录。再对本地下载游戏比较，840 相同、30 不同、0 缺失。注意这组 840/30 是本地副本比较，不能写成与最新 main 的全量比较。

固定 main 的 player/combat/world/actors 目录 blob 另行核对，发现本地副本与 main 的三个差异；原文已重新读取、校验 blob，diff 保存在 JSON：

| main 变化 | 对机制的实际影响 |
|---|---|
| `jump_ability.gd` 新增 `reconcile_capacity()` | 暂停换装时立即缩小 `_air_max`，增容量不免费恢复本次飞行跳数 |
| `action_resources.gd` 新增 `reconcile_capacity()` | 暂停换装时将 `_flight_cap` 与当前枪数夹到当前 max_air_shots |
| `traversal_ability.gd` 新增 `has_capability()` | 查询独立 double/wall/hook 权限；装备不授予这些核心能力 |

这三份文件的原 advance、跳跃、射击相关主体与数值常量没有在 diff 中改变。固定装备、固定能力的普通 jump/recoil 基线静态未见因此改变；暂停换装与容量变动生命周期明确不同。这是静态范围说明，没有实跑等价认证。

此外，`weapon_action_runtime.gd` 的 main 与本地相同，和 Harness 不同：Lv1 `recoil_bomb` 增加 accepted shot identity/airborne 记录，并可实际触发 mechanism receiver；机关命中不授予敌人资源。不能把整个武器行为矩阵写成一致。

已核对相同的固定 main 文件包括 Motor、PlayerController、ShootAbility、PlayerProjectile、ActorResources、ShotLatch、PlatformingModule、移动平台／锯、player tuning、Traversal 资源与 player 场景。其余本地 29 个变更文件列在 JSON 的全量比较中，尚未逐个证明无功能影响。Harness 入口、能力 adapter 与正式游戏生命周期也有范围差别。

因此，后续正式 Module 应绑定准确运行时。即使只迁反冲平原，也需固定装备/能力范围、记录完整依赖，再做有限真实复验；**不能把旧 `12f6cb0` 的通过记录改标成 `879b39e`**。

## 新地基还缺什么

72 份原资源中，world_bounds 的宽和高同时为 128 倍数的有 **0 份**。全部旧参考的新地基资格仍是 UNKNOWN，需要独立处理：

1. 选完整矩形 Block 占地；保留 Cell 原像素形状，显式解决新的边界端口，不能假设补空白就自然吻合。
2. 将旧角色站位与行进 direction 转成真正的边界格面中心端口、外法线、AIR/ROCK/ONE_WAY_PLATFORM、INPUT/OUTPUT/INOUT。
3. 测实际完整有向 Route 矩阵，含自关系；区分原路线草图与物理可达，区分能力集合与暂态资源／机关状态。
4. 认证未用端口的真实物理封口及支持的封口组合，保持所需内部路线。伤害面不充当封墙。
5. 绑定全部真实机关、奖励、敌人、动态包络和原始运行时；镜像另验，不把方向变体算新基础模板。

本轮只修改这两份 inventory 文档：0 游戏文件修改、0 Module 修改、0 Godot/物理运行、0 新认证、0 commit。精确来源可用性与尚缺的认证分别保留，没有把盘点结果写成迁移成功。
