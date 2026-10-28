# 任务 A：内容工坊第一阶段

交付 **6 个不同动作挑战家族、每个 2 种接口，共 12 份标准 Module**，另有 1 份从现有 Map Director 需求适配的载台上升样品。全部是候选，人工观感、人工试玩和生产认可均未获得。第一份 A1 已在其余家族完成前通过提交 `21f9512` / PR #2 交给 B；本报告是后续增量。

主目录：[`generation/workshop/v1`](../../generation/workshop/v1/)，合同与图在 `modules/`，6 段正常速度短视频及合集在 `videos/`。入口 `pcg/prototype/workshop/` 继承已有 PlainsEngine、原角色与资源、ShotLatch、ModuleMovingPlatform、SimpleRoomReward；入库继续使用 CandidateLibrary。没有新 Map Generator、运动模拟器或生产准入体系。

## 基线与边界

- 检查 main `b9318cf`、PR #1 实际代码 `b624752`；独立分支 `content/task-a-workshop`、独立 worktree。PR 以 PR #1 为依赖基线，未合并 main，未修改正式主游戏。
- 主游戏参考 main `26e7f2a`，实际查阅动作、枪械、资源、风铃与平台代码，SHA 在 `game-reference.json`。它不是本批物理版本标签。
- 实际物理为原固定 `12f6cb0` / 870 份保护原件，官方 Godot 4.7.2：二进制 SHA `8d106cbe6144c2dc7e881d61d2429c1a8a76e6b22ef48bd5e48dcf934953f71e`。未迁移或混称最新游戏机制；每轮完整源快照、输入、输出、失败与命令均保存。
- 公共合同、Map Director、共享 Harness 均未改。`restore_archive.py` 只增加新归档名称。多路线入库扩展沿用同一 CandidateLibrary `candidates/` 存储；旧单路线消费者跳过 `passed_scoped_multi_route`，不会将一组路线误认作可交换入口出口。
- 家族不是 Seed、标题或尺寸计数。商店、休息点、普通汇合点未计数。敌人续航是对已有 air-refund 方向的真实新地貌实例，不宣称首次发明该机制。

## 真实玩法

所有内容只授予 move / jump / shot_recoil，使用原一发空中弹药、冷却与真实恢复条件；敌人命中回充和接地恢复分别识别。没有注入金币、精力、弹药或额外能力。精力等状态保留在原始帧中，不按“落地”推断任意进入状态下回满。

