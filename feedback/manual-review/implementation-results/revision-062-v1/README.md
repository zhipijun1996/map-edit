# 最新审批模块实现与旧失败修复（revision062）

基于main `f3aff10f229dfd461aee72650c8c40bd77affc0e`，新实现第二轮S04/S06/S09，修复HQ01/HQ03/HQ07及第二轮S10/S12。第二轮规格与旧同号模块分开记录。

本轮8项、34个原生固定方向、8段实际影片，完整v2通过4项。原游戏870份保护文件和设计网页未改。

| 规格 | 状态 | 原生方向 | 正式案例数 | 下载与证据 |
| --- | --- | --- | --- | --- |
| hq01 | 完整v2通过 | 6 | 492 | [证据](hq01.json) · [试玩ZIP](downloads/hq01-native.zip) · [短片](videos/native-hq01-T-to-L-v1/native.mp4) |
| hq03 | 完整v2通过 | 6 | 488 | [证据](hq03.json) · [试玩ZIP](downloads/hq03-native.zip) · [短片](videos/native-hq03-R-to-L-v1/native.mp4) |
| hq07 | 技术复测通过，独立资格未完成 | 2 | 172 | [证据](hq07.json) · [试玩ZIP](downloads/hq07-native.zip) · [短片](videos/native-hq07-L-to-R-v1/native.mp4) |
| rs10 | 完整v2通过 | 2 | 169 | [证据](rs10.json) · [试玩ZIP](downloads/rs10-native.zip) · [短片](videos/native-rs10-B-to-R-v1/native.mp4) |
| rs12 | 完整v2通过 | 12 | 970 | [证据](rs12.json) · [试玩ZIP](downloads/rs12-native-reobserved-v2.zip) · [短片](videos/native-rs12-B-to-T-v1/native.mp4) |
| s04 | 双向可玩，扰动未达标 | 2 | 0 | [证据](s04.json) · [试玩ZIP](downloads/s04-native.zip) · [短片](videos/native-s04-B-to-T-v1/native.mp4) |
| s06 | 双向可玩，扰动未达标 | 2 | 0 | [证据](s06.json) · [试玩ZIP](downloads/s06-native.zip) · [短片](videos/native-s06-B-to-T-v1/native.mp4) |
| s09 | 双向可玩，扰动未达标 | 2 | 0 | [证据](s09.json) · [试玩ZIP](downloads/s09-native.zip) · [短片](videos/native-s09-L-to-B-v1/native.mp4) |

## 新实现与未完成项

S04采用两组原生风铃分别控制P/Q；真实事件仅影响各自载台并保留独立时钟。S06实现原生ShotLatch刚性挂在P下方64px，实际离台射击启动、反冲接回，原始28个案例逐帧偏移正确。S09保留原锯、岩面刺和原空怪；L→B真实空中命中原怪，B→L先清怪仍能返回，无自动刷怪或资源注入。

三个新模块固定双向和原生包均通过，但扰动筛选未达标，未开启独立留出，不标完整合格。具体比例、原因与后续控制建议见各JSON。有限控制失败不能证明模块无解；移动风铃、扩净空、改速度/轨道均没有擅自实施。

## 旧失败如何处理

先用上轮失败的实际校准输入、相位与噪声原样重放，8个失败均复现，再修输入策略。HQ01修Q→P落点、左岸地面反冲及顶口起跳；HQ03修右侧安全战斗站位；HQ07把实际高度并入射击触发；第二轮S10修起跳与反冲边界余量；第二轮S12修右侧登Q和从Q左侧上行。需要替换已知池的正式运行使用真实修订程序与预登记池；HQ07默认池曝光漏记单列，不宣称独立通过。全部旧失败保留，不调已观察的留出。

HQ07当前只标技术复测通过，独立资格仍未完成：发现旧守卫仅扫描完整报告，漏记上一轮中断前已完成的R→L留出。当前同一程序换独立池被守卫拒绝，未分配seed；没有强行重跑。对应规则见[物理skill](../../../../.agents/skills/pcg-physics-contract/SKILL.md)：“改名、换Route标签或只换seed不产生新独立留出”。已补充按完整批次登记曝光，并用真实旧raw做隔离回归检查。

HQ07正式反例遇到缺省direction驱动错误：已完成批次逐字节复用，仅12个完全相同的反例输入用新的观察驱动续测。原错误、实际命令、驱动源码、批次SHA和额外原始重算均独立绑定；没有新校准或留出。反例是删除指定计划动作的固定策略搜索，不能当作穷尽所有玩家操作的无解证明；实际请求均保留在raw中。

HQ09新鲜T入口首输入前受刺的冲突仍待用户确定设计修订；没有擅自改变初态权限或尖刺，上一轮单向样品及冲突证据保留在[revision060](../revision-060-v1/README.md)。

## 试玩与证据

ZIP在仓库根目录解压，按[WORKSPACE](../../../../pcg/WORKSPACE.md)恢复原项目资源；官方Godot4.7.2运行JSON的nativePlayable.scene，省略--replay为手动，加--replay回放实际输入，--case N切换方向。ZIP引用原资源和官方引擎，不重复包含。影片60FPS、1倍速、结尾冻结1秒；strict=false为REVIEW_ONLY，严格差异完整保留。

[授权和预算](authorization/request.json) · [旧失败分类](authorization/failure-triage.json) · [相同输入重跑](verification/prior-failure-replay.json) · [几何/源码/预算核验](verification/geometry-source-budget.json) · [完整报告原始重算](verification/full-report-rederivation.json) · [原始归档核验](verification/raw-archive.json) · [AI实际抽帧观察](verification/ai-video-observation.json)

```bash
python3 pcg/tools/restore_archive.py approved-revision062-implementation-v1 --verify-parts-only
python3 pcg/tools/restore_archive.py approved-revision062-implementation-v1 --extract
python3 -m pcg.manual_review.audit_revision062_v1
```

完整通过仅限精确版本及已测配置的技术候选资格，人工试玩、生产批准、镜像、封口组合、任意进入态和完整Map仍UNKNOWN。S12最后六个顶口检查仅因旧观察器0.05px高度容差失败。官方原PlayerMotor实测safe_margin=0.08；实际支撑ID、全身位于指定相邻平台、连续静止均成立，脚底偏差0.0678px在原边距内。按真实支撑只读复核后通过，原失败与六类否决测试保留，未放宽越界/健康/奖励/世界状态门槛。复核报告留在原预登记执行目录；缺失路径只读链接到同输入续跑的归档原件，另有逐项SHA清单，没有修改池预留或新增物理运行。

S12环境恢复时已完成29个封装批次及1个未封装完整批次：后者由原输出、完成标记和真实内核子进程退出码0恢复执行回执，计时UNKNOWN，未伪造计时或重跑该批。其余同输入继续，候选/协议/池/种子均未改变。

没有修改设计网页、部署或合并main。
