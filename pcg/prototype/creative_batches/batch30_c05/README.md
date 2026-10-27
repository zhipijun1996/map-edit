# C05 追台时选择哪一个岸

当前是待统一 FULL 的技术原型，未有人类试玩或趣味批准。`api_v1` 仅公开横向斜升断拱接口 0；高庭接口 1 的近岸失败，返回具体缺口，不把仅有远岸的试件算作分叉。

三个端口属于同一真实物理世界。A 在旧拱下方，B 是旧拱上方的向西出口，C 是中心柱另一侧的高处向东出口。原移动平台实际承载、上升；近岸提前离台、落内部窄岸、跳上旧拱；远岸继续乘行，再击铃换开远门并利用反冲上岸。B 不是为了凑端口增加的安全恢复口。原引擎的线性往返平台没有被宣称为环形旋转平台。

只公开 A→B、A→C。两个动作方案共用地貌、奖励、入口与最初机关状态。所有反向及 B↔C 有向关系、接缝和连续外部挑战保持 UNKNOWN。内部恢复地面不是端口。世界不默认包外框。

## 复现

在仓库根目录执行：

```sh
python3 -m pcg.prototype.creative_batches.batch30_c05.screen_v3 --name workshop-batch30-c05-reproduce-wide --interface 0
python3 -m pcg.prototype.creative_batches.batch30_c05.counter_v3 --name workshop-batch30-c05-reproduce-counter --interface 0 --near 1 --far 0
python3 -m pcg.prototype.creative_batches.batch30_c05.recovery_v4 --name workshop-batch30-c05-reproduce-recovery
```

统一生产入口由主代理执行，使用原 Workshop 质量门槛、独立留出及持久化库，子代理尚未执行：

```sh
python3 -m pcg.prototype.creative_batches.batch30_runtime.produce_v2 --name workshop-batch30-c05-full --rules pcg.prototype.creative_batches.batch30_c05.api_v1 --index 7 --interfaces 0 --protocol pcg/creative-production/batch30/protocol-v9.json
```

技术原型片：`generation/workshop/plains30-v1/prototypes/C05-wide-v3-far/moving-station-choice.mp4`。原录像器严格检查 294 帧的身体、输入、资源、接触、机关和奖励字段全部通过。它绑定原型 case，不能替代未来正式候选的录像证据。交互场景为 `res://prototype/creative_batches/batch30_c05/main_v1.tscn`，需原录像器或 Workshop 的真实 case 初始化，不提供另一个物理实现。

## 实际证据与限制

`probe-receipt-v1.json` 逐运行绑定 209 次 Harness 尝试，包括最初验证器拒绝和失败；另一次真实录像，保守合计 210/220。三版生成规则，未改共享物理、合同、Harness、原 Cell。核心近岸控制 1 与远岸控制 0 各通过 6/6 mild、6/6 moderate 小筛选；不是独立留出成绩。两接口共 72 个有限反例没有完成同目标，不能证明其他解不存在。

起步铃原地射击使人在真实移动台上发生横移，控制根据实测人物位置离台。主动行走、早离台或地面预选属于可接受的替代动作，只要真实移动台确实承载并支持出口选择；不要求复刻“必须空中射铃”的词序。等待不自动送到两个站外出口。

同世界漏过近岸离台机会后，继续乘行转去远岸：clean、6/6 mild、6/6 moderate。真正漏射选择铃后，远门实际阻挡，人物落在原中心柱上，补射原铃，再跳与向下射击反冲到岸：同样 13/13，通过 4 枪 3 跳，无重置、传送或回充。失败版本和误把命中当漏射的测试完整保留。完整空气落失后的所有位置恢复与所有外部返回关系尚未穷举。

`unsatisfied-tall-v1.json` 保留第二需求失败：四个近岸离台控制均错过窄岸，不能拿远岸通过替代整个三端口需求。下一轮若研究新控制或更宽接收地貌，必须重新注册和绑定版本。

技术通过后仅进入候选库。人类趣味、试玩与生产认可分别保持 UNKNOWN。
