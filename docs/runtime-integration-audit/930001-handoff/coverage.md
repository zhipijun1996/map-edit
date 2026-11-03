# 930001 宿主机制覆盖表

绑定 gunman-rush `e7d703f47c97f09bd5c5d48e24f0a400c958ad40`、map-gen `93c5221a9708d079c2864f3c14b415e81bb5de07`、模块包 **1.1.0**。完整 46 实例覆盖 20 个精确 Module 版本。本表由冻结数据抽取，按机制归类；不是逐实例装载成功清单。

原 Provider 非空拒绝项：`wall_platform_indices/hazards/thorns/saws/hooks/latches/enemies/reward_sites`；`approved_hq_cells` 非空也拒绝；未知扩展字段拒绝；moving_platforms 只接受 `clockwise_ellipse/v1`。当前只有 M16/M18/M21 切片有宿主执行证据，M38 的同类型椭圆只能称 schema 可表达。

## 机制组与适配缺口

每项对象的完整稳定 ID、完整内容版本、字段索引/原值、关联 ID、服务需求、原资格报告 SHA 均在 [mechanism-coverage.json](../../../evidence/runtime-integration-930001/mechanism-coverage.json) 的 `groups`；下表实例可经末表定位版本。服务名是已有宿主职责说明，不是新增协议/全局服务。

| 机制 / 对象数 | 实例 | 编译字段与原生语义 | 宿主缺口 / 服务 |
|---|---|---|---|
| `safe_lesson` / 1 | M01 | `latches`；原生弹丸命中风铃开启实体门；open_seconds=0 为永久开。 | Provider 当前拒绝；projectiles, player, lifetime |
| `linear_ferry` / 27 | M02, M04, M05, M07, M08, M09, M12, M14, M15, M17, M32, M34, M35, M36 | `moving_platforms`；双向线性中心轨迹，停留/行程/初相，默认随模块时钟；不能套椭圆字段。 | Provider 当前拒绝；player_motor, module_clock, lifetime |
| `native_one_way_carriers` / 6 | M02, M04, M09, M15, M32, M36 | `approved_hq_cells`；仅 ids 指定的移动体 CollisionShape 为可穿，不能由固定台索引代替。 | Provider 当前拒绝；player_motor, module_clock, lifetime |
| `enemies` / 18 | M02, M04, M06, M09, M11, M13, M15, M19, M22, M25, M28, M32, M33, M34, M36 | `enemies`；definition 指定原种类；本地放置ID/初始冷却/命中回充/击败/接触时序保持。 | Provider 当前拒绝；player, policy, lifetime, enemy_factory, projectiles |
| `group_motion` / 11 | M05, M07, M08, M12, M14, M17 | `approved_hq_cells`；一项有效射击原子切换 targets 运行状态，保留各自时钟；access 是额外接收铃。 | Provider 当前拒绝；projectiles, player, lifetime, module_clock |
| `clockwise_ellipse/v1` / 2 | M16, M38 | `moving_platforms`；椭圆中心/半径/周期/x_sign，保持物化镜像后的方向。 | 仅椭圆 schema 支持；M16 有受控执行，M38 未签；player_motor, module_clock, lifetime |
| `timed_gate` / 7 | M20, M22, M23, M25, M31, M37, M39 | `latches`；open_seconds 定时开门，保留 return_access 与任意侧接收语义。 | Provider 当前拒绝；projectiles, player, lifetime, module_clock |
| `reward_sites` / 11 | M20, M23, M24, M41, M42, M43, M44, M45, M46 | `reward_sites`；玩家落地且中心在 region 时调用原生领取；position 是展示点，amount 是现有金币数。 | Provider 当前拒绝；player_motor, player_health, wallet, lifetime, module_state |
| `closed_polyline_loop/v1` / 1 | M24 | `moving_platforms`；按原闭合折线及周期运动；carrier 可由指定铃启停，不重置相位。 | Provider 当前拒绝；player_motor, module_clock, lifetime, projectiles |
| `hazards` / 3 | M24, M34, M35 | `hazards`；源危险矩形；1.1.0 接触发射器默认 ENVIRONMENT 1HP/0.7s，非实体平台。 | Provider 当前拒绝；player_health, policy, lifetime |
| `toggle_ferry` / 1 | M24 | `latches`；射铃切换目标 carrier 的 running 状态，保留 motion_clock。 | Provider 当前拒绝；projectiles, player, lifetime, module_clock |
| `thorns` / 12 | M28, M41, M42, M45 | `thorns`；按 platform_index/face/offset/length/depth 绑定实际平台表面，默认原生接触伤害。 | Provider 当前拒绝；player_health, policy, lifetime |
| `hooks` / 1 | M29 | `hooks`；kind=bounce 是原生反弹果，不是固定悬挂锚；保留 source_id 与反弹/恢复语义。 | Provider 当前拒绝；player_traversal, lifetime |
| `original_region_chests` / 1 | M29 | `original_region_chests`；原区域宝箱 tier/resources/领取状态；M29 同时有coin和note，不能当 reward_sites 金币箱。 | Provider 当前拒绝；player, wallet, lifetime, meta_progression, region_state |
| `refresh_carried_enemies` / 1 | M34 | `refresh_carried_enemies`；enemy 引用已有敌人、carrier 引用已有平台，不额外生成怪；warmup=2 只初始化位移观察样本。 | Provider 当前拒绝；player, policy, lifetime, enemy_factory, module_clock |
| `saws` / 7 | M35, M41, M42, M43, M44, M45, M46 | `saws`；origin+travel*sin(TAU*(clock/period+phase))；圆锯扫掠接触、独立脉冲去重。 | Provider 当前拒绝；player_motor, player_health, policy, lifetime, module_clock |
| `reward_pair` / 3 | M43, M44, M46 | `approved_hq_cells`；指定 reward_id 真正 COMMITTED 且金额>0 后切换两扇门；初始开口、延迟防夹和保存恢复均保留。 | Provider 当前拒绝；player, lifetime, wallet, reward_commit, module_state |

