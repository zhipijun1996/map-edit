# C08：放出借火，再关回通路

**needs_design，0新候选，namespace冻结。** 这版是真实可玩原型，不具备原regular稳定性，不应进入完整校准、留出、候选库或网页发布。

玩家主动开原charger围栏B，同时关闭前路A；等真实冲刺开始，跳起用原弹丸击中敌人，实际HP3→2、空中射击资源回充；第二次空中射铃将B关/A开，利用该枪反冲到高岸。围栏重新关闭时敌人可能已经在外，不能称作“敌人必然收回笼内”。同世界的接地分段跳为明确允许的较慢替代方向，敌人不作为地图必需钥匙。

两接口各有四个clean真实成功轨迹，3枪1跳，等待冲刺后的响应延迟8/16/24/32帧；所有动作、敌人冲刺、弹丸碰撞、资源和门的防夹均为原机制，未写人物或敌人位置/资源。

固定先选control0之后进行mild6/moderate6：宽空间6/6及1/6，高差空间6/6及3/6。**未通过。** 宽空间的主铃枪会被真实移动敌人挡住或命中地貌；高差空间的第一枪会先碰主铃而不是敌人，失去回充；有一例确实重开A仍错过落岸。宽空间的接地分段试件撞Stage1下侧，落到底部恢复地；该恢复地不是额外port。反例、实际敌人死亡后替代、一般恢复、回程、视频观感和人工趣味仍UNKNOWN。

这个失败反向约束下轮提案：主动“借火”不仅要让敌人进入交互位置，还必须让两次瞄准的真实弹丸通道在原扰动下彼此分离。三次规则修订已经耗尽本轮上限，不通过改名、换seed或降低门槛继续计数。

57/220探针、11个原始run、全部失败及源码SHA见 `probe-receipt-v1.json`；解释与下一轮未执行假设见 `design-feedback-v1.json`。原始大帧数据保留在各Engine压缩输出，未重复到摘要。

复现需使用新不可覆盖run名：

```sh
python3 -m pcg.prototype.creative_batches.batch30_c08.probe_v3 \
  --name <new-C08-reproduction-run> --interface 0 --route air --mode clean --controls 0 1 2 3
python3 -m pcg.prototype.creative_batches.batch30_c08.probe_v3 \
  --name <new-C08-noise-run> --interface 0 --route air --mode noise --controls 0
```

另一接口使用`--interface 1`。原可玩消费者`main_v1.tscn`支持原手动输入与Engine编译动作回放，但未拍摄/人工批准。`runner_v2.gd`只复用原`enemy_world/runner_v2.gd`的敌人状态触发条件；世界运动和射击仍由原AI/Cell执行。
