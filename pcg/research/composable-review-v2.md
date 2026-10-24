# PCG-RESEARCH-02：可组合能力生成器独立源码审查

审查者：独立子代理 `ability_contract_audit`。实现者为父代理；审查者未修改被审查代码，未占用实现者正在使用的 Godot 进程。本报告采用项目 `gameplay-reviewer` skill，职责依据 `/workspace/gunman-rush-latest/AGENTS.md:102`。审查是研究原型审查，不是正式游戏内容、玩家趣味、视觉或设备认可。

## 当前结论

**源码修复与最终物理数据核算范围 ACCEPT；三个已证实退化候选需要 REWORK，趣味与正式游戏集成 UNVERIFIED。** 已提出的 R1–R5 已修复；8 个现有纯 Python 测试及 4 类独立反例检查通过。最终批次产生 572 个稳定几何候选、101 个实际动作词，20 个交付候选的两种干净策略及输入录像回放均通过。它们支持“有类型/资源前置条件的有限动作组合提案 + 原角色真实物理回放”的工程方向，不支持“任意新机制、任意能力集合都有可玩关卡”或“大量有趣模块已获验证”。

最初源码测试回执见 `evidence/composable-audit/phase2-review-checks.json`；最终独立核算脚本、输入/输出哈希、源版本差异和回执见 `review_final.py` / `final-data-review.json`，执行退出码 0、核算失败列表为空。最终实际使用的 12 个源文件精确快照在 `final-reviewed-source/`。游戏原运动源冻结于 `12f6cb006d7119598e3235f4ca4f7323e4c9d092`，Godot 4.7.2；真实机制审计见 `research/composable-audit.md`。此前失败/诊断结果仍保留，不能追认成最终通过。本次最终复核只读取已有 JSON、源及日志，没有启动引擎、浏览器或观看录像；“数据复核通过”不冒充第二次独立引擎执行。

## 发现、修复与复核

| ID | 原问题与实际影响 | 当前修复 | 独立复核状态 |
| --- | --- | --- | --- |
| R1 | fixed 尾部每一次 axis 展开单独受扰动，feedback 的逐帧 settle 没有对应随机触发，比较混入额外噪声机会。 | shared settle-start 命令仍用同 noise key；固定尾部 axis 设置 `timing_noise=false`。worker 仅允许 axis 使用此开关。 | 源码及最终共同事件误差/尾部零 jitter 复核通过。 |
| R2 | “wall”替代解先朝出口而非实际墙面；跳墙同帧反向轴会先解除贴墙，容易把未真正搜索墙跳误报为未发现捷径。 | 从 `wall_platform_indices` 选择实际墙与接近方向；等 `wall_attach` 后跳，最终改为 `wall_kick` 握手且至少 1 帧后转向。 | 最终源码与实际帧通过；仍不以家族名代替受理证据。 |
| R3 | 每条替代成功路线均当捷径，可能惩罚更难/不同技能的合法路线并在其上堆障碍。 | 只对实际使用能力真子集，或同能力集合且关键事件更少的路线自动细化；其他成功路线保留。 | 独立偏序反例通过。仅为机械成本偏序，不等于风险/难度/趣味评分。 |
| R4 | raw `hook_contact` 是射线命中/开始拉拽，不代表抵达挂点；hang/bounce 合并使不同词被误当实现。 | 从逐帧状态真正进入 `hook_hang` / `hook_contact_kick` 提取不同事件；忽略 raw contact；expected word 保留挂点类型。 | 独立合成反例与最终真实帧词复核均通过。 |
| R5 | `Registry(custom_path)` 内容来自自定义文件，snapshot hash 却取全局默认文件，契约来源不一致。 | Registry 保存并哈希 `self.path`。 | 独立 custom-registry 反例通过。 |

## 最终冻结数据复核（2026-10-23）

独立脚本逐批检查输入哈希、输入/输出 ID 对齐、进程退出码、原日志错误、游戏源 SHA，并重新从实际帧提取动作词。hook 只在真正进入 `hook_hang` / `hook_contact_kick` 时计入，不使用 raw hook contact。所有已收录候选与 40 条 clean 策略的实际词相符。

