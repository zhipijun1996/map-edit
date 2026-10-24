# 《失序之钟》Map Generator 首轮研究与实验

任务 MAPGEN-RESEARCH-01，2026-10-23。所有关卡研究、原型与证据在 **map-edit** 管理；主体游戏是需求、内容、能力与真实操作输入。本轮没有修改主体游戏 tracked 文件或正式生成流程。

**结论：建议采用统一 Mission/Exploration IR + 内容感知约束嵌入作为演进方向；目前证据不支持选出最终算法或替换正式生成器。** 已完成实际源码审计、论文/八个参考项目研究、三路线可运行组件与对照、240 Seed 样本、现有游戏60图生成基线、真实完整路线与录像。新算法尚未接入真实模块装配，物理与探索趣味未验证；不能把237张抽象布局签为237张可玩地图。

## 交付入口

- [实际代码现状与调用路径](current-state.md)：先于原型形成，涵盖平原/森林与十项审计问题。
- [森林详细审计](forest-audit.md)、[L1–L3 / Foundry / Harness / Map Notes审计](module-foundry-audit.md)。
- [论文与参考实现研究](references.md)、[精确源码/许可证/论文阅读清单](sources.json)。
- [数据契约、统一区域接口与开发路线](architecture.md)。
- [运行原型与复现命令](../../experiments/l4-mapgen/README.md)、[工作台与证据打包说明](../../experiments/l4-mapgen/WORKBENCH.md)。
- [交互对照工作台](../../experiments/l4-mapgen/viewer.html)：HTTP服务打开；可切区域/Seed、查看三阶段、下载SVG、查看失败与基线录像。尚未部署到在线Map Notes。
- 不启动网页也可读 [任务图](../../experiments/l4-mapgen/results/figures/plains-0-A-mission.svg)、[探索图](../../experiments/l4-mapgen/results/figures/plains-0-A-exploration.svg)、[二维布局](../../experiments/l4-mapgen/results/figures/plains-0-A-spatial.svg)、[算法并排图](../../experiments/l4-mapgen/results/browser/comparison.png)。

## 当前系统的关键结论

审计固定最新开发集成分支 `integration/four-lines-20261023@f50fe78630fd98339186349f4ea91d92540d6c5b`，同时核对main及相关功能分支，未只读main或README。Map Notes基线为 `ccbb21e`，其内容快照来自游戏 `74d8a06b...`，与本轮运行源分别记录。

平原使用三种手写骨架的受约束变体：保护语义分岔汇合、删边保连通、按配方真实宽度分配列距、加入高奖环和背侧捷径。它有真实大图与非线性基础，但主干关键职责固定，空间仍受共享列轴约束。原generator默认版本常量v10不能代表App实际内容：App显式选择已准入root-bell-v3，本轮实际生成版本为 `plains-region-v12-root-bell-spaces`。

森林普通入口默认v15，v18是显式开发候选而非正式默认。v15从v10底稿经多代手写空间安装器叠加；v18是场所接续与有限次序变体，没有全局任意图嵌入。图与空间已有不同字段，但绝对坐标/动作程序与图仍耦合。canonical重生成/hash验证很有用，却不是无Softlock或真实运动证明。

Foundry确实执行连续真实Motor、扫掠和回放；其phrase/itinerary是开发池内容，不等于多出口Macro认证。已有 `level_design_contracts.py` 对单武器与单调能力图作状态穷举和回程检查，本轮已实际复用交叉验证；无需重新建立同义设计标准。

## 参考算法给出的取舍

Mission–Space支持目标与空间双向反馈，其平台案例并非严格单向流水线；Cyclic论文只产JSON图；2018 ASP案例仅树；2023 ASP慢例约600秒且通关检查非真实Motor。这些文献提供方法，不提供本游戏的质量保证。ManiaMap可借鉴不规则Cells、configuration space、循环/链分解与回溯，不能假设它已有模拟退火或真实运动端口。直接采用Godot.NET适配会给当前Standard/GDScript及Web工具链增加成本。[详细来源与适用边界](references.md)。

建议Runtime采用有界语法/回溯和预认证候选，ASP先作离线约束与反例参考，MAP-Elites先作离线多样性档案。模拟退火是布局优化候选；BSP/CA/WFC用于保护路线内的空间填充。该建议仍需下一阶段同真实内容实验确认。

