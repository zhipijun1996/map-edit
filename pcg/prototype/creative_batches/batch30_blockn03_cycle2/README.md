# N03 第二外层控制周期：两条名义动作可执行，廉价地面反例拒绝入库

首周期 `batch30_blockn03` 已固定2规则/32调用/0合格后关闭。本目录为另注册外层周期，最多1控制规则，谱系仍≤80，未修改旧原件或 Cell/几何。不得把此周期当新玩法家族，旧 root index15不跑full；新index17也因反例未启动。

真实上台后先向右走20/24帧到台中，C空中实弹射铃后短时向右输入16/24帧修正相对距离，再中立等实际接台。没有写人物位置/速度/资源，也没有瞬移平台。4 joint控制中B只依赖走台帧数，故只跑2个独立B控制+4个C控制，6 clean覆盖8控制映射，全部目的通过。最小index0在noise/反例/full/held前冻结：B2枪2跳，C3枪3跳，C第308帧真正落回反向台，枪1/冷却0/跳0/精力100，0身体越界。C位置屏障超时600帧由完整西行距离事前声明，仍须等实际位置，而不是加时间假装到达。

16个同世界精确反例里，**地面台上射同一铃**真实达到同C和12币：3枪2跳、699帧首次稳定；名义空气接回为3枪3跳、705帧。二者最终同为向西、同实际满资源接地、无伤无重置及所有权无越界。此反例省一跳且没有额外枪/时间成本，实质移除了空中反向接回挑战，并非仅靠动作词判失败。原classifier保留拒绝，**0候选/0Module/0新家族成功**。

因此没有继续24noise、full或held，未从noise/held换控制，未修第2控制版本。新周期22调用，谱系54/80；是预算上限，不为凑满浪费失败版本。结论/具体冲突见 `final-receipt-v1.json` 与 `request-response-v1.json`。下一修订需要新几何/视线设计，比如铃在台外且偏下，使地面实弹被原实心台挡、空中才绕过台沿；这是尚未实施的假设，不使用“必须空中命中”的人为资格门槛掩盖问题。

## 相位与门槛澄清

原 Python `evaluate.instantiate` 会随机**未被铃控制**的移动台相位。本规则完整case仍有 `ferry_id='reverse-carrier'`，controlled集合保留 authored initial_phase=0；Godot安装时才去掉原latch以装隔离新Cell，不影响Python展开。只读144个原instantiate记录全为0，见 `phase-and-policy-clarification-v1.json`，0新增物理。**非零相位未支持，不能忽略后声称已验所有动态相位**。原通用snapshot中的module-clock phase不是新signed playhead，应读 `workshop.reverse_carriers.clock/signed_direction` 与原真实position/PhysicsServer速度。

首周期protocol-v1写mild≥.8是文字错误，旧原文保留。本澄清依据实际原 `quality.POLICY.regular`：mild≥.85、moderate≥.65，实际full gate完全未改。本周期没有noise/full统计，不能把clean转换成regular通过。

## 可审阅研发见证与失败接口

`review_cases.json` 有真实B名义、C名义和地面廉价反例3份录入输入，由原public_witness helper从原gzip读出；不是人工认可或候选。`counter-causal-audit-v1.json` 绑定原输入/结果/源码SHA、真实成本和终态，0新增物理。场景明确显示设计拒绝，支持手动探索或root之后录制对照：

```sh
pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 --path pcg/prototype/godot /workspace/map-edit-task-a/pcg/prototype/creative_batches/batch30_blockn03_cycle2/main_v1.tscn -- --cases-json /workspace/map-edit-task-a/pcg/prototype/creative_batches/batch30_blockn03_cycle2/review_cases.json
python3 -m pcg.prototype.creative_batches.batch30_blockn03_cycle2.request_v1
```

Godot场景只做原 `--check-only` 语法验证，尚未录视频或核对native回放。没有输出仍写start/pause的假标准合同；新Cell的正式导出/B安装必须另行实现，当前返回具体缺口。无 shared Harness、物理、导出器、候选库或Map生成器修改。

原件：`pcg/results/workshop-batch30-blockn03-cycle2-{clean-v1,counters-v1}/`，包含所有失败、源快照、原gzip SHA；复现使用新输出名。人工观感/试玩/生产 UNKNOWN。
