# N08 折页回廊：上桥取奖，下桥作为另一种回程

这是 AI 创意卡 B31-N08 的实际实现，也是旧 C09 三规则12次失败后的新 Block 生成规则；**不继承旧物理、不计新独立家族**。来源原卡逐字段保留在 `proposal-source-v1.json`，解释、可执行规则、实验、候选和人工观感分开。没有在线模型创作服务或训练宣称。

## 一份真实连续世界

1536×1408，12×11 Block128所有权，未生成实体外框。A W anchor[0,704] / 身体[24,718]，B E[1536,320] / 身体[1512,334]；两个外邻均未拥有。内部高度没有按Block缩放：上桥544、奖励岛352、石柱160，去程三次升高均192；低层桥736跨越两低岸间576空隙。原paired v3的真实弹丸、事务、防夹、承载和角色/资源保持原组件。

玩家实跳上桥，落奖岛通过原SimpleRoomReward领取一次16币，越柱到B。B向原access射击，使上桥撤去、下桥闭合，再真实落右低岸、普通跳落新下桥并返回A。下桥实承载约105帧，原接地回枪/跳恢复，未写人物位置/速度/资源。原低层恢复阶按192/192/128布置；其通用返回能力尚未签证。

首次4闭环因沿用wait_x180帧上限，在已经落新R并回走时过早超时，全部失败保留。第二规则仅把位置屏障超时按全宽1536/真实速度260×60+120=475预计算；仍必须实际到达，不以时间充当位置。四个完整闭环控制全通过，按事前登记的L/岛/柱/R完整24px身体最小左右裕度最大、同分小index选c0（最小61.95px），在noise/held之前冻结。两条标准方向clean、三canonical各3mild3moderate共18/18小筛通过。

## 下桥不是捷径

同一真实16币任务，三条路径都先走上桥、实取箱一次、实到B，再回A，不用无奖低路冒充同目标：

| 回程方式 | 全任务枪/跳 | B稳定到A首次稳定 | 结论 |
| --- | --- | --- | --- |
| B射access换下桥 | 4 / 4 | 391帧 | 名义新R实际承载 |
| 保上桥沿旧高路反走 | 4 / 4 | 372帧 | 合法，快19帧 |
| 落低岸后射primary换R | 4 / 4 | 449帧 | 合法较慢替代 |

因此不称下桥更快、节省动作或更有趣；它是另一个空间/操作选择，观看价值待独立模型和人工评审。16个同任务对照还保留普通跳、去程省枪、576空隙省R、错误access等失败。缺少“换态/下桥”词不构成拒绝合法旧路的理由。

fresh B→A 的旧高路经过尚未领取的真实箱，会实际从0币取得一次16币；这是合法额外收益，不伪造已取奖状态。名义fresh B下桥仍0币。另1次故意miss access后，在实际右低岸用原primary实弹重试成功，5枪4跳、原16币单次事务保留、无reset；仅1clean，不外推成通用恢复。

## 标准接口与闭环附证分开

标准Module只有A→B与fresh B→A。原schema禁止self-route，完整A→B→A是单独fixture：原ModuleDefinition保留合法A/B静态marker，但实际goal/end明确A，不伪写B出口，不作为第三条Module路线入库。

独立 `full_loop_v1` 使用原evaluate/regular，校准25/25、留出25/25全部通过。`loop-attachment-v1.json`在Module入库前绑定50个真实案例、世界/ports/所有权结构与实际out/back程序哈希。隔离 `export_v1.mjs`先复用原Block导出器，再验证冻结loop源case与当前Module几何/程序完全一致、附sidecar和成本表、重算合同版本并运行原校验；没有改共享schema、Harness、Cell、库或Map生成器。该附证不授予任意状态/边界/整图返回保证。

最新来源为实际 `862b736c491502ae9934265bc7415805b4c122b9`：Block128公式和JS不变，Python新增boundary_gates所有权；本规则没有Map边界门，不推断单向。B的paired Cell安装、边界接缝、任意机制/奖励状态、整图均UNKNOWN。不是无奖exp0_0适配。

## 保留Module首轮拒绝，只修反例范围分类

标准full-v1花57真实案例，在cal/held之前按原框架拒绝入库：B最外侧射击反冲借用外空气，唯一失败是完整身体离开预留。原件/拒绝保留。实际仍1枪1跳、新R实承载104帧回枪，真正连续稳定A比名义慢15帧；身体32帧越界、扫掠33帧，最大右超57.225px，涉及未拥有的(12,2/3/4)，不能当作Module内部或Map已验证解。

`api_v2`只是独立分类注册修订：名义purpose、完整身体、形状、端口、控制和门槛全不变。仅实际目标/资源/无伤/无reset/核心R全部通过、只剩ownership理由、枪跳不少且首次12帧真正稳定A不更快时，分类outside_contract_alternative，`accepted_module_solution=false`、空间/Map依赖UNKNOWN。没有扩owned或按kind白名单放行，便宜或省核心的方案不能用此例外。2名义与43反例定义除注册/分类元数据完全相等，原43实际strict purpose全部相等，只有这一例分类改变，见equivalence receipt。新full必须完整重跑，不能继承首57的不存在的held。

```sh
python3 -m pcg.prototype.creative_batches.batch30_runtime.produce_v3 \
  --name NEW_IMMUTABLE_MODULE_RUN \
  --rules pcg.prototype.creative_batches.batch30_blockn08.api_v2 \
  --index 20 --interfaces 0 \
  --protocol pcg/creative-production/batch30/protocol-map-block-v4.json
```

注意显式v4协议，原默认旧v2未擅改。`candidate_for_request`严格匹配完整奖励/状态/空间请求，其他需求返回具体冲突、已搜索范围与可协商条件。第二空间尚未实现，2物理/控制规则已用完，不看held再扩尺寸。

真实新N08 probe46/80（含所有失败、比较、fresh真实奖励和1次恢复），loop full50，Module full-v1拒绝57；新Module full-v2结果由root登记。最终是否候选看新完整原门槛，人工趣味/试玩/生产仍UNKNOWN。

## 回放和比较

`return-comparison-review-cases.json`有同一完整世界的下桥与旧高路两份真实输入。两片应先录完整A→奖→B→A，再按原生实际帧裁回程，不能fresh B并设置16币。`return-comparison-review-manifest-v1.json`给出geometry/时段/证据范围；目前尚未替root录片或宣称原生严格一致。标准场景 `main_v1.tscn`复用原paired与C09稳定机关命名。

原件前缀 `pcg/results/workshop-batch30-blockn08-*`，包含原输入、压缩raw、快照和SHA；复现需新输出名，不覆盖旧结果。原loop数字seed271547284/285不变，早先公式文本多一位0已单独澄清为index20+500003；未用held选控制、未变原regular .85/.65。