## 新算法组件实验

冻结内容：四种**合成**不等尺寸矩形/L形mask，统一grounded类型代理端口；18节点、6主节点、3奖励支路。平原profile基础jump/recoil，森林额外grapple。每区Seed 0–29，A/B/C及C_random各30次，总240。固定SHA256 counter命名随机流、catalog digest和源码SHA；所有失败保留，无重抽。

- A：Mission义务有限改写 + 图增边 + 有界空间回溯。
- B：真实clingo 5.8.0选择循环/返回边，约束 `(node, permanent-open-mask)` 状态；本轮能力取初始profile，不演示正式局中多能力授予。保存每例完整ASP程序及hash；独立Python状态搜索复核。
- C：实际拓扑mutation与MAP-Elites档案，后接共享embedding；不是已完成任务/空间联合进化。
- C_random：与C相同24次拓扑评价的随机搜索消融；并非严格等墙钟预算。

空间闭环失败可回跳相关房间；最终独立检查掩码、端口类型/方向、逐边空间端点、额外暗连、走廊冲突与所有边落实。它仍不是平台物理。

| 区域 | 算法 | 逻辑 | 抽象布局 | 生成中位ms | P95 ms |
|---|---|---:|---:|---:|---:|
| 平原 | A | 30/30 | 30/30 | 244 | 2525 |
| 平原 | B | 30/30 | 30/30 | 302 | 2238 |
| 平原 | C | 30/30 | 29/30 | 275 | 3827 |
| 平原 | C_random | 30/30 | 30/30 | 381 | 3758 |
| 森林 | A | 30/30 | 30/30 | 179 | 2491 |
| 森林 | B | 30/30 | 29/30 | 314 | 2314 |
| 森林 | C | 30/30 | 29/30 | 342 | 2764 |
| 森林 | C_random | 30/30 | 30/30 | 413 | 1591 |

总逻辑240/240；抽象布局237/240。失败为 `plains-C-14`、`forest-B-28`、`forest-C-17`，各到48次route checks/backjumps后按预算拒绝。六例重新生成的deterministic digest一致，含三个失败。[原始CSV](../../experiments/l4-mapgen/results/results.csv)、[完整聚合Manifest](../../experiments/l4-mapgen/results/benchmark.json)、[汇总](../../experiments/l4-mapgen/results/summary.json)、[独审](prototype-review.md)。

指标包含同状态完成成本、奖励绕行、分支深度、全开门下的回程节省、有限路线数与标签不变WL指纹。23–30种拓扑指纹只证明有限家族中存在结构差异，不证明体验足够好。所有样本主线成本固定5.0，**本轮无法比较主线节奏或任务顺序多样性**。隐藏路线、远处可见暂不可达、完整区域身份仍是设计接口而非本轮已验证功能。

A增边0–2、B2–3、C最多4，预算未完全匹配；筛选分数还含枢纽/捷径代理，未经玩家校准。因此不能按分数给算法排名，也不能因为C更复杂就选C。物理通过率、人工试玩、真实敌人与奖励风险收益一律未测。保留对象内存约169–198KB，不是瞬时峰值/clingo RSS；毫秒为离线Python包络，不是Godot Runtime预测。

## 真实内容接入探针

当前Map Notes 177条：138 partial、39 unspecified，完整能力条件0、统一难度实评分0。72条有Resource端口：68条2端口、3条3端口、1条5端口。3/5端口资源存在，但`integration.usage=unverified`；不是正式准入证据。

只检查端口数量、乐观忽略职责与能力时：使用全部72资源的必要条件240/240通过；限制到已审阅正式25资源时，25条均2端口，直接“一节点一Resource、独占端口”替换240/240拒绝。**这不证明无法用多个Module/Cell组成多出口Macro，也不对森林Dictionary factories下结论**；它说明不能靠把正式单链模块默认当四门房间完成接入。[真实内容盘点](../../experiments/l4-mapgen/results/content-inventory.json)、[容量探针](../../experiments/l4-mapgen/results/real-content-feasibility.json)。

现有游戏设计validator已对240个投影图实际交叉验证，240/240设计合法。永久开门flag在投影中显式映射为合成单调变量，复用fixture仅提供schema上下文，没有把真实房间/挑战证据赋给新图。[回执](../../experiments/l4-mapgen/results/game-validator-crosscheck.json)。

