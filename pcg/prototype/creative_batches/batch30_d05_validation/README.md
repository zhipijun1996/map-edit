# D05 同世界失败恢复（原 regular，独立留出）

这是 `batch30_d05.api_v3` 两接口的连续验证试件，新增 Module 数为0。core几何、原角色、平台、ShotLatch、资源和原 Harness 均未改。

`summary-v1.json` 绑定四轮全部992/1000实际案例，剩8；D05原220 probes另外保留。两个失败类的两接口均通过原12 clean /12 mild /12 moderate regular校准和冻结选择后的独立留出：

| 失败类 | 选择 | 每接口校准 clean/mild/moderate | 每接口独立留出 |
| --- | --- | --- | --- |
| 空中打偏，平台未启动 | 原地跳2tick再右移上第一梯 | 12/12、12/12、10/12 | 12/12、12/12、11/12 |
| 已启动但没接住人，台继续运动 | 回A后走到原岸205；观察实际左向近岸台，射铃暂停再登台 | 12/12、12/12、9/12 | 12/12、12/12、10/12 |

两类都真实落底层、按序踩 Platform4→5→6→原A，随后在同一世界重试，第一次重试射后支持必须是 `catch-deck` 且有真实弹药恢复，再过岸取得奖励。没有重建世界、设置人物坐标、传送、补资源或删除碰撞。失败样本仍计入分母；没有因失败降低质量门槛。

第二类的 `moving_runner_v1.gd` 是隔离只读策略观察器：`trigger.carrier_observation` 与原 `grounded` 条件共同生效，直接读取原平台的实际 global x、motion_running 和 PhysicsServer2D 线速度。它不由 module.clock 推断 bell-controlled motion_clock，不改变原输入调度和物理。全程4次实际射击，暂停/重试是恢复成本，不是新玩法家族；具体总时长及从A到暂停（含走向岸沿）范围见 summary。

失败保留：unstarted-v1 的斜向错枪在噪声下有时擦中铃，未保留控制；unstarted-v2 用真正远离铃的竖直下射并在未消费的旧 held 前固定选择。moving-v1 从A远射移动铃可靠性不足，104筛选无保留，未消费其新 held；moving-v2 在相同cal seed下缩短真实射程，再完整校准/选择/消费原新held。未通过的旧case不改标通过。

复现（每条全流程产生新目录，勿覆盖）：

```sh
python3 -m pcg.prototype.creative_batches.batch30_d05_validation.run_v2 \
  --name workshop-fresh-d05-unstarted-recovery --screen registered
python3 -m pcg.prototype.creative_batches.batch30_d05_validation.moving_run_v2 \
  --name workshop-fresh-d05-moving-recovery --screen registered
```

原件分别在 `pcg/results/workshop-batch30-d05-recovery-full-v2` 和 `pcg/results/workshop-batch30-d05-moving-recovery-v2`；两目录的 `review_cases.json` 已用真实 recorded_frames、原batch/index、module SHA准备好，原生回放消费者仍是 `batch30_d05/main_v1.tscn`。这些是验证试件，不可作为新的2个Module入库；视频尚需root原生录制和严格比较。

声明边界：仅上述精确几何、初始支持/资源及有界扰动策略；B→A、任意平台初相/任意资源入口、接缝与整图仍 UNKNOWN。人工观感、实际试玩和生产批准 UNKNOWN。
