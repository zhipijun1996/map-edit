# 审批修复与六个双平台交付（revision063–064）

按本次原话完成H09初始上方只出不进、第二轮S09地刺净空增加16px、HQ07/S04/S06修复及六个LT/LB双平台。12项全部有真实Godot原生可玩包，共23条固定方向；11项完整v2通过，四台三锯升降井仍未通过扰动筛选。固定通关不等于完整合格。

对应规格已提交main：`c04fca59`。42、51、52、196、三怪、升降井规格同步至已实现布局；另落实本次H09/S09修订，8份精确版本与接口矩阵均留在[规格同步回执](../../spec-sync-r063-receipt.json)。未将实现分支整体合入main，未改其他设计提案。随后同步main `e0c0a9a1`的大型奖励房图文更新，确认这12项审批绑定未变，新大房间仍待审、不实现。

| 规格 | 状态 | 原生方向 | 正式案例数 | 下载与证据 |
| --- | --- | --- | --- | --- |
| lift | 固定可玩，扰动未过 | 2 | 0 | [证据](lift.json) · [试玩ZIP](downloads/lift-native.zip) · [短片](videos/native-lift-A-to-B-v1/native.mp4) |
| lt-1x2 | 完整v2通过 | 2 | 123 | [证据](lt-1x2.json) · [试玩ZIP](downloads/lt-1x2-native.zip) · [短片](videos/native-lt-1x2-A-to-B-v1/native.mp4) |
| lb-1x2 | 完整v2通过 | 2 | 121 | [证据](lb-1x2.json) · [试玩ZIP](downloads/lb-1x2-native.zip) · [短片](videos/native-lb-1x2-A-to-B-v1/native.mp4) |
| lt-2x1 | 完整v2通过 | 2 | 124 | [证据](lt-2x1.json) · [试玩ZIP](downloads/lt-2x1-native.zip) · [短片](videos/native-lt-2x1-A-to-B-v1/native.mp4) |
| lb-2x1 | 完整v2通过 | 2 | 124 | [证据](lb-2x1.json) · [试玩ZIP](downloads/lb-2x1-native.zip) · [短片](videos/native-lb-2x1-A-to-B-v1/native.mp4) |
| lt-2x2 | 完整v2通过 | 2 | 123 | [证据](lt-2x2.json) · [试玩ZIP](downloads/lt-2x2-native.zip) · [短片](videos/native-lt-2x2-A-to-B-v1/native.mp4) |
| lb-2x2 | 完整v2通过 | 2 | 121 | [证据](lb-2x2.json) · [试玩ZIP](downloads/lb-2x2-native.zip) · [短片](videos/native-lb-2x2-A-to-B-v1/native.mp4) |
| hq07 | 完整v2通过 | 2 | 172 | [证据](hq07.json) · [试玩ZIP](downloads/hq07-native.zip) · [短片](videos/native-hq07-R-to-L-v1/native.mp4) |
| hq09 | 完整v2通过 | 1 | 89 | [证据](hq09.json) · [试玩ZIP](downloads/hq09-native.zip) · [短片](videos/native-hq09-L-to-T-v1/native.mp4) |
| s04 | 完整v2通过 | 2 | 170 | [证据](s04.json) · [试玩ZIP](downloads/s04-native.zip) · [短片](videos/native-s04-B-to-T-v2/native.mp4) |
| s06 | 完整v2通过 | 2 | 176 | [证据](s06.json) · [试玩ZIP](downloads/s06-native.zip) · [短片](videos/native-s06-B-to-T-v1/native.mp4) |
| s09 | 完整v2通过 | 2 | 169 | [证据](s09.json) · [试玩ZIP](downloads/s09-native.zip) · [短片](videos/native-s09-L-to-B-v5/native.mp4) |

## 修复及验证流程

H09 TOP初始OUTPUT，按L→T验证，不再生成非法顶口进入夹具。S09仅把下沿岩体及其上刺下移16px，矩形、端口、锯和敌人不变；按真实窗口高度射击，底部返回先起跳再移动，避免入刺。HQ07改用实际站位与支撑判断，消除近铃水平反冲和桥边战斗越界。

S04存在验证流程缺陷：分组风铃原生控制的P/Q初始停位被旧采样器错误随机化。诊断证明后冻结版本化采样修订，用原候选、原种子与全部无关扰动重验；72项比对通过，正式170例通过，没有新抽留出。历史采样函数和旧失败保留。S06顶口连续夹具第二次穿台请求早于原Motor清除前次穿台记录，增加4帧真实输入等待后，原候选及原正式输入复测176例通过。没有写入位置或资源。

六个双平台保留原冻结程序，经窄范围、预登记的v1→完整v2升级，各分配一次此前未登记的独立池；13项正反检查约束例外，普通同程序换池仍被拒绝。HQ07/S09在校准失败后使用真实修订控制，按同一用户任务、原FULL协议最多2次适应的上限预登记revision064；不是新的人类审批。旧063失败完整保留，未用留出调参。

## 升降井剩余问题

原四载台、三锯与原空怪保留，上方口初始只出不进、射铃开门；可选宝箱真实取得4币，已有完整上行取箱再出顶口的原生包和影片。当前交付v8固定通关及同世界重试成功，但上行轻扰动4/6、中等1/6。最后v13筛选仍失败，12个实际候选已用尽预设预算，未启动独立留出。不证明模块无解。

主要难点是下台→上台交接、躲中锯和上锯、到达上层起跳窗的联合时序。建议审核上下组相位与停留配合，给交接和上行各一个稳定安全窗；当前未擅自改周期、速度、轨道或危险。详见[lift.json](lift.json)、[宝箱实证](fixtures/lift-optional-chest-v1/reward-evidence.json)与[宝箱试玩ZIP](downloads/lift-optional-chest-native.zip)。

## 试玩与证据

ZIP在仓库根目录解压，按[WORKSPACE](../../../../pcg/WORKSPACE.md)恢复原游戏资源，用官方Godot4.7.2运行各JSON的nativePlayable.scene：

```bash
pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 --path pcg/prototype/godot "$PWD/<scene路径>" -- --case 0
```

省略`--replay`为手动操作，加上回放实际输入；`--case N`切换方向。ZIP引用原游戏资源与官方引擎，不重复包含。影片为实际编译场景，60FPS、1倍速，结尾冻结1秒。strict=false保留REVIEW_ONLY及逐字段差异，不以影片替代独立物理证明。S04首段AVI没有终止回执，终止原因UNKNOWN，保留但不作通过证据；当前选用已完成且场景SHA一致的v2影片。其他旧场景影片及失败也保留。

原游戏870份保护文件未改。11份通过报告均从原始数据只读重算，原始归档包含063/064所有成功、失败、零帧拒绝与源码快照。人工试玩、生产批准、镜像、封口组合、任意进入态和完整Map仍UNKNOWN。

[授权与预算](authorization/request.json) · [续轮授权](../revision-064-v1/authorization/request.json) · [源码/几何/累计预算](verification/geometry-source-budget.json) · [完整报告重算](verification/full-report-rederivation.json) · [原始归档](verification/raw-archive.json) · [AI抽帧观察](verification/ai-video-observation.json) · [最终检查](verification/final-checks.json)

```bash
python3 pcg/tools/restore_archive.py approved-revision063-064-implementation-v1 --verify-parts-only
python3 pcg/tools/restore_archive.py approved-revision063-064-implementation-v1 --extract
python3 -m pcg.manual_review.audit_revision063_v2
```
