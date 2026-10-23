# L4 原型独立只读审查

审查对象：`/workspace/l4-prototype/mapgen.py`。冻结源 SHA-256：`d89bab385158e4a82cf233b4c8d243bdc6cf8379683bf6dd043c9c135dc39a60`。仅运行外部临时反例，没有修改原型文件。旧源反例与当时摘要见 `prototype-prefixed-evidence.json`；修复结论以下述冻结源复查为准。

## 最多三项关键问题

### R1：几何输出可能产生未声明入口（已复现并修复）

旧 `route_layout` 只用 room 占用格阻挡 A*，没有保护 room 外侧净空。三间 3×3 房间 a=(0,0)、b=(10,0)、c=(5,1)，仅布置 a→b 走廊，算法返回成功，但走廊 (4,1)、(5,0)、(6,0)、(7,0)、(8,1) 与未连接的 c 共边。若以后将这些 mask / corridor 格解释为行走空间，将多出拓扑中不存在的出入口，甚至绕开锁。

建议：room halo 保护，只开放本条连接明确绑定的两个端口；路由后用独立检查器核对占用、走廊相邻、端口接触、边覆盖和未声明邻接。仅做路由前判断不足以声明最终几何合法。实现者已确认，并重新生成结果，旧全失败样本不可签为新源成功证据。

修复后：增加 halo、最终 `validate_layout`、逐边端点绑定和端口朝向 / outside / 路径一致性。独立复查最终 `plains-A-0` 的布局通过；互换两条走廊的 edges 列表会被明确拒绝 `edge_endpoint_mismatch`。旧布局泄漏反例也已纳入测试。此结论仅覆盖抽象格几何。

### R2：奖励绕行成本混用了不相容的角色状态（已复现并修复）

反例：s↔r 花费1；s↔k 花费100；k↔r 花费100；r↔goal 花费1但需要k能力，k节点授予k。逻辑验证正确通过，最短完成成本201。旧指标分别取“到r最短成本1”和“从任一r状态到终点最短成本1”，得到绕行成本-199；两段所需能力状态并不一致。

应计算 `min_state_at_reward(dist_from_start[state] + dist_to_goal[state]) - shortest_completion_cost`，两段连接同一个完整状态。该例应为0。此问题会污染 C 的质量选择，在引入新能力时尤其严重。另有指标命名问题：自身锁后的能力目标不可达时，旧 `ability_lock_correct` 仍为true，因为只搜索错误字符串里的 ability；应按明确验证条件报告，不能以字段名代替能力正确性证明。

冻结源独立复查：反例绕行成本为0，原本的 -199 已消失；`ability_lock_correct` 在验证有错时为false，返回 scope 仍注明单调能力 / 开门模型，未提升为物理正确性指标。

### R3：算法验证范围必须与名称一致（冻结源范围已复核）

原 B 确实调用 clingo，原 C 确实进行父代选择、变异和分箱精英替换，均不是仅贴标签。但初版 B 只在“所有锁全开”的图上筛选候选边，基础图本已强连通，因此 reach/back 对选边没有实际鉴别力；候选双向边也未在 ASP 中展开反向弧。实现者正升级显式有限状态约束，最终需给实际 program、solver结果及独立验证器的一致性证据。

冻结源 B 已生成 `(node, opened-switch-mask)` 有限状态转移，双向候选也展开反向弧；ASP 约束实际覆盖关键目标可达、所有可达状态能返回或完成，以及 Boss 开门状态；原 program 保存在 search 数据。能力谓词仅按本实验的初始 profile 判断，明确不声称 ASP 已处理运行中授予新能力，Python 验证器另行重查。该实验范围内可接受。

C 当前只进化额外连接及成本 / 方向，布局在进化结束后另行计算。它可称“拓扑 mutation MAP-Elites + 共享 embedding”，尚不能声称完成了 Mission–Space 与空间成功率共同优化。A/B/C 共享六主节点、三条奖励支线的有限语法家族；多 Seed 证明的范围应限制于此家族，不能外推任意网状拓扑和真实模块。

A 允许额外0–2条边，B在2–3条中优化，C最多4条。质量启发式包含决策枢纽 / 捷径数量，因此本轮分数不可直接宣布算法优劣；应后续匹配边预算或按复杂度分层。C_random 是相同评价次数的消融，明确并非相同墙钟预算。

