# C02：Block128 原生接口样品

冻结生产入口 `pcg.prototype.creative_batches.batch30_blockpilot.api_v2`。它沿用 C02 的真实两门空中换序规则，属于接口适配，**不新增玩法家族**。根任务已用原 regular 校准和独立留出形成两份候选；本目录79次小样不能替代该182次完整验证。

| 版本 | 真实 anchor | 内侧身体 staging | 保留轮廓范围 |
| --- | --- | --- | --- |
| 下沉一格 | A `[-128,320]` / B `[896,448]` | A `[-104,334]` / B `[872,462]` | 1408×896，47个连通Block |
| 同高近岸 | A `[-128,320]` / B `[896,320]` | A `[-104,334]` / B `[872,334]` | 1408×896，46个连通Block |

两者均 `ground64/v1`：开口中心下32px是地面，下14px是角色站立中心；实际 staging 位于端口内侧24px。Port 在拥有cell的实际边界中心，法线方向邻cell不属于该Module。轮廓可凹形，不要求Port在包围矩形最外沿。

适配复用 Map 分支 `a685fae...` 的 `anchor/raster/declare/validate` 和ground64语义。内部地貌不按Block缩放，不补矩形外墙。整份原布局平移 `[82,-68]`；原Platform0/7终岸顶面上移18px，接收岸分别下移18/20px，全部≤32。入口改为原Platform7的真实侧口，玩家实走进入原动作起点。原恢复底层和全部楼梯保留，未删除失败地貌。成对门B、两个接收器及奖励实体均参加预声明所有权；动作空间是保守预留，真实身体逐帧不得出界。

`raw.ports`、`entry_port`、`exit_port`继续是内侧身体点，供原Harness；`raw.block_ports`单独保留真实锚点、grid及stagingPosition，原标准文档导出时映射为 `generationContract.space.blockGrid` 与标准Port锚点，不另造Module格式。

真实 Map 请求 `block-demand/exp1_0` 来自最新规划器，明确 `rewards:[]`。因此默认生成0币新版本，未把旧12币或金币当主要道具。原带奖励版26次小样保留，但未冒充该请求的通过结果。角色只支持traversal，能力必须已定义且含jump/shot_recoil；Boss、junction、5Port、Block256、缺反冲、奖励服务等有明确拒绝。显式B→A/双向/折返需要额外真实验证，返回 `needs_verification`，不映射成A→B。请求守卫的9项0物理拒绝见 `request-guard-receipt-v1.json`。

对真实请求的回答是 **candidate_for_joint_mapping**：已知局部A→B候选，不承诺joint端口映射、未知进入状态、区域环回或人类难度2。整体探索图和Map验收仍由B负责。

## 已执行证据

- 带奖励 v1：2 clean、12 mild、12 moderate，全部通过。
- 无奖励 v2：2 clean、12 mild、12 moderate，全部通过；预冻结Block掩码覆盖完整24×36身体。
- 14个预反例未达到相同外在目标；完整34/精确路线由根任务重跑，有限反例不是无其他解证明。
- 边界新试件：原样品完成后进入完整镜像接收器，再跨回原岸，clean成功，真实地形为两个源变换的精确并集。镜像仅新接收器几何版本，没有继承镜像挑战/B→A资格。
- 边界小扰动为mild3/6、moderate2/6，**不合格**。原控制的过紧 `actor_x` 等待与settle停止点差0.016–0.072px而超时，失败完整保留，未降低门槛/放宽比较。不能从一次clean签通用接缝。
- 原形自身直接相接存在实际恢复台/整格所有权冲突。四组准确静态拒绝、来源版本、已搜索范围和可协商项见 `adjacency-refusals-v1.json`；不删恢复台强拼。

`probe-receipt-v1.json`逐run绑定79/80次实际成本和原压缩raw。根完整版本为：

```text
sha256:30f7380fbf6652b319cf468af648141e34403fd49951832a1ba0e45149980b85
sha256:edb7ee7a3d7cb43010f3dc4c6396b3894cd21686d648da9188247a226110c337
```

原regular完整验证属于 `pcg/results/workshop-batch30-blockpilot-full-v1/block128-serial-airlock`，不能移标旧C02物理结论。人工观感、实际试玩、生产批准均UNKNOWN。

## 复现

```sh
python3 -m pcg.prototype.creative_batches.batch30_blockpilot.probe_none_v2 \
  --name workshop-fresh-blockpilot-none --interfaces 0 1 --levels clean mild moderate
python3 -m pcg.prototype.creative_batches.batch30_blockpilot.counter_probe_v1 \
  --name workshop-fresh-blockpilot-counters
python3 -m pcg.prototype.creative_batches.batch30_blockpilot.boundary_probe_v1 \
  --name workshop-fresh-blockpilot-boundary --levels clean mild moderate
```

使用新目录，原件不可覆盖；Godot、能力和资源仍是原工坊实现。
