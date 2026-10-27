# C02 同世界失败恢复：原门、原梯、真实支持确认

两个接口均已通过原 regular 校准及冻结选择后的独立留出；这是原 C02 的验证试件，新增 Module 数0。原已入库core、Cell、共享 Harness、地貌和能力/资源全部未改。

流程：原核心先穿第一门、空中换门，故意在接收岸之前停下并落底；用原 access 铃复原A，沿原 Platform4→5→6→7逐级回原A，然后在同一世界重新执行原核心、取B奖励。实际交换序列B/A/B、完整身体过门、每帧真实XOR碰撞状态、逐级真实支持和资源恢复均核验。

旧控制问题不只是jump时机：`settle(next)` 后立即jump，尚未站稳当前梯中心；`grounded` 可能仅指失败后仍在底层。新独立只读runner扩展 `trigger.actual_support`，与原grounded共同要求实际support ID、目标x±4、实际y±0.3和真实速度≤1；每级先居中停稳，再原地上升4/6/8/10tick后横移。它不修改人物位置、速度、资源或物理。

第一轮接口0通过；接口1的真实失败是靠B510太近时地面射击进入防夹区，交换正确拒绝。第二轮只修未通过的接口1：落底后主动站到原access正下x430并确认实际底层支持，再射铃。没有削弱防夹。接口0已过held的控制保持原样，未拿其held挑选接口1。

| 接口 | 冻结控制 | 校准 clean/mild/moderate | 独立留出 |
| --- | --- | --- | --- |
| 0 下沉接收岸 | v1、lead4 | 1/1、12/12、11/12 | 1/1、12/12、11/12 |
| 1 抬高近岸 | v2、access430、lead4 | 1/1、12/12、12/12 | 1/1、12/12、11/12 |

clean1沿用原静态Module policy，与原C02 full182一致，没有编造12次动态clean。两轮实际229+177=406/600，全部源绑定、失败、选择、held、成本与附加初次完整身体过门复核见 `summary-v1.json`。screen只保存purpose/evidence/关键摘要，完整frames仅在原Engine gzip；没有额外重复大轨迹。所有通过的held样本还额外核对第一次换门时的原完整身体净空。

复现（新独立目录，勿覆盖）：

```sh
python3 -m pcg.prototype.creative_batches.batch30_c02_validation.run_v1 \
  --name workshop-fresh-c02-recovery-i0
python3 -m pcg.prototype.creative_batches.batch30_c02_validation.run_v2 \
  --name workshop-fresh-c02-recovery-i1
```

原件：`pcg/results/workshop-batch30-c02-recovery-validation-v1`、`...-v2`。各自 `review_cases.json` 已准备真实recorded_frames、原batch/index及module SHA；原生消费者仍为 `batch30_cell/main_v3.tscn`，未放宽录像比较。此处尚未录制新视频。

证明范围仅以上精确世界/初始资源及策略和有限扰动。B→A、任意初态/接缝/整图仍UNKNOWN。人工观感、实际试玩和生产认可UNKNOWN。
