# PCG-DYNAMIC-04：真实动态机制独立审计

审查者 `ability_contract_audit`，实现者为父代理及 `composable_worker`。只读审查游戏源、研究适配器与冻结数据；允许写入本报告和 `evidence/dynamic-audit/`，不修改worker、核心或算法，不占用Godot租约。采用项目 `gameplay-reviewer`。实现前接口意见与最终独立数据复算分别记录；审查者没有启动Godot、浏览器、操作试玩或观看录像。

已保存18个相关源/测试文件及SHA-256，见 `evidence/dynamic-audit/source-index.json`。游戏原动作源为12f6cb；前轮核验其动作/资源路径到54573a未变，不在本轮臆造新的运行版本。

## 最终结论：限定研究结果 ACCEPT

**未发现阻断当前限定研究发布的虚假物理成功。** 原始真实对象/伤害回放、目的词、载人证据、随机输入与区域实际几何的独立复算通过。四个有真实便宜替代路线的模块、低相位容错模块仍需REWORK，不能因为技术审查通过而晋级为高质量量产内容。趣味、完整随机地图、正式区域Bible、Runtime成本、用户与设备认可均未验证。

独立脚本 `evidence/dynamic-audit/review_final.py` 退出0，回执 `final-review.json` 的 `failures=[]`；逐批输入/输出/执行记录哈希及统计见回执，命令输出见 `final-review.log`。脚本重新实现动作词、连续性、载人、低成本偏序和统计，逐批读取大JSON，不调用引擎。区域部分既调用已冻结合同检查，也另外独立检查真实岩块/端口尺寸、上升量、同列竖缝、接触墙并集高度与禁止对象，避免把标签当证据。

| 范围 | 独立复算结果与解释 |
| --- | --- |
| dynamic-search-v3 | 16运动提案、584校准回放，313无接触稳定出口，共600物理case；按四族统计与报告一致。校准档案确只按出口归档，最终评价另外按purpose筛选；313不是高质量模块数。 |
| dynamic-evaluation-v1 | 507条holdout/扰动/等待消融 + 196条替代策略 =703；所有被记为成功的原始帧无contact、无HP下降、无return，末帧真实速度≤1且出口稳定≥6帧。各族/各模块safe_stable与purpose_valid重新计算，全部吻合。 |
| 真实目的 | 非载人族必须实际词相等且首末关键事件间无grounded；hook只在进入hang/contact_kick计入，wall用实际wall_kick事件。carrier显式canonical目的为上船ground_jump、离船ground_jump，再air_jump或recoil，未借旧metadata少记一次地面跳。 |
| 真实载人 | 每个目的通过rollout有真实support_id=carrier的零轴帧与引擎platform_velocity。最低观测134零轴支持帧、256.68wu载人位移、106个速度>20wu/s的支持帧，远超设置的30/100/20门槛；并非站附近。载人成功允许合法地面恢复，不冒充连续空中挑战。 |
| 相位与消融 | 独立Random(741901)重建每一次draw，与全部label/实际input initial_phase完全匹配，未落在4个校准相位；108对clean/no-phase-gate实际几何与相位相同，删改仅为指定等待条件。mild/moderate另抽相位，所以不是同一相位的纯噪声配对。每个正式候选只有1个动态对象，不能外推多机关联合相位覆盖。 |
| 伤害校准 | 原始smoke中saw/thorn分别真实提交HP5→4、返回一次、epoch+1、同帧clock不倒退；99伤害导致HP0/fatal且无return。normal Controller与priority driver的完整frames逐项相同。未把submit受理等同实际扣血。 |
| 区域真几何 | region-sky-v1：16运动提案、10区域几何回放、128扰动，共154物理case；8个词与连续性通过，实际上升240–428wu，rock/port尺寸、墙缝与连墙高度均符合指定输入，禁止的thorn/saw/carrier实际不存在。不是更名/换色。 |
| 区域反证 | `thorn_wall-m3-v0`虽稳定到出口但中途grounded从91帧开始；`sky-mixed-m4`在142帧grounded。两者确从最终8个中剔除。三条混合成功实际词如下，不按能力标签计数。 |
| UI与浏览器记录 | 已检查既有17个浏览器完整回放的状态与零错误记录，以及12+5个UI对照回执，共7404帧，safe/HP/位置误差均吻合。该结论是已有自动化回执审计，审查者没有亲自运行浏览器或观看4段视频，不签视觉/设备/趣味。后续metadata重打包须保留自己的新回执。 |
| 原件 | 870份受保护原始文件逐SHA检查，0漂移；未发现为实验改Motor、伤害政策或恢复规则。 |

