# M35 与 M01：精确机制交接

只消费历史 **1.1.0**。冻结内容来自 map-gen PR3 `93c5221a9708d079c2864f3c14b415e81bb5de07/reference_package/fixtures/success/`，同时与该提交 GDScript 0.3.0 `validation-930001/actual.json.gz` 完整 content_store 相等。主游戏目标是 PR127 **`e7d703f47c97f09bd5c5d48e24f0a400c958ad40`**，不是旧原生资格宿主。完整版本/SHA 见 [frozen-checks.json](../../../evidence/runtime-integration-930001/frozen-checks.json)。

坐标约定：下表“源”为 ZIP 原始 compiled，“局部”为已物化占用矩形坐标。`world = origin_blocks*128 + local`。`source_affine` 仅追溯源变换，**不再对已物化点应用一次**；尺寸/位移向量不做原点平移。不从 main 同名 Module 读取内容，也不把源 module.tscn 叠加到物化几何上。

## M35 / game-plains-ferry-gears

- 完整内容版本：`sha256:18e0578b0631239884f0ff9bb598b04867396bcbe3988c036b512ebe32e092b3`。
- 源文件 `module_pack/modules/game-plains-ferry-gears/compiled-content.json`；源原件 SHA `dd1d2679a7390fa1b3bea2acd36d21c542ef39eebd31e5cb380f049650c2d533`。
- [完整原编译内容](../../../evidence/runtime-integration-audit-20261103/samples/package-1.1.0/game-plains-ferry-gears.compiled.json)；完整物化 [M35.content.json](../../../evidence/runtime-integration-930001/focus/M35.content.json)，逐字节匹配上游独立 `content/M35.json`，SHA **`99de30fea7541920ba0d024372927dcee387c7da453916d9e3b05a7093214d1c`**；完整 [instance/Ports/Routes](../../../evidence/runtime-integration-930001/focus/M35.instance.json)。
- 源 bounds `[0,342,1024,768]`，local bounds `[0,0,1024,768]`，source_affine `[1,0,0,1,0,-342]`。实例 origin_blocks `[12,9]`，world 原点 `[1536,1152]`，未镜像，entry/exit/C 全部连接，无封口。
- 完整性：4 固定平台、one_way_platform_indices=`[2]`、2 linear ferry、1 hazard、1 saw；没有敌人、奖励、latch、HQ，不得删危险物凑可支持切片。

| 内容 | 源坐标 | 物化局部 |
|---|---|---|
| 固定平台 0 | `[0,950,180,40]` | `[0,608,180,40]` |
| 固定平台 1 | `[620,700,120,40]` | `[620,358,120,40]` |
| 固定平台 2（可穿） | `[320,398,640,40]` | `[320,56,640,40]` |
| 固定平台 3 | `[960,438,64,24]` | `[960,96,64,24]` |
| ascent_0 中心 start→finish | `[250,932]`→`[550,792]` | `[250,590]`→`[550,450]` |
| ascent_1 中心 start→finish | `[830,630]`→`[500,490]` | `[830,288]`→`[500,148]` |
| hazard / danger_0 | `[44,1000,912,40]` | `[44,658,912,40]` |
| saw / relay_gear 中心 origin | `[512,710]` | `[512,368]` |

两个 ferry 各自 size=`[120,24]`，travel_duration=3s、dwell_duration=1.5s、initial_phase=0；没有 trajectory_kind，使用原生线性定义，不能补成 `clockwise_ellipse/v1`。周期 `2*(3+1.5)=9s`，令 `e=fposmod(module.clock+initial_phase*9,9)`：0..1.5 停 start，1.5..4.5 线性去 finish，4.5..6 停 finish，6..9 返回。t=0/3/4.5/7.5 时 ascent_0 中心依次 `[250,590]`/`[400,520]`/`[550,450]`/`[400,520]`；ascent_1 为 `[830,288]`/`[665,218]`/`[500,148]`/`[665,218]`。平台顶面是中心 y−12，玩家站立中心还需减其半高18，不能把平台中心当脚下台面。

锯的 `travel=[0,240]` 是振幅，不是终点；radius=20、period=4.8s、initial_phase=0、damage=1、contact_interval=0.7s。中心 `origin+travel*sin(TAU*(module.clock/4.8+phase))`；t=0/1.2/2.4/3.6 的局部 y=368/608/368/128。圆锯与24×36身体用原生相对扫掠接触，不以整个运动包围盒持续扣血，也不扩大半径。world 初始中心 `[2048,1520]`。

静态 hazard 不是实体平台。1.1.0 `module_loader_v3-1d72f57d63dd.gd:97` 对 `world_static_hazard_records()` 创建 `DemoContactEmitter`：ENVIRONMENT，默认 amount=1、interval=0.7s，本地 source `danger_0`。锯和危险区均向**同一** FrameDamagePolicy 提交带 lifetime/token、actor/health epoch、exposure/pulse 的请求，间隔按 `policy.player_clock()`，由宿主统一结算无敌/去重；不是每帧直接写 HP。

注意：最新 `PlatformingModule.world_static_hazard_records` 会把本矩形推导为 `fall_plane`，但 1.1.0 loader **没有将该 role 写入 emitter.fall_plane**。不能自动启用 `DamageBoundary.has_landing_below` 抑制或改成跌落传送来代替包原伤害语义；如主游戏拟采用其全图跌落策略，应单独说明行为差异并定向验收。

