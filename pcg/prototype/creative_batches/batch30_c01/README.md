# C01：跳出去，桥才出现

冻结生产入口 `pcg.prototype.creative_batches.batch30_c01.api_v1`。原regular完整校准、独立留出和候选入库由根任务执行；这里的202次小实验不能替代准入。

入口低岩唇限制直接起跳位置。初态A桥闭合提供真正伸出的助跑面、B桥开启。玩家在A上越过岩唇，从外侧跳起，左下击铃；同一枪使身体反冲向右上，同时撤A、造B。首个post-shot接地必须为真实关闭的B门碰撞体，此时原枪数从0恢复1，再从B起跳到可见宝箱与出口。第二跳若普通单跳即可到达，也接受它，不用第二枪词强制否定等价核心。

两种实际Map空间：宽1700的横渡（B桥350高、岸330高），宽1250的紧凑升层（B桥280高、岸180高）。无默认外框，恢复地面和左侧攀回支撑不是伪第三个地图口。两个端口A/B；只请求A→B，反向、任意进入状态、接缝、整图都保持UNKNOWN。

失败后同一世界：故意错过B落到下层，三段原跳跃/反冲返回入口，真实地面射击把A桥恢复，再重试取宝。没有重建、传送、复活敌人或写资源。四恢复控制各两接口clean8/8，按先序选r0后mild12/12。通用恢复及反向仍未签完整门槛。

## 原件与实际小实验

- v1四控制均失败，输入过早归零，人物只到x709..766，旧失败保留。
- v2继续向B移动后3/4clean通过，c2/c3各6/6mild。两条实际合法边缘支撑被旧中心点判断错拒，raw保留；最终改按真实grounded、脚底高度、24px身体交叠及关闭门状态判断。
- v3两空间×四控制：8/8clean、48/48mild、48/48moderate。按预声明同分先序选择各control0，未看holdout。
- 最终命名适配clean2/2、精确主动反例16条没有推翻；root完整阶段每路线38条。早期34条反例中岸上切换只朝终点settle，缺少可能在B成功后的下一跳，证据范围有限；已修为真正B后续控制，不用旧失败夸大排除绕法。
- 真实空中枪数在射击后为0，直到B接地才为1；不是命中门返枪或擦固定平台回充。

总probe202/220，源码规则3版本；逐批输入输出、源快照、失败、SHA见 `probe-receipt-v1.json`。额外原生视频单列，不算完整留出或人工批准。

`runner_v1.gd`/`main_v1.gd`只将原paired Cell两门的真实Node.name设为稳定 `PairGateA_bridge-pair`、`PairGateB_bridge-pair`，避免自动名字随UI对象数改变导致严格support_id不一致。门行为仍完全来自冻结batch30_cell v3，角色、物理、弹丸、资源均未改。main另做纯表现镜头。

```sh
python3 -m pcg.prototype.creative_batches.batch30_runtime.produce_v1 \
  --name workshop-batch30-c01-full-new --rules pcg.prototype.creative_batches.batch30_c01.api_v1 --index 3
```

此命令使用原WorkshopEngine/evaluate/produce/WorkshopLibrary，不建立第二套模拟或库。技术候选、模型趣味判断、人工观感、实际试玩、生产批准分别记录，后四者当前UNKNOWN。
