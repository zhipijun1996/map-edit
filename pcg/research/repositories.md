# 七个开源项目的代码、许可与维护审计

审计日：2026-10-23 UTC。所有项目均实际浅克隆；OR-Tools 仅稀疏检出 Python CP-SAT 和 examples，未下载历史/全量源码。逐文件证据见 [source-audit.json](source-audit.json)：固定提交、读过的关键文件、SHA-256 与永久代码链接。`vendor/*-metadata.json` 保存 GitHub 元数据；`vendor/audit-manifest.json` 保存提交与维护快照。下面“最近提交”指默认分支 HEAD，不等于所有开发分支最近活动；pushed_at 也可能来自其他分支。没有从一次更新时间推断作者承诺持续维护。

没有运行这些项目的整套实验，也没有声称它们与游戏 Godot 版本已经实机兼容。本次关注源码架构和可移植性；游戏专属原型另有运行回执。

## 1. Mario-AI-Framework

- 仓库：[amidos2006/Mario-AI-Framework](https://github.com/amidos2006/Mario-AI-Framework)。默认 `master`，冻结 `b0f01f224f868cdedf6a4b1f75ecc4c7a1f53545`；最近提交 2025-01-20，修复 enemy flower clone 的合并；未 archived。
- 实读 README、`src/engine/core/MarioForwardModel.java`、`MarioWorld.java`、`MarioLevelGenerator.java`、`MarioResult.java`、`src/agents/robinBaumgarten/AStarTree.java` 和 `SearchNode.java`。
- 最有价值接口：[clone 与 advance](https://github.com/amidos2006/Mario-AI-Framework/blob/b0f01f224f868cdedf6a4b1f75ecc4c7a1f53545/src/engine/core/MarioForwardModel.java#L234)、[预算化搜索](https://github.com/amidos2006/Mario-AI-Framework/blob/b0f01f224f868cdedf6a4b1f75ecc4c7a1f53545/src/agents/robinBaumgarten/AStarTree.java#L19)、生成器与代理解耦、事件/结果可观测性。模型快照复用比给测试角色搬坐标更接近可验证的玩家规划。
- 迁移建议：借鉴 `observe→clone→advance→plan→execute→compare` 架构，游戏仍用自己的 Motor、资源与射击/钩索事件；不能套用 Mario 跳距、碰撞箱或仅向右启发。
- 许可：未找到根目录通用 LICENSE，GitHub license 字段 null。README Copyrights 明确研究用途、预期非商业，并指出 Nintendo 角色和图像权利归属。**不建议把该仓库源码或资产直接复制进本商业 Demo；独立实现架构与算法。**

## 2. FI-MAP-Elites

- 仓库：[konsfik/FI-MAP-Elites](https://github.com/konsfik/FI-MAP-Elites)。默认 `main`，冻结 `ef8d6fcada38393f625359f08cd68d635a1e12d5`；最近提交与 push 为 2022-07-30；未 archived。README PDF 链接仍写 coming soon，实际论文从作者站获取。
- 实读核心：[FI_MAP_Elites.Operators.cs](https://github.com/konsfik/FI-MAP-Elites/blob/ef8d6fcada38393f625359f08cd68d635a1e12d5/FI_MAP_Elites__PCG/FI_MAP_Elites__Core/Algorithms/FI_MAP_Elites/Algorithm/FI_MAP_Elites.Operators.cs)、[PSM__Random.cs](https://github.com/konsfik/FI-MAP-Elites/blob/ef8d6fcada38393f625359f08cd68d635a1e12d5/FI_MAP_Elites__PCG/FI_MAP_Elites__Core/Algorithms/FI_MAP_Elites/Parent_Selection_Methods/PSM__Random.cs)、实验 `Templates__FIME_Experiments.Fitness_And_Constraints.cs`、`EM__Average__Hierarchical.cs` 与 csproj。
- 实现不是“一个分数罚不可行”：父代从 F/I 档案交替抽取，深拷贝后变异；按可行性选择 evaluator、BC 和目的档案，再作档案内替换。实验可行质量优化房间面积精度；不可行评价是 Voronoi、Geometry、Details 三层，前层未达标时停止后层累分。原 BC 是整体/平均房间 compactness，不是角色动作。
- 核心项目 netstandard2.0，有 Common_Tools 和 Triangle.NET 等依赖。迁移到 Godot Standard 的最佳方式是 Python 离线双档案实现及 JSON worker 协议，复用搜索思想；不移植整套房间几何应用。
- 许可：根目录无通用 LICENSE、GitHub license null；仓库中的 TriangleNet_Beta4/LICENSE 只覆盖该依赖，不能当成整个 FI 仓库授权。可研究方法，直接复制代码前需澄清授权。本原型可独立实现算法伪代码。

## 3. pyribs

- 仓库：[icaros-usc/pyribs](https://github.com/icaros-usc/pyribs)。默认 `master`，冻结 `7bd723cf9863d480c8f2fec5ba9aa36f3b68c083`；2026-07-22 准备 v0.12.0；MIT，未 archived。
- 实读 README、LICENSE、pyproject、[GridArchive](https://github.com/icaros-usc/pyribs/blob/7bd723cf9863d480c8f2fec5ba9aa36f3b68c083/ribs/archives/_grid_archive.py)、[GaussianEmitter](https://github.com/icaros-usc/pyribs/blob/7bd723cf9863d480c8f2fec5ba9aa36f3b68c083/ribs/emitters/_gaussian_emitter.py)、[Scheduler](https://github.com/icaros-usc/pyribs/blob/7bd723cf9863d480c8f2fec5ba9aa36f3b68c083/ribs/schedulers/_scheduler.py#L361)。
- `ask()` 批量提出候选，外部运行 Godot 后 `tell(objective, measures, **fields)` 回传；回传顺序必须与 ask 一致。适合独立缓存候选ID、生成器版本、trace URI/摘要和资源快照。已有向量基因用 GaussianEmitter 很方便；变长语法树需自定义 emitter 或外部变异，不能指望连续高斯自动保持语法合法。
- Python >=3.10；当前依赖包括 NumPy >=2、Numba、SciPy、scikit-learn、pandas 等。它是离线研究依赖，不应塞进 Godot Web Runtime。FI 双档案、不可行评价、动态特征与全流程 worker 调度仍需项目自己实现；不能把两个普通 Scheduler 接起来就称完整 FI 复现。

## 4. Google OR-Tools

- 仓库：[google/or-tools](https://github.com/google/or-tools)。默认 **stable**，冻结 `100f66e6242ab8bf8d32feb8f3bf086db66ae2b5`，2026-09-17；仓库 push 为 2026-10-23（不代表 stable 同日有新提交）。Apache-2.0，未 archived。
- 实读 README、LICENSE、[ortools/sat/python/cp_model.py](https://github.com/google/or-tools/blob/100f66e6242ab8bf8d32feb8f3bf086db66ae2b5/ortools/sat/python/cp_model.py)。有 CpModel、CpSolver.solve、hint、assumptions 与可行/无解/未知状态。
- 离线 Python wheel + Godot worker 成本低；离散坐标、Cell不重叠、端口兼容、能力/奖励图适用。连续运动靠实际回放。
- 原生 Godot Runtime 要自行做 GDExtension/C++ 与目标平台构建、线程/超时、二进制体积、序列化；C# wrapper 不代表能在 Standard GDScript 或 Web 直接用。编辑时可复用模型和 hints、用 assumptions 诊断冲突，但不要承诺 CP-SAT 像 Tanagra/Choco 一样提供任意撤回后的增量求解或保留搜索树。Runtime 首版建议有限候选表与轻约束传播，测到必要性再引入原生 solver。

## 5. godot-constraint-solving

- 仓库：[AlexeyBond/godot-constraint-solving](https://github.com/AlexeyBond/godot-constraint-solving)。默认 `master`，冻结 `45e3edd8ea120476bdc9be0c657a77a5846bb6fd`；2025-05-13 “import to godot 4.4”；MIT，未 archived。project.godot 的 features 是 4.4。
- 实读 README、LICENSE、project.godot、[solver.gd](https://github.com/AlexeyBond/godot-constraint-solving/blob/45e3edd8ea120476bdc9be0c657a77a5846bb6fd/addons/wfc/solver/solver.gd)、solver_settings、generator_2d 与 precondition_2d_dungeon。
- 通用离散 CSP 求解器、AC-3传播、回溯上限、WFC封装、TileMapLayer/GridMap、部分多线程与预条件。README 明确 **未实现全局路径约束**，示例 dungeon 先用别的算法限制道路，再 WFC 填充。
- 适合 Cell/美术局部拼接，不作为 Module 设计器。本项目要求 Godot 4.7.2；4.4 API 风格提供迁移线索，**未跑 4.7.2 导入与实际调用就只能标兼容待验**。回溯和多线程会增加内存和确定性管理成本。

## 6. WaveFunctionCollapse

- 仓库：[mxgmn/WaveFunctionCollapse](https://github.com/mxgmn/WaveFunctionCollapse)。默认 `master`，冻结 `de7d22e705e816b62b4d613199d0463820fcaef3`；2026-03-21 nonperiodic input fix；仓库 pushed_at 2026-10-15；未 archived。
- 实读 README、LICENSE、[Model.cs](https://github.com/mxgmn/WaveFunctionCollapse/blob/de7d22e705e816b62b4d613199d0463820fcaef3/Model.cs#L69)、OverlappingModel.cs、SimpleTiledModel.cs。共享模型维护 wave/domain、邻接兼容计数、熵/MRV/scanline观察以及禁值传播。`Run(seed,limit)` 遇传播矛盾返回 false；有限 limit 用尽也会 return true，因此消费者还需确认是否真的完全观察，不把布尔返回一概当成完整关卡。
- 代码 LICENSE 是 **MIT**（GitHub API 显示 Other/NOASSERTION，不能据API误判）；许可证末尾明确样本图像/tiles不属于软件许可。引入代码可依 MIT 保留声明；图像逐项审查。
- 适合后置填空：锁定可玩区、完整身体净空、入口出口 halo、危险表面后再拼 Tile。它能提高局部美术一致性，不能自行评价技巧、奖励或全图通关。

## 7. Algorithmica / procgen-lab

- 仓库：[Holizer/procgen-lab](https://github.com/Holizer/procgen-lab)。默认 `master`，冻结 `15e5d62f8882a4a4c0b7edcd5d65641e45287a9e`；最近提交 2026-08-02；MIT，未 archived。
- 实读 README、LICENSE、project.godot、csproj、BspProcessor、LevelTopology、[TopologyPlacer](https://github.com/Holizer/procgen-lab/blob/15e5d62f8882a4a4c0b7edcd5d65641e45287a9e/source/wfc/services/topology_placer/TopologyPlacer.cs)、[WfcSolver](https://github.com/Holizer/procgen-lab/blob/15e5d62f8882a4a4c0b7edcd5d65641e45287a9e/source/wfc/services/WfcSolver.cs)。不是只有 README 所称的笼统 Godot4：实际 `Godot.NET.Sdk/4.7.0`、net8.0，Android 条件 net9.0；project.features 4.7/C#/Forward Plus。
- 重要迁移点是显式分开拓扑和几何：房间节点/连接→MST→Bresenham路径→socket要求→WFC。`TopologyPlacer` 会取生成树，**不能照搬而丢掉游戏需要的奖励环路和再汇合边**。`WfcSolver.Solve` 默认最多256次重试，用domain快照恢复，不是完整树回溯。
- README 明说部分受限授权图像未分发、工程不能独立构建。MIT 代码不等于第三方美术可自由分发；用于本项目应独立移植拓扑接口，用已有合法素材与GDScript消费者。
- 这里“道路连通”是俯视几何性质。横版平台图的边必须是具备方向、入口/出口速度、能力、资源与相位条件的动作合同；不能用 MST 连通冒充可通关。

## 采用顺序

1. 独立实现动作关系/真实物理回执，参考 Mario 的 forward-model 架构，但不复制受限代码资产。
2. Python离线用 pyribs/MAP-Elites组织档案；先自实现可复查的双档案逻辑，再按需要换 emitter。
3. OR-Tools用于离散几何与分支约束；未经基准不引入 Web/nativeRuntime 依赖。
4. 本项目可玩空间已锁定后，少量试用 Godot CSP/WFC 做局部拼接；保留原物理与危险语义。
5. Map级借鉴 procgen-lab 的 topology→space分离，重新设计有向多路线嵌入，不能照搬其树化拓扑。