## 接口与业务绑定

| 项目 | 真实范围 / 剩余工作 |
|---|---|
| 静态平台 / 固定可穿索引 | Provider 已表达，受控切片通过；其他实例的全部组合未执行，不能以此签所有 Module。 |
| 未用口封口 | 冻结结果共 40 个 `gear-seal/1`，作为实体几何单独追加一次，不写回平台原索引；全部原 `certified=false/NOT_RUN` 保留。M01、M24 定向结论见专项资料。 |
| 可穿 Port 接缝 | 9 条：C003/C004/C008/C011/C015/C021/C025/C026/C029；当前 Provider 只支持 ROCK 内部接缝，不能因有可穿平台组件便称已支持。M35 的 C008 也受此限。 |
| 单向权限 | M20/E、M23/E 是合法 INPUT，当前都未用并已封口，不是当前连接图的非法值；未来接入合法 INPUT/OUTPUT 内部接缝仍缺宿主限制，不能伪改 INOUT。 |
| 起点 | M01/player_spawn 仍 UNRESOLVED；PR78 固定候选证据与本图配置匹配，但新宿主出生/射铃/跨接缝尚待执行。 |
| Boss/终端 | M40/game-plains-boss-arena，role=boss，镜像，只有 entry 连接，exit 已封。boss_arrival 是 STATIC_GRAPH_ONLY，boss_encounter=HOST_BINDING_REQUIRED，boss_completion=UNRESOLVED；地形不等于已放 Boss/结算。 |

## 精确模块版本索引

下面是完整冻结输出的全部模块，没有从 main 拉同名内容。原件在锁定 1.1.0 ZIP 的 `modules/<ID>/module.mapnote.json`，编译内容同目录。

