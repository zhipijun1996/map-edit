# C07 关出一面能接住反冲的墙

一个待统一 FULL 的碰撞用途适配，未自行算作独立新家族。当前仅横向接口 0 有技术潜力；第二个高井需求真实失败，不能用镜像或部分动作代替完成。人工趣味、试玩、生产认可均 UNKNOWN。

从旧岩沿向右跌出，向右上方的铃开枪。原反冲把人物推向左下；同一弹丸打开前门 A、关闭背后墙 B。人物完整身体在墙外时关闭，随后以实测约 −984px/s 接触 B 的真实碰撞面（法向 +X），横速归零，落在袋面恢复原资源。再向前跳、向左下射击反冲，到可见宝箱岸。

这是一条更省跳跃的技巧路线。玩家也可以先跳起来开门，再真实落回初始岩或落在袋沿，再跳一次到奖。两条实测 2 枪 2 跳、245/233 tick，名义路线 2 枪 1 跳、197 tick。允许这两条付费替代，不宣称新墙在每个解里都必需。`accepted_policy_v1.py` 依据真实额外 ground_jump、射后接地回充、目标与安全分类；没有按 counterkind 白名单放行。名义一次跳的碰墙和身体净空门槛保持原样。独立模型审查见 `pcg/creative-production/batch30/c07-design-review-v1.md/json`，没有人工批准。

## 复现

```sh
python3 -m pcg.prototype.creative_batches.batch30_c07.screen_v3 --name workshop-batch30-c07-reproduce-core --interface 0
python3 -m pcg.prototype.creative_batches.batch30_c07.counter_v3 --name workshop-batch30-c07-reproduce-counter --interface 0 --control 1
python3 -m pcg.prototype.creative_batches.batch30_c07.recovery_v2 --name workshop-batch30-c07-reproduce-recovery
python3 -m pcg.prototype.creative_batches.batch30_c07.prepare_video_v1 --name workshop-batch30-c07-reproduce-playable
```

通过最后一项产生原 case 初始化后，可用原 Godot 场景 `res://prototype/creative_batches/batch30_c07/main_v2.tscn` 手动试玩/程序回放；它薄继承原 Cell 和 Workshop，没有另一个物理实现。

原型短片为 `generation/workshop/plains30-v1/prototypes/C07-horizontal-v3/new-wall-collision-brake.mp4`（4.37 秒，正常 60fps）。原录像器 197/197 帧标准字段严格通过，补充的原 Motor 接触数组也 197/197 完全一致；见影片目录 `contact-observer-check-v1.json`。这是 prototype 证据，不能替代未来正式候选的绑定影片。

主代理待执行的统一入口（本子代理未跑 FULL/留出/入库）：

```sh
python3 -m pcg.prototype.creative_batches.batch30_runtime.produce_v2 --name workshop-batch30-c07-full --rules pcg.prototype.creative_batches.batch30_c07.api_v1 --index 9 --interfaces 0 --protocol pcg/creative-production/batch30/protocol-v9.json
```

## 真实结果与失败

87 次 Harness 尝试与 1 次原生录像，保守 88/220；完整来源见 `probe-receipt-v1.json`。v1 墙太远，v2 一些早射控制利用了旧岩边，失败和反例保留。v3 令铃更高、旧岩更薄、门墙从岩底延伸，当前核心 6/6 mild、4/6 moderate 小筛选；不是完整 regular 或留出通过。

18 个精确反例逐一保留目标和真实成本。地面预开三种测试均被旧岩挡枪。没有按指定射击词拒绝轴向释放；同枪后松开方向的程序实际仍碰墙，成功保留。两个多跳替代的原始 nominal-purpose 失败没有改写；独立的 `counter-policy-audit-v1.json` 解释其允许理由。有限测试不证明其他解不存在。

真正第一枪漏铃后，原门态保持不变，落原下层地面，经两个原台阶，以原跳跃/反冲到奖：clean、6/6 mild、5/6 moderate，3 枪 3 跳、clean 432 tick。它是昂贵的同世界恢复，出口世界状态与名义路线不同，明确记录，不用 required_pair_states 把它藏起来。第一版恢复曾被上层台阶底面阻挡；第二版从台阶边缘留出完整身体空间，再原地跳/反冲，未补地貌或资源。

两个端口只公开名义 A→B；背后袋面和恢复台阶都是内部结构。B→A、接缝、任意入口资源/机关状态均 UNKNOWN。高井接口 4/4 到奖失败见 `unsatisfied-vertical-v1.json`；三次生产规则修订已经用完，不继续换名凑成功。
