# J06 双岸会合风口：静态三口局部岔口

最终规则 `rules_v3.py`，原 Cells / WorkshopEngine / Godot，能力仅移动、普通单跳、反冲；没有奖励、铃、敌人或隐形恢复地板。两个需求为横向宽口（台阶间隔150/高差70）与紧凑高差口（125/85）。A为西上来岸，B为西下外接廊，C为东侧外接廊；共享落地后向B下降或向C登阶，两个去向即使没有奖励也成立。模块不创建外部地区；B仍需在具体地图里接上后续路线。

声明4个所需有向对 A→B、A→C、B→C、C→B，加1条不重建世界的A→B→C连续策略。设计不希望轻易返回高A，但反向**仍UNKNOWN**，不从有限失败签no_path。

## 探针记录（不是正式校准/留出）

- v1：10/10 clean Godot成功，固定中途停顿使连续路线约13秒，因此保留原件后做节奏修订。
- v2：仅用原实际ground条件替换每段60帧等待；几何不变。10/10 clean成功，120/120 mild/moderate预校准扰动成功。一般路线约3–5秒，连续A→B→C约7秒。
- v3：物理与名义控制完全沿用v2，只补23条/路线廉价替代，via条件与原外在事务统一为grounded、x误差≤30、y误差≤1，增加明确依赖别名与版本绑定。
- v3反向有限搜索：36条真实Godot策略（先升到东岸后起跳反冲，3个跳跃保持×3个瞄准×2来源×2接口），成功0；关系仍UNKNOWN。
- 总探针176/220。无人工操作、人工评分或生产认可。

`protocol-v1.json`里的606/607是本子任务探针预声明种子；实际probe-v2 screen只使用606。根正式生产另有统一冻结protocol与独立holdout seed，**不使用这里的607作为正式留出记录**。

## 共同决策状态

`pcg/results/junction-windgap-common-prefix-v3.json`比较实际clean轨迹的物理/资源/世界前缀：同一接口的A→B、A→C、A→B→C在初始104帧/103帧完全相同，并共同到达Platform2上静止、满血、原精力100、1枪、无冷却的决策状态。之后才向西/东选择。此证据只覆盖精确clean初态，不能外推任意接缝/进入速度。

## 复现

在仓库根执行，先按WORKSPACE恢复原runtime。运行目录不可覆盖，probe命令传新名字：

```sh
python3 -m pcg.prototype.creative_batches.junction_windgap.probe_v1 --revision v3 --name junction-windgap-fresh-probe
```

本目录的screen/reverse/prefix脚本是原始实验的固定复现入口；若重跑需为它们的输出选择新版本路径。完整校准、留出、导出和入库由根复用既有生产驱动完成，不以这些探针代替质量门槛。
