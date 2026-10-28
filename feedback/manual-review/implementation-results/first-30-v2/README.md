# 前 30 项人工审核实现交付

基于 main `2ccd4ea5` 的冻结交接：保留 15 项，废弃 15 项。设计 JSON、审阅网页、队列与人工意见未修改。实现使用统一 Module skill，候选留在隔离目录；人工设计保留不等于已试玩或生产认可。

**15 个候选均可玩，55 条名义路线通过原生 Godot 加载和输入回放，另有 17 的同世界连续回程样品。完整本地技术检查：12 PASS、17 FAIL、02/03 UNKNOWN。** UNKNOWN/FAIL 均未入正式库；其余候选也未自动升级生产状态。

| 编号 | 本地技术检查 | 原生路线数 | 实现与证据 |
|---|---|---:|---|
| 01 | PASS | 12 | [b31-n06-fourport-two-low-ingress](01.json) |
| 02 | UNKNOWN | 2 | [b31-n08-reward-return-interface0](02.json) |
| 03 | UNKNOWN | 2 | [b31-n12-three-side-port-interface0](03.json) |
| 04 | PASS | 4 | [b31-n14-static-three-sideports](04.json) |
| 05 | PASS | 1 | [b31-n16-west-low-east-high-interface0](05.json) |
| 06 | PASS | 6 | [b31-n17-threeport-cross-shaft-v2](06.json) |
| 07 | PASS | 1 | [batch30-block-c02-0](07.json) |
| 10 | PASS | 1 | [batch30-block-d05-0](10.json) |
| 12 | PASS | 16 | [batch30-block-n04-0-2](12.json) |
| 17 | FAIL | 1 | [batch30-d04-0](17.json) |
| 23 | PASS | 3 | [batch30-n11-e-e-width96](23.json) |
| 25 | PASS | 1 | [batch30-n19-west-high-east-low](25.json) |
| 27 | PASS | 2 | [block-demand-a1-bidirectional-risk-reward-1](27.json) |
| 28 | PASS | 2 | [block-demand-a3-bidirectional-map-traversal-0](28.json) |
| 30 | PASS | 1 | [block-demand-c01-0](30.json) |

## 01–03 的归因与修正

- 01：首轮误选单件 350 次预算，却实际执行 900 次，旧结果未追认为通过。修复 D→C 的真实接地等待，并按 full v2 预先计算预算；新正式记录为 984 次。C 口额外射击造成的外部空间绕行按精确设计/反例范围单列 UNKNOWN，仍不算内部解。
- 02：修复出发/重设落点的顺序，基于实际高度松开跳跃；避免下降中撞柱。最终去回两路完整校准均 36/36，原生回放均通过。
- 03：复用原敌人、子弹和回充机制，按实际死亡/射击就绪/落地状态控制；先落小平台再选择高、低岸。最终高路沿用已通过校准与留出的真实程序，低路修复后完整校准 36/36；两路原生回放通过。

这些事实说明旧流程缺少协议/预算预检、控制 DSL 持续状态检查及真实触发观察，也存在消费者/观测器缺口。失败的固定策略不能证明 Module 无法实现。skill 已先行修订；本轮没有通过改设计、补弹、删危险或放宽门槛救过。

**02/03 的最终修订尚未获得新独立留出资格。** 原协议每来源最多两次替换池已用完；追加各一轮的 [具体预算请求](proposed-extra-holdout-budget.json) 待用户答复，未分配新种子。之前失败记录和原门槛保留。

## 其余边界与未完成项