三条已实际执行且无关键区间落地的混合链：

- `sky-mixed-m0`：wall_jump→hook_bounce→air_jump→hook_bounce→recoil→air_jump，上升412wu。
- `sky-mixed-m3`：wall_jump→hook_bounce→air_jump→hook_bounce→recoil→hook_bounce，上升364wu。
- `sky-mixed-m5`：wall_jump→recoil→air_jump→hook_bounce→air_jump→hook_bounce，上升240wu。

| 族 | clean目的通过 | mild目的通过 | moderate目的通过 |
| --- | --- | --- | --- |
| thorn_wall | 3/3静态 | 27/36 | 13/36 |
| hook_saw | 36/36 | 36/36 | 27/36 |
| carrier_double | 25/36 | 30/36 | 21/36 |
| carrier_recoil | 36/36 | 36/36 | 34/36 |

低成本反例复核与summary一致：12个模块中4个有较低能力集合或同能力但较少关键动作的真实成功策略，共12次成功替代测试，不夸大成12种不同路线。`thorn_wall-m2-v0`可普通跳/双跳或纯墙跳过；三个carrier_recoil均可删离船普通跳，只保留上船与反冲。它们已保留在数据/警示中，不以堵掉每条替代路线换取好看的必要性数字。其余未发现不证明能力必需。

尤其不能用均值掩盖 `ferry-v4-double` 的clean仅1/12（mild9/12、moderate6/12），也不能把 `thorn_wall-m2-v0` moderate稳定到出口9/12、目的词0/12算设计成功。二者属于诊断/返工候选。扰动相位不同，不能据轻扰动比clean高就声称误差提高成功率。

### 已发现并界定的metadata差异

旧region输入在扩大本局可用能力时更新了`capabilities`，却沿用动作提案的`capability_contract.ids`。前5个墙跳区域候选的提案contract只有4项，真实actor snapshot与实际capabilities为全部6项；三条混合候选没有该差异。引擎绑定与purpose均使用正确的实际能力，所以8个真实成功不因此失效；旧contract不能作为本次实际能力快照。

实现者已接受：旧原始输入/输出不改；未来生成器及派生交付保留旧`proposal_capability_contract`并重建实际contract，附纯metadata修复说明，并保证capabilities、几何、控制、recorded_frames逐项不变。该修复不应借重跑覆盖原件；重打包的浏览器验证由实现者另留回执。本独审未把旧字段签成实际快照。

当前报告的数据口径与边界基本准确。区域编译后的高质量体验仍需真人实际试玩与多seed机制对照，不能把101种词、17个回放或全部相位通过升格为长期丰富度、苦痛之路级设计质量。

## 正式对象与最小接入

