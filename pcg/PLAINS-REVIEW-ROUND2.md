# 平原连续挑战：第二轮生成与视频审核

2026-10-24。分支 `main`，前置版本 `3b9f1d4`。本轮已完成生成、独立物理筛选和原生录像；下一关是人工观感审核。人类观感反馈、手动试玩、批准仍均为 **0**。6个技术候选不是6种玩法，更不是已批准的量产库。

[播放及下载入口](https://zhipijun1996.github.io/map-edit/generation/) · [连续短片 R，17.27秒](https://zhipijun1996.github.io/map-edit/generation/videos/plains-round2/all-samples.mp4) · [模块图与Map Notes JSON](https://zhipijun1996.github.io/map-edit/generation/contracts/plains-round2/)

## 本轮实际创造了什么

保留现有动作语法、轨迹生成接收面、真实Godot验证和按行为分组的离线生产路线。新增连续第二段动作和局部折返，而不是手工画好完整Module后换Seed。

- **R01：击钟抬升 → 落台恢复 → 低顶棚下第二次反冲 → 齿轮区。** 第二段接收平台、顶棚、荆棘位置由实测运动生成。两次普通起跳、两次射击、两次落地都须实际发生。
- **R02：击钟登台 → 转身折返 → 改变瞄准方向反冲 → 落台与齿轮区。** 保持第一段方向，在内部反转第二段路线，不是整体镜像。用持续的实际速度与输入确认转向，刹车抖动不计新动作。出口朝西，单独声明方向。
- **R03：空中命中怪物回充 → 第二枪改瞄风铃 → 反冲落台 → 齿轮区。** 原EnemyActor、子弹、伤害和回充组件实际运行，事件及空中射击资源增加共同证明回充；不能把落地恢复计为空中命中回充。

R01/R02共用较多机制，是否足够不同仍需人评。这是3条实际执行动作链的代表，不是证明算法能自由发明任意动作。动作链和几何由程序构造、测试；本轮没有调用大模型逐模块生成，也没有训练模型。

## 运动参数和失败修复

只允许移动、普通单跳和反冲；无二段跳、墙跳或钩索。原始角色脚本、资源、碰撞和正式枪口保持不变。空中射击上限1次，真实命中或落地按原游戏恢复；射击不额外扣精力。运行绑定游戏 `12f6cb0`；审计当前游戏main `cd4989a68613e0b457cdfd5e252634dd57008505` 对应机制未变。原870份保护文件逐SHA核对，漂移0。原始许可和素材归属沿用 `prototype/godot/asset_licenses_provenance.json`。

官方Godot `4.7.2.stable.official.ed1daf0bf`，二进制SHA256：`8d106cbe6144c2dc7e881d61d2429c1a8a76e6b22ef48bd5e48dcf934953f71e`。

修复了此前跑批中断的具体原因：快速headless退出时，原风铃的Ogg音频播放对象尚未被音频线程释放。旧输入重复10批中3批报错。新增 `prototype/godot/plains_lifecycle.gd` 仅在测试场景拆除时停止并解绑音频、清理子弹，等待真实播放对象的WeakRef释放，500ms超时仍报错；不屏蔽错误、不修改角色物理。初步24批/288案例无退出错误；最终冻结源回归 **30批、360案例、40848帧逐字段一致、0引擎错误**。这些是重复基础设施回归，不是360个新Module，也不并入质量试验样本。

连续关卡探索也留下了失败：首轮折返接收面挡住第一跳/子弹；后续先检查原前缀轨迹与新几何交叠，再整段真实重验。怪物链最初固定方向对误差脆弱；改为输入策略在射击时按实际目标位置瞄准，再独立叠加瞄准噪声。它不设置玩家位置/速度，也不赠送资源。目标过高又导致向下反冲、扰动后落坑；因此降低目标，重新模拟飞行并生成接收面。所有修改只用发现/校准集，失败批次保留。

## 固定选择与新留出数据

校准合并18个候选，只合并已有数据，不冒充新增模拟。按**实际执行动作链**分组，每组最多2个，排序为校准质量再UID。选择规则冻结后只跑一次新留出Seed `104300711`，没有按留出结果再调整几何、门槛或挑幸运相位。

本轮正式生产：**6候选、3行为组、6技术通过、3供视频审核代表，416次真实物理运行、35批、0引擎错误**。其中正常策略216次（6×3档×12），替代策略200次。整次验证生产耗时 **85.44秒**；这是该批验证成本，包含反例测试，不是从零发现新Module的端到端时间，也不是无限量产性能结论。每批记录实际wall/CPU和子进程峰值RSS，详见 `physics/*.execution.json`；RSS为系统累计子进程高水位，不当作独立单模块内存测量。

| 代表 | 无输入误差，随机相位/敌人初始冷却 | 轻微误差 | 较大误差 |
| --- | --- | --- | --- |
| R01 连续向前 | 12/12 | 12/12 | 10/12 |
| R02 内部折返 | 12/12 | 12/12 | 10/12 |
| R03 怪物→风铃 | 12/12 | 12/12 | 11/12 |

轻微误差：动作时序±1帧、瞄准±2°；较大误差：±3帧、±6°，实际采样见 `evaluation.instantiate` 和原输入。候选门槛沿用regular：clean≥0.90、mild≥0.85、moderate≥0.65，且低成本替代策略不得通关。另3个同组参数变体较大误差分别10/12、9/12、10/12，未计作3种新玩法。

这些是固定程序策略的有限测试，不是人类成功率、最优路径证明或真实玩家难度。每个12样本也有显著不确定性，例如12/12的Wilson95%下界约0.757；不同候选共享扰动条件，不能把样本相加冒称独立观测。

替代策略保留原始结果：

| 替代策略 | 无伤稳定到达 / 次数 |
| --- | --- |
| 全部不射击 | 0/24 |
| 不射击并延长普通跳跃 | 0/24 |
| 仅省略第一枪，保留时间间隔 | 0/24 |
| 仅省略第一枪并延长本段跳跃 | 0/24 |
| 仅省略第二枪，保留时间间隔 | 0/24 |
| 仅省略第二枪并延长本段跳跃 | 0/24 |
| 错误瞄准 | 0/24 |
| 移除怪物、保持两枪策略 | 0/8 |
| **跳过齿轮观察等待** | **22/24** |

反例每个候选4个相位，不是24个独立相位。最后一行说明**不能宣称必须观察或等待齿轮**：当前保守等待策略在很多相位多等了。视频完整保留等待，交给人工判断节奏；没有把它包装为必需决策。替代测试范围之外的捷径仍未知。

## 输出契约和录像可信范围

沿用 `gunman-rush-level-sketch/v1` 加 `generationContract`，新3份文档及SVG在 `generation/contracts/plains-round2/`。6份候选完整导出也在生产归档。此次增加**第一次输入之前**的实际进入快照，区别于第0帧执行后的状态；保留真实出口观测，不扩张为对所有进入状态的保证。R02有显式西向出口。

允许交付UNKNOWN设计候选。本轮进入状态范围、完整动作净空、接缝、未验证变换、回程和通用出口资源保证等仍有UNKNOWN。所有 `source.integration` 均为false，自动地图拼装准入仍关闭；没有声称Macro或整图通过。图、文档内容版本与视频中的原始Module SHA交叉校验。现有工程导入保留身份，改几何会使旧合同失效。

录像是真实原生60Hz、1倍速输入回放；每段完整动作约4.67秒，末尾另保留1秒冻结完成画面，加引擎起止帧后视频约5.75秒。合集只顺序拼接3个完整单段，无删等待、无补画轨迹。`pcg/delivery/plains-phrase-video-v2` 在完成初版录像后增加完整逐帧观察，最终公开此版本：**280+280+281=841帧**的位置/速度/输入/射击次数/跳跃/精力/HP/平台/齿轮/支撑等字段与headless见证完全一致，Cell事件、敌人HP/位置/状态、风铃状态也逐帧一致。仅归一化伤害来源里进程局部的Godot ObjectID后缀。原生追踪JSON和SHA随 [manifest](https://zhipijun1996.github.io/map-edit/generation/videos/plains-round2/manifest.json) 公开。

门旁的同色风铃图标是原机关关联标记；本适配器没有在那里额外放一个可射击风铃。是否容易误读也可反馈。

本地Chromium实际解码4组合集并下载R核对SHA，3个新SVG正常解码；JSON导入身份、浏览器与Node版本哈希一致，几何修改后失效状态刷新仍保留。自动检查不计人工评分。

## 复现、源码和完整原件

源码位置：

- `prototype/plains/phrases.py`：动作续接、接收面与折返前缀过滤。
- `prototype/plains/{phrase_pilot,enemy_phrase_pilot,reactive_pilot,relay_pilot}.py`：有界发现/修复实验。
- `prototype/plains/{evaluation,produce}.py`：实际动作描述、扰动、冻结选择、逐枪省略反例和regular准入。
- `prototype/godot/runner_plains.gd`：原输入路由与实际Cell目标瞄准；`plains_lifecycle.gd`：退出资源回收。
- `prototype/plains/stability_round.py`：冻结源的基础设施回归。
- `tools/record_plains.py`、`prototype/godot/movie_plains.gd`：完整原生回放与逐帧比对。
- 仓库根 `tools/export-module-contracts.mjs`：输出适配；`module-contract.js`：契约检查及保守准入。

仓库根恢复（所有原始成功/失败及阶段快照一起保存，不覆盖历史）：

```sh
python3 pcg/tools/restore_archive.py godot-runtime-v1 --extract
python3 pcg/tools/restore_archive.py plains-generation-v1 --extract
python3 pcg/tools/restore_archive.py module-contract-v1 --extract
python3 pcg/tools/restore_archive.py plains-review-round2-v1 --extract
# 安装已注明SHA的官方Godot4.7.2，按WORKSPACE.md完成导入。
cd pcg
# 重放已冻结的18个校准候选选择与同一留出；新目录，不能覆盖历史。
python3 -m prototype.plains.produce --name round2-reproduce --calibration plains-phrase-final-calibration-v1 --holdout-seed 104300711
# 基础设施重复回归，与新生成质量试验分开。
python3 -m prototype.plains.stability_round --name round2-stability-reproduce --production plains-phrase-production-v1 --batches 30
# 要探索新候选，使用新实验名；旧holdout已经公开，不再作为未来独立留出。
python3 -m prototype.plains.phrase_pilot --name next-phrase-discovery --bases plains-phrase-bases-v1
```

新归档 `archives/plains-review-round2-v1` 包含音频诊断、控制回归、最终稳定回归、所有本轮发现/校准/失败/生产、每阶段运行源快照、完整输入输出、录像v1/v2及浏览器/命令日志；每文件、分片、整体均有SHA。重建AVI、引擎和导入缓存不重复上传。生产6份候选与审核3代表的UID/源证据绑定分别见 `results/plains-phrase-production-v1/{protocol,catalog}.json`、`results/plains-phrase-review-v1/playlist.json`。最终交付源另冻结在归档 `results/plains-round2-source-v1/`，不能将它冒称早期失败运行的源。

## 现在需要的人工审核

直接按R01/R02/R03聊天反馈即可：哪段想玩、哪段无聊；R01与R02是否只是相似套路；R03第二枪目标是否看得懂；齿轮等待是否拖沓。不要求亲自试玩，不从视频反馈编造手感或玩家通关率。

获得反馈后才决定保留哪类结构，优先缩短无意义等待、增加可读的压力选择，再以新留出重新验证。当前适合继续离线生产与审核；尚无稳定大量高趣味Module、任意能力组合、Runtime预算或苦痛之路级设计的证据。仍先解决Module质量，再谈Macro/Map拼装。