## 本轮真实Godot结果

使用锁定Godot4.7.2 Standard，实际完整public generate（含内部validate/重建），不是只计 `_candidate()`。10root×两图×三profile=60；每例另做原public validate和JSON回放，60/60通过、零fallback。记录选定源前后hash稳定，正式tracked源码干净。

| 实际profile | 样本 | 完整生成中位ms | P95 ms |
|---|---:|---:|---:|
| 平原App对应root-bell-v3内容 | 20 | 320 | 385 |
| 森林默认v15 | 20 | 381 | 402 |
| 森林候选v18 | 20 | 541 | 589 |

它们含20–78个area和完整内容，与18抽象节点的Python实验不具备性能直接比较条件。Godot进程内存计数、生成时间与物理离线验证分别记录；Web/目标设备延迟未测。[基线脚本/参数/原始证据](../../experiments/l4-mapgen/godot/README.md)。

真实操作：v15、root `forest-depth-hollow-00`、map2、`bible_backbranch_journey`。从原始出生点完成43/43段，4114物理帧，实际领奖→开门→回营，无中途位置/资源注入，原runner PASS、exit0、零失败；不含Boss战或自然跨区成长。第二次真实渲染录像也完成相同行程，但事件字节不声称与headless完全相同。

[25秒真实Godot录像](../../experiments/l4-mapgen/results/motor/forest-v15-backbranch-30s-55s.mp4)（完整68.88秒影片的30–55秒）、[截图](../../experiments/l4-mapgen/results/motor/forest-v15-frame.png)、[回执/原始轨迹压缩包引用](../../experiments/l4-mapgen/results/motor/receipt.json)。录像4133展示帧/60fps，软件GL离线渲染约190秒，不是目标设备实时性能。直接执行原runner，未把它签为完整Harness profile；未预先抓取完整传递输入inventory的边界已在回执保留。当前新算法不继承这些基线物理通过。

## 验证、风险与下一阶段

21项组件/内容守门测试通过；独立500随机图单调状态oracle一致；现有Map Notes `npm run check`通过；真实Chromium验证240数据读取、四算法卡片、筛选、失败Seed、SVG下载、详情及手机宽度。CI仅增加Map相关Python/数据/JS检查，未排入游戏全量昂贵物理。[浏览器回执](../../experiments/l4-mapgen/results/browser/receipt.json)。

独审发现并已修复：走廊暗连、奖励路径跨状态拼接、边ID数量相同却错绑空间端点。原失败与修后证据均保留，不能把早期失败删成成功历史。

下一可验收里程碑：从现有内容选固定多出口Macro集合，补内部端口transfer matrix、净空和真实低资源/相位/回程证明；随后将同一IR编译到游戏现有Manifest，复用Foundry/原Harness完成新地图接缝与完整路线。再统一边/搜索预算，对A/B/C作同真实内容消融、比较主路线/奖励深度/捷径价值及玩家探索评价。依此证据决定保留或替换算法，避免继续森林多代继承堆叠。[具体接口与分阶段开发路线](architecture.md)。

最终成功标准尚未达成：本轮没有证明新图已经物理可玩、具有足够空间认知与设计感或适合长期肉鸽复玩；当前结果足以支持下一轮真实内容集成，而不足以批准正式替换。

## 2026-10-24 整图效果补充

已以最新合入main的游戏 `cd4989a68613e0b457cdfd5e252634dd57008505` 为只读输入，截取平原、森林默认v15、森林候选v18各3张4096×2304实际整图；同组Seed00/03/04、地图2。相机适应整图、HUD隐藏，未改生成/几何或搬运角色。原9例退出0、截图hash核对通过；另附新A/B/C的实际结构布局，明确未接入游戏。这里不覆盖前文f50fe基线的版本身份或验证结果。

[截图索引与原图](../../experiments/l4-mapgen/results/whole-maps-20261024/README.md) · [平原对照](../../experiments/l4-mapgen/results/whole-maps-20261024/plains-comparison.png) · [森林默认对照](../../experiments/l4-mapgen/results/whole-maps-20261024/forest-comparison.png) · [森林v18候选](../../experiments/l4-mapgen/results/whole-maps-20261024/forest-v18-comparison.png)
