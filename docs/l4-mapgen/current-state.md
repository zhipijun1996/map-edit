# L4 Map 现状分析（先于新算法实施）

任务 `MAPGEN-RESEARCH-01`，2026-10-23。工作主仓为 **map-edit**；gunman-rush 是固定版本的需求、内容、操作与测试输入。本轮不修改主体游戏正式流程。审计对象是开发集成分支 `integration/four-lines-20261023@f50fe78630fd98339186349f4ea91d92540d6c5b`（10月23日16:30 UTC），同时核对 `main@e9ab0e0`（10月22日）和相关功能分支。开发集成分支比 main 前进118提交，不以 README 或日期较旧的 generation_current 文档代替源码。branch-audit.json 保留检查到的分支身份；Compare API 文件列表有300项截断，不把列表外文件判为无差异。

## 结论

目前已有真实大地图、分支、回环、单向回程、状态化捷径、物理模块及连续 Motor 测试；**还没有统一、可替换的 L4 生成接口，亦没有整图全状态物理可玩证明**。平原是三套手写骨架上的受约束变体；森林默认是多代手写空间配方叠加，开发场所库增加有限次序变体。增加随机选择或回环数量不能直接解决探索体验重复。

## 十项问题的代码答案

| 问题 | 实际能力 | 限制 |
|---|---|---|
| 平原算法 | `PlainsExplorationTopology.make/route_specs` 三种手写15/18格足迹；`PlainsRegionGenerator._candidate` 邻接建边、保语义路线删边、背侧锁/单向落下、高奖环 | 固定关键路线和汇合；共享列轴和层高；非通用图语法/嵌入 |
| 森林算法 | 默认 v15：v10底稿→v12纵向段→v13交错→v14果挂→v15 Bible；v18显式开发候选 | v18不是默认/正式池；场所接续按右支撑边+80wu、端口Y对齐，无全局回溯 |
| 并行系统 | 正式两图、RandomStage Preview、Foundry、environment/place/world_rebuild/spatial_golden候选和森林多版本共存 | 许多是明确的开发路径而非冲突；正式森林多代重构和重复validate有维护/运行成本 |
| Foundry/Harness/Skills | Foundry生成/修复/连续Motor回放，promote开发池；Harness执行与证据守门；Skills约束创作/验收 | 后两者不是Runtime Map算法；工坊通过不等于地区正式准入 |
| Module / Macro | 平原 Resource Definition/Port；工坊 phrase/itinerary；森林factory Dictionary / geometry_instances | 三种macro表达并存，缺统一多出口占用/transfer contract |
| 图/空间分离 | Manifest已有areas/connections与nodes/geometry；平原先拓扑再配方再列距；森林有局部embedding | Mission依赖尚无统一独立IR；大量边携带绝对坐标/driver程序，图空间仍耦合 |
| 分支/锁/奖励/Boss | 真实支路与回归熟悉营地；backside门和奖励开捷径有运行状态；Boss从起图存在 | 奖励职责/位置多手写；森林BFS推荐路线不看完整condition/能力状态 |
| 模块选择 | 平原 `PlainsRouteRecipes.choose` 按purpose/identity/history筛选，实际宽度参与空间预算；森林调用已知factory | 不是任意图节点的角色/端口联合约束搜索；模块名称变化不等于体验变化 |
| 运动/通关验证 | 真实Motor、危险全身扫掠、输入回放、相位样本；现有design validator按能力/单武器穷举回程 | Resource端口目前要求落地、反冲结束；能力包络不是碰撞证明；完整资源/相位状态覆盖缺失 |
| Map Notes | 177条固定来源模块草图，能力条件三态、1–10难度协议、路线/机关预览 | 当前无Mission/Exploration图、整图结果、算法Seed对照；完整能力条件和难度评分样本尚为空 |

## 平原关键调用链

`project.godot → scenes/demo/demo.tscn → DemoApp._load_stage (scripts/demo/demo_app.gd:411) → PlainsRegionGenerator.generate → _candidate → PlainsExplorationTopology / PlainsRouteRecipes → PlainsRegionStage → PlainsRegionAssembler.build → PlatformingModule / 真正玩家与敌人/Boss`。

1. `scripts/generation/plains_region_generator.gd:26` 最多4候选，再走固定已命名fallback；fallback仍需本身validate，不能据命名推断任意新内容已物理验证。
2. `plains_exploration_topology.gd:5` 三种固定footprint；`:25` 的short_technique/upper_discovery/creek_return职责与关键节点固定。
3. `plains_region_generator.gd:99` 起删非保护边，保持连通/环路和Boss前厅入度；`:150` linked_rings把部分stairs改为单向drop。
4. `:169` 先选实际配方；`:191` 读取Module世界宽度，`:210` 起形成共享column_positions；这比固定等尺寸房间进一步，但任一同行节点仍共用列位置，不能放任意形状图。
5. `:579` 高奖/顶奖用有限已写配方+单向落下回到别处；`:278` 中箱位置有明确偏好，风险字段多为作者常量，未由真实路线风险反馈求解。
6. `:830` 正反洪泛只遍历condition=open的有向边；`:845` E−V+1只是弱图环秩，不是实际方向/状态下的有效循环数。
7. `:861` 显式保护首访路线的合法方向和基础能力；`:893` validate核hash、已知版本、结构数量、支持能力、latch及canonical重生成。它有价值，但不等于softlock状态模型或真实整图通关。
8. `scripts/generation/plains_region_assembler.gd:10` 消费同一manifest，实例化所有模块及真实碰撞；`:73` 背侧机关开门后记region_state，不能从可视图线推测门已打开。

## 重构边界

保留可追溯内容、真实操作、命名RNG和状态/保存消费者作为输入；实验放在map-edit。先让独立Mission/Exploration IR生成可审查artifact，通过能力状态验证后再试模板/端口空间求解；失败返回所属阶段与约束。不能为了嵌入成功删关键边，也不能把手写driver修改或推荐路线重排当地图变化。

新层不再继续继承森林v19→v18→…式生产堆叠。等新路径达到相同当前消费者验证和真实试玩后，再由主体游戏显式选择新generator版本；历史只按实际保存需求保留，不为实验默认新增兼容负担。

详细代码证据见 [森林审计](forest-audit.md)、[L1–L3/Foundry审计](module-foundry-audit.md)；外部方法的证据强弱见 [算法研究](references.md)。本文件形成时仅完成源码审计，后续实际实验和本轮新鲜引擎结果另记，不把旧测试日志记成本轮通过。