| 对象 | 实际语义 | 最小真实接口与应记录证据 |
| --- | --- | --- |
| `ModuleMovingPlatform` | `AnimatableBody2D`，priority −100，读取module.clock，用sync_to_physics交给引擎；不手动搬角色。definition的start/finish/size是module本地坐标。 | 真实模块/definition与有效shape。记录floor碰撞器身份、get_platform_velocity、全局位移、normal_velocity与相对漂移；至少一段零轴随船。坐标接近不足以证明上车。 |
| `ModuleSawHazard` | priority900，正弦动态圆锯；角色矩形与锯圆以相对运动段做swept_contact；伤害经FrameDamagePolicy，非直接die。 | definition、module、setup_damage(controller,policy,life)。记录当前/前一锯位置、真实module.clock、接触与请求/提交、HP/epoch。不要误用world/SawHazard实例：它的消费路径是直接actor.die。 |
| `PlatformThornDefinition` | surface_id、真实platform_index、face、offset、length、depth；danger从宿主面向外推出，有四个危险方向。 | `is_valid(platforms)`通过后用danger生成真实ENVIRONMENT `DemoContactEmitter`。应保留宿主索引与面，不能用悬空矩形或最近平台字符串代替附着。 |
| `DemoContactEmitter` | priority900，角色体积膨胀后的相对线段碰撞、唯一exposure/pulse事件；支持fall_plane特殊语义。 | policy/controller/source_id/kind/amount/half_size/interval。surface thorns不能误设fall_plane；否则DamageBoundary可能把实际危险抑制。 |
| `FrameDamagePolicy` | priority1000，真实HealthState提交；同帧每target只选一条，ENV优先，再伤害量、source/event字典序。 | lifetime、register_target(player,health,true)成功、register_player_controller、fatal/return/batch signals。日志以batch_resolved的实际result为准，不将submit=true当扣血。 |
| `SegmentRespawn` | 全身净空、三脚支撑与危险区域检查后激活静态anchor；return_to_anchor调用选择性返回并invalidate_actor。 | configure、danger_bounds、add/activate_anchor返回值；ENV return接回此对象，成功后policy.protect_player。实际返回前后位置、HP、clock及epoch应完整记录。 |

`PlatformingModuleDefinition.is_valid()`还要求有效ports/anchors、world_bounds容纳全部动态envelope、spawn/静态anchor避开锯和ferry全包络。若研究适配器只把PlatformingModule作为类型化clock host，没有走完整definition消费者，应明确这一范围；真实对象复用不等于完整模块数据已获正式准入。

## 必须保持的时序

正式物理顺序是module.clock（priority −200）→moving platform（−100）→角色controller/Motor（通常0）→hazard sweep（900）→damage commit（1000）。角色每帧只能执行一次真实Motor.step/move_and_slide。snapshot需要发生在伤害批次之后，否则会把当前撞击的HP/return漏掉。

SceneTree.physics_frame信号在节点_physics_process之前发出。沿用旧静态worker的“await physics_frame，立即controller.physics_tick”会让角色先于module/carrier更新，偏离正式顺序。最小修复是独立priority0 driver注入Router与调用controller.physics_tick，禁用controller自动tick防双算；在1000之后observer或physics结束的process_frame采样。不可用手工修改平台坐标+角色坐标制造搭乘，也不可在同帧另外调用一次move_and_slide补偿。

两个时钟都要保留：module.clock控制几何相位，policy.clock控制接触脉冲/保护。初始phase是周期比例，saw的period单位秒；ferry的period是2×(travel+dwell)，其phase也以完整周期归一。fixture warmup会推进时钟，输入initial_phase不等于第一次正式控制帧的实际相位，必须记录真实开始clock与对象位置。用绝对秒相位和归一phase混用会产生看似覆盖实则重复的测试。

若同时有锯和carrier，仅测试它们同取0/.25/.5/.75会只覆盖对角线，漏掉相对相位。应明确独立相位网格或独立holdout采样；也要测试不同到达时间而不重置模块时钟。状态反馈允许读取实际可见对象位置，不应靠隐藏seed选硬编码成功输入。

## 真实扣血、返回与epoch

`FrameDamagePolicy.submit`校验token、actor_epoch、health_epoch、event/source、健康状态与保护；通过只入队。resolve先给所有选中target提交HP，再决定fatal或environment return。非致命ENV伤害发返回信号；fatal先lifetime.end，再发fatal，不能零HP后又返回。实际提交结果才可作为伤害证据。

`controller.return_to_segment`保留HP、stamina、cooldown和stage services，清输入、运动、jump、projectiles与行动资源，session_id递增；`SegmentRespawn`再invalidate_actor。不要用reset_at代替，因为那会恢复legacy health。环境返回应保留module.clock/锯轮/carrier的现有相位，不重新开始同一安全周期。返回后policy.protect_player默认0.6秒，初始正式场景也调用保护；因此HP未变不能推断没有危险接触。成功率若定义为无接触，需独立记录contact；若定义无扣血，应把保护窗口和返回次数一起报告，避免保护硬穿冒充无伤。