| 数据集 | 独立核算结果 | 接受范围 |
| --- | --- | --- |
| `composable-search-final`，seed 920102 | 378 条运动提案；663 个几何回放；572 个稳定通过；101 个实际词与档案项；16 个 move+jump 基底集合均有通过。批次总耗时 25.82 秒。 | 一条提案可产生两个落点宽度候选，572 不等于 572 种玩法；耗时是批量离线运行，不是 Runtime 每模块时延。 |
| `composable-evaluation-final`，holdout 331051 | 20 模块；每模块两种策略各 1 clean、20 mild、20 moderate，共 1640 次。40/40 clean 成功且词匹配；所用几何与 selected 完全一致。 | 对这批确定策略和扰动模型成立，不是人类成功率。 |
| 成对误差 | 820 对中 6226 条双方实际执行的共同 noise key 的 timing/aim 误差完全一致；698 条 fixed 尾部 axis 的 timing_error 全部为 0。 | control_plan 的记录在 `fired_commands`；`noise_records` 为空，不能拿空表签成对一致。201 个未共同执行的 key 来自分支等待/失败后停止，不补造未执行误差。 |
| 反例细化 | 450 个替代策略测试；原 9 个模块发现更低机械成本解，8 次细化均保住原真实动作词与稳定见证；10 个其他成功路线保留。 | 剩余 3 个模块仍有已证实低成本解，详见下表；17 个未发现不等于 17 个已证明能力必要。 |
| `composable-delivery-v2` | 20/20 真实录制输入回放通过，实际词与 selected 相同。 | 数据一致性通过；审查者未播放视频，未操作浏览器。 |
| `composable-contract-matrix-v2` | 64 子集与 2 负例；36 个合法子集静止通过，28 个非法子集及两个负例拒绝；能力绑定无错配。 | 绑定/拒绝矩阵，不是 36 或 64 类动作关卡生成覆盖。 |

| 自动策略 | clean | mild（触发 ±1 帧、瞄准 ±2°） | moderate（±3 帧、±6°） |
| --- | --- | --- | --- |
| feedback | 20/20 | 389/400，97.25% | 363/400，90.75% |
| fixed | 20/20 | 306/400，76.5% | 219/400，54.75% |

平均数不能掩盖 combo4 `c-c4-w0-v0-w160`（bounce→bounce）：feedback mild **9/20**、moderate **12/20**，fixed 对应 **9/20、4/20**。当前应作为低容错诊断候选，不宜直接批量扩产。中噪声比轻噪声多通过三次是这 20 个确定种子的有限样本现象，不表明增大误差会改善通用难度。交付已有“容错待优化”warning。

| 需 REWORK 的模块 | 实际低成本通关反例 | 当前交付标记 |
| --- | --- | --- |
| `c-c12-w0-v0-w160`，wall_jump→hook_bounce | 单 wall_jump 即通过，grapple 可消融。4 个成功策略中三个 wall 测试实际重复，不能称 4 种独立路线。 | 已标“已发现较少动作/能力的替代解”。 |
| `c-c12-w10-v0-w160-refined`，双 hang→anchor_jump→wall_jump | 普通 ground_jump 可过；另一条 ground_jump→单 hang→anchor_jump 也过。 | 同上，2 个成功策略。 |
| `c-c12-w11-v0-w160-refined`，起跳→hang→bounce→wall_jump | ground_jump→单 hang→anchor_jump 可过。 | 同上，两个时机测试，不夸大路线类型。 |

源版本审计发现并闭合两项差异：前三批 evaluation 记录旧 `search.py`，现源新增显式能力 CLI/准确计数与注释，evaluate 不导入它；本审查原快照 SHA 与旧记录完全一致。最终实验后 `synthesis.py` 新增无 move 的空跳/接收帧分支，原最终执行版本已按记录 SHA 精确保存；最终 16 集合全含 move，且已冻结输入，新增分支不属于此次结果准入。原始来源告警及差异保留在 `final-data-review-first-pass.json`、`final-search-interface.diff`、`final-synthesis-postrun.diff`。search 与 matrix 原 execution 回执未记录逐文件 source_sha256，只记录输入哈希/游戏源等；不补签它们具有更细粒度的历史来源记录。

## 真实机制与组合边界

审查未发现当前源码仍把 hook/墙跳当作回子弹。`contracts.py` 的 recoil 消耗一发，hook 恢复二段跳资格而不恢复 round；从地面 recoil 后只剩可用的额外空跳，不能再凭空获得一次“普通跳”。规则允许 jump-shot-double、jump-double-shot 等不同顺序的提案，但顺序有效、实际发生和动作对空间的必要性是三个不同命题。

`jump_from_anchor()` 与普通 extra air jump 要区分；墙跳使用真正的 wall_attach 与 `wall_climbable` 碰撞墙，并有朝向/重新接触条件。挂点后的第二枪必须有真实落地或真实空中命中回能机制；目前无敌人 probe 不应生成射击资源重置。具体原代码位置、距离和输入时机见首轮机制审计，不重复参数。

可扩展性必须按 provider 实现：注册 ID、依赖/冲突、动作前置/效果、实际 Godot binding、可供合成的 affordance、正例/负例测试一起增加。JSON 的 `runtime_binding` 非空只是一项静态检查，不能自动创造机制实现；worker 的 SUPPORTED 仍明确只有 6 个 ID。所谓“任意能力组合”可作为未来接口目标，当前交付应称“已实现六种能力的合法组合框架”。