- 17：去程和同一世界 A→C→A 的实际回程、奖励 12 币及原生回放通过；无世界重建/状态注入。当前控制策略仍未通过扰动门槛，有限控制小样也未找到合格修订。保留 FAIL；任意全新 C 初态返回 UNKNOWN。该失败尚不构成设计无解或修改设计的依据。
- 06：新双齿轮 Cell 使用原真实子弹和接触伤害；两条齿轮带同步收回/再次伸出，原平台保留。实际正反检查保留。
- 12/23：AIR 按完整 24×36 身体向下穿越验收，不冒充地面落稳；三偏移接口实测通过。23 的两个入口探针错误继承空中出口目标，仅修正探针目标元数据并重跑两次；全部原校准/留出和失败原样保留，补证通过严格谱系/原 raw 校验。
- 07/12 的付出额外射击、退出矩形再回来的反例保留为外部空间依赖 UNKNOWN；23 的额外跳跃同理。它们不算模块内部合法解，名义路线的完整身体约束未放宽。
- 封口组合、镜像、任意进入状态、完整 Map、人工试玩和生产认可均 UNKNOWN。

## 废弃删除

删除 08、09、11、13、14、15、16、18、19、20、21、22、24、26、29 的 `modules/<id>/` 实际目录及 catalog 项，225→210。未移入回收库；[删除回执](deletions.json) 保留版本、文件数和历史迁移信息。前 30 项以外未处理。

## 可玩、录像与复核

各编号 JSON 的 `nativePlayable.path` 指向当前可玩目录。已安装仓库原 Godot 资源后，例如：

```sh
pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 --path pcg/prototype/godot "$PWD/pcg/manual_review/implementation/first-30-v4/b31-n12-three-side-port-interface0/playable/demo.tscn" -- --case 0
```

A/D 移动、空格跳跃、鼠标射击；加 `--replay` 回放冻结输入。17 的 `earned-loop-playable` 是同世界回程样品。04/05 复用未改变的上一轮实现与原生证明。

本轮录像位于 [videos](videos/)，均为真实官方 Godot 4.7.2、原生 60 Hz、1 倍速度。每段有 case/source/raw/native trace/SHA 和比较记录，保留 1 秒明确尾停留，无剪切或加速。严格比较失败的片段明确为 review-only，所有差异另存；不能替代技术证明。新增 16 段中 6 段严格一致、10 段 review-only；04/05 的旧片仍单独引用。

已查看 13 个首次代表片的中段抽帧：完整矩形、Port 与主要地貌可见，齿轮/风铃/桥的关系可辨。抽帧不等于看完所有影片或人工试玩；新 07/10 片和 03 高路片已有完整逐帧比较/差异记录，未冒称 AI 已逐帧观看。

原 raw 与所有失败、零帧拒绝、控制筛选及源码快照已放入 `pcg/archives/approved-first30-implementation-v2`：100 个运行目录，83,423 个逻辑文件，8 分片，约 80.8 MB；整包 SHA `980fccd527923cc977a195848d10bdff0b3c9fb3e167af55079b8d964fbd0f8a`。旧首轮证据仍在原 v1 归档。

```sh
python3 pcg/tools/restore_archive.py approved-first30-implementation-v2 --verify-parts-only
python3 pcg/tools/restore_archive.py approved-first30-implementation-v2 --extract
python3 pcg/tools/restore_archive.py approved-designs-batch001-implementation-v1 --extract
python3 -m pcg.manual_review.summarize_first30_v2
npm run check
python3 -m unittest pcg.migration.tests.test_godot_package pcg.migration.tests.test_holdout_guard pcg.migration.tests.test_pool_protocols pcg.migration.tests.test_offline_reanalysis pcg.migration.tests.test_review_air_runtime
```

审计重跑只读复核既有证明，不启动新校准/留出。重建历史 Harness 需与快照一致的 `/workspace/map-edit-task-a` 仓库符号链接；可玩包入口不使用 Harness 控制搜索。全部运行与原游戏提交 `12f6cb006d7119598e3235f4ca4f7323e4c9d092` 绑定，870 个保护文件无修改。

验证：`npm run check` 全部通过，catalog 210 项；框架回归 42 项（1 项跳过）；新 Cell/AIR/反例范围/入口补证含真实正例及故障反例；归档逐项 SHA 完整核验通过。具体日志见 [verification](verification/)。
