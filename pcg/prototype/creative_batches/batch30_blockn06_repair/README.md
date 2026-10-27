# N06 中庭双翼换桥：明确几何修订

这是旧 N06 首周期失败后的独立模型修订，不覆盖旧 52 次 / 2 规则的 needs_design。根任务另登记本周期**仅 1 几何规则、4clean+24noise=28**，总谱系恰好80次，未跑 held、未新增候选或新家族。原 regular/full 门槛保持。

新世界只有两项实体修改：M [544,608,192,64]→[480,608,256,64]，向左增加接收裕度且右缘736不变；铃 [800,672]→[800,560]，缩短真实弹丸射线以改善原瞄准扰动。两座桥、三端口、底岸/恢复阶梯、完整Block所有权、原Cell v3/角色/资源与两种控制计划全部不变。全来源见 `idea-source-v1.json` 与原 `batch30_blockn06` 首周期。

四次clean全部通过。选控制先执行 `protocol-v1.json` 的预注册公式：实际第一M落脚及实际第一对应桥落脚，各自计算24px完整身体的左右包含余量，四值取min，分高优先、同分小index。两支 c1=54.833px，c0=51.467px，因此在任何noise之前冻结c1；没有沿用旧first-valid或看noise挑样。随后两路线各6mild、6moderate，共24/24通过。

冻结可执行接口：

```sh
python3 -m pcg.prototype.creative_batches.batch30_runtime.produce_v3 \
  --name NEW_IMMUTABLE_NAME \
  --rules pcg.prototype.creative_batches.batch30_blockn06_repair.api_v1 \
  --index 16 --interfaces 0
```

这仍是同一世界、同一中央M与原资源初态下的分叉：左可射空保留实体左桥，右跳离击铃使左撤右现；两支真实落自己的桥回枪，再上小岸、普通跳到高端口。A W[0,704] / B W[0,64] / C E[1280,64] 是128边界中心，身体dock分别[24,718]/[24,78]/[1256,78]。底岸没有充数为Port；其恢复与重试保证仍UNKNOWN。只声明A→B/A→C，其余4对 UNKNOWN，不冒充真实Map要求全部互通的三口节点。

`policy_v1`沿用首周期已审查的真实阶段观察：额外M地面枪造成的小反冲、重新落M，再真正离M落桥，是可能的付费替代。它按真实离M→第一落脚、实际桥碰撞状态和原回枪判定，不按counterkind、枪数或标题放行。原身体所有权、目标、HP、能力、无reset和右桥交换都保留。新几何是否存在此替代仍需新证据。

旧ordinary反例模板漏jump的错误没有覆盖；本路径 `alternatives_v1.py` 新绑定修复为真实 `jump→jump_release`。每个精确方向20个反例，交根任务full实际执行，本周期没有再挤probe预算或将旧几何反例当新证据。原 Godot check-only、新 Block/spec 预检与原精确ID/geometry绑定均先于物理通过。

原始输入、压缩raw、完整冻结源和证据：`pcg/results/batch30-blockn06-repair-clean-v1` 与 `pcg/results/batch30-blockn06-repair-screen-v1`。`probe-receipt-v1.json`包含旧52+新28计数、选择公式/排序/余量、源码SHA与实际限制。人工趣味、真人试玩、生产批准均UNKNOWN；单接口成功不签第二空间、任意初态、通用接缝或完整Map。

## 原完整准入结果

root index16 `workshop-batch30-blockn06-repair-full-v1`实际154例，A→B/A→C两向所有cal/held clean1/1、mild12/12、moderate12/12，入原库9450553d…。两native分别327/346帧，原严格比较仅26/30帧匿名support_id不同，全部差异公开为review-only，不改变物理资格或比较器。仍仅三口本地两方向，第四口/反向不继承；独立四口需求由另外版本完整实现/验证。