| 家族 | 玩家观察与决定 | 地貌、因果与奖励 | 失败/回程与失效反例 |
| --- | --- | --- | --- |
| A1 尖刺窄通道 | 先看上下刺面与可见宝箱，再选低跳与略向下左射 | 同一反冲的横移和短暂抑制下落穿过限定身高带；24×36 全身体扫掠；宝箱受支持接触给 8 金币。两接口落点前缘 460/490、地面 438/418 | 原接触伤害/回退保留，失败不是免费重刷。另验原状态连续往返；反向用较短跳高，不能直接倒放。普通跳跃、越顶、去枪分别实测 |
| A2 主动截获载台 | 射铃启动后追赶未来落点，在实际承载中短暂稳定，再选离台时机 | 第一枪同时反冲和启动，第二枪命中同一机关的近侧接收器，暂停载台并离台。原承载/速度继承/碰撞，真实零输入承载。奖励 8；两接口目标 x=680/715 | 无被动乘到出口策略通过。错过载台后落到作者提供的下层地面，经真实动作重返并重试；原状态往返另测。只支持原启动/暂停，不支持任意改向/加速平台 |
| A3 短时风铃门 | 在空中选能命中铃、又将自己推向门的方向 | 用同一枪打开门并穿过。校准实际弹丸飞行 3–5 tick，命中至完整身体通过最多 26/31 tick；加 6 tick 容错并向上取整为 **0.55/0.65 秒**。封闭局部宝库，真实 12 金币 | 原防夹不变。深入等待实际关闭，再从内部命中原返回接收器，离开并由下岸攀回入口，连续验证；地面提前射击、去枪、普通跳跃反例。不是一帧操作 |
| 主动：悬檐下刹车入袋 | 先看岩唇下方凹槽，判断何时从下落改为向左制动 | 向右射击会清除下落速度并使身体转向，进入深缩进奖励袋；上方原岩体同时支撑入口和限制接近方向。两凹槽地面 438/468，奖励 10 | 漏接可落到下岸；通用回入口仍 UNKNOWN。专门搜索普通转身下落、从左右边缘绕落及去枪，不能将“有一枪”本身当目的成立 |
| 主动：一发资源两种落点 | 同时看到远低岸与高处金币，把本次空中一枪用于横移或升高 | 同一三端口实体地貌；A→B 低路线、A→C 高奖励路线，落地才由原组件恢复。高台 232/212，低出口 650/680，奖励 12 | 高处取宝后不再射击，实际下落汇入低岸；与去程升高关系不同。6 个有序对逐项声明；没有把未测反向标成互通 |
| 主动：敌人作为空中续航机会 | 读敌人威胁与高岸，先在空中实际命中，再决定第二发时机 | 真正提交伤害和原资源回充后，冷却结束再反冲到升高 320/340 的高岸；整个两枪间没有接地。敌人初始攻击冷却独立采样。奖励 16 | 漏打或漏接的完整再试尚 UNKNOWN，下面真实安全岸仍在；检查省略各枪、普通跳跃和一发直接斜/竖射。没有用落地充弹冒充命中充弹 |

所有家族的观感、手感、重复感与人工难度仍待反馈。上表的技术差异不是已获“好玩”评分。

## 校准、选择、留出与反例

`protocol.json` 在初始实验前固定六家族、每家族每轮最多 12 个几何候选、最多 8 次校准修订、校准 Seed、独立留出 Seed、12 次扰动样本和原 regular 门槛。几何/控制来自程序执行与原物理反馈，Codex 辅助提出关系、实现规则和分析；没有在线模型创作服务或训练。

最终 12 个 Module 对应的主挑战共有 **394 个预定测试案例**。clean 对静态内容 1 次、动态内容按既有规则 12 次；mild 为 ±1 tick / ±2°、moderate 为 ±3 tick / ±6°，各 12 次。受控载台开始在作者声明的停靠点，不将随机初始停靠位置冒充相位扰动；真实命中时间受独立输入扰动影响。敌人原初始攻击冷却另行采样。重复 clean 样本不宣称独立动态相位。

| 家族 | 两接口 clean | 两接口 mild | 两接口 moderate |
| --- | --- | --- | --- |
| A1 | 1/1、1/1 | 12/12、12/12 | 10/12、10/12 |
| A2 | 12/12、12/12 | 12/12、12/12 | 12/12、12/12 |
| A3 | 1/1、1/1 | 12/12、12/12 | 12/12、11/12 |
| 刹车入袋 | 1/1、1/1 | 12/12、12/12 | 11/12、11/12 |
| 三端口取舍 | 每接口两路线各 1/1 | 四路线各 12/12 | 12/12、12/12、12/12、11/12 |
| 敌人续航 | 12/12、12/12 | 12/12、12/12 | 11/12、11/12 |

这些是有限自动策略的工程样本，不是人类成功率或难度分数。门时间先由校准求解，再重新跑同一预定留出，未从留出选择几何。初始试探窗口和求解后的版本都保留，没有改旧版本时间。

反例使用相同几何，省略枪时保留时间间隔，另有 18 种普通跳跃、越顶、提前开门、被动载台、直接单枪和普通下落转身。**308 条去重反例**与发布实例的确切几何/初始状态绑定在 `counterexample-coverage.json`；敌人另补发布相位的反例，不把父候选相位记录自动当成固定实例证据。有限反例没有找到绕法，不证明必要性。