| Port | 局部接口 / 内部接岸标记 | 实际邻接 |
|---|---|---|
| entry | `[0,576]` / `[24,590]` | C052 → M41/L，ROCK，world `[1536,1728]` |
| exit | `[1024,64]` / `[1000,78]` | C051 → M34/exit，ROCK，world `[2560,1216]` |
| C | `[576,0]` / `[576,38]` | C008 → M04/B，ONE_WAY_PLATFORM，world `[2112,1152]` |

此模块保留 6 条有向 Route，但不等于新宿主已执行。C008 当前 Provider 明确不支持；M34/M41/M04 也有尚未接入内容，所以先验收完整 M35 单模块，再扩真实邻接，不能从邻居删掉机关/怪物以取得通过。

## M01 / game-plains-windchime-lesson

- 完整内容版本：`sha256:b2ee44df5422a7b4dd9be1358a075c46cefb00992de802607389f6f94ecfa433`。
- 原件 SHA `0846f23881d9106d68032323b6278e4f79550e33f1cb73cf4e920323039da942`；[完整原编译内容](../../../evidence/runtime-integration-audit-20261103/samples/package-1.1.0/game-plains-windchime-lesson.compiled.json)；物化 [M01.content.json](../../../evidence/runtime-integration-930001/focus/M01.content.json)，SHA `b1dd1d6a46a609d56a1673a969b361fb17a095986093e948b22dc35a8936d18e`；[完整实例](../../../evidence/runtime-integration-930001/focus/M01.instance.json)。
- 源 bounds `[0,76,512,384]`，source_affine `[1,0,0,1,0,-76]`。origin_blocks `[0,0]`，未镜像，只连接 exit。entry 实体封口 `[0,128,32,128]` 正好匹配 PR78 定向夹具；封口原状态仍 NOT_RUN，不补认证标记。

| 内容 | 源坐标 | 物化局部 / 此实例 world |
|---|---|---|
| 出生候选（身体中心） | `[48,282]`、`[64,282]`、`[140,282]` | `[48,206]`、`[64,206]`、`[140,206]` |
| entry 接口 / 接岸 | `[0,268]` / `[24,282]` | `[0,192]` / `[24,206]`；均不能作封口后的出生 |
| 地面 | `[0,300,480,40]`，`[480,300,32,24]` | `[0,224,480,40]`，`[480,224,32,24]` |
| bell / gate | `[170,235]` / `[320,80,24,220]` | `[170,159]` / `[320,4,24,220]` |
| exit 接口 / 接岸 | `[512,268]` / `[496,282]` | `[512,192]` / `[496,206]` |

`latches[0].id=windchime_plains_windchime_lesson`，kind=safe_lesson，open_seconds=0：初始闭门，原生弹丸实际命中铃后永久打开。保留玩家原生射击、冷却、命中与生命周期校验，不用“靠近自动开门”替代，也不直接设置 latch.is_open。

PR78 的三候选均在原生24×36身体、原物理/射击配置下站稳，实际一枪开门，走至约 `[495.92,205.93]`；未射铃停在约 x307.99。已有精确 [Godot 观察](../../../evidence/runtime-integration-audit-20261103/godot-probes.json) 和脚本 SHA，不在本轮重跑旧宿主。源码点和零点不是已证出生。

**配置匹配的进展与边界**：原来未拿到图的封口快照，现在已精确核对；但该见证仍来自12f6cb0/Godot4.7.2，不是 PR127。M01 在本图 `routes=[]`：entry 封后生成器裁掉原 entry→exit，start_departure=exit 仅为 STATIC_GRAPH_ONLY。出生候选到 exit 的实际路径不能因此宣称已成为图内认证 Route。

实际连接是 **C001：M01/exit→M02/R**，ROCK，world `[512,192]`。新宿主必须分别验收候选稳站、实际射铃开门、身体到出口接岸，再在 M02 完整适配后验收跨 C001；M02 有两载台、可穿载台配置和空怪，当前不能签真实跨缝。保留 `anchors.player_spawn=UNRESOLVED`，直到下游以此版本/封口/身体绑定新出生证据。

## 新适配器的最小验收依赖

PR127 Provider 当前拒绝 M35 hazard/saw/linear、M01 latch；这不是 Module 运行失败。下游提供**精确适配 commit、实际引擎、适配版本、冻结 map/content、spawn binding、能力/物理快照**后，map-edit 再定向复验，不预签兼容。

- 时钟沿当前 Stage 的 `state.clocks[instance_id]`，建树前恢复；模块 pause 时不推进。原生处理优先级 module=-200、carrier=-100、hazard=900；载台由 AnimatableBody2D/原 Motor.step 承载，不能手动平移玩家或多调用 move_and_slide。M35 两台/锯无铃控，不新增另一份壁钟。
- 以完整 M35 做两台各阶段承载/上下落、危险区实际一次及持续接触、圆锯扫掠/离开再进入、pause/restore/死亡 epoch/退出后旧请求拒绝；固定台原索引保持，封口只追加一次。
- M01 做三个候选（或明确选择其一）、未射击负对照、真实射击正例、永久开门、暂停/换图取消和恢复；先到接岸，跨邻居单列。
- 复用主游戏已有玩家、policy、钱包、lifetime、状态；包声明 policy/lifetime/wallet 保留，但这两个例子不发奖。保留实例/本地对象 ID，不用 get_instance_id/数组全局下标作为持久身份；damage/restore 继续绑定 PR127 的三层身份，不把 session/token 放生成指纹。
