# 内容工坊 v2：撤回真实绕法，交付修订后的六家族

当前交付在 [`generation/workshop/v2`](../../generation/workshop/v2/README.md)。共 **6 家族 × 2 接口 = 12 份标准 Module**，另有 1 份现有 Map Director 需求适配。全部为技术候选，人工观感、试玩及生产认可为 0；通用 Macro 和整图验收未完成。

v1 的 A1、短门、刹车凹槽、三端口资源取舍、敌人续航沿用其原件和验证；**v1 A2 及其依赖的 Map 适配已撤回**。不要用 v1 的六家族通过表作为当前结论。旧文档、Module、视频、物理输出和错误判断均原样保存。

## 为什么撤回 A2

在 v1 的普通跳跃、逐枪省略和被动乘台反例之外，增加“先跳上静止载台，再用一枪离台”后，6/6 条策略到达旧宝箱；其中存在完全未启动机关的成功路径。原有反例覆盖不足，不能据动作词或两枪见证认定世界变化有用。

`pcg/feedback/content-withdrawals/a2-static-dock-bypass-v1.json` 记录旧内容版本与真实反例原件。**原 CandidateLibrary 现在在检索/入库时检查技术撤回名单**；已知失效版本不会因旧记录还写着 passed_scoped 而重新出现，依赖它的 Map 索引也拒绝复用。旧记录不可变，没有把撤回伪装成人工评分或删除失败。

这是本轮唯一新增的共享候选库行为：接口签名与正常记录兼容，只增加已知失效版本的拒绝。共享 Module 合同、物理 Harness 和 Map Director 未改；B 可审阅同一 PR 的 `pcg/map_directed/library.py` 与撤回清单，不需要维护第二套候选库。

## 新 A2 的动作关系

原 ShotLatch、ModuleMovingPlatform、承载、速度继承、弹丸与弹药机制保持不变。

- 载台由 `[330,450]` 移至 `[480/515,350]`；需要先射铃释放，再主动追赶落点。
- 实际落台后有 0.6 秒零输入承载，再主动接近前缘，在合适时机跳离并射中近侧接收器暂停。
- 接收岩体前缘改为 x=790/825，稳定出口 x=880/915，地面 y=288。静止停靠点离目标更远；即使载台到远端，普通跳也不足以到同一接收面。
- 接收器设在 `[490,290]`，避免第二发被载台本体遮挡；没有扩大隐藏命中盒或改变原平台行为。
- 宝箱可见，原受支持接触事务给予 8 金币；失败落入原下岸。连续回程采取下岸再攀升，漏接后重试通过真实落地/动作返回入口，不重置角色、机关或奖励账本。

修订没有增加一个新家族，也不是仅改标题/Seed。它修复了原 A2 中“世界移动可以被省略”的因果缺口。

## 固定预算与结果

`protocol-carrier-rework-v2.json` 在这轮修订前固定：最多 2 次校准修订、每次 2 个接口、原 regular 门槛、12 次扰动/级别、新留出 Seed **261025943**。第一版因射线被载台遮挡失败；第二版通过校准后才进入新留出，没有降低门槛或利用留出挑候选。

| 内容 | clean | mild | moderate |
| --- | --- | --- | --- |
| 新 A2 / 接口 0 | 12/12 | 12/12 | 12/12 |
| 新 A2 / 接口 1 | 12/12 | 12/12 | 11/12 |
| 新 Map 适配 | 12/12 | 12/12 | 11/12 |

新 A2 每接口 22 条原策略反例、108 条静止登台笛卡尔枚举反例，另各 3 条在载台远端普通跳的反例；全部未到达出口。全交付按发布实例几何/初始状态去重绑定 **530 条反例**，不是必要性证明。

最终 12 个 Module 仍对应 394 个预定主挑战样本，按原 regular 门槛筛选。静态内容 clean 1 次，动态内容按原规则 clean 12 次；mild/moderate 各 12 次。其余五家族的数值与技术边界见 [v1 原报告](content-workshop-v1.md)，其中旧 A2 结论已由本报告替代。

