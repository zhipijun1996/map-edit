# 平原整图拼装、动作净空反馈与验收缺口 v1

本阶段把 PR #1 的 32 核心地点蓝图落实为真实 Godot 整图：39 个 Macro、55 处零间隙接触，414 个静态实体全部来自标准 Module 输出。Map 新增地形为 0。**这是整图拼装实验，尚未达到“比正式单图更大、更有趣、更合理”的关卡交付标准。** 地形仍有明显楼板感，行动家族重复，奖励职责、敌人生态和 Boss 尚未物化；没有进入生产库，也没有新的真人趣味认可。

实现沿用 `research/l4-map-generator` / PR #1。重新 fetch 后，map-edit main 为 `b9318cf82cdd182645b4b42137e5e8eaaeb75731`，游戏 main 为 `26e7f2a4459623f35613a857da8a75e89daa3e62`。正式游戏工作树没有修改。物理仍绑定既有受保护 Harness `12f6cb0`；当前 main 与 Harness 的 `player_tuning.json` 字节一致（SHA-256 `65abb4abffd122f79bc4718a94e6db1bbe19a8e2c5dcdac314aa10cd9698114c`），这不等于整个运行时已迁移到 main。人物、移动平台继续走上一阶段真实正式安装器，完整敌人、Boss、前景和战役的统一仍未完成。

## 实际链路与增量

`region_scale/design.py` → 原 PR #1 `region_network.construct(...,32)` → 原接触布局 `direct_join/layout.py` → `direct_join/director.requests` → 既有 `CandidateLibrary.find_direct_instance` → `regional_macros.generate` 对原 `room_modules.generate/routes` 的隔离内容适配 → 原 `canonical.export_reload` → 原 `assemble_modules/audit` → `CompleteEngine` / 原 PlayerMotor、Controller、资源和动态 Cell。

没有另写任务图、探索图、物理模拟、模块格式或候选库。仍输出 Map Notes `gunman-rush-level-sketch/v1` 和 `generationContract`。独立端口关系、通用状态传递及完整动作净空仍为 UNKNOWN，有限整图轨迹不能替它们签署准入。

- `direct_join/layout.solve` 增加可选输入图和内容尺寸约束，保留旧默认入口。首个固定蓝图得到 39 个变尺寸接触预约区域。
- `room_modules.py` 增加显式开放边界、可关闭旧可选核心等能力；旧默认封闭模板保持原选择。预约框不生成外墙。
- `regional_macros.py` 复用实测 180wu 反冲核心，在两处纵向通路形成真实空中击铃反冲；其他角色仍主要是旧词汇，不能称为完整区域内容生成器。
- `direct_join/director.py` 增加 opt-in 联合端口列搜索。复用原候选列，有限回溯最多 25,000 次；分离同一模块的上方升降井与下入口，避免停靠平台成为入口顶棚。
- `region_scale/feedback.py` 实际读取失败整图与源动态范围，运行一次有限空间反馈。自动解析出的 Challenge / seam 与随后重验的接触规格完全相同。图节点和边保持不变，Map 不填平台。
- 非服务层跨井改为先观察原平台相位、再执行原跳跃。遇到可走出边缘的上层单向支撑时，使用原移动输入走出；避免全局下穿屏蔽期间一起穿过目标层。旧策略默认行为不变。
- `check_footprints.py` 扩展原源对象审计：42 个移动平台全行程、6 个门体均在所属预约空间内；预约空间外的静态实体只允许显式共享接缝落点。这仍不是任意动作净空证明。

## 为什么淘汰直接放大的版本

首个真实整图 `full-region-physical-stress-v2` 主路通过，却用时 127.4 秒、射击 0 次。它证明“能生成、能走到终点”不足以满足平原设计。没有把这张图按规模宣布成功。

加入动作需求后的候选主路约 81 秒、6 次射击，但扩大覆盖暴露了三类真实问题：升降平台横穿/入口干扰、长枢纽短动作超时、跨井途中撞到上方停靠平台。初次核心覆盖为 7/12。后续策略修正也保留了失败，包括过短跳跃、错误等待锚点、过窄 settle 死区和一次 GDScript 类型推断编译失败；没有删危险、传送角色、补资源或重抽获胜 Seed。

一个具体例子：旧布局 `r6` 的升降井与下入口同列。失败帧角色位于 `[2880.7434,4412.0752]`，停靠平台中心 `[2816,4382]`、尺寸 128×24，平台底面约贴住角色头部。把等待延长不能修正这个空间接口。联合端口约束将两列分开，随后整图重验。另一个问题是 `r18` 的非服务层横穿；必须先避开上方停靠平台，再跳过真实井口。

这些是开发迭代与基础设施修复记录，不是等预算算法优劣实验。早期日志中的 `module_generator_calls=39` 只计标准输出物化，漏计另外 39 次结构分配探针；当前代码分别记录两者与总调用。旧日志原样保留，不改历史数字。

## 当前真实覆盖

冻结候选：`pcg/results/full-region-phase-aware-calibration-v1`。

