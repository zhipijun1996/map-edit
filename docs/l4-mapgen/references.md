# L4 Map Generator：论文与参考实现审查

审查日期：2026-10-23。本文是研究证据和适用性判断，不是这些项目在《失序之钟》中的集成验收。八个仓库已实际克隆并检查下述实现；本轮没有编译运行这些第三方工程，也没有复制其源码进游戏。精确提交、许可证文件和下载论文 SHA-256 见 `sources.json`。代码位置均对应清单中的提交。

## 1. 直接影响方案选择的发现

- Mission–Space 论文确实支持任务与空间分层，但其平台游戏案例让空间和任务相互指导。不能把该研究解释为必须严格单向生成，也不能把其中需要设计者纠正歧义的过程当成自动正确性证明。
- Cyclic Graph 论文的实验产物只是 JSON 图模型；文中少死胡同的结果不证明平台游戏不会发生 Softlock。
- 两篇 ASP 研究有不同边界：2018 年案例主动限制成树；2023 年案例生成有向平台房间，但慢例达到分钟量级，其通关检查是 ASCII 路径检查。
- ManiaMap 是最值得借鉴的空间求解基础。它已经支持不规则占用格、方向门、门码、图分解与回溯。真实角色速度、精力、钩索状态与落地安全仍需本项目建模。
- BSP、CA、WFC 能填充或整理既定空间，不能独自承担探索职责、能力依赖和整图物理正确性。

## 2. 论文阅读与适用性

### P0：Mission–Space / Mixed-Initiative

