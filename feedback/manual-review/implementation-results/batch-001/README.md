# 01–05：已确认设计的候选实现与真实 Godot 证据

五个精确设计版本均已实现为隔离可玩候选，21 条设计路线均有无伤、稳定到岸的真实见证，21 条原生包回放及五组键鼠输入冒烟检查通过。**当前不能把五项全部称为技术认证通过：04、05 的定向验证通过；02 去程及 03 高奖励路线未达原 regular 稳健性门槛；01 的首轮资格运行因误选旧预算协议无效。** 不入正式库，不改设计网页或人工意见。

| 编号 | 实现 | 最终验证范围与结果 |
|---|---|---|
| 01 | 原双翼互补门、俯冲怪、四个真实 Port；补齐全部 12 个不同端口方向的控制程序 | 12 路冻结见证及扰动率观测通过；48 个接缝/连续出入观察通过。首轮误选 v1 的 350 次上限，实际 900 次，资格 **INVALID**；后续仅补 84 次入岸/反例并重分析旧轨迹，不重抽留出。72 反例中原分类器保留 3 个越外界标记。技术资格 **UNKNOWN**。 |
| 02 | 左裁一列后 A=(128,704)，保留互补桥、16 币宝箱和高台哨兵 | 去程校准 mild 7/12、moderate 4/12，**FAIL**，未跑该路留出；新建世界的返程通过校准/留出。另三组同世界 A→奖→B→A 均无伤、16 币一次到账、零重置，但不能替代扰动资格。16 接缝观察通过。 |
| 03 | 保留左右岸、两怪与宝箱；实现 (108,400) 的 40×12 可穿平台 | 高路先命中空中怪恢复弹量，落小台后再次起跳；高路校准 clean 11/12、mild 8/12、moderate 2/12，**FAIL**，未跑该路留出。低路通过校准/留出。22 接缝观察通过。 |
| 04 | 按设计增加右下 D 口及 368×32 支撑 | A→B、A→C、D→C、D→B 四路通过原校准/独立留出门槛，32 接缝观察通过，28 反例无否决。原向同场景实测，不推定其余 8 个方向或 Module 镜像。 |
| 05 | 高台增加原生哨兵，保留永久开门和 8 币宝箱 | 同枪开门反冲登岸，再普通跳越怪。校准/留出各级均 12/12，14 接缝观察通过，6 反例无否决。未额外要求杀怪。 |

完整逐路线率、N×N（含自环）矩阵、实际进入/离开资源、源码与输入 SHA、命令和未知范围见 [index.json](index.json) 及 [01.json](01.json)–[05.json](05.json)。部分 Port 封口、镜像/换边、任意资源进入、通用 Map 拼接、人类难度、人工试玩和生产认可仍为 UNKNOWN。原向、全口开放的局部邻岸试件不等于任意 Map 接缝认证。

## 可玩样品

从包含 Git 归档分片的仓库检出，在 Linux x86_64 上运行：

```sh
python3 -m pcg.manual_review.bootstrap_approved_batch001
python3 -m pcg.manual_review.play_approved_batch001 04
python3 -m pcg.manual_review.play_approved_batch001 01 --route C-to-B --replay
```

A/D 移动、空格跳跃、鼠标瞄准/松开射击。`01`–`05` 选择样品，`--route` 选择该设计的路线起点，`--replay` 使用冻结的真实输入。入口与包在 `pcg/manual_review/implementation/batch-001/<module-id>/playable/demo.tscn`。包仍依赖仓库已有的原 Godot `res://` 资源；bootstrap 复用原归档，验证官方引擎和额外六份原资源的 SHA，不附带引擎二进制或缓存。

`playable/load-evidence/` 保留每条路线的真实原生命令、输入、日志和回执；`input-smoke/` 证明键鼠输入确实到达原角色组件，只是自动输入响应检查，不是人工试玩或无伤通关认证。

## 下载短片

均为原生 Godot 60 Hz、1 倍速、保留末尾 60 帧全世界冻结停留。每项仅展示一条代表路线。