|证据|结果|边界|
|---|---|---|
|两条进场路线 + 营地连续回程|3/3|同一完整世界内连续运行，不重建/回满|
|核心有向边覆盖，12 条从入口出发的巡回|12/12|实测覆盖核心及 Boss 入口 90 个方向；Boss 为地点目标，未实例化战斗|
|独立初始相位样本|12/12|预先固定 seed 94751039 的 4 个随机相位 × 3 条路线；两相位接近，不称总体成功率|
|逐枪省略 + 首枪延长跳跃反例|7/7 未完成|只否定这些有限较低成本策略，不证明所有门无法绕过|
|最新原生录像|4927 帧逐字段相同|完整位置、速度、输入、资源、动态 Cell、敌人/机关事件及最终 extra；只归一化原进程 ObjectID|
|手动 WebGL 冒烟|通过|原键鼠 Router 的移动、跳跃、射击、重试、整图；不是真人通关|

主路 82.12 秒、6 枪；另一进场路线 103.5 秒、3 枪；营地往返 108.88 秒、0 枪。这些是固定自动策略的实际成本，不是玩家平均通关时间。两条进场路线在 Boss 前不共用边。

当前 55 条逻辑边有 106 个有向职责，实际完成覆盖 90 个；剩余 16 个方向属于两条奖励远征及未兑现的回程捷径。6 个奖励职责未变成真实宝箱，不在地点中心自动发钱，也不预先打开其奖励回程旗标。`reward-fit` 的生产器探针发现 `r15` 和 `exp0_2` 暂无兼容核心；另外四处的动作核心存在，也仍需封闭宝箱空间和连续回程实测。

全图实例候选入库实际被既有库拒绝：`actual_map_directed_edge_coverage_incomplete`。未把核心巡回全部通过冒充整图入库，更没有把候选变为生产内容。当前复用搜索是既有 exact-demand 整图候选索引；逐 Module 的状态匹配和按需适配仍未完成，自增长库闭环不能因此宣布完成。

## 与正式单图的差距

正式 main 的相同 5 Seed / intro、advanced 基线为 20–23 地点、58–68 个较小 Module。当前是 39 个 Macro、32 核心地点，粒度不可直接比较。当前世界外框 7232×4844 wu；探索网络地点较多，不等于有效探索空间已超过正式地图，也没有达到既定 1.5 倍有效面积和 96–128 内容预算。

当前主路静止世界速度的帧占约 46.5%，替代路线约 54.7%。其中包含观察、瞄准和稳定到达，不能直接当无聊时间，但与长楼板、频繁升降等待一起表明节奏仍需重做。6 次反冲使用的是重复的同类关系，不是 6 种玩法。17 个数学独立环也不等于 17 个有效探索回环。

正式游戏已有实际敌人、宝箱、Boss、地图发现和战役；本候选敌人/宝箱/Boss 均未物化。不能依据更多图节点或技术通过声称整体优于正式游戏。截图中楼板感依然很强：根因是预约矩形之后才铺楼层的旧内容词汇，下一步必须让地貌、挑战关系和真实多端口 Macro 的形状先参与空间设计。

离线 CP-SAT 首轮 45 秒预算，保存的是实际可行布局；多工作线程求解不承诺再次运行得到同样的首个布局。固定布局、源与输入可复现实验。Headless 输出全量轨迹的墙钟、子进程 RSS 和软件录像成本不是 shipping Runtime 生成时间或玩家 FPS。当前更适合离线 Director/内容制作，不具备正式 Runtime 接入结论。

## 下一轮必须满足的内容合同

1. 从四个区域职责提出不同地貌/动作需求，先匹配实际 Macro 占用和动作范围，再嵌入；不能继续扩大薄楼板词汇或重复竖直反冲梯。
2. 落实 6 个奖励职责，优先生成失败的 `r15`、`exp0_2` 所需多出口挑战；宝箱价值绑定实际额外成本、危险与回程。
3. 真实敌人/机关组合与门的绕过反例必须参加整图验证。开铃计数不证明门必要，也不证明整个锁区隔离。
4. 主线减少无目的长走和升降等待；支线承担更深入的连续技巧。保留原始成本，不为过关降低阈值。
5. 多 Seed 的完整空间/物理及主游戏当前运行时接入，仍是验收职责；现有 3 Seed 蓝图只有这一 Seed 做了物理物化。

## 复现与查看

恢复已有 runtime、open-valley、valley-complete、formal-style 依赖，再恢复本轮 `full-region-spatial-v1` 归档。新批次目录不可重用。原始失败、输入、压缩输出、源快照、病例/模块 SHA、动态状态和媒体都保留。

```sh
# 有界失败 → 空间需求反馈；不修改旧结果
python -m pcg.map_directed.region_scale.feedback \
  --source pcg/results/full-region-stable-policy-v1 \
  --failed-run pcg/results/full-region-stable-core-v1 --name fresh-feedback
python -m pcg.map_directed.region_scale.materialize \
  --layout pcg/results/fresh-feedback/layout.json --name fresh-region --mode main --profile recoil
python -m pcg.map_directed.region_scale.verify \
  --source pcg/results/fresh-region --name fresh-core --mode core
# 标准输出、源实体、全行程和门体
python -m pcg.map_directed.region_scale.check_footprints \
  pcg/results/fresh-region/compiled.json pcg/results/fresh-region/footprints.json
```

[本轮真实整图、连续短片、完整路线、任务状态与结构化数据](../../generation/maps/full-region-spatial-v1/report.html)。最终公网地址与下载 SHA 见同目录 `PUBLICATION.json`；当前状态始终为 `target_met=false`。
