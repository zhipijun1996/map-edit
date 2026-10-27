---
name: pcg-module-factory
description: 用有界离线搜索生成动作模块，比较策略并输出可追溯质量档案。
---

适用：新增生成算法、修复搜索、提高产量或行为多样性。先读 `pcg/WORKSPACE.md`，在 `pcg/` 运行模块CLI。

## 当前平原入口

**最新 Map 约束（2026-10-27）**：生产前读取当前 Map 分支的真实策略与适配代码，不只读README。本轮已核对 `research/l4-map-generator@6c864ae6423b6409990564371aca34a322b66253`，证据在 `pcg/creative-production/batch30/map-constraint-source-v2/`。当前入口为 `batch30_runtime.produce_v3`；复用原Engine/evaluate/store，增加上游Block合同预检。Block128连通所有权、128倍数包围尺寸、真实边界中心Port及独立内部staging必须在几何生成前满足。内部挑战不缩放，不增外框；两门、移动铃包络、恢复地貌和完整身体扫掠均不能漏。旧候选缺少该合同即返回缺口，不由标签补齐。见[契约](../../../docs/l4-mapgen/graph-block-module-contract-v1.md)。
最新实际Map还使用`graph_map/domains.required_pairs`：精确匹配incident端口数，逐有向对满足需求，UNKNOWN不能顶替反向。`graph_map/joint/build`已做有限Block联合求解；不要沿用“只有逻辑图”的旧结论。奖励经`workshop/map_budget.py`重绑会产生新语义版本，必须重验真实经济与Map，不能继承旧宝箱证明。互斥双门/移动铃仍缺B消费者安装，必须返回此集成缺口。旧a685源绑定与实验作为历史原件保留，不重标。


先求解端口岸体的Block相位及预算，再跑真实动作。不能在留出失败后扩大所有权掩码，或删除名义路线未访问的恢复岸来强行拼接。受支持的终岸微调不满足时，记录具体相位/空间冲突；要重构岸体则另建生成规则及新版本完整重验。staging成功、边界穿越、反向、状态连续性、全图分别绑定，绝不相互代签。

本阶段按 [反冲平原配方流程](../pcg-creative-producer/references/plains-recoil-workflow.md) 收窄能力与内容职责。原库视图：`python3 -m pcg.prototype.creative_batches.plains_workshop.catalog_v1`。两个已试验的有界适配配方接收完整需求：`python3 -m pcg.prototype.creative_batches.plains_workshop.produce_v1 --name new-plains-demand --specifications demands.json`；`--examples` 输出格式。其他家族仍按现有具体生成规则处理；统一入口不宣称任意需求可生成。

## 持续生产入口

多端口职责先用 [pcg-multiport-junction](../pcg-multiport-junction/SKILL.md) 设计：在同一可兼容进入状态下形成有意义的去向选择，端口数和恢复路线不替代空间构思。按fork/merge/interchange等真实需求决定有向关系；可以部分单向，不强制全互通或固定A出2/3口。意图单向不等于已证单向，未验反向仍UNKNOWN。创意/缺口明确后才进入本skill的原技术管线。

用户要求持续生成新 Module 时，执行 [固定生产循环](references/production-loop.md)，不要为每个样品重新组织整套实验。程序入口：`python3 -m pcg.prototype.workshop.production_loop --name workshop-new-batch --cycles 4`。它复用原 Engine、regular 评价器、标准导出与 CandidateLibrary。

用户要求先积累、AI去重、再人工审核时，外层按 [批次生产协议](../pcg-creative-producer/references/batch-production-v1.md) 调度；不用每个点子等待人工批准。仍先过原技术门槛再入候选库；AI分组不会修改物理结论、删除候选或替人类批准。

Codex 负责提出和实现新因果规则；程序负责规则域内的动作/几何搜索、反例、校准、独立留出和入库。创意外层使用 [pcg-creative-producer](../pcg-creative-producer/SKILL.md) 的实际 Codex 会话或授权子代理；当前没有独立在线模型服务，不承诺单独运行循环程序能自主发明任意新机制。规则耗尽必须输出 needs_design，并将未实现创意和下一步缺口交回设计环节，不能继续换 Seed 冒充新内容。

每轮先静态合同预检、clean 与少量 mild 筛选、廉价解法，再做完整校准和留出。小样通过不是技术准入；沿用原 regular 门槛。发布见证必须在留出前固定为反例测试过的精确几何/敌人相位，留出统计单独描述父候选扰动范围。相同规则源码的失败持久化，后续进程跳过；标题和 Seed 不清除失败。运行整个冻结轮次期间，不编辑其源码。

衡量新候选/独立动作家族/复用/拒绝/耗时，不能用验证次数当产量。先做 Module；Macro、通用回程或接缝只有需求需要时才扩展，不能让每个新原型都承担整图级工作。

1. 明确支持的能力/区域/挑战家族与不可变物理基线。动作词可重复，动作数量不是道具库存；未注册机制拒绝而非改名替代。
2. 写实验protocol，固定候选预算、共同相位/噪声、选择规则、指标与新holdout seed。比较组具有相同上限，记录实际唯一候选数；不足预算不得冒充满配。
3. 用 `core.engine.Engine` 分批执行实际Godot。保留完整输入/输出/失败/gzip原字节SHA和源快照，不只成功截图。
4. 行为描述来自实际动作与轨迹。记录同格替换、可行/不可行父子，不把首次插入/随机seed计为设计改善。
5. 只用校准集选择修订，选完一次独立留出；另测较低成本替代路线。regular失败不可事后改名precision成功。
6. 输出summary、comparison、review_cases、命令/成本/局限与视频。目的动作、危险/伤害、稳定出口、载人/连续性都须符合；到达不替代动作要求。
7. 当前只签有限自动策略证据；人类观感/手感单独记录。新区域/长链/运行时预算需另验。

每轮更新 `references/iterations.md`：假设、工具版本、实际结果、失败、下一步；共性检查进入代码和测试，不只追加说明。只有重复证据支持才修改默认算法。

平原迭代：`prototype/plains/`是小型动作/压力关系生成器。Cell可为原EnemyActor/ShotLatch；让地形、机关、资源条件改变玩家的判断与动作顺序。实际落地后的安全恢复带可解耦连续难点，但须重新留出验证；不要把降低压力等同趣味提升。见`pcg/PLAINS-REPORT.md`。

输出合同（用户明确要求）：后续交付复用Map Notes格式与`generationContract`，见`pcg/OUTPUT-CONTRACT.md`。主生产器已接`contract.export`；其他实验CLI交付前也须转换。原研究raw cases不是地图接口。运行`npm run check`与`tools/check-module-contracts.mjs`，未完整声明/验证的进入状态、端口方向、净空、变换、回程和Macro连接保留UNKNOWN；不得自动填落地回满。

第二轮共性：新接收面/顶棚可能破坏前一段，先用已有身体轨迹过滤交叠，再真实整段重验；这不等于完整动作净空。逐枪省略反例要保留时间间隔，并分别测试延长普通跳跃，防止第二枪仅被动作词要求强行认定有价值。齿轮等待22/24反例可跳过时不宣称必要；保留原等待视频供节奏审核。见PLAINS-REVIEW-ROUND2.md。

三端口迭代：三端口候选必须共享全部物理Cell、位置及初始机关状态；6个有序对独立声明。主路到B合法不等于完成经C的支路，要检查真实坐标与落地。参数变体不增加玩法种数。 参见pcg/PLAINS-THREE-PORT-REPORT.md。