`Registry.combinations()` 的关卡搜索固定 move+jump，枚举其余四项的 16 种集合。`check_matrix.py` 的 64 子集矩阵验证的是绑定/拒绝与静止落地，不是 64 类动作关卡生成；double 要 jump、wall 要 move 的非法集合应被拒绝。墙跳可以在普通 jump 被禁用时由现有低层 API 执行，但这不自动证明对应能力集合已得到生成覆盖。

## 搜索与评价能证明什么

`Grammar.derive` 在有限 depth、候选 front、anchor/wall 次数预算内派生动作词；`compile_probe` 用少量关系式锚点/墙/输入规律实例化，`materialize` 从真实轨迹放置接收平台与避开轨迹的障碍。这减少完整预制 Module 依赖，确实与“按 Module ID 排列”不同。它仍是有手工 affordance 合成偏好的有限生成器，不是无先验发明所有动作设计。

`search.py` 只收真实物理稳定落地且实际词等于预期词的候选，并按 `(能力集合, 实际动作词)` 留档，当前 quality 仅接收平台宽度。该档案不是已经实现的 FI-MAP-Elites；行为 descriptor 也只是计数/反转统计。几何 hash 仅是量化几何代理，未覆盖全部碰撞语义，更不等于新的玩家决策或趣味。archive 的不准确 geometry 注释已更正，实际 key 没有改变。

`actual_word` 比输入 token 强：跳、射击使用受理事件，hook 使用真实抵达状态。然而射击受理可能未承担通关作用；二段跳可能被随后动作覆盖；挂点可被绕过。必须保留动作消融与替代解，不能用动作次数替代设计价值。

`alternatives` 目前是少量 walk/jump/double/recoil/hook/wall 低成本家族、3 个起始时机，以及单动作删除。它能找出真实反例；没有找到只表示这批策略未找到。它没有穷举瞄准、连续空控、多挂点选择、动态相位、最优到达时间或能力子集下全状态空间。因此 `remaining_shortcuts=0` / `modules_without_discovered_shortcuts` 应逐字解释为“有限搜索未发现”，不能推出必需能力、最小动作数或不存在高手捷径。仅删除动作但保留后续状态 gate 也会缩小搜索能力，不能据其失败认定被删动作必要。

`separate_counterexample` 在参考轨迹体积之外添加少量伤害矩形，再回放原 witness。这样证明的是保住这条参考路径并对已知低机械成本解作反例细化。它不证明噪声下公平，也不证明荆棘有真实宿主；当前是抽象危险 Cell，不应作为已完成森林美术/生态附着规则验收。其他成功路线被保留是正确的多解处理，不应为了提高组合必要性数字删掉有价值路线。

## 成对扰动应如何解释

当前修复建立相同几何、同一 seed/语义 key/幅度的触发时机与瞄准扰动。feedback 仍每帧读取完美状态，settle 轴直接应用，state gates 可等待真实状态；没有传感器误差、执行器延迟或持续摇杆误差。应称“自动策略对命令触发与瞄准扰动的成功率”，不能称玩家操作容错、人类成功率或真实手感稳定性。

fixed policy 从干净参考回放提取时刻/方向/尾部轴，属于同轨迹 open-loop 基线。干净组两者必须都回放成功；否则先排查基线实现，不应比较有噪声百分比。正式复核还要检查共同 key 的 noise_records 一致、固定尾部 axis 零额外 jitter、相同模块几何哈希、修复/选样发生在 holdout 之前。重复 seed 跨模块形成相关样本；不能把所有 rollout 当独立玩家样本计算漂亮置信度。

## 后续准入与未验范围

1. 冻结 v5 搜索与新 evaluation，逐组公布成功/失败和 proposal 总预算；缺覆盖的组合不隐藏。保留原始输出、引擎日志、源哈希与旧失败。
2. 点查 wall、hang、bounce、double/recoil 顺序与 two-hook chains 的实际帧、资源及稳定落地；检查 holdout 配对和低成本替代解分类。
3. 在同 Cell/物理预算下增加真正不同的控制候选与参数搜索，输出替代 witness，分别报告发现反例与未发现的范围。将实测动作效应、风险/奖励、落点选择、恢复机会作为后续设计维度，不只追求更长动作词。
4. 从有效候选抽取少量不同体验假设，由独立审查实际试玩/录像；主动比较最便宜打法、原打法、失败恢复与重复决策，淘汰无新增判断的候选。当前无人类试玩证据，趣味保持 UNVERIFIED。
5. Runtime 只应消费已验证的规则/参数安全域和轻量回退；本轮离线批次耗时不能外推到帧内生成，也没有证明全 Macro Module/Map 的资源连续性、动态敌人、能力锁或 Map Notes 正式消费者。

本轮范围状态：机制源码审计、纯 Python 合同与独立反例 passed；修复后 Godot 原始数据独立核算与配对统计 passed；3 个有退化解的内容候选 REWORK，低容错 bounce 链需优化；动态挑战、独立可视试玩、运行时预算、正式游戏集成、用户与真机认可 unverified。没有将技术状态合并为“游戏需要已全面满足”。
