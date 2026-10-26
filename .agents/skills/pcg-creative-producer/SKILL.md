---
name: pcg-creative-producer
description: 用当前 Codex 大模型持续提出、实现、反驳并筛选不同玩法关系，交给原 Godot 工坊生产。
---

先读 `AGENTS.md`、`pcg/WORKSPACE.md`、`pcg/OUTPUT-CONTRACT.md`，并使用 `pcg-module-factory`、`pcg-physics-contract`、`pcg-video-review`。这是模型主持的内容生产流程，不是随机模板替代模型，也不是无人值守的在线服务。

## 当前优先：反冲平原

最新人工否定见`pcg/feedback/workshop/junction-boring-observation-v1.json`：J06/J03的四份实现无聊，暂扣于优选之外。原五案D02—D05的价值在具体动作/后果的耦合；不以最低实现成本选静态几何来代替。先冻结不可丢失的体验与地貌，单份可玩原型表现出来后才做接口适配/完整批次。物理通过与模型接口审查不能替代体验实现，详见多端口skill的纠偏段。无需新增逐件人工批准流程，仍在已授权范围内推进。

**多端口的新优先级**：用户已指出旧多口偏向“挑战＋额外安全口”。所有三/四口创意、改造与Map路口请求先执行 [pcg-multiport-junction](../pcg-multiport-junction/SKILL.md)：先输出不同空间构图、共同选择点、端口地域职责和有向意图，再接原工坊。环岛仅是试例；不默认全连通，也不默认所有三/四口都从A出2/3口。旧批次出口数量达标不等于新设计标准达标。原空间需求见`pcg/feedback/workshop/multiport-spatial-choice-feedback-v1.json`，旧15版侧边审查见`pcg/creative-production/curation/multiport-junction-audit-v1.json`。用户后已授权实际实现；首次J06/J03落地受到上述明确否定，不再把审查阶段的范围或模型结论当作当前状态。

最新已完成用户50件目标：`generation/workshop/plains50-v1/manifest.json`、`pcg/creative-production/curation/plains50-final-ai-review-v1.json`、`pcg/creative-production/plains50-receipt-v1.json`。新增39双口/7三口/4四口，21审阅组+29适配不是50新家族。公网发布回执在`generation/workshop/plains50-v1/publication-v1.json`。继续工作先读本批新失败和方向/资源缺口；旧campaign-v2的未完成状态不能覆盖新回执。双口配方400、多口900为本批运行前预算，后者仍逐路执行原门槛；不是事后降低。新版注册视图`plains_workshop/catalog_v2.py`与统一`plains50_catalog.py`读取原库。下一批根据新需求继续，不把已完成50计作再次新增。

用户已整体正向评价20项，当前收窄为平原，特殊能力仅反冲（保留移动/普通单跳）。先执行 [平原内容配方流程](references/plains-recoil-workflow.md) 与 `pcg/prototype/creative_batches/plains_workshop/profile-v1.json`，读取最新反馈；钩索/墙跳/二跳内容留作其他区域，不继续为数量扩展。能力兼容与反冲教学职责分别评估。

## 两个循环

用户要求持续扩库时，执行 [批次生产与 AI 去重协议](references/batch-production-v1.md)。当前续作账本为 `pcg/creative-production/plains-campaign-v2.json`，不是已完成回执。每轮先读取账本关联的最新人工反馈：PR-D01已被用户否决为冗余，不再作为新创意实施；PR-D02至D05获设计正向意见，不表示技术/试玩/生产通过。不逐项等待人工同意，先完成授权范围内的候选生产和批次筛选。

外层由实际大模型会话工作：读人类原话、Map Challenge Specification、现有家族与持久失败 → 提出因果假设 → 判断 Cell/规则缺口 → 在隔离路径实现 → 看实验轨迹修订。内层使用 `pcg.prototype.workshop.production_loop.run`，由程序有界搜索几何和控制、做原 Godot 验证和导出。规则用尽返回 `needs_design` 给外层；禁止重置 Seed、改标题或把不支持的创意替换为普通房间。

本批实际创意来源是用户授权的当前 Codex 会话及子代理；`pcg/creative-production/campaign-v1.json`、各任务设计卡及源码保存身份。外部 `creative_producer.py` 确实调用过 Codex CLI，返回401；失败回执保留。未来只有实际调用成功并保存原提示、响应和回执后，才能记录外部模型成功。不得虚构模型版本、训练、API成功或后台持续运行。