连续阶段 v1 **87/104，失败**：A1 第二接口反向跳高受顶刺限制，门后再攀升策略余量不足。原失败保留；另做新校准 104/104 后，预先声明新留出 Seed 261025940，修订版连续 **104/104**。求解后第二门窗口单独重绑 **26/26**；载台漏接→下岸→返回入口→再次启动/暂停/出关另有 **26/26** 连续留出。全程同一世界、角色、机关与奖励账本，不传送、不重建、不直接写资源。

接缝 **26/26**：把原 A1 接收岩体在接缝处切成相接的两个碰撞体，几何并集不变，穿越后再返回。新增实体面积 0。首轮 Definition 拒绝跨两个碰撞体的端口身体支撑，失败保留；试件把静态端口标记放在单侧完整支撑上，再测实际接缝。它只证明该具体碰撞接缝，不签两模块任意拼装，更不签整图。

## 来源、失败反馈和修订

`ideas.json` 原样保存 A1/A2/A3 原话、稳定 ID、human_idea 类型，解释与假设单独存放。`intake.py` 实际写入版本化来源文件，拒绝覆写旧修订；`source-aliases.json` 解析生成关系 ID 到稳定提案 ID，不增加创意数。`source-lineage.json`、`traceability.json` 关联来源、规则、版本、物理与后续修订。

- 首轮分岔高台可被普通大跳取得，**确实拿到奖励**；对应 `unexpected_shortcut` 观察会使提案选择权重变为 0。提高高台并重验后，带明确 resolved_by 证据才重新参与选择。不是换标题清除失败。
- 载台初版只主动抵消平台位移，缺少零输入承载证据；改为真正随台移动。远铃在瞄准扰动下漏中；使用原近侧接收器重做控制和全部留出。
- 敌人初版出生接触受伤，以及较早释放造成侧撞高台均保留；最终从更安全的腾空时序获得真实命中回充，不降低高度目标或改名 precision。
- 候选检索发现机械坐标放在 objective 中会被既有生态粗键忽略；新增多路检索在粗索引后严格核对机械约束。旧错误检索回执保存，新回执与防跨匹配测试单列。
- 未编造 boring、观感分数、手动尝试或批准。真实未来反馈可沿原 factory.feedback 手动报告/策展流程；视频观察与技术观察单独保存，不填假手感评分。

## Map 的实际调用与持久化复用

`map_demand.py` **导入既有 Director 的真实 ascent Challenge Specification**：升高 100、900×800、两端口向外、基础三能力、奖励 0。先原样保留，再显式记录从 bell_lift 到主动载台家族的本地需求修订；没有修改 Map 拓扑、布局或原 Director。它是隔离调用试件，不能称 B 已批准该家族替换。

适配内容修改接收岩体高程/水平承诺、未使用的后岸与下方恢复岸占用，并去掉非需求奖励。四轮保留：静态端口侵入动态范围；可省略离台射击；禁用占位门仍使真实边界超出 900；最终紧凑占用与远落点修订。每轮有界，不从留出抽幸运候选。最终 Map 需求版本 clean/mild/moderate 各 12/12，反例无成功，标准合同、候选入库、新建 Library 后磁盘检索通过；生成调用 1，检索复用时生成调用 0。详见 `generation/workshop/map-demand-v4/`。

普通候选使用原 CandidateLibrary.enroll/find。三端口在相同存储中以独立 scoped multi-route 状态索引，绑定全部路线案例；两个不同机械需求不能互相误命中。每次读取检查文档版本、原物理字节与案例绑定，篡改会拒绝。归档恢复后可重新查询，不依赖内存计数。通用生产接口仍 UNKNOWN；新的适配一定是新版本并重验。

## 与 B 的接口