## 已检查且未发现当前错误的部分

- 显式状态为 `(node, ability frozenset, opened frozenset)`，自动取得永久能力和永久开门状态；按这套单调模型，通关 / 返回入口的逆向闭包能检测单向困住。该结论不涵盖可关闭开关、消耗品、资源不足、战斗或真实动作。
- 独立整数 bit 状态 BFS / 逆向闭包对500个随机小图（5节点、2永久能力、2永久开门flag、有向/双向与随机条件）交叉检查，reachable_states 与 unsafe_states 无差异；见 `state-oracle-evidence.json`。该证据绑定当时源码摘要，不冒充整个最终批次运行。
- prep 授予被抑制后 Boss 仍可达会被报为 bypass；这种反事实验证比只看节点先后更有意义，但并不覆盖任意未来 Mission 依赖。
- 重新命名所有 node ID，并倒置 nodes / edges 数组，A/plains/seed11 的 topology 与 experience WL 指纹均保持相等。WL 是同构不变量；相同指纹不能证明同构，指纹数量也不是趣味或人类体验差异的证明。
- 输出明确写了 synthetic footprints、物理未验证、未准入正式运行、主观未验证；这些边界必须保留。不同 region 当前只改变初始能力、风险和目标坐标比例，不等于已实现区域独立探索设计。

## 当前审查结论

**ACCEPT：隔离实验用算法组件及抽象逻辑 / 几何验证；UNVERIFIED：正式 Map Generator 质量。** 冻结源17项相关测试通过，R1/R2外部反例及错绑反例复查通过。最终多 Seed 批次尚在生成，汇总应以其 source hash 对应的实际结果为准。整图真实物理、既有 Module / Macro Module 内容集成、探索趣味仍未验证；合并、上线、艺术与设备认可不属于本审查结论。

## 最终多 Seed 结果独立复查

最终批次为 plains / forest × A / B / C / C_random × Seed 0–29，共240个唯一运行。逐个重新调用逻辑验证和最终几何检查后：240/240逻辑通过，237/240抽象布局通过，240个物理状态均为unverified。失败保留为 plains-C-14、forest-B-28、forest-C-17，均为 embedding_budget_exhausted；没有替换失败Seed。复查证据见 `prototype-final-review-evidence.json`。

本机独立运行17项相关测试通过（2.331秒）；B的永久pit反例另有真实clingo UNSAT与Python Softlock结果。批次 provenance.json 绑定上述冻结源与全部输出摘要。该结果不构成真实Module内容成功率、Godot物理通过率、原生内存峰值或人工探索趣味的证据。A/B/C策略与边预算不一致，平均启发式不用于宣布胜者。

## map-edit 最终打包与抽样复现核验

核验路径：`/workspace/map-edit/experiments/l4-mapgen/`，核心源码摘要与上述冻结源一致。`results/benchmark.json` 中240个完整 run，`summary.json` 与聚合对象中的 summary 相同；逐个按原始 `indent=2` 序列化重建其原 manifest 字节摘要，240份全部匹配原批次 provenance。60份 B 的 program 原文摘要全部匹配 `program_sha256`，catalog digest 也匹配。源码、catalog、17项测试、README和requirements的五个文件摘要与 source-manifest 一致。

没有重新执行整个批次。重新生成以下六例：A/plains/0、B/forest/9、C/plains/14、B/forest/28、C/forest/17、C_random/forest/29。六例的 deterministic_digest、布局成功状态和 failures 全与归档相同，三个失败全部可复现；B 例的 ASP program hash 同样一致。证据见 `map-edit-package-review-evidence.json`。

限制也经数据核实：240个主线完成成本**全部等于5.0**，因此本轮不能比较主线长度 / 成本分布和主线节奏变化；区域profile也没有提供不同主线拓扑。原批次 provenance 使用 `manifests/*.json` / `runs.json` 原路径，而最终发行聚合为 benchmark.json，应另存打包 provenance 绑定最终路径、摘要与原批次，不要求保留240份重复文件。原内容摘要已经核对一致，不能把原路径缺失误解成运行数据丢失，也不能省略新的打包绑定。
