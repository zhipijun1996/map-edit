# C03：借火以后，把射窗封回去

最终冻结入口 **`pcg.prototype.creative_batches.batch30_c03.api_v2`**，仅`--interfaces 0`。同一侧龛世界有两条A→B策略：空中借火捷径、避开敌人的两跳分段路。下龛接口1真实伤害与moderate失败，明确`needs_design`，没有换成普通房间或计数。原四源码版本、失败和全部输入输出保留。

玩家先击铃，让敌人射窗A打开、通口B关闭。跳起后真正击中原3HP敌人，枪数从0回到1；下一枪打另一个铃目标，使A关闭/B打开，并靠这枪反冲跨过高通口落岸领奖。第一枪不会穿过敌人再击铃，两枪分别产生真实事务，中间没有接地。敌人扣1HP且仍活着；关窗会失去继续借火机会。

闭窗有实际返回作用。实测取12币后在原世界回A，关闭的射窗允许站120ticks仍HP5；再次射敌，弹丸在门右缘`x66.95,y356.76`碰撞，敌HP保持2。对照真实开窗站A，在frame86受到原敌人伤害变HP4。初态闭窗站A并射击120ticks同样稳定HP5/敌HP3。后续任意回程/进入状态、接缝、整图仍UNKNOWN，不能把这些小试件签成通用返回。

分段路在初态闭窗/通口开时不借敌人：第一跳到东侧中层，实际落地恢复后从平台东侧起跳回折到高岸，躲开高岸下表面。首枪必须避免误击铃；最终控制使用较晚的真实枪口位置，保留了名义两枪两跳，不靠硬锁输入。

敌死不是永久钥匙。`validation_v7.dead_fixture()`从同一新世界通过原枪实际清掉3HP，保留死亡，真实走到x140射铃关窗/开通口，然后走同一分段路取得12币、HP5并落稳B；clean1与mild2均通过，7真实枪，没有重建、复活、传送或写资源。这是小样本验证，不是完整regular/留出通过。旧`api_v1.dead_fixture`是保留的失败历史，不应作最终恢复入口。

## 固定预算与失败回流

本工人总probe **220/220**，其中原3规则172，根任务在protocol-v9预注册一次48上限的控制修复，完整regular/holdout均留给根任务。最终air与staged各clean1/mild6/moderate6通过；不是因此自动入库。全回执见`probe-receipt-v1.json`，原Engine已保存gzip原字节、输入、日志、source_snapshot及SHA；后期screen只存摘要和evidence，不重复存所有frames。

- v1空中核心可玩，但接收时序余量不足。
- v2提前枪发现真实冷却导致12/14tick发射被拒；目标高岸没有直接降到单枪可达。
- v3新铃落在旧分段第一枪射线上，虽然到了宝箱，末态错误，仍失败。下龛需求有实际伤害，保持缺口。
- v4有限射线控制修复使分段路线避免误铃。闭窗与不闭窗分别比较世界结果及goal-only；三种4枪/1跳借火越顶都未达到同奖励，不能证明其他解不存在。
- 实际地面射击略向下会产生向上反冲，短暂离地并改变空中枪数，不能用固定间隔假定一直在地面。
- 实际闭门射击反冲曾把人从x87推到x38，原完整身体防夹正确拒绝关门。改为真实移动到x140再射，弹丸命中时身体仍清门，无机制放宽。

```sh
python3 -m pcg.prototype.creative_batches.batch30_runtime.produce_v2 \
  --name workshop-batch30-c03-full-new \
  --rules pcg.prototype.creative_batches.batch30_c03.api_v2 --index 5 --interfaces 0 \
  --protocol pcg/creative-production/batch30/protocol-v9.json
```

以根任务实际driver版本为准。必须同时记录required pair state与goal-only反例，不能用末态字段掩盖更便宜取奖路径。当前无人工观感、试玩或生产批准。普通入口/原角色/原武器/敌人/承载/恢复与Cell v3全部复用，main仅显示与镜头，runner仅稳定真实Node名称；未建立第二套物理、库或Map Generator。
