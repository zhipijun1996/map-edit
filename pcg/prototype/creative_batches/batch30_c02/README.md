# C02：先穿第一门，再换第二门（暂停中的原型）

来源：`creative-production/batch30/design-cards-v1.json` 的 B30-C02。
复用已冻结的 `batch30_cell/runner_v3.gd`、原 WorkshopEngine、原弹丸/反冲/资源。
没有修改共享物理、Harness、Cell 或候选库。

首次预算见 `protocol-v1.json`：最多3规则、220探针，先一个核心再两接口。

已执行：

```sh
python3 -m pcg.prototype.creative_batches.batch30_c02.probe_v1 \
  --name workshop-batch30-c02-clean-v1
```

v1 四个射击窗口均失败，实际0/4完整通关、0候选、0留出。
原始输入/输出/源码冻结在 `results/workshop-batch30-c02-clean-v1/`。
每条均真实先穿开着的A、空中击中原铃、A关闭/B打开、身体穿过B；但落点不够远，撞到远岸侧面后坠下，最终出界，未取奖。
以control0为例：第56帧真实射击，第61帧交换（身体中心415.31,283.75），第90帧到565.04,375.69，第95帧586.70,442.24，已错过x680/top438远岸。
现有恢复底层仅到x660，后续持续前进还会离开恢复层；不能称失败恢复已实现。

后续候选修复方向（尚未执行）：把同一个铃放得更靠近A的垂直下方，使真实瞄准得到更陡的向上反冲，或者把远岸改成较低接收面。必须重新绑定规则版本、先验证原核心净空和实际落岸，再做扰动及低成本解。
不通过更改动作词、移除门或把无奖下路当作完成来填数。

根任务发现D04更优反例，要求核心修复优先，本namespace保留并暂停新增物理/源码修订。
已用4/220探针、1/3规则；剩216探针、2规则。两接口适配、完整校准/留出、原生录像、回程与入库均未完成。

## v2恢复实现后的真实状态

最终核心注册入口：`pcg.prototype.creative_batches.batch30_c02.api_v1`，物理世界在冻结 `rules_v2.py`。
需求0为下沉接收岸（x590/top530），需求1为抬高近岸（x550/top400），都不是中段加落脚点。
每个接口的control0均clean、mild6/6、moderate6/6通过。四控制只用于预留出前选定；最终均选择control0。
两接口共68精确反例，另6个修复为实际可到达的地面切门控制：0同结果绕过因果；其中6例改射击窗口仍完成相同穿门/空中交换因果，保留为合法替代，不强迫固定按键。
原34反例中的3个旧interface1地面发射位在关门后，不可到达；最终API已修为B前40的实际位置，旧失败没有删除。

```sh
python3 -m pcg.prototype.creative_batches.batch30_runtime.produce_v1 \
  --name <new-immutable-run> \
  --rules pcg.prototype.creative_batches.batch30_c02.api_v1 --index 4
```

root已在独立目录启动原regular完整校准/留出，本探针记录不替它宣布技术通过或入库。

同世界失败恢复：`recovery_v2.py`在两接口两控制clean4/4真实完成“故意失手落底→原access铃复原→原楼梯回原A→再试取得B奖励”，没有重置、传送或改资源。
但是恢复扰动仅接口0 mild5/6、moderate3/6，接口1 mild5/6、moderate2/6，**未达到原regular**。第一梯靠近撞底与后续ground不代表登上正确梯级仍有问题，不能宣称恢复可靠。
纯控制后续修复应逐级等真实目标support，而不是仅ground；或者第一跳先垂直越过梯底再横移。没有在这轮预算内继续换参数求幸运通过。
主Module反向与通用恢复保持UNKNOWN，标准合同不得外推。

累计214/220探针；全部11个run/失败/源码SHA见 `probe-receipt-v2.json`。没有自行跑holdout/入库，人工/生产批准仍UNKNOWN。
