# 冻结的20种新因果关系

主表20种，另有攻击提交开门1种额外技术关系。旧六家族不占名额；技术通过不代表人工趣味、试玩或生产批准。

| # | 稳定关系ID | 名称 | 留出安全稳定 |
|---|---|---|---|
| 1 | `jump_wall/late-air-rise` | 保留二跳越低檐 | 23/25 |
| 2 | `jump_wall/step-off-wall-return` | 踏空贴墙反蹬 | 25/25 |
| 3 | `jump_wall/switchback-wall-ascent` | 双壁绕刺越顶 | 25/25 |
| 4 | `grapple/anchor-gap` | 空中挂停主动跃出 | 24/25 |
| 5 | `grapple/jump-refill` | 触环恢复二跳 | 24/25 |
| 6 | `grapple/bounce-brake` | 自动弹钩后改轨 | 25/25 |
| 7 | `machinery/carrier-rendezvous` | 两台相会转乘 | 36/36 |
| 8 | `machinery/saw-pursuit` | 跟锯穿廊掉层 | 36/36 |
| 9 | `enemy-world/absorber-bell` | 清敌身露射铃 | 36/36 |
| 10 | `resource-routes/sightline-backtrack` | 探身开锁再折返 | 25/25 |
| 11 | `occupancy/live-enemy-pressure-support` | 活敌压区维持门 | 34/36 |
| 12 | `resource-routes/trapdoor-commit` | 撤桥自坠 | 25/25 |
| 13 | `enemy-world/displace-landing` | 击退腾出落位 | 36/36 |
| 14 | `jump_wall/bell-wall-rebound` | 反向击铃借墙折返 | 25/25 |
| 15 | `grapple/hazard-window` | 周期危险择时离挂 | 35/36 |
| 16 | `machinery/evacuate-rejoin` | 离台避险重接同台 | 36/36 |
| 17 | `resource-routes/moving-projectile-aperture` | 弹丸穿运动射线窗 | 34/36 |
| 18 | `jump_wall/wall-slide-launch-window` | 缓降高度预算择窗 | 36/36 |
| 19 | `resource-routes/ordered-target-transaction` | 可见双目标有序事务 | 23/25 |
| 20 | `machinery/carrier-dual-service` | 先压门再取回载台 | 35/36 |

精确原run、case、MapNote module、contentVersion、字节SHA、提案/冻结源与独立性父家族比较见 `selected20.json`；完整审查见 `review-v7.json`。

最终逐项审查见 `checker-suppression-audit-v2.json`：现有safe反例被purpose词拒绝0项，20份module字节/版本/case绑定一致，全部与已知撤回及暂扣版本不相交。有限反例不构成必要性穷尽证明。
