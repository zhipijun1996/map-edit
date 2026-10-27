# D05独立恢复验证：固定Block版本下尚未满足

**最终needs_design；0恢复资格、0新Module。** 这是已入库D05两个Block版本的独立同世界恢复试件，不修改它们的几何、Port、掩码、名义控制或原SOURCE_DEPENDENCIES。

精确绑定：

- 接口0：`sha256:82d2d47c4d0f75594652428a5d44df1bc2f97a98e7f1165f6391a787a29127fe`
- 接口1：`sha256:383496cb92cbca40e93ddb3e2baa6b7d895d72a05f397d7e74ea169feb7cbfda`

每次构建都从原API生成，再逐项核对持久化候选cases中的全部物理实体、身体端口、Block Grid/ports/reservations、能力、spawn和目标完全相等；两份库record/cases/document字节绑定见 `final-receipt-v1.json`。恢复输入与证据独立冻结，不追加进旧Module的原准入依赖。

## 为什么旧楼梯路径不能直接签内部恢复

旧两clean实际完成错枪落底、原四级支撑、同世界重试取12币，但身体进入未保留cells(-3,2)/(-2,2)。后者是A西口明确不属于本Module的外邻，不能补掩码宣称通过。

真实A实体为 `[-128,352,400,100]`，末梯为 `[-248,434,120,30]`。末梯右缘与A左立面都是x=-128，A立面覆盖y352..452。人物从末梯向右会撞A立面；不能先走到中心-112再用coyote跳来穿墙。要从左边越A顶，整个身体bottom必须不高于352；但仍在墙左升到该高度时，身体已占用禁止外邻row2。仅微调末跳时机不能把这段真实西侧攀升变成本Module内部空间证据。(-3,2)的额外高跳可以用低跳研究，仍不能解除这项A外邻约束。

这说明旧路径的当前空间合同冲突，不是对所有可能玩家策略的全局无解证明。B仍可把原名义A→B候选集成研究，但不能据此承诺本Module有已验证的内部失败恢复。

## 两次有界原机制实验

我们尝试一条不借西侧外部空气的替代：错枪落原底岸，走到原停台右侧，普通跳+向下竖直反冲，向左回落原静止catch-deck，再实际走回A dock后重试。没有新增落脚或补资源；恢复本身多花一枪，接台/重试均需真实落地回充。

v1预注册4个底岸起跳x（548/562/576/590）×两接口8clean全部失败，没有真正落上原台或返回A。控制中还识别出原 `settle` 的持续自动转向会覆盖后来的axis；此行为属于原Harness真实API，不修改共享代码，失败保留。

v2在执行前登记最后3个控制×两接口6clean：以原axis+真实wait_x代替中间settle，延后至24tick靠近真实跳顶开枪，并提前左转。横向已真实执行，但6次仍没有登台；最高完整身体bottom为371.535，停台top353，仍差18.535px净空。原PlayerMotor的shot burst清除normal_velocity.y并只给有限时长反冲，不能用未发生的弹道惯性补出高度。

14次新clean全部身体留在原冻结所有权内；这是**没越界的失败**，不是恢复通过。连同旧2次越界失败共16/160实际案例。两次控制修订上限已用尽，因此0calibration、0holdout；剩预算不是继续第三次控制修订或降低regular门槛的许可。

## 复现与下一条件

```sh
# 用新name与新selection路径复跑第一版；不要覆盖已保存原件
python3 -m pcg.prototype.creative_batches.batch30_blockd05_recovery.run_v1 \
  --name fresh-D05-independent-recovery-screen --mode clean \
  --selection /workspace/scratch/fresh-D05-recovery-selection.json
```

第二版执行入口为 `clean_v2.py`，它写固定不可覆盖run `workshop-batch30-blockd05-independent-recovery-clean-v2`，原件已存在；复现前须另登记新输出路径，不能覆盖或以重抽样冒充新控制。原压缩raw、输入、所有source_snapshot及批次SHA在final receipt逐run绑定。一次新辅助脚本的语法错误在0物理执行前修复，单独登记于 `import-failure-v1.json`，没有隐藏成成功实验。

继续修复须另开登记周期：若改左侧恢复所有权或A端口，就是新Module版本并重新准入，不能重标上述两版本；若保留它们完全不变，则需另一条真正使用内部已存在地貌/真实机制的恢复关系。不得增加A外邻cell、隐形平台、传送、资源、墙跳或二段跳来凑通过。

本试件只研究铃未启动的错枪类；已启动移动台漏接、任意相位/资源状态、边界穿越及通用回程均UNKNOWN。人工观感、实际试玩、生产批准均UNKNOWN。