已读取 8 页全文，原始链接失败后，从研究项目网站自己的论文链接下载：[全文镜像](https://livegamedesign.github.io/assets/FDG2015_Karavolos.pdf)，[发表记录](https://publications.graphics.tudelft.nl/papers/261)。

§3 的地牢案例把抽象行动图细化后交给空间求解器，钥匙与锁通过共同 ID 关联。§4 的平台案例输入空间草图和能力获得顺序，标记各路径可用能力，再放锁与模板；表 1 明确两案例不同。平台分支歧义允许设计者修订，动作参数改变后模板还需重新检查。

本项目建议：保存 Mission、Exploration、Spatial 三种可独立检查的表示；允许空间求解报告“需要额外端口 / 节点尺寸不可满足”，由探索语法重新展开。能力依赖不可在铺完地图后随意添加。论文的人工修订环节应由本项目的确定性状态验证和有界重试补齐。

### P0：Cyclic Graph

已读全文：[论文页](https://journal.ugm.ac.id/ijccs/article/view/81178)，[下载 PDF](https://journal.ugm.ac.id/ijccs/article/download/81178/35784)。

§2 用 init、extend、secret、obstacle/reward、key/lock 规则及 recipe 扩展循环图，再评价候选。评价包括最短路线、边时长、分叉率、类型变化。§2.5 区分 path、单向 gate、仅可见 window 与锁关系。§2.6 明确输出只是不可玩的 JSON 图。论文的 dead-end 数量不是运动 Softlock 指标。

本项目建议：每次循环展开要带职责和见证，例如“拿奖励后开启通回旧枢纽的单向门”。对照同能力状态下开门前后的回程成本，记录节省时间和重新遇到的地标。不能用 `E-V+1` 独立定义探索质量；应区分闭合形状、实际可走回路和具有回程价值的捷径。

### P0：2023 Metroidvania ASP

已读全文：[论文](https://aircconline.com/csit/papers/vol13/csit130511.pdf)。

§3 用 clingo 先解房间图，再逐房解几何，边界冲突时撤回最小邻居组合。房间有方向性；为求解速度限制相邻单向门。§4.1 的 20×20 无锁、无邻居房间慢例最高约 600 秒；§4.2 约 100 图用 ASCII 路径检查钥匙和终点。该证据不足以证明复杂角色物理可玩，也不足以支持本项目 Runtime 预算。

本项目建议：先把 ASP 放在离线规则开发、反例发现及小型逻辑图验证中。运行时优先使用同一规则的显式状态搜索；跨平台交付前单独测 clingo 绑定、求解超时、内存、导出支持和缺解回退，禁止直接把完整 tile 几何交给运行时全局求解器。

### P0：2018 Action-Adventure ASP

已读全文，大学入口下载失败后找到会议存档：[全文](https://pcgworkshop.com/archive/smith2018graphbased.pdf)，[大学记录](https://researchportal.bath.ac.uk/en/publications/graph-based-generation-of-action-adventure-dungeon-levels-using-a/)。

§3 将空间父子 `paft` 与任务时间前置 `taft` 区分，并用完整性约束限制 Boss、奖励、锁等。§3.1 明确只生成树，替代路线、循环与捷径留待后续。§4 以多 Seed 的表达范围热图检查输出是否集中，说明合法生成仍可能缺乏变化。其示例不是循环图求解器。

本项目建议：借鉴声明式约束、反例和表达范围分析，而不是照搬单父节点模型。方案 B 若真实实现 ASP，必须独立支持有向循环与能力状态；若只是 Python BFS 验证，应准确称“循环语法 + 状态验证”，不能标成已运行 ASP。

### P1：2021 Evolutionary Dungeon

[原论文](https://www.sciencedirect.com/science/article/pii/S0957417421004504)正文访问被拒；仅读取出版方摘要和检索可见节选，**未阅读全文，不声称已核实其全部交叉、修复和性能细节**。可确认其用树同时编码布局与锁钥任务，并以玩家实验评价生成结果。找到同作者早期[硕士论文原始记录](https://teses.usp.br/teses/disponiveis/55/55134/tde-25032019-144917/pt-br.html)，该记录也说明树编码；未以其替代 2021 正文。

本项目建议：进化对象优先是带职责的图语法展开和布局参数；不使用会直接破坏任务前置条件的任意删边。每个后代先满足硬约束，再比较软质量，防止高分非法地图进入精英集。

### P1：MAP-Elites 与该研究系列的后续

已读[原算法摘要](https://arxiv.org/abs/1504.04909)；另读直接扩展 2021 工作的[2022 后续全文方法与结果](https://arxiv.org/html/2202.09301)。后者用树编码、子树交叉、重叠分支移除和修复，并用宽容度与探索系数构建 5×5 精英档案。其探索系数依赖 flood-fill 覆盖，不等于本游戏的探索趣味；树结构也不解决复杂回环。

本项目建议：用“主路线成本 / 最深奖励绕行成本 / 纵向比例 / 解锁后回程改善”等描述符分箱，同箱保留质量好的可行地图。质量函数和描述符分开；先保留人工评审面板，再用试玩数据校准。不能只保留全局最高分 Seed，也不能把节点重编号后的不同哈希当成体验多样性。

### P1：模拟退火

参考[算法说明](https://en.wikipedia.org/wiki/Simulated_annealing)。作为候选布局优化器，每步移动、换模板或重新选端口，以 `exp(-ΔE/T)` 概率接受变差解并逐步降温。适合优化连接长度、紧凑度和横纵比例；有限预算不保证最优。

本项目建议：只在满足拓扑、无重叠、端口兼容和锁合法性的可行集合内退火。硬约束不应因温度较高而暂时对外输出违规地图。先缓存模板对的兼容位姿，再局部变动与增量计算；设固定迭代预算，输出最好已验证状态，而不是最后状态。

## 3. 八个开源项目关键实现

### A. amidos2006/GraphDungeonGenerator — MIT

关键文件：`src/MissionGraph/Generator.cs:40`、`Pattern.cs:31,58,76`、`Recipe.cs`、`src/LayoutGrammar/Generator.cs:27`、`src/Program.cs:44`、`src/Helper.cs:33,92`。

规则目录以 `input.txt` 和一个或多个 `output*` 表达图替换，recipe 控制次数；模式匹配后拆边、添节点、按相对 access level 重连。布局阶段遍历任务图，通过锁 / puzzle 传播父职责，再补 lever 连接。入口对任务图和网格结果各做 solvability 检查，多轮失败可返回空结果。

可借鉴：任务 / 空间分层、规则文件、recipe、验证置于两阶段之间。不能直接借用其验证器充当本游戏物理证明：`Helper` 使用钥匙计数和递归可达性，没有动作资源状态。源码还存在需先审查的细节，例如 `Pattern.checkPatternApplicable` 接收 subgraph 却用 `graph.nodes[i]` 检查度数，移植前必须用反例测试其节点对应关系。程序入口使用新的 `Random()`，也需改为明确版本化随机流。

### B. mpewsey/ManiaMap — BSD-3-Clause

关键文件：`src/ManiaMap/RoomTemplate.cs:35,265,657,725`、`ConfigurationSpace.cs:47`、`Configuration.cs:77`、`Door.cs:126`、`Graphs/GraphChainDecomposer.cs:49`、`Generators/LayoutGenerator.cs:168,397,445`、`Layout.cs:110,251`、`Generators/PipelineBuilder.cs:17`。

模板是可以含空格的不规则 cell 数组；门包含类型、方向、门码，支持单向连接和多层。模板对枚举相对偏移和对齐门形成 configuration space。图先分循环和分支链；布局逐链构造，失败以布局栈回退。闭环插入需要同时满足两侧连接。数量限制和碰撞独立检查，默认管线是图随机化、布局、收集物分配。

可借鉴：模板几何与逻辑图分离、兼容位姿预计算、优先闭环、模板配额、显式失败和取消。**不是等尺寸矩形房间系统**。但门码是离散标签，不提供速度 / 精力 / 接触 / 动态机关相位。`LayoutGenerator` 类注释明确未实现 simulated annealing；`IsComplete` 检查模板数量，不是玩家通关证明。生成时完整性失败会从基底重新开始，集成时应加总尝试和时间上界，不能只依赖单链 rebase 限制。

### B2. mpewsey/ManiaMap.Godot — BSD-3-Clause

关键文件：`ManiaMap.Godot.csproj:1`、`addons/mpewsey.maniamap/scripts/runtime/graphs/LayoutGraphResource.cs:14`、`runtime/RoomTemplateDatabase.cs`、`runtime/RoomNode2D.cs`、`runtime/LayoutPack.cs`。

Godot 侧提供 Resource / Node 的编辑器与运行时适配，不是独立生成算法。实际项目文件使用 `Godot.NET.Sdk/4.4.1`、`net8.0`，引用 ManiaMap 2.5.3；README 的旧版本徽章不能代替这些实际依赖。当前游戏使用 Standard GDScript，直接采用意味着引入 C# 及另一套导出工具链，Web 尤需先核实平台支持。优先选择离线生成 JSON 或移植核心数据与回溯思路，保留现有 Godot Consumer。

### C. tcoxon/metazelda — BSD 风格 3 条款，按仓库 LICENSE 原文保留

关键文件：`src/net/bytten/metazelda/generators/DungeonGenerator.java:504,552,682`、`Condition.java:25,78,194`、`generators/LinearDungeonGenerator.java:77,120`、`constraints/IDungeonConstraints.java`。

生成阶段覆盖入口、房间树、Boss/目标、开关、强度、钥匙、graphify 和最终可接受性检查。graphify 比较相邻房间前置条件，相同条件可直连，差一个符号时加对应锁，防止新连边绕过任务。Condition 用有序 key level 和一个 switch state 简化状态。LinearDungeonGenerator 反复生成，用受钥匙条件限制的 A* 计算重走房间数，选回程较少的图。

可借鉴：添加回环也保留条件、前置条件蕴含、显式终点和回程成本。局限是 key level 代表固定获得次序，不覆盖本游戏任意 AND / OR 能力组合或可耗资源；不能照搬 Linear 目标使全部奖励支线变浅。Java 与外部 gameutil 依赖也使逻辑重写更合适。README 明确当前分支为 v3 工作中，文档可能落后，因此本文以实际 generate 顺序为准。

### D. halftheopposite/graph-dungeon-generator — MIT

关键文件：`src/generate/parse.ts:7`、`src/generate/index.ts:30,47,100,147`、`src/generate/collisions.ts`、`README.md:37`。

输入被递归展开成带单一 parent 的 Node 树；以 BFS 放矩形房和直走廊，AABB 冲突后退到父节点重试。README 明确不支持循环和 L 形走廊。解析没有任意图的 visited 集，循环输入不能安全处理，汇合也会被树展开。`placeCorridor` 的碰撞检查处于注释状态。

可借鉴：简单 AABB、局部放置、可视化阶段分离。不能用于最终复杂回环；把输入 API 从树改成有向图还不够，必须重做闭环约束、共享节点及走廊冲突。其随机工具使用运行时随机源，若复用须替换为传入的可复现 RNG。

### F. Holizer/procgen-lab — 代码 MIT，素材另有边界

关键文件：`source/bsp/services/BspProcessor.cs:10,78`、`source/cellular_automata/services/AutomataSimulator.cs:13`、`source/wfc/services/WfcSolver.cs`、`source/wfc/services/topology_placer/TopologyPlacer.cs:15`。

BSP 依深度、最小尺寸和长宽比控制分割；CA 用邻居数量演化；WFC 可先约束宏观道路再填充。值得注意，TopologyPlacer 从输入连接中选 MST，再绘制道路，并不保留输入图所有回环。因此不能直接用于本项目已规划网图的铺设。工程为 C#/.NET；README 还明确部分素材未包含，不能独立构建，不能把 MIT 代码许可延伸到素材。

借鉴目标是可调实验界面、Seed、时间 / 内存展示和预约束填充。若移植 CA 或 WFC，仅写入已规划的填充区域，保留可行走走廊、端口净空、观景线和地标。

### P2. mxgmn/WaveFunctionCollapse — MIT

关键文件：`Model.cs:73,99,135,143,182`、`OverlappingModel.cs`、`SimpleTiledModel.cs`。

核心是选择低熵变量、按权重观察、传播相邻兼容关系，矛盾则返回失败。局部模式相似不意味着全局连接、钥匙先于锁或平台可达。额外注意 `Run(seed, limit)` 在有限迭代用尽时也返回 true，消费者需确认完整解，不能仅凭布尔返回声明所有格已完成。

适合地形纹理、背景、局部 Cell 补全。对正式碰撞地形的每次补全，仍须复核保护路径和真实移动验证。

### P2. AlexeyBond/godot-constraint-solving — MIT

关键文件：`addons/wfc/solver/solver.gd:1,100,139,205,256`、`solver_settings.gd:14,18,26,66`、`problems/problem.gd`、`problems/2d/preconditions/`、`README.md:29,38`。

GDScript 通用有限域 CSP，提供 AC-3 风格传播、实验 AC-4、回溯、稀疏历史和多种预条件。README 明确尚未实现全局 / 路径约束。设置允许回溯失败后继续寻找不完整解，接入时须核实完整状态并拒绝部分解；不能把“已返回状态”当通过。

可借鉴为离散模板域和局部端口兼容的求解器，尤其避免引入 .NET；但运行时需要明确搜索步数、内存和失败语义。其 path precondition 示例只是先生成连接道路，不负责完整 Mission、能力依赖或 Motor。

## 4. 面向《失序之钟》的组合建议（本研究提出，需本项目实验检验）

### 三路线应真实分工

| 路线 | 可验证实现 | 主要风险 | 合理首轮目标 |
| --- | --- | --- | --- |
| A Grammar + Backtracking | 任务职责语法；固定模板池；配置空间回溯闭环 | 图可行但模板端口不足；深搜索 | 形成快速、透明的运行时基线 |
| B Cyclic + ASP | 有目的循环规则；clingo 约束；独立状态搜索交叉验证 | 把树ASP或BFS误称循环ASP；模型未包含单向困住 | 离线约束对照、反例和合法性上界 |
| C Mission–Space + Embedding + Evolution | 双向失败反馈；固定预算图 / 参数变异；硬约束过滤；精英档案 | 搜索预算大；指标投机；只得到一种“最佳地图” | 离线构建多风格图档案，选出运行时策略 |

第一轮不把论文中的不同房间内容混进比较。固定模板池及版本、角色能力、地图规模、Seed 清单、最多尝试次数、总求解步数；各阶段分别计时。失败要保存当时图、约束、模板候选和失败原因；不得只统计成功样本。

### 三类图不能混用

Mission 中的“奖励使能力可用”是逻辑依赖；Exploration 中的边是玩家能采用的有向路线；Spatial 中的边绑定真实端口与位姿。可见关系独立于通行边，捷径解锁独立于能力授予。每个语法规则应产生结构化 trace，指出保留的主线职责、增加的可选目标、回程用途与局部闭合要求。

### 状态验证契约

至少区分 `exists_finish_path` 与 `all_reachable_states_can_finish_or_escape`。只证明开始状态有通关路线，会漏掉玩家选择单向跳落后永久困住。逻辑状态可用 `(node, ability_bits, world_flags)`；能力永久获得时可剪枝，但不可把不同世界开关、已耗资源或入口状态的节点合并。资源和动作只做离散保守抽象时，应明确适用边界，不把逻辑验证提升成物理证明。

对于模块，端口需要位置、朝向、净空、速度区间、接触状态、能力条件、最低资源，以及到其他端口的方向可达关系。只检查 entry/exit 的坐标相接会忽略高速进入撞墙、落入平台底部、精力不足、不能回程等问题。兼容配置缓存必须绑定 Motor/tuning/模块内容 hash。

### 质量与设计感

硬约束失败先拒绝，软评分不能补偿。把回环用途与可测证据放在一起：替代路线是否应用不同能力；捷径节省多少返程；奖励额外成本是否对应价值；远景可见点是否最终被重访；主线是否被奖励绕路强迫延长。拓扑多样性应忽略 ID 重编号，至少比较角色/条件图结构、关键目标顺序和能力应用差异；布局平移不算新探索体验。

人工试玩仍应记录“是否记得地标 / 是否愿意走支线 / 是否理解返回路线 / 是否觉得奖励值得”，与图指标分开。MAP-Elites 的不同箱只是设计候选的组织方式，不是趣味证明。

## 5. 阅读和验证边界

本次已读全文：2015 Mission–Space、2023 Cyclic、2023 Metroidvania ASP、2018 Action-Adventure ASP；2022 MAP-Elites 后续的方法和结果已读。2021 Evolutionary 原文仅摘要 / 节选，全文仍缺；MvSPG 仅项目说明和展示说明，未运行其工具、未核实二进制或源码许可。[MvSPG 官方页](https://ionn.itch.io/metroidvania-procgen)明确目前仅结构生成，升级从预设池选取，不可当完整内容生成器。

所有关于 Runtime 的推荐均是移植判断，不是本机对第三方库的性能测试。论文原始性能不能替代本项目相同内容、同能力、同规模的实测。未引入第三方源码；后续若复制实现，保留对应许可和第三方声明，素材逐项独立核验。