锯轮/emitter遇actor_epoch变化，会把previous_actor/previous_relative重置到当前实际位置，防止把teleport当扫过路径。不要每帧重置这些变量，否则真正高速接触会漏判。日志应同时记录request携带的旧epoch与commit/return后的新epoch，而非因回调顺序把合法提交误判为陈旧事件。

entry必须有真实安全支撑与体积净空。危险检查至少包括static dangers与锯全envelope；正式definition还会排除ferry包络。不能选一个只在当前相位安全、下一帧又被carrier/锯覆盖的恢复点。返回后若没有安全anchor，应保留失败并停止，不能直接把角色写回任意坐标。

## 必备正负校准

1. 正常控制下踏上真实carrier，零轴随船，观察非零platform velocity和小相对漂移；下船后在静态接收台稳定。不要用body位置差或grounded单项作为搭乘证据。
2. 在保护期后真的撞静态thorn和移动saw，观察真实ENV提交、HP5→4、actor_epoch+1、回安全entry、module.clock不倒退；旧请求再提交应拒绝。
3. 高速角色/锯交叉的中间帧只有sweep命中时也必须提交；相反，epoch变化的teleport不应构成跨场景sweep。
4. 同tick两个环境源/环境加怪物只按生产policy提交选中事件；致死伤害结束lifetime且不返回，不把一次接触源计数直接转成HP减少次数。
5. 真实pause冻结module和carrier，resume延续相位；若本轮未测pause，就把它保留为源语义，不签运行通过。

旧 `tests/dynamic_module_tests.gd` 的boarding/neutral carry/连续性断言很有价值，但fixture会把max_jumps改为测试值、max_air_shots设0，且主轨迹只做独立几何sweep，没有真实hazard damage。不能原样复制这些调参或将历史测试当本游戏默认能力实测。`continuity()`用手工DamageRequest校验返回生命周期，能证明政策接口，不能代替本轮真实锯轮接触提交。

## 三种体验假设与最便宜反证

| 假设 | 玩家需要做的判断 | 最低成本替代/消融 |
| --- | --- | --- |
| 墙+double+荆棘压力带 | 安全墙段之间选择离墙时刻、空跳窗口与重新贴附的落点；失败后有可读的恢复点。 | 只反复墙跳不空跳；从下方走/普通跳绕过；在接收台提前落地重置；保护期或扣血硬穿。若替代更好，保留多解或淘汰无价值动作，别一律封死。 |
| hook+移动锯口 | 在安全观察/挂点位等待，判断退让相位，再穿过锯口并空控接收。 | 等一周期后普通跳/走；跳过hook直接反冲；绕出锯包络；在安全挂点无限等。先区分有界观察窗口与无意义拖时。 |
| carrier上/下车+recoil或double | 选择登船窗口、在中立轴下判断离船时点，利用离船轨迹去不同接收台。 | 岸上直跳/反冲；等最近点走下船；全程不需要离船技巧；以移动台落地自然恢复资源（合法，但必须记录，不能误作连续空中能力恢复）。 |

合格候选应呈现不同的观察、等待、路线/落点选择与资源后果。动作次数、saw相位遍历、几何hash与一次确定策略成功只能证可行/覆盖，不能签“有趣”“能力必要”“高手无捷径”。需保留目的打法与真实便宜替代的witness，再由独立实际试玩/录像审查淘汰没有新增判断的候选。

## 当前验收状态

源码/接口审计与本轮冻结数据独立复核完成，限定研究结论ACCEPT；原始metadata差异已明确且交付派生修正由实现者采证。趣味、视觉、正式游戏消费者、Map Notes、Runtime成本、用户/真机认可均未验。前轮公开V2与旧静态噪声统计不能作为本轮动态测试结果。
