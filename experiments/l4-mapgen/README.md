# L4 Map Generator 隔离算法实验

这是 Map Notes 的离线研究原型。**所有默认内容均为 `synthetic_spatial_proxy`，未接入游戏，不是可玩地图，也不能作为完整游戏地图质量对照。** 使用真实固定 Module/Macro 内容与 PlayerMotor 验证是下一阶段，不在本结果中冒签。

## 运行

Python 3.12；B 必须安装真实 `clingo==5.8.0`，缺依赖时 B 返回 `clingo_unavailable`，不降级冒充 ASP。

```sh
python3 -m pip install -r requirements.txt
python3 -m unittest -v test_mapgen.py
python3 mapgen.py generate --algorithm A --seed 0 --region plains --out example.json
python3 mapgen.py benchmark --seeds 30 --embedding-attempts 8 --out results
```

也支持将依赖安装到本目录 `.deps/`。CLI `generate` 发现逻辑或布局失败返回非零；`benchmark` 为收集成功和失败样本而完成后返回零，不能把此退出码解释成所有种子成功。逐样本 `failures`、`logic_validation` 和 `layout.ok` 才是结果。每个失败不换 Seed、不删边、不偷偷退化为树。

输出为 `results/summary.json`、`results/results.csv`、各 `manifests/*.json` 及一次导入可视化的 `results/runs.json`（`runs` 数组）。API：

```python
from mapgen import generate, default_catalog, strict_catalog_feasibility
manifest = generate('B', '12', 'forest', default_catalog(), search_budget=24, embedding_attempts=8)
```

## 实际实现

- **A**：任务义务改写成固定预算 18 节点图。主线 6 节点，三个有不同职责的长支路，分岔重汇、深处奖励和发现后打开的单向回程捷径。再作有限图增边改写，用模板掩码与有界回溯嵌入。不是通用图语法解释器，使命结构家族仍少。
- **B**：相同任务图与内容，真实 clingo 从候选连接中选 2–3 条。ASP 显式展开 `(node, opened-switch-mask)` 状态，约束奖励/Boss 可达、每个可达状态可以回入口或完成、Boss 必须持有 prep 打开的访问标志。能力按该区域初始配置筛选；本轮不伪造正式局中能力授予。`search.program` 保存完整程序，`program_sha256` 绑定。独立 Python 状态遍历复核，不能把 ASP 模型本身当物理证明。
- **C**：24 次实际变异搜索，从 MAP-Elites 档案父代删除/添加候选边或改变可选边方向/成本；只保留通过状态验证的图，在不同完成成本、有效捷径和奖励成本比的行为格中保存精英。最终按 Seed 选择档案格，不把单一最高分作为所有风格。
- **C_random**：与 C 相同的 24 次拓扑评价和相同档案规则，使用独立随机图改写，作为“额外评价次数”对照。它不等于严格相同墙钟预算；不能只根据 C 高于 A 推断进化优越。

额外连接预算也未完全匹配：A 为 0–2 条，B 约束为 2–3 条，C/C_random 上限 4 条。首轮只能比较成功/失败和搜索行为，不能据总分直接排名算法优劣；后续需固定边预算、搜索预算和真实内容再作消融。

空间层使用四种不等尺寸矩形/L形掩码，按语义位置先验选择模板/坐标。房间不得重叠或贴邻；端口类型必须匹配。A* 通道不得穿过其他房间、贴到未声明的房间、与其他通道相交或相邻。循环闭合失败会向相关较后端点房间回跳，再试模板/位置/端口，保留 `route_backjumps` 和失败账本。每布局最多 8 次总体尝试、每次 6 次完整路由、总 4000 次放置试探；A* 单次 12000 次展开。这些是实验搜索预算，不是游戏 Runtime 承诺。

最终独立 `validate_layout` 再核房间掩码、逐边端点、朝向/端口/通道一致性、所有边恰好落实、无额外空间接触。它验证抽象占用与连接，没有碰撞体、空中状态、运动学、敌人或资源消耗。

## 数据与证据边界

`catalog.json` 与生成策略分开，默认只有明确合成模板；`catalog_digest` 绑定冻结内容。外部 catalog 可通过 API 传入，但其 footprint/port 语义必须先适配，不能把真实单进单出模块伪装成四门房间。`strict_catalog_feasibility(graph, catalog)` 要求显式 `ports:[{id,type}]`，检查每个逻辑节点所需连接数是否有真实端口容量；这只是必要条件，既不推导可嵌入，也不推导物理通过。

平原 profile 只有 `jump/shot_recoil`，森林增加 `grapple`。这是对现有正式授予的抽象输入，不是创建新能力。两个区域目前只比较能力条件、竖向比和风险标签，尚未形成完整区域设计语法。

复现使用与游戏相同的 SHA256 counter/52-bit 选择形式，mission/exploration/layout/solver/evolution 命名流分离。新实验流版本单独为 `l4-mapgen-experiment-v1`，不修改游戏现有 RNG 或存档。

状态验证保证单调能力/开关模型中的目标可达与全部可达状态安全出口，主动检查压掉 prep 授予后能否绕过 Boss 锁。未建模消耗钥匙、装备切换、精力/冷却、机关相位、落体/反冲、敌人、掉落、存档和能力丢失，均需要后续真实消费者。

指标包括实际状态图完成成本、同一个奖励状态的完成绕路成本、全开后的回程捷径节省、支路深度、有限简单路线数量、分岔职责及奖励价值/成本比。奖励数值固定，不拟合评分。`quality_heuristic` 是未校准工程筛选函数，**不是好玩评分**。`route_choices_bounded` 忽略锁并有 128 上限，报告明确该边界。

拓扑/体验签名采用标签不变的 Weisfeiler–Lehman 指纹，测试节点重命名不变；不同指纹可说明图不同，相同指纹不构成同构证明。主线/支路结构组件仍有限，不能根据哈希数量声称探索体验已经足够丰富。

时间为 Python 离线纯生成/验证/优化/嵌入包络，不含 Godot；内存为生成后 manifest 的递归 `sys.getsizeof` 保留对象估计，**不是瞬时峰值、不是 clingo 原生 RSS，也不是游戏 Runtime 内存**。三个算法的复杂度与预算不同；使用中位/P95、成功率和失败原因共同判断。

`physics.status`、`subjective.status` 始终 `unverified`，`runtime_admitted=false`。人工试玩、Godot 整图通过率没有实验数据时保持 null，禁止填 0 或 100%。

## 已保留的发现与回归反例

独立审查发现过：通道贴到非端点房间形成隐式连接；奖励路径把不同能力状态的两个最短路拼起来产生负绕路；最终验证器只比较边 ID 总数而允许边与空间端点错绑。均已修复并有故意失败测试。早期失败/中断样本保留在 `pre_halo_failed_validation`、`traced_timing_aborted`、`pre_final_guard`，它们不是最终通过证据。

测试覆盖真实 ASP、Seed/RNG流、标签不变性、自锁能力、单向陷坑、Boss 绕锁、未知开关、同状态奖励成本、真实两端口池拒绝假 Hub、合法闭环布局、重叠/暗连/端口类型/边端点篡改及搜索预算耗尽。不得删除失败例来提高成功率。