- 输入：沿用 `map-notes/challenge-specification/v1`。当前每家族两份明确注册接口，另有 Map 的 100 高差/900×800 载台适配；其他尺寸/端口/能力组合明确返回 `unsatisfied + conflicts + searched + negotiable`。不是通用任意尺寸求解器。
- 输出：原 `gunman-rush-level-sketch/v1 + generationContract`。几何只在 objects，地图可读 SVG；真实端口方向、有向关系、支撑、独立 route 证据与所有 UNKNOWN 显式保留。
- 多端口六有序对齐全；通用进入状态、通用传递保证、变换、整图连接等不因一次连续见证而自动升级。`continuous-evidence-bindings.json` 另绑**具体内容版本与同实体连续试件**。
- 门、敌人、宝箱等均为原 Cell。工坊的原始 `reward_sites` 使用局部 position/region/amount 组合格式；给现有 `direct_join` 原始消费者时须显式映射到其 target/reward 字段，禁止悄悄丢弃奖励。标准合同 reward 对象保留完整实际来源。B 的整体消费者仍须重验真实金币事务。
- 不自动补平台、传送或回资源。自动 production assemblyInterface 继续默认拒绝 UNKNOWN。没有签 Map Director、区域环路、Boss、整图验收或人工趣味。
- 本批新增的是 Module 生产规则；连续试件不冒称独立 Macro。通用 Macro 组合生产、任意形状匹配和完整失败再试范围仍需后续工作。

## 运行与反馈

```sh
# 首次：依 WORKSPACE.md 安装指定引擎，并恢复依赖与新证据。
python3 pcg/tools/restore_archive.py godot-runtime-v1 --extract
python3 pcg/tools/restore_archive.py plains-generation-v1 --extract --prefix prototype/godot/
python3 pcg/tools/restore_archive.py workshop-a1-first-v1 --extract
python3 pcg/tools/restore_archive.py content-workshop-v1 --extract
pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 --headless --editor --path pcg/prototype/godot --quit

# 真实可操作样品，鼠标释放射击；可选 14 条路线案例。
pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 --path pcg/prototype/godot \
  "$PWD/pcg/prototype/workshop/main.tscn" -- \
  --cases-json "$PWD/generation/workshop/v1/review_cases.json"

# 新的有界离线生成/验证：名字不可覆盖已有实验。
python3 -m pcg.prototype.workshop.calibrate --name workshop-new-calibration
python3 -m pcg.prototype.workshop.experiments counters --name workshop-new-counters
python3 -m pcg.prototype.workshop.experiments produce --name workshop-new-holdout --counters workshop-new-counters
python3 -m pcg.prototype.workshop.map_demand --name workshop-new-map-demand
python3 -m pcg.prototype.workshop.intake --name workshop-new-intake
# 新人工创意 JSON：id、source_type=human_idea、source_revision、original_text，解释另列。
python3 -m pcg.prototype.workshop.intake --idea my-human-idea.json

# 原工具与新增边界检查。
python3 -m unittest discover -s pcg/prototype/workshop/tests -v
python3 -m pcg.prototype.workshop.audit_delivery
cd pcg
python3 -m unittest discover -s prototype/factory/tests -v
python3 -m unittest discover -s prototype/plains/tests -v
```

根目录 `npm run check`、26 个 factory、19 个 plains、28 个 Map 和 13 个工坊边界/真实持久化检查通过。新合同逐个走原 verified_document 和 Module validator。自动键鼠事件进入 manual 模式的原 UI smoke 验证实际移动、跳跃和射击；这是自动测试，不是人工试玩。

六家族主录像 **561 帧**逐字段精确一致，正常 60Hz/1 倍播放，每段末尾保留注明的 1 秒完成画面；另有 380 帧漏接后重试及 135 帧 Map 适配录像精确一致。首次额外短门完整回程录像有 5 帧 support_id、3 帧 normal_velocity 差异（位置等其他实测字段一致），**严格比较失败**，未计入精确视频通过；原片、原 trace 和差异报告保留。没有放宽比较器或用旧录像替换新内容。

可在聊天按 A1/A2/A3/刹车/分岔/续航反馈“是否想玩、哪里难读、哪里重复、哪里等待过久”。视频反馈不要求先试玩，也不自动成为手感评价或生产批准。