同世界的新 A2 回程与漏接重试分别 **26/26**；新留出 Seed 分别为 261025944、261025945。与其余家族共同去重后，发布版本绑定 **130 条连续案例**；另有原 26/26 接缝试件。转移保证、通用回程和整图关系仍 UNKNOWN，不由这些见证外推。

六段主录像正常速度、599 帧逐字段精确一致；新 A2 漏接重试 428 帧、新 Map 适配 168 帧另经精确核对。v1 额外短门回程录像的严格比较失败仍保留，未放宽比较器。

## Map 实际需求与复用

继续读取原 Director 的 100 高差、900×800、两方向端口、基础三能力、奖励 0 需求，并原样保存。玩法家族修订显式记录；未修改其拓扑和布局，也不声称 B 已批准替换。

较低的 Map 接收面在扩展静止登台搜索中再次出现 1 条绕法，因此第一轮适配被拒，**没有进入留出挑选**。第二轮将接收岩体放到 `[850,338,50,100]`，稳定出口 `[875,320]`，保持 900×800 原硬约束；校准、扩展反例、新留出与新建 Library 后的磁盘检索通过。

见 [`generation/workshop/map-demand-rework-v3`](../../generation/workshop/map-demand-rework-v3/) 和 `workshop-map-carrier-rework-v3` 原件。该适配是同一家族的额外接口，不计为第七家族。每次新放置或 Map 组装仍须 B 真实整图重验。

## 来源和持续生产入口

人工原话仍为原稳定 ID / human_idea 修订 1；解释、生成规则、提案、物理、失败与内容版本独立关联。新增 `a2-static-dock-resolution-v2.json` 将发现绕法、撤回、两轮修订、扩展反例和新版本关联。工坊提案会因 unresolved 的 unneeded_mechanic 而停止选择，修订证据不会批准旧版本。

```sh
# 原依赖与历史证据恢复方式见 v1；本次额外恢复：
python3 pcg/tools/restore_archive.py content-workshop-a2-rework-v2 --extract

# 14 条可操作路线案例，原 Godot 键鼠输入；没有在线模型服务。
pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 --path pcg/prototype/godot \
  "$PWD/pcg/prototype/workshop/main.tscn" -- \
  --cases-json "$PWD/generation/workshop/v2/review_cases.json"

# 新人工创意，稳定 id/source_revision、原文与解释分别提供。
python3 -m pcg.prototype.workshop.intake --idea my-human-idea.json

# 原物理/候选库上的新批次，不覆盖旧名字。
python3 -m pcg.prototype.workshop.evaluate --name workshop-new-carrier-calibration --families chase-landing
python3 -m pcg.prototype.workshop.carrier_rework --name workshop-new-carrier --produce
python3 -m pcg.prototype.workshop.carrier_rework --name workshop-new-map-carrier --map --produce
python3 -m pcg.prototype.workshop.audit_delivery
python3 -m unittest discover -s pcg/prototype/workshop/tests -v
```

标准合同继续使用 `gunman-rush-level-sketch/v1 + generationContract`；不支持的需求返回具体冲突、搜索域和协商条件。多端口逐有向关系声明，未知状态保持 UNKNOWN；不自动补平台、传送或资源。对现有 direct_join 原始奖励消费者，position/region/amount 到 target/reward 的映射仍需显式适配，不能丢弃奖励。

受控铃的标准对象 `targetId` 指向真实载台，局部门占位声明 disabled，近侧接收器与原铃共享事务。旧 gate-only 降级器还需显式映射到原 `ferry_id/return_access`，不能把每个接收器各生成一套机关。未完成该消费者适配时必须返回缺口；本批不宣称 direct_join 已自动支持这些新对象组合。

根目录 `npm run check`、17 个工坊、28 个 Map 检查通过；原有 26 个 factory、19 个 plains 检查保持先前通过结果。撤回记录的检索拒绝和生产拒绝均有回归检查，不以人工批准覆盖已知技术反例。

当前支持范围仍是已注册接口与这个额外 Map 适配域；通用尺寸/形状搜索、独立 Macro 生产规则、完整失败恢复范围、正式主游戏及整图验收尚未完成。人工观感、手感、难度与生产批准也未获得；本轮交付证明的是可复现的内容候选与能够纠正失败的工坊闭环。
