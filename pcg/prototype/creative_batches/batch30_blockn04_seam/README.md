# 给B的真实Block连续接缝：N04 → N04

**一份精确连续试件通过原regular校准和独立留出，新增Module/家族/库记录均0。** 总90实际案例（含原失败），低于160上限；探针15，低于80。最新入口索引是 `handoff-v2.json`（v1原件保留），源Module仍为原标准Map Notes+generationContract，没有创建第二个候选库或Map生成器。

| 内容 | 精确值 |
| --- | --- |
| 两份不可变源 | `sha256:87b8ed50f5b86fe4eafb92bc593864a15f1c59b7c99c60fae0d55f8c56460efc` |
| Left路线 | 原A→C |
| Right放置 | 原样平移 `[1280,-384]`，原A→C |
| 接缝锚点 | Left.C = Right.A = `[1280,320]` |
| 两侧实际身体dock | Left `[1256,334]` → Right `[1304,334]` |
| 最终身体dock | Right.C `[2536,-50]` |
| 真实收益 | Left/C12 + Right/C12，各领取一次，总24币 |
| 校准clean/mild/moderate | 1/1、12/12、12/12 |
| 独立留出clean/mild/moderate | 1/1、12/12、10/12 |

上述为完整目的通过数，有限自动案例不是人类成功率。两个held中等扰动在右段关闭时完整身体离grow区余量不足，严格计失败并保留；没有因终点/金币成功放宽原质量目的。人类观感、试玩和生产认可仍UNKNOWN。

## 不是接缝补路

两份原source从持久化库重新读取，record/cases/document逐SHA绑定。Left80个ownedcells为原0..9/0..7；Right整体变为10..19/-3..4，160格没有任何重叠，只在接缝邻接。双方原实体的既有几何审计都没有正面积冲突，连共面岸体也只接触边界。

14个原静态平台、2个原timed ShotLatch、4个原宝箱是两个源平移后的**精确并集**。只为link/奖励加left/right唯一ID，避免串铃/账本重复；没有增加、删除、裁切或移动任何源实体，没有新接缝台、隐形恢复或资源补给。独立11项数组相等核验见 `entity-union-audit-v1.json`，初始0physics拒绝检查见 `static-placement-v1.json`。

这份组合实际有6个外露源接口（L-A/L-B/L-D/R-B/R-C/R-D），只有L-A→R-C经过这次验证。Left.C/Right.A是内部连接，没有复制成额外外Port；其他连接、反向、任意进入条件不默认互通。

## 一个人物、一次世界、真实跨界

Left原开门反冲/完整上穿/关回/同门顶落脚回枪完成后，人物真实到Left.C。跨1280时完整24×36身体经过共同ground64开口，整段有原岸支撑；随后在Right原A±7px、y±1px、|vx|≤1且正确支撑上连续稳定至少12帧，再继续原Right门循环到其C。

新observer继承原Runner，只给两个scoped原门稳定Node名并读取真实open/collision/disabled/顶面支撑；不改原N04 observer、角色运动、世界或资源。每段目的检查把实际scoped事件/位移映回其源语义；完整跨界与全程body另外对160格并集逐帧核验，接缝中不把跨两份掩码的身体误判为需要新增土地。

`body-and-state-audit-v1.json`独立读取50个完整原压缩raw，核验无body越界、同一连续帧/世界时钟、Right进入前其原门未被左段提前打开。`body-sweep-audit-v1.json`又用原raster核对每两个真实相邻帧的保守24×36完整身体扫掠，50条全部在精确并集内，并绑定原角色RectangleShape2D文件SHA；不是只检查中心或增加物理模拟。48个完整目的通过的实际Right入口样本：真实接地、正确Platform7支持、1枪、cooldown0、jumps_used0、energy100、HP5；这些是**观察值**，不是给任意进入状态自动补满资源的合同。

## 控制失败也保留

第一轮2clean仅controller0严格合格，controller1虽到24币终点却没在Left.C真正稳定；不能把 `settle` 当阻塞到达。controller0小扰动6/6后，完整校准moderate仅7/12，原regular拒绝，held未执行。该33次原件保留。

第二次且最后控制修订使用原持续settle反馈，但在其后添加真实Left x位置等待，再接地并保留稳定时间；Right入口与其后原阶段显式retarget原控制目标。不设置身体坐标、速度、资源或机关。严格purpose仍逐帧检查±7/|vx|≤1/连续12帧，实际screen Left29帧、Right17–20帧稳定后才跨界/继续；固定wait本身不被视为成功证据。

新screen7/7后，在held前固定controller2；完整cal25/25、held23/25目的通过。没有从held回修或再挑其他控制。两种控制修订、两组不同源绑定/fixture版本与所有失败都保存，90不是把失败移出分母后的计数。

## B如何用

读取 `handoff-v2.json`：它引用原标准Module文档/版本、两个精确实例变换、内部端口对应、冻结输入controller与原证据、观测入口状态范围、原始case下载路径。原库内容与泛用assembly资格没有被修改。B可复跑此精确试件，或在自己的实际地图中使用相同源再做连续验证；不能将单次放置提升为任意平移、任意状态或整图准入。

```sh
# 官方Godot和原运行时按WORKSPACE恢复；使用新不可覆盖输出目录
python3 -m pcg.prototype.creative_batches.batch30_blockn04_seam.run_v2 \
  --name fresh-N04-exact-seam-full --stage full
```

该入口读取冻结controller2，按原evaluate执行cal/held；不生成其他布局，不搜索Map。真实回放case在 `pcg/results/workshop-batch30-blockn04-seam-full-v2/review_cases.json`，在held前固定，原生消费者为 `main_v1.tscn`。原 `workshop.record` 仍须严格逐帧比较，额外 `n04_seam` 两门观察字段另行核对；没有录像资格由headless自动继承。

这次交付没有输出自动准入Macro：现有演示composer假定main/entry/exit及200px间距，不能直接套用N04四口与零间隔连接。标准源组件与精确试件索引足以复用，本任务不为此另写一套组合生成器。通用seam/变换/任意ingress/返回、其他外接口关系与B整图均UNKNOWN。
