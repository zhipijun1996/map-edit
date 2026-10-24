# 平原三端口 Module：独立有向通路与连续分支

2026-10-24。本轮基于 `main@9b3e110`，实际生成两个三端口候选 T01/T02。两者属于**同一种分支结构的参数变体**，不计作两种新玩法。生成、搜索和验证由程序执行，没有逐模块大模型调用。

[播放及下载短片](https://zhipijun1996.github.io/map-edit/generation/) · [三端口合集 T，约16.7秒](https://zhipijun1996.github.io/map-edit/generation/videos/plains-three-port-v1/all-samples.mp4) · [模块图与JSON](https://zhipijun1996.github.io/map-edit/generation/contracts/plains-three-port-v1/)

## 真实的三个端口

- **A**：西侧下层支撑位置。
- **B**：东侧下层支撑位置，主路线目标。
- **C**：东侧上层支撑位置，反冲击钟分支的出口。可以连接未来奖励内容，但本轮**未实例化奖励服务或发放奖励**。

三个端口有不同坐标、支撑引用及几何朝向。一个端口可在不同路线兼任入口和出口。它们不是入口/出口重命名，也不把路线上的任意空中点当端口。

下层路线 A→B 经过移动齿轮；上层路线 A→C 需要普通起跳、瞄准风铃、反冲升高并登台。另有**同一场景连续执行 A→C→B** 的见证：在C实际落地，然后从平台右侧回落、进入下层并到B，中间不重建场景、不补资源、不改机关。

实际几何由之前程序生成的反冲飞行/接收面继续扩展，新增下层支撑、第三端口和齿轮。没有人工完整预制Module库。当前只证明这种三端口结构；更复杂的分支、三入口、多重开关锁仍需新实验。

## 六个方向分别验证

每份文档声明6个有序端口关系，配置7条路线：

| 路线ID | 方向 | 作用 |
| --- | --- | --- |
| main | A→B | 下层主路 |
| upper | A→C | 上层可选支路/第三出口 |
| upper_rejoin | A→B，经C | 连续上层分支再汇合 |
| return_main | B→A | 主路反向 |
| drop_to_main | C→B | 从上层回落到下层出口 |
| return_upper | C→A | 先向右下台，再返回西侧 |
| approach_upper | B→C | 返回起跳区后进入上层 |

所有路线在**相同物理Cell、尺寸、位置及相同初始机关相位**中验证。仅进入端口、角色初态、输入策略和目标按路线分别配置。导出时若任一平台、危险物、机关初态或端口定义不同，禁止合并成同一个Module。

当前原游戏的 `PlatformingModuleDefinition` 仍只有entry/exit两个槽；测试适配器按每个有序对分别绑定这两个槽，三个对外端口由Map Notes的 `generationContract` 统一表达。第三个支撑位置始终存在于同一份几何。**这不是正式地图消费者已经支持三端口的声明**，正式接入仍为false。

## 实验与失败保留

发现阶段固定4个布局、每个7条路线。首轮28次中24次满足目的；B→C失败，因为前一段的settle控制持续生效。第二轮修正方向后仍24/28：固定等待30帧并不表示已经到达A，角色在途中提前起跳并受齿轮伤害。第三轮加入实际位置到达条件及停稳时间，28/28通过。旧两轮全部保留。

校准阶段：4个布局×7路线×3误差档×4次，共 **336次**。按最差路线校准成功率排序，同分按布局ID；每个生成接收面父代最多保留1个，固定选2个。规则在独立留出前冻结。

新留出Seed **104301903**：2布局×7路线×3档×12次=504次，另48次替代策略，合计 **552次、46批、0引擎错误、107.88秒验证生产耗时**。该时间包括路线扰动与反例验证，不是从零发现单Module的成本。实际命令、wall/CPU、进程峰值RSS见每批 `physics/*.execution.json`；RSS是系统子进程高水位，不冒称单Module独立内存测量。

| 每个候选的路线（T01与T02本轮计数相同） | 无输入误差 | 轻微误差 | 较大误差 |
| --- | --- | --- | --- |
| A→B 主路 | 12/12 | 12/12 | 12/12 |
| A→C 上层 | 12/12 | 12/12 | 9/12 |
| A→C→B 连续汇合 | 12/12 | 12/12 | 9/12 |
| B→A | 12/12 | 12/12 | 12/12 |
| C→B | 12/12 | 12/12 | 12/12 |
| C→A | 12/12 | 12/12 | 12/12 |
| B→C | 12/12 | 12/12 | 11/12 |

轻微误差±1帧/±2°，较大误差±3帧/±6°；包含随机齿轮相位。全部14条路线样本满足沿用的regular工程门槛。12/12不等于人类成功率100%，也不是通用进入状态证明；候选之间使用共同扰动，不能把相关样本相加冒充独立观察。

两个候选各路线均导出**clean trial 0**，不为每条边另挑好看的相位。由此同一份文档的各路见证共享实际初始机关状态。内容版本绑定7份独立验证，逐方向保留进入/离开观测、能力、资源、物理输出及SHA。

### 替代路线不能冒充完成分支

对upper和upper_rejoin各测“不射击”“不射击并延长普通跳跃”“错误瞄准”，每种每路线两候选×4次=8次。

- A→C：三种替代策略均 **0/8** 无伤稳定到达C。
- A→B经C：三种替代策略均 **8/8** 能到B，但均 **0/8** 实际在C落地。这是合法的下层主路，不算完成上层分支，更不算绕过上层挑战。

评价显式检查C的实际坐标与落地状态，不能靠 `via_ports=['C']` 标签或最终到B判定通过。反例仍只覆盖这些输入策略，未证明所有其他路线不存在。

## 状态、回程及拼装边界

能力只包含移动、普通单跳和反冲；未授予二段跳、墙跳或钩索。物理绑定游戏 `12f6cb0`，已审计当前游戏main `cd4989a` 对应机制一致；原870份脚本/资产SHA漂移0。使用原枪口、子弹、ShotLatch、资源恢复和真实伤害。原始许可/素材归属保持不变。

官方Godot `4.7.2.stable.official.ed1daf0bf`，二进制SHA256 `8d106cbe6144c2dc7e881d61d2429c1a8a76e6b22ef48bd5e48dcf934953f71e`。

六个方向各有独立的新建场景进入状态测试，**不能据此把任意实际出口状态当作反向路线的合法初态**。尤其机关时钟、开门剩余时间、装备和资源覆盖尚未形成通用状态传递保证。因此return保证、接缝、完整动作净空、通用变换和跨模块状态兼容仍保留UNKNOWN；所有自动拼装接口关闭。

连续A→C→B则确实在一个世界中携带角色资源和机关状态完成，是专门增加的恢复/汇合证据，不通过重建场景伪造。它同样不证明所有允许进入状态都能恢复。

输出继续使用现有 `gunman-rush-level-sketch/v1`＋`generationContract`，没有新建重复Module格式。两个JSON、SVG与视频manifest交叉绑定同一内容版本及各自路线原件；最终图的生产源见gallery的 `delivery-source.json`。14个路线见证只合并成2个Module，不算14个Module，也未生成Macro。

## 视频与人工审核

四段正常速度原生60Hz录像：

- T01-A-B：主路线，约4.83秒。
- T01-A-C：第三出口，约2.23秒。
- T01-A-C-B：同一场景分支与汇合，约4.82秒。
- T02-A-C-B：第二候选，约4.82秒。

每段保留完整输入过程和等待，另有1秒冻结完成画面；合集仅顺序拼接，约16.7秒。为避免C标签与目标框重叠，第二版仅改善端口文字位置；第一版录像也保留。公开第二版，每帧位置/速度/输入/资源/机关及全部Cell事件与headless见证完全相同，计 **225+69+224+224=742帧**。追踪JSON与SHA随manifest发布。

同一齿轮相位让本例主路与完整上层支路最终时长接近，不能把它当成节奏丰富的证明。可以从视频判断分支是否值得绕行、三个端口是否好认、等待是否拖沓；操作手感仍需实际试玩。

上一轮R收到用户原话“我觉得非常棒。之后可以大量生产吗？”，记录于 `feedback/plains-round2-positive-v1.json`，类型为整体视频观感，不擅自拆成每个样例评分或正式批准。本轮T视频尚无人工反馈；手动试玩和正式批准仍为0。

## 源码、恢复与下一步

- `prototype/plains/three_port.py`：同几何布局、6方向/7路线、实际C落地检查。
- `prototype/plains/three_port_produce.py`：有界校准、父代去重选择、独立留出、替代策略与输出。
- 仓库根 `tools/export-module-contracts.mjs` 的 `multiportDocument`：拒绝混合几何/相位，合并端口、逐对关系和验证，不改生成算法。
- `contract/export.py`：核对原始输入输出并重新计算路线目的，不信任外部“已访问C”标签。
- `prototype/godot/lab_draw_v3.gd`：只显示实际A/B/C位置，不添加碰撞/能力。

```sh
# 仓库根；先安装WORKSPACE中指定SHA的Godot。
python3 pcg/tools/restore_archive.py godot-runtime-v1 --extract
python3 pcg/tools/restore_archive.py plains-generation-v1 --extract
python3 pcg/tools/restore_archive.py plains-review-round2-v1 --extract
python3 pcg/tools/restore_archive.py plains-three-port-v1 --extract
cd pcg
python3 -m prototype.plains.three_port --name new-three-port-discovery --bases plains-phrase-bases-v1
python3 -m prototype.plains.three_port_produce --name new-three-port-calibration --source new-three-port-discovery --mode calibrate --seed 104301217
# 复现公开历史留出；未来独立试验必须换新seed，不能继续用此公开留出调参。
python3 -m prototype.plains.three_port_produce --name reproduce-three-port-production --source plains-three-port-calibration-v1 --mode produce --seed 104301903
```

`archives/plains-three-port-v1` 保存三轮发现、校准、正式生产的全部成功/失败、原始输入输出、每阶段源快照、初版/最终录像、命令日志和浏览器检查。逐文件、分片与整体SHA核验；不重复提交官方引擎、导入缓存或可重建AVI。最终交付源另存 `results/plains-three-port-source-v1`，不冒称早期运行源。

新契约测试43项、平原规则19项、原factory规则26项；现有编辑器检查继续执行。新测试覆盖混合几何/相位拒绝、虚构支撑拒绝、单方向不能推断全互通、实际到B不能代替访问C。纯测试不充当物理证明。

先看本轮三端口录像并反馈结构，再扩大三端口生产。正式随机地图接入前，应补端口接缝、连续跨模块状态验证和入库准入；不能只因三端口六方向样本都通过就默认任意拼接安全。