- [01 A→B](videos/01-v2/central-two-wing-bridge-choice.mp4)：review-only，原严格比较的 26 个 `support_id` 差异全部保留。
- [02 取奖去程](videos/02-v2/folded-reward-upper-out-lower-back.mp4)：review-only，38 个 `support_id` 差异全部保留。
- [03 高奖励路线](videos/03-v3/one-shot-two-routes.mp4)：202 个物理帧通过原严格字段/事件比较。
- [04 A→B](videos/04-v2/pass-receiver-turn-fork.mp4)：244 帧严格比较通过。
- [05 A→B](videos/05-v3/wall-projection-unlock.mp4)：222 帧严格比较通过。

没有放宽比较器或归一化 `support_id`。03 的首次录制在完成后的展示停留阶段出现原敌人继续 tick 的错误，失败日志/trace 保留在 `videos/03-v1/`；新的展示包装器仅在完成后冻结所有子节点。03/05 的 v3 只修正继承的旧提示文字，不增加内容/留出样本；旧片保留。每段有源绑定、原生 trace、MP4 SHA 和抽帧；已实际查看五项代表抽帧，未记录人工观感批准。

[公网字节复核](public-download-verification.json) 已从提交 `6e69a54a` 下载五段代表 MP4、五个可玩场景及四个归档分片，14 项 SHA 全部一致。后续交付凭据提交不改变这些工件。

## 原始证据与复核

使用原 `WorkshopEngine`、Actor/Motor/Router、弹丸、资源恢复、敌人、互补门和质量门槛。官方 Godot 为 `4.7.2.stable.official.ed1daf0bf`，二进制 SHA `8d106cbe6144c2dc7e881d61d2429c1a8a76e6b22ef48bd5e48dcf934953f71e`；每轮核验原游戏 870 份受保护文件，未改原物理或数值。

原始 Harness 输入共 1713 案：1710 案实际步进，3 案为同世界回程首稿超出 Harness 帧数上限的零帧拒绝。修正预算后另三案真实回程通过。资格、校准、控制修订、反例、无效运行及完整冻结源统一保存在 [38,181,448 字节归档清单](../../../../pcg/archives/approved-designs-batch001-implementation-v1/manifest.json)，共 25,403 条路径、1,654 份去重原件。

```sh
python3 pcg/tools/restore_archive.py approved-designs-batch001-implementation-v1 --verify-parts-only
python3 pcg/tools/restore_archive.py approved-designs-batch001-implementation-v1 --extract
```

`archive-verification.json` 验证全部分片、整 ZIP、每个解压条目的 SHA。`deep-raw-verification.json` 是原 `physics.verify_report` 对 04/05 全部 raw、输入、源快照、率、接缝和反例的只读重推导。`npm-check.log` 是完整 `npm run check` 通过日志。

补齐 Port `aperture/grid/crossing_offset` 时未改碰撞或动作。原冻结 cases 和绑定原样保留在各候选 `revisions/observer-metadata-v2/`；`metadata-reconciliation.json` 显式解析旧 SHA，当前 cases 与验证 cases 一致。旧 01 资格的预算错误不会因元数据修订而变成通过。

重建研究环境额外使用 `python3 -m pcg.manual_review.bootstrap_approved_batch001 --authoring`，它恢复反馈 001 及原 Harness 历史路径别名。已观测资格不得重新抽取留出：复核现有报告；新真实程序需先冻结并通过原 `holdout_guard` 预登记。复现单案可直接用归档 `physics/*.execution.json` 中的真实命令，换新的输出路径，标为重放而非新独立留出。

## 授权与反馈

启动时 main 为 `fd7120b`。期间 main 前进到 `44f9464`，交接队列扩到九项；已逐项确认 01–05 的设计/sourceModule 行完全未变。本任务仍严格限制 01–05，使用 [授权快照](authorization/source.json)，不自动处理后来批准的 06/07/10/12。

待设计会话复核的具体问题见 [design-conflicts.json](design-conflicts.json)。02/03 的失败说明当前参数不合格，不证明设计物理上不可能；未移动怪物、增加安全台、扩大矩形或覆盖设计稿。候选、有限技术结果、人工试玩及生产认可分别保留。
