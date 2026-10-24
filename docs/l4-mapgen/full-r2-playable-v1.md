# 完整 R2 多环地图的真实空间落地

2026-10-24，PR #1 / `research/l4-map-generator`。用户指出上一段视频只有一个小挑战组合、安全连接过长。本轮回到原先认可的**完整风铃平原 R2 Seed 0：27场所、39连接**，保留全部分支、汇合与大回环。

当前为**可玩结构候选**，尚非内容成熟的区域。大部分仍是导航Cell，长梯井、重复跳台、地标与敌人内容不足；没有达到《空洞骑士》一个区域的探索品质。旧小motif及其技术PASS不作为本轮设计验收。媒体、公开入口与回执见 [`generation/maps/r2-full-v2/`](../../generation/maps/r2-full-v2/)。

[公开整图与两条闭环视频](https://zhipijun1996.github.io/gunman-rush-previews/launchers/MAPGEN-R2-FULL-01/d3e29ca31ba1dcaa304a9ccf745b3455d563cb73/ea8109a49fe6/report.html) · [完整手动地图](https://zhipijun1996.github.io/gunman-rush-previews/launchers/MAPGEN-R2-FULL-01/d3e29ca31ba1dcaa304a9ccf745b3455d563cb73/ea8109a49fe6/)。公开14资产/8页面文件均核对完整字节；浏览器实际键鼠、地图切换与三视频加载通过，原900MiB托管门禁和旧预览检查通过。

## 输入与实际调用链

输入是既有 `experiments/l4-mapgen/results/region-network-v2/runs.json` 的 `plains-R2-0`，SHA256 `9e45f846e8009d862478cd94d2a20f6698080cc64424445a783ffaaf0dea8d1b`。复用原Mission/Exploration及二维布局，没有另造拓扑或固定横向主线。

```text
原R2图/布局 → compiler.py全部场所与连接
  → pressure.py原动态Cell → bell_room.py紧凑风铃侧室/实际回程井
  → validate.py / growth.py有状态路线、需求与库匹配
  → FullMapEngine → 原PlainsEngine/Simulator
  → r2_runner/r2_pilot → 原Controller/Motor/资源/碰撞
  → state_extra/bell_extra → 原奖励服务与实际状态门
```

35条双向、4条单向，共74个合法有向连接；无向独立环秩13只是结构统计，不是趣味评分。原入口r5、前庭r6、东西奖励区、隐藏锁和回程标志不被删减。一个原注释为drop的连接在布局里实际向上，当前如实实现单向通道门，未冒称重力下落。

实际世界11808×10624wu，1412平台/1168单向支撑、499地刺面、5锯轮、6门、1风铃。壳体隔开原布局空间，防止跳出区域绕过锁，不是完成的区域美术。角色从原 `[4368,2254]` 出生，单次路线不重建、不传送、不写位置/速度、不直接补资源。到达要求精确XY、真实落地/速度及三脚底射线命中指定支撑，撞到另一层不算通过。

编译器当前只支持这个冻结Seed与96×128wu导航模板，不是通用不规则Macro嵌入器，也不能描述为全部由成熟Module库自然拼成。

## 需求补缺、候选入库与再次复用

原已验证风铃模块的1600wu底座不满足656×624wu房间需求。`compact_bell.py`复用实际动作平台、门、铃和输入，仅裁短pit底座及地刺，得到568.59×510wu新版本；旧PASS不转给新几何。固定8次适配：正向3/4、反向2/4，失败全留。

再固定候选、不开新搜索，以独立Seed241024991执行原regular门槛：clean1/1、mild12/12、moderate11/12。真正调用既有export与CandidateLibrary.enroll进入主候选库：

`sha256:08aed42071a32fe5eab6004cffb6158b56bb000895d78e9b6eeb0f53d4bfd4b5`

同需求重新find实际命中1条。`growth.py`先搜索并复用该版本，再新建完整地图跑风铃远征：7580帧/360腿通过。库缺失时最多一次紧凑适配、一次固定留出；失败返回不可满足条件，不删Map边、不无限修。证据在 `pcg/results/r2-full-library-reuse-v1/` 与 `r2-compact-bell-holdout-v1/`。

旧nominal版本与新regular版本身份不同，旧整图/媒体不改签新contentVersion。`library-reuse-geometry.json`核对实际世界逐字段相同，另有新版本实际整图运行。生产准入false、人工质量待审、通用assemblyInterface仍拒绝；有限策略不能代替一般进入状态/回程包络。

## 整图证据与未覆盖项

| 执行 | 结果 | 实际范围 |
| --- | --- | --- |
| 5条连续巡视 | 5/5 | 全部74个合法有向连接，每条从原出生点出发 |
| 主路、东西奖励远征 | 3/3 | 实际领奖、捷径、回到入口后继续主路 |
| 两闭环×四锯轮初始相位 | 8/8 | 经不同场所实际回到入口 |
| 风铃侧室远征 | 1/1 | 击铃、原服务领取8金币、实际回程、继续到Boss入口 |
| 新入库候选再复用 | 1/1 | 独立库命中后重新实例化整图执行 |

前17条聚合见 `validation-summary.json`，新增库复用独立记录。它们覆盖78/154种方向合法的枢纽有序Port对；忽略单向限制枚举则为172对。其余组合、任意进入资源和任意操作下可达性仍未知，74条边见证不等于一般无softlock证明。

四个真实反例均失败：移低必需平台造成真实伤害；不开Boss标志被实体门挡住；省略风铃射击不能完成侧室/领奖；合法开通捷径后从禁行侧反走被实体门挡住。没有用抽象图检查提前伪造失败。

失败原件按批次保留：宽Dock截住水平跳，强制upper-first又暴露不可行斜跳，最终仅允许明确上层中转并真实下穿；转角碰头落空后调整原跳跃释放并将普通接收面32→48wu，重跑全部巡视；风铃底座下只有步行净空，改成496wu短恢复底路与独立侧井；1wu输入deadband低于原最小步幅导致摆动，改3wu但保留精确落地验收，再跑全套；另有一次编排源中途改动被原Engine冻结检查拒绝，不倒签该批。

## 媒体、成本与集成界限

`lower-loop.mp4`38.77秒/2261帧，`upper-loop.mp4`47.77秒/2801帧：完整闭环、正常1倍60fps、右下实际整图及Motor轨迹。逐帧运动/资源/输入/机关/事件0差异。风铃完整远征127.42秒/7580帧同样0差异；30秒摘录取原片70–100秒，明确不是完整路线。保留初始化/暖机及末尾1秒。4096整图PNG仅改镜头，不搬角色。

Web复用官方Godot共享底包/overlay打包器与原键鼠控制，M整图、R重试、可导出输入；自动浏览器冒烟不是人工试玩。Boss当前是入口目标，没有正式Boss战、存档或区域生态。

本机5次Python具体编译中位243ms、进程峰值约47MiB，不含Module创作、Godot实例化/验证/绘制/下载；headless约190–371物理帧/秒，不是目标设备帧率。软件渲染录像低于实时，Web启动约120MB共享依赖与新包，移动端性能未验。

物理仍绑定工坊12f6cb0与官方4.7.2；最新map-edit main检查仍为b9318cf。没有悄悄更新物理标签或改正式流程。下一步优先缩短重复竖井、提高动作/观察/地标多样性，补更多成熟模块及余下Port组合，再扩跨Seed与一般Macro布局；不得给导航Cell改名计产量。

复现：按WORKSPACE恢复原件后在仓库根执行，每次使用新输出名：

```sh
python3 -m pcg.map_directed.r2_full.validate --name fresh-cover --mode cover
python3 -m pcg.map_directed.r2_full.validate --name fresh-routes --mode routes
python3 -m pcg.map_directed.r2_full.validate --name fresh-phases --mode phases
python3 -m pcg.map_directed.r2_full.growth --name fresh-library-reuse
```
