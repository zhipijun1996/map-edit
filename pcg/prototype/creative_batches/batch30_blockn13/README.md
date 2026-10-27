# N13：停车前给身体留后退余量

状态：`needs_design`，未入候选库，人工趣味 `UNKNOWN`。这是原 A2／载台风铃与 Dock 门的组合扩展，不计作新基本玩法家族。

使用原 `dock_latch_v11`、D05 挂载接收器和真实移动平台。没有修改承载、碰撞、反冲、时钟或资源机制。平台停在原生 Area2D 停靠区时保持门开启；离台后还能否返回是独立的实际用途，不能由 `requiredPark` 字段代替验证。

本周期使用两版规则、51/80 次真实 Godot probe；full、heldout 均为 0。原始结果见 `pcg/results/batch30-blockn13-*`，精确逐帧证据由各 `results.json` 的 evidence 指向。`original-cycle-receipt-v1.json` 汇总实验、源码哈希和范围。

实测后、中、前站位确有区别：后位停车反冲使身体掉台；中、前位均可保留承载。四份东向 clean 均到奖。停车名义策略 mild 6/6、moderate 2/6，未达到原质量要求。两例 moderate 到奖但离台枪再次击中挂载铃，重新启动平台并关闭停靠门；另两例停车枪未击中移动铃，之后落底出界。真实弹丸、碰撞和相对位置记录于 `noise-failure-audit-v1.json` 与 `aim-relative-audit-v1.json`。

不停车抢窗是合法替代：2 枪、1 跳、344 帧到 B，快于停车的 3 枪、1 跳、379 帧。不能为维持停车叙事把它判为作弊。停车的同世界 A→B→A 真实 clean 为 4 枪、2 跳、724 帧，一次领取 12 币；尚无连续任务的 regular／heldout 认可。四种不停车延迟回程策略失败仅是有限反例，不能证明停车必需。

镜像接口、fresh B→A、任意动态相位、接缝和整图均保持 `UNKNOWN`。源代码冻结；没有交付可签发的 API。若进行下一修订，须另登记外层范围，保留本周期失败，整个 N13 谱系仍至多 80 probe。
