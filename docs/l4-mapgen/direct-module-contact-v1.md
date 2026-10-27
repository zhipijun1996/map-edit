# 直接拼接 Module 的完整平原 Map · v1

本轮针对用户反馈“module和module之间，填充了很多短平台……module之间是完全拼接的”返工。上一版 `r2-full-v2` 保留为被否决的历史实验；没有将旧录像换名交付。

新入口：`python -m pcg.map_directed.direct_join.run --name fresh-direct-map --mode full`。复用 PR #1 原 R2 平原 Seed 0 的 Mission/Exploration 图，27 场所、39 连接、35 双向和4单向连接；无向投影13个独立环。这个计数描述拓扑，不是趣味评分。正式游戏流程未改。

## 这次如何拼接

`direct_join/layout.py` 用 CP-SAT 求矩形接触嵌入：相连场所的边界必须贴合，接触区有宽度，房间不得重叠。不是先放远房间再插入走廊。保留全部39条图边，不删困难回环。`shape_feedback.py` 将 Module 的接口不可满足项反馈给 Director，最多4轮局部扩尺寸；本次第一轮7个需求失败，第二轮满足。宽448–1280、高384–960世界单位，非统一尺寸。

`direct_join/director.py` 将端口数、准确朝向/位置、玩法职责、能力和回程、奖励/资源要求、空间限制交给现有 Plains Module 生成路径。`prototype/plains/room_modules.py` 在生成 Module 时创建完整地形、自己的边界开口和动态机关。复用原三端口反冲击铃核心；紧凑位置缺失的180高度反冲击铃子挑战，由 `vertical_bell.py` 使用原动作探针和真实射线生成。校准失败原件保留；不能把14个击铃实例称14种新玩法。

`canonical.py` 与 `export_modules.mjs` 复用 Map Notes 原格式和合同检查器，导出27份 `gunman-rush-level-sketch/v1` + `generationContract` 文档。随后从文档 `objects` 重读静态地形、移动轨道、齿轮、钟和门，再交给 `assemble.py` 只做平移实例化。地图配方保存文档ID/版本/SHA和位置。不是导出一套供看的文档、实际仍用另一套地形。

Map层新增地形为0，连接模块为0，短平台补路链为0。338个Module源静态对象拼成321个世界对象，17处垂直接口具有两侧共同声明、几何完全一致的共享落脚面，仅对这17组去重。水平地板在切口直接相接；垂直井道/承载平台属于对应Module，不是Map填充。动态平台的大小/行程可在独立Module文档中查看。

`audit.py` 逐对象核对来源、刚性变换、版本、两侧端口位置/相反法线、未声明跨Module碰撞和齿轮完整运动范围。加一块短平台、拉长平台、移动一个Module产生1单位缝隙、危险扫入邻居，都会被拒绝。此检查独立于物理通行测试。

## 实际 Godot 验证

`direct_join/runner.gd` / `carrier_pilot.gd` 继承已有整图Harness，只发真实Router输入。沿用原Controller、Motor、资源、伤害、ShotLatch、移动平台、奖励服务。每条长路线从地图入口开始；途中不传送、不重建、不补血/补射击次数。

最终结果为14/14条通过，225,818帧实际仿真；逐条读取物理输出的edge-terminal落地记录，核对74/74个有向连接，未以输入计划推断覆盖。

最终批次：`pcg/results/direct-contact-final-v1`。主线、东西奖励路线、击铃奖励回环，加10条接缝巡视。巡视需真实坐标、支撑对象/脚部射线、低速稳定落地，记录实际经过方向，不用抽象图代替。独立反例在 `direct-contact-negative-v1`：禁止取得Boss开门标记、删去r5奖励击铃射击，都应被真实碰撞/动作检查拒绝。

本轮真实失败包括：底板过厚导致连续下穿受限、承载平台与接收面高度不匹配、靠墙下落停在墙顶、齿轮扫入相邻Module、返回路径斜穿危险、出口跳跃滞空不足，以及单向门关闭后截住落点。对应修订没有增加Map补路平台。最后两项接缝修订分别在 `direct-canonical-repair-v1` 的完整巡视中复验通过，之后重跑统一最终批次。所有原始失败、输入、冻结源码和引擎日志按新归档保留。

录像使用同一最终案例的真实输入，正常1倍60Hz连续回放，位置/速度/资源/机关逐帧与headless对照。整图图片为实际Godot场景相机缩放拍摄；Module边界只是只读显示。手动版本复用原键鼠适配器，浏览器测试与原生通行证据分别记录。

## 范围和成本

这是一个完整、多回路、直接拼接的平原实验实例；不是任意Module、任意进入速度或任意能力的通用拼装保证。文档中的未知有向关系、进入状态与通用变换仍为UNKNOWN，生产准入关闭，不能把整图有限策略见证冒充独立Module全部状态通过。技术验证不等于人工趣味认可。

本轮优先解决直接接合和完整地图。现有14处击铃核心主要来自两类动作，33个承载平台也有重复，内容多样性仍需继续迭代。Boss节点是可达目标和门，未加入实际Boss战；隐藏奖励依赖和发现标记不能称完整的隐藏视觉设计。没有把这些未完成项当成功。

CP-SAT布局使用45秒离线预算，8工作线程；保存的布局/需求/Module文档可准确重建，但限时多线程重新求解未保证逐位产出相同布局，不称Runtime45秒可接受。Runtime只实例化保存的Module及其真实机关；本轮未签整机帧率/内存预算，也未证明森林效果。所有物理成本见各批次 execution.json。

依赖复用已有 OR-Tools 9.15.6755（Apache-2.0）；不引入第二套物理、奖励或路线搜索框架。新多端口Module留在隔离候选路径，待独立Module状态覆盖和人类内容评审后才可升级生产。在原CandidateLibrary增加隔离整图候选索引，不建立第二套库。完整整图通过后登记文档和原物理证据的哈希；仅精确匹配相同需求，通用关系不升级。`direct-contact-library-reuse-v1`在另一进程复用27/27份标准Module文档，Module生成调用0，再以真实Godot通过接缝。需求不同不命中此保守缓存；跨Map部分复用、通用进入状态和独立Module准入仍待扩展。已有候选库依然是生产资格的权威入口。


## 查看与复现

[整图与短视频](https://zhipijun1996.github.io/gunman-rush-previews/launchers/MAPGEN-DIRECT-MODULE-01/91796f3eb43db1f82c514f33d7fb9b9b5dfb89db/9a565e1007ef/report.html) · [手动试玩](https://zhipijun1996.github.io/gunman-rush-previews/launchers/MAPGEN-DIRECT-MODULE-01/91796f3eb43db1f82c514f33d7fb9b9b5dfb89db/9a565e1007ef/)。新原生回环5855帧、主线6519帧逐字段一致；两份原生录像和连续40秒节选见 generation/maps/direct-module-v1。公网字节校验与浏览器回执随PUBLICATION保存。

恢复原Godot runtime与官方引擎后，执行：

```sh
python pcg/tools/restore_archive.py direct-module-source-and-failures-v1 --extract
python pcg/tools/restore_archive.py direct-module-run-payloads-v1 --extract
python -m pcg.map_directed.direct_join.run --name fresh-direct-map --mode full
```

默认布局使用已保存的可重建结果；重新布局还需 pcg/requirements.txt 中的OR-Tools。初次发现已登记的候选证据缺失会拒绝，须先恢复原件，不能跳过哈希检查。候选索引沿用原库目录 map_directed/library/map-instances，标记为整图实例有限通过，独立Module与生产仍未准入。