## 每轮必做

1. 先读候选库及 `pcg/feedback/`。人工创意稳定ID/source_type=`human_idea`，原话逐字保留；模型解释、实现猜测另存。Map需求保留端口、能力、空间、资源、风险收益、回程条件。
2. 每张提案卡写：观察与决定；一次行动对人物/世界的因果；所需Cell/能力/资源；支撑因果的地貌；奖励的可见性与取得；失败恢复；方向差异；廉价解法；与既有关系的体验差异。状态区分提案、可执行规则、缺口、技术候选、人工观感、生产认可。输入 `implemented=true` 没有注册规则和运行证据时无效。
3. 按机制关系拆工作，用户或适用指令允许时可用子代理。实现者和新颖性评审者分开；所有评审都是模型评审，不能替代人类。共享Engine/合同的改动在启动实验前统一协调；一轮源码冻结期间不得编辑冻结树。每个新规则放 `pcg/prototype/creative_batches/<owner>/`，通过 `extra_sources` 加入真实绑定。
4. 用原生产循环：合同预检 → 每接口最多4个候选、两接口的清洁/小扰动筛选 → 精确发布几何和相位的廉价解法 → 原regular完整校准 → 留出前固定选择与见证 → 独立留出。实际协议在运行前写入，失败不可事后降门槛。动态相位、身体净空、资源、奖励、出口稳定和适用恢复都看真实轨迹。新Cell薄接原组件，不重写角色、模拟、候选库或Map Generator。
5. 反例问“是否绕过因果关系”，不问“是否复现指定按键”。安全且仍完成相同核心关系的替代策略必须接受。省略关键动作、长按普通跳、提前开门、越顶、入口同步、重复同墙复位、射杀当钥匙的敌人等按机制主动扩搜。保留有限搜索范围；未找到绕法不构成不存在证明。
6. 一旦反例推翻旧候选，新增 `pcg/content-technical-withdrawal/v1` 通知，原件不改；后续检索拒绝该版本。修订用新几何/规则/版本和新校准留出。失败按规则源码SHA+需求持久化；同源重跑跳过，不用无意义重复消耗预算。
7. 创意阶段只预筛明显重复/已否决关系；积累技术候选后进行独立模型批次审查，比较玩家决定、因果、路径/资源权衡。尺寸/Seed/装饰/动作词/多堆一个机关不增加家族。批次评审为代表、有效适配、冗余变体或待查分别留理由和版本绑定，不删除原件，不把重复写成技术撤回。既有基线不算本轮新内容。复合关卡只有产生新的决策耦合才可新增关系计数。评审不能把技术不通过的内容补算进去。
8. 通过原标准导出 `gunman-rush-level-sketch/v1 + generationContract`，用原 CandidateLibrary 入候选库。版本绑定全部地貌/端口/策略/Cell/证据。每个有向关系独立声明，未验回程/状态/接缝为UNKNOWN，不补平台、传送或资源。随后在新进程从磁盘原库检索相同完整需求，证据逐SHA验证，记录生成调用0。
9. 第一种通过即交B；不用等全批。单Module只证明局部有限策略，未知接缝和整图由B用真实连续验收。缺口返回具体冲突、搜索范围和可协商条件。
10. 每关系发布短MP4、标准JSON/SVG、可玩场景、原case、源码/校准/留出/反例/失败索引。原 `workshop.record` 逐帧比较不可放宽；自有Cell通过 `--scene` 薄消费者载入。视频观感、实际试玩、技术通过、生产认可各自记录。没有人评不得自动生产准入，但不阻断候选与B集成。

## 本轮复用

严格20项选择：`pcg/creative-production/novelty-review/selected20-v2.json`；独立评审和反例标签审计在同目录。`generation/workshop/creative20-v1/` 提供交付目录。原六个基线、双环Macro、recast和普通升降适配不计这20项。

下一轮不要从零写20个脚本：先用现有规则适配Map需求；真正未支持的关系再由模型新增隔离规则。迭代结果更新版本化设计卡、失败账本与新选集，历史选集及实验不覆盖。停止条件由用户目标定义；达到数量只是里程碑，不能以重复玩法或未经验证的点子填数。