| 稳定 Module ID | 完整 contentVersion | 生成实例 |
|---|---|---|
| `game-plains-windchime-lesson` | `sha256:b2ee44df5422a7b4dd9be1358a075c46cefb00992de802607389f6f94ecfa433` | M01 |
| `idea-interface-s12-001` | `sha256:9d2244662c5fe81484ba67440de1400469b828c390f96ce38ec87e41f4174447` | M02, M04, M09, M15, M32, M36 |
| `game-plains-fork-paths` | `sha256:3b796ef52899c779c10d1f1eee55e3a3c18aedc4aa3ebc8c52ac381bbe6b9783` | M03, M10, M27, M30 |
| `idea-spec02-s12-001` | `sha256:86fbe2242a6250453f2be3fe14276bcb698d88b88226a34999506d720816df2d` | M05, M07, M08, M12, M17 |
| `workshop-macro-gate-brake-return-0` | `sha256:f2c78c40ffb898db69ff256ef31358ad0cc25d90a1530dfc861d394be08a3b13` | M06, M11, M19 |
| `workshop-one-shot-two-routes-1` | `sha256:4fd014e93e44920aacff3e4990882245ce400c4f747145acad1058c80b504874` | M13, M33 |
| `idea-plains-hq01-001` | `sha256:8c7d18090e298ee20bcdccfcb1c360b05f7460a5897ffbb8fb4c13c2ffcd6e95` | M14 |
| `idea-spec02-s11-001` | `sha256:afa52a8edc28fa26655f38815c277a21e68c56224c74c2bf125cfa580bd727ae` | M16, M38 |
| `game-route-junction` | `sha256:fbb52222ffe928c803c5cfd3107028e3ca86e8d2e44ae3aba1ea0ba987e12d40` | M18, M21, M26 |
| `batch30-block-n04-0-2` | `sha256:e1f079fad67ab89b1920da3a016b90a99c8ab553b330ce8944ae2e5fb3b207a2` | M20, M23 |
| `b31-n06-fourport-two-low-ingress` | `sha256:5aebe7b7a122a26eabb4f25a4a4324244b336552d1d450b41c1659a01b6c8c0f` | M22, M25 |
| `idea-orbit-choice-001` | `sha256:ee5cdeb5d7672eb1c9fbe9c502273114039a346817b8bf5ea7a7dd65045a1317` | M24 |
| `idea-plains-hq03-001` | `sha256:2ef8ba7aa09337a48422ac17fae4096b6c517c618ea910979b57d6e75c27c7cb` | M28 |
| `game-forest-exploration-modules-backlook-fruit-cache` | `sha256:670e89047187a3531c1e096e1820bf7a0f1ac74e1c43c91d8789f00c6abeaf10` | M29 |
| `idea-interface-s11-001` | `sha256:69e521575c88d5bce822eb037773288e3ad10efa4365192945185a0aa76f1dc7` | M31, M37, M39 |
| `game-moving-transfer` | `sha256:69e4b597822a6d9063905c928bcefb17e2064453fb04bfebfd842e3da7dfef19` | M34 |
| `game-plains-ferry-gears` | `sha256:18e0578b0631239884f0ff9bb598b04867396bcbe3988c036b512ebe32e092b3` | M35 |
| `game-plains-boss-arena` | `sha256:b11d7715850df541281f897be00d547b34fce0ef09262ec24ffb505f1064a083` | M40 |
| `idea-spec02-s13-001` | `sha256:e99c333410c8de43d1bb9b23ce2dc6190b6c66fb77bc15d486586e43c5da0246` | M41, M42, M45 |
| `idea-plains-hq04-001` | `sha256:163b7af98b953336d1d6dde95e62283c91f90517a057f5397b4ab7438c74edf5` | M43, M44, M46 |

## 证据怎么读

- E0：1.1.0 原报告/原生资格与 portable 场景装载。每个版本的精确报告 SHA、宿主和范围保存在 JSON.moduleIndex；它们不是 PR127 的新适配器证据。
- E1：[PR78 原生观察](../../../evidence/runtime-integration-audit-20261103/godot-probes.json)：M01 候选/射铃、M24 原领取对照及封口形状查询；运行宿主固定12f6cb0/Godot4.7.2。
- E2：[PR127 既有结果](https://github.com/zhipijun1996/gunman-rush/blob/e7d703f47c97f09bd5c5d48e24f0a400c958ad40/docs/worklines/mapgen_host_v2_02/results.md)：M16/M18/M21、身份恢复、原生与 Web 受控切片；不扩成完整46项。
- 各非空字段都需要目标适配器；本轮只读核对其拒绝原因。后续拿到精确 commit、实际引擎、适配版本和冻结输入后，再验证伤害/钱包/取消/恢复/物理组合；不拿 E0/E1 代签。
