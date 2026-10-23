# 算法与论文核验（2026-10-23）

本文件记录论文事实及迁移设计，不把其他游戏的可通关结论、性能数字当成本游戏实验结果。实际本项目实验以主报告和逐次物理回执为准。论文部分没有找到可直接接入 Godot 的 Tanagra / 2013 Action Grammar 官方维护代码；不能将本文原型称为原论文完整复现。

## 论文准确身份与可验证结论

| 优先级 | 来源 | 核实后的内容与边界 |
| --- | --- | --- |
| P0 | Gillian Smith, Jim Whitehead, Michael Mateas. **Tanagra: An Intelligent Level Design Assistant for 2D Platformers**, AIIDE 2010, 223–224. [原文](https://ojs.aaai.org/index.php/AIIDE/article/download/12379/12238/15907)，[条目](https://ojs.aaai.org/index.php/AIIDE/article/view/12379) | 用户链接是两页 demonstration。ABL 表达分层几何模式、监控改动；Choco 求几何约束。Beat 表达玩家动作与节奏。原文明确依赖预先规定的 pattern library：五种单 Beat、两种多 Beat 模式。其保证依赖简化运动模型与受支持模式，不能直接外推到反冲、抓钩、移动敌人。2011 扩展论文准确标题是 **Tanagra: Reactive Planning and Constraint Solving for Mixed-Initiative Level Design**，DOI [10.1109/TCIAIG.2011.2159716](https://doi.org/10.1109/TCIAIG.2011.2159716)。 |
| P0 | Kate Compton, Michael Mateas. **Procedural Level Design for Platform Games**, AIIDE 2006, 109–111. [原文](https://ojs.aaai.org/index.php/AIIDE/article/download/18755/18531)，[条目](https://ojs.aaai.org/index.php/AIIDE/article/view/18755) | 四层为 **Components → Patterns → Cells → Cell Structures**。Component 是参数化基础构件；Pattern 有 basic、complex、compound、composite 四类；Cell 封装一段线性 Pattern；Cell Structure 表达 branch、parallel branch、hub、valve 等非线性连接。原文以递归语法展开结构，以物理和操作窗口估难度，以爬山调 Pattern 参数；是原型与架构提案，不能引用为成熟 Runtime 质量保证。 |
| P0 | **Roland van der Linden**, Ricardo Lopes, Rafael Bidarra. **Designing Procedurally Generated Levels**, AIIDE workshop 2013, 41–47. [作者机构原文](https://graphics.tudelft.nl/~rafa/myPapers/bidarra.RvdL.IDP13.pdf)，[条目](https://ojs.aaai.org/index.php/AIIDE/article/view/12592) | OJS 作者元数据简写 Roland Linden；PDF 是 Roland van der Linden。设计者声明动词、目标、子动作、分支、共处和语义关联，形成 gameplay graph grammar，再布局对象。实验是 dungeon crawler，不是高连续精度平台跳跃。语法产生新的合法推导，但规则和原子动作仍由设计者定义；论文没有证明自动发明运动机制或开放式发现全新技巧。 |
| P0 | Jean-Baptiste Mouret, Jeff Clune. **Illuminating search spaces by mapping elites**, 2015. [原文](https://arxiv.org/abs/1504.04909) | 按设计者选定的行为维度分箱，各箱保留高质量候选。它提供质量与特征覆盖的搜索组织方式，并不自带关卡趣味指标；高维档案易稀疏，几何差异不等于行为差异。 |
| P0 | Konstantinos Sfikas, Antonios Liapis, Georgios N. Yannakakis. **A General-Purpose Expressive Algorithm for Room-based Environments**, PCG workshop 2022. [作者原文](https://www.konsfik.com/papers/a_general-purpose_expressive_algorithm_for_room-based_environments.pdf)，[实现](https://github.com/konsfik/FI-MAP-Elites) | FI-MAP-Elites 是 MAP-Elites 与 FI-2Pop 的结合。可行档案优化质量，不可行档案优化 feasibility score，两者都维持特征覆盖；两档非空时交替选父代。原任务是房间面积、连通、门宽等约束下的 Voronoi/方格/六角格布局。README BibTeX 的标题末尾另写 Game Levels；报告引用实际 PDF 标题。 |
| P1 | [Google CP-SAT 文档](https://developers.google.com/optimization/cp/cp_solver)，[实现](https://github.com/google/or-tools) | 使用整数变量与约束；FEASIBLE/OPTIMAL、INFEASIBLE、UNKNOWN 必须分开。有限计算预算后的 UNKNOWN 不是无解证明。Solver 处理离散关系，不能独立证明连续角色碰撞与操作时序。 |
| P1 | [Mario-AI-Framework](https://github.com/amidos2006/Mario-AI-Framework) | 提供 forward model 的 clone/advance、代理接口、生成接口、运行结果与事件。Robin Baumgarten 代理以快照模拟和有时间预算的前向搜索规划；启发与去重带工程近似，不宜一概称为满足标准 A* 最优性定理的实现。 |
| P1 | Adam Summerville, Shweta Philip, Michael Mateas. **MCMCTS PCG 4 SMB: Monte Carlo Tree Search to Guide Platformer Level Generation**, 2015, 68–74. [条目](https://ojs.aaai.org/index.php/AIIDE/article/view/12816)，[论文副本](https://proceduraldoctoratelabyrinth.wordpress.com/wp-content/uploads/2014/11/mcmcts-pcg-4.pdf) | **MC 是 Markov Chain**。从 SMB 语料学习竖切片转移，以 MCTS 搜索构造。文中用低精度离散 A* 控制器评价，未纳入敌人；不是每次 rollout 跑完整真实物理。其约 30 秒级、200 rollouts/步的选择是论文当时的设置，不是本项目 Runtime 性能。 |
| P2 | [Maxim Gumin 的 WaveFunctionCollapse](https://github.com/mxgmn/WaveFunctionCollapse)，[Godot 插件](https://github.com/AlexeyBond/godot-constraint-solving) | Overlapping 与 simple tiled 模型通过熵/MRV选择及邻接传播求局部一致。原版遇矛盾可失败重试；Godot 插件有回溯与 AC-3。局部一致无法表达“必须反向制动落台”或保障非线性能力锁。 |

## 四层词汇如何落到本项目

不要把 2006 年论文 Cell 直接等同本项目 Cell。建议保持项目已有命名，新增 schema 中显式保存层级含义。

| 本项目层级 | 可执行责任 | 对应论文概念（近似，非一一同义） | 适合算法 |
| --- | --- | --- | --- |
| Cell | 有正式碰撞/危险/交互合同的最小参数实体，带占据、可站立面、钩点等 affordance | Component | WFC/约束传播负责覆材；CP/FSM 约束局部实体 |
| Module | 一个入口状态集合到出口状态集合的挑战；保存 witness 输入、容错曲线和所需能力 | Pattern，部分 Cell | 动作语法 + Tanagra 式参数求解 + 真物理验证；QD 发现变体 |
| Macro Module | 连续挑战、分支再合流、恢复区；负责跨模块资源与节奏 | Cell + Cell Structure | 图重写、约束规划、连续状态传播、QD 局部优化 |
| Map | 能力进程与探索图嵌入世界空间；预留预算、回环、返回与保存 | 更高阶递归 Cell Structures | Mission/能力图 + 空间嵌入 + 接口约束；WFC 末端美术填充 |

## 推荐技术路线：把动作“关系”作为生成对象

以下是迁移建议，不是上述论文已经完成的功能。首选 C 的最小版本，其核心先实现 A；B 用于离线改进规则和量化覆盖，避免把海量搜索放进玩家等待帧。

1. 定义少量真实动作原语：地面起跳、空中跳、反冲、空中方向输入、钩索发射/抓取/释放、等待/落台。每个原语有前置状态与后置状态区间，引用真实配置，不能在生成器复制一套物理参数。
2. 动作语法从空间任务推出约束，例如“向右加速穿越→反向制动→下降接收”，同时限定恢复窗口、输入复杂度和替代解。规则节点描述关系与区间，绝不能暗中选择一份完整预制 Module。
3. 以真实 Motor 采样建立短程运动包络：入口位置/速度/资源/冷却/相位 → 输入程序 → swept body 轨迹 → 出口状态。射击方向、钩点距离和目标运动都要进入状态；落点不能只用质点轨迹判断。
4. 约束求解布置基础 Cell，使轨迹附近有合理地面、障碍与落点；保留动作要求。几何修正必须复跑同源物理。平台边界、危险方向、视野与美术可表达性都参加约束。
5. 有预算的 forward planning 寻找 witness；轨迹通过只证明该输入在该版本下成功。未找到路径标为搜索预算内未解，不能把“规划器失败”标成物理无解。
6. 做动作因果消融：删除反冲、冻结空中方向、禁用钩索分别重试，同时寻找便宜绕行。如果普通跳可以同样拿到高奖励，不能声称形成了必须用反冲的挑战。
7. FI-QD 变异语法推导树、动作时长与几何参数，保存可行/近可行设计。回传失败类型以指导局部修改：缺能量换恢复位置；碰刺改间距/相位；落点速度过大改制动窗口。不可行档案只用于离线探索，不能直接上 Runtime 池。

### 复合动作约束的最小形式

状态 `s=(x,y,vx,vy,jumps_left,energy,shot_cooldown,grapple_mode,target_id,phase,epoch)`；必要时加入武器、敌人活性与机关离散状态。近似求解时可删减状态维度，但最终验证必须回到真实系统。

`exists u[0:T], geometry: s[t+1]=F_real(s[t],u[t],geometry), swept_body(t)∩hazard(t)=∅, budget(s[t])>=0, s[T]∈exit_set`。

这并不意味着把整个等式塞入 CP-SAT。CP-SAT 负责有限候选选择、整数坐标、端口、互斥、支路、能力锁；连续关系通过预采样表、保守包络与真实回放验证。动态机关必须采样相位，并在时间上检查玩家完整身体。

长动作搜索可先对“落地/抓取/释放/关键射击”事件建粗图，再在边内短时展开输入。去重除了位置，至少保留速度、资源、动作状态与机关相位，否则会合并表面相近但后续能力不同的状态。启发函数不具 admissible 证明时应称启发式前向搜索；最优性不是本实验主要目标。

## 三组合的可行性判断（设计推断，非性能实测）

| 方面 | A：动作语法+约束+验证 | B：FI-QD+自动试玩 | C：混合 |
| --- | --- | --- | --- |
| 首次实现成本 | 中；先把少量关系做准 | 中高；评价器与有效表示难于进化循环 | 高；需版本化地连接表示、物理与档案 |
| 典型收益 | 意图清晰、参数化强、较易控资源与难度 | 跨玩法分箱保留差异，近失败可继续探索 | 保留 A 的快速可控性，用 B 修正规则和覆盖盲区 |
| 创造边界 | 受语法及运动包络限制 | 受基因表示、变异与评分器限制 | 可在已知机制内生成新复合关系；仍需人工确认新体验 |
| 首要风险 | 只有固定动作链的拉伸/镜像，名为创造 | 利用评价漏洞、只为一个代理设计；物理预算很大 | 高估可行域、离线/Runtime模型不一致 |
| Runtime 角色 | 小范围新推导+有界参数求解与验证 | 本地后台可小预算；主搜索离线 | 推荐：Runtime 轻生成，离线 FI-QD 维护参数域和规则统计 |
| 验证优先顺序 | 首先做实验1；其后钩索再分支 | 与 A 使用相同候选表示和物理预算 | 必须做 A、C去掉QD、C去掉物理反馈等消融 |

MCTS 值得在“动作推导树下一步选择”做独立对照：预算计入所有 rollout 和物理调用；前缀缓存与乐观评分可能节省计算，长时依赖也可能使随机 rollout 浪费。没有测量前不将 MCTS 定为 Runtime 主干。WFC 则在可玩空间、端口 halo 与危险边界锁定之后执行，装饰失败不能移动已验证碰撞体。

## 行为多样性与评价设计

推荐初期小档案（2～3维，每维约5～8箱），按武器/能力快照分开。描述符从 **被接受的真实事件和轨迹** 计算：空中换向次数、反冲实际贡献的速度/高度、连续悬空时长、钩索占时/抓取次数、落点速度与安全余量。不要把“含三个钩点”直接算作三个钩索动作。一个 witness 不能代表整关全部体验；在已有可行 Module 上用不同策略代理和真人轨迹重估特征，并检查描述符稳定性。

质量指标分三层：硬约束是无强制损血、真实资源合法和到达；可优化代理指标是误差下成功率、容错窗口、恢复性和目标难度距离；主观指标是人工试玩的可读性、公平性、技巧感、新鲜感与重玩意愿。趣味不能用几个自动指标加权后宣称已证实。

重复率需同时报三项：几何规范化结构（去平移/镜像等）、动作事件n-gram、完整行为轨迹簇。镜像或坐标抖动造成新哈希不算新玩法。组合新颖性必须说明相对哪个训练/种子集，并用未参与优化的 holdout seeds、物理误差与玩家测试检查泛化。

不可行度建议保存向量而非混合总分：危险重叠/净空违反、目标距离、能量缺口、落台速度、接口条件、规划状态（已证失败/预算未解）。可行与不可行档案各自有行为分箱；不可行描述符需要在中途失败时仍有定义，无法确定的后段动作不能伪造。

## 离线与 Runtime 边界

离线运行真实批量试验、FI-QD、容错/消融、规则提议与人工盲测，产出的是小型语法、可行参数区域、近似运动表、接口合同、失败分类及少量已验证保底。它可以压缩庞大人工 Module 库，但仍保存必要的安全回退与已批准设计原则。

Runtime 按能力/武器状态选择语法，生成新动作关系与几何参数，轻约束传播/表查询，必要时有限物理验证，预算到达后回退。Seed、生成器版本、核心参数SHA、语法版本与能力快照必须进入 Manifest。若以表查询作验收，必须给出表的保守性和版本有效域；离线单点成功不能授权整个连续区间。

本研究不预先承诺“任意 Runtime 自动创造都快速、高质量”。应先证明一个 Module 的动作依赖、容错和玩家体验，再把状态集合与资源合同向 Macro/Map 推广。
