# PCG-RESEARCH-02：重复墙跳与挂点循环独立审查

审查者 `ability_contract_audit`；只读审查实现者的算法、已有输入/输出、日志及游戏源。采用仓库 `gameplay-reviewer`，未修改算法、未启动 Godot、未以旧公开 Web V2 代替本轮测试。当前按冻结版本分别记录，旧失败保留。

## v5 最终结论

**ACCEPT：限定静态基础Cell原型的重复动作合同、连续恢复与接收回放。** `repetition-v5` 及 `repetition-search-six-final` 原始数据的独立核算通过；`v4` 的三条假连续反例没有被追签，另存于下节。

| 检查 | 最终实际结果 |
| --- | --- |
| 专项墙循环 | same/alternating × 2/3/6次 × 有/无二段跳，共12个probe与12个接收Module；每条实际wall_jump/air_jump数量与请求相同。每阶段合计44次墙跳、22次空跳。 |
| 真实分离、再贴墙 | probe与Module各32段相邻墙跳区间；从真实贴墙位置计算最大离墙横移最小62.67wu、最大183.85wu，均超过5wu，实际再贴墙与墙跳受理可见。单墙接触x约182.9；双墙x约182.9与−0.9交替。 |
| 排除落地恢复 | 12条墙probe与12个Module从首个到末个关键受理事件之间均无grounded，包含每次墙跳后的最后一次空跳；v4偷恢复已被修复。 |
| 挂点恢复 | 四次真实bounce抵达+四次air_jump，probe与Module关键区间均无grounded，Module稳定。纯四钩仍只有三次抵达、第4次miss，失败保留。 |
| 收尾 | 13/14专项动作词实现；13个已物化Module全满足ok、实际词匹配、关键区间无落地，最终稳定接收。运动probe本身没有真实终点，常以frame_budget/out_of_bounds结束；不将“先完成动作后出界”说成整个probe通关。 |
| 语法自动搜索 | six-final：6条提案、12几何回放通过；仍只有1种六wall_jump词、6个几何hash、1档案项。不是12种新动作体验。 |
| 不可满足预算 | move+shot_recoil请求最少6动作，返回0提案/0几何/0物理调用，原因no_grammar_word；没有降为空词。独立重跑12项纯Python测试通过。 |

独立核算命令：`PYTHONDONTWRITEBYTECODE=1 python3 evidence/composable-audit/repetition/review_repetition.py v5`，退出0、`failures=[]`。逐案例帧区间、动作数、接触x、离墙量、输入/输出哈希、源检查、测试输出见 `evidence/composable-audit/repetition/v5-review.json`，日志见 `v5-review.log`。作者运行与审查者读取数据是两个角色，本报告不冒充独立再运行Godot。

修复使用真实Router输入：同墙空跳后及时回向原墙，避免长时间远离后降回起台；接收面筛掉会提前截获旧下降支路的候选，再用物化后轨迹复核。没有抬初次跳、改物理或直接补资源。接收面的提前截获检查仍是保守几何提案过滤，接受依据是最终真实回放与中间落地检查。当前只证明确定性干净输入下这些有限循环可行，未做本轮噪声容错、低成本替代路线或人类趣味评价。

实际执行源码与冻结现源的运动/生成文件哈希一致。两份v5运动回执记录旧11项测试文件，之后仅新增不可满足预算的第12项测试；旧测试源恰好已由本审查快照保存、SHA匹配，测试文件不参与生成运行。旧/新测试文件与来源告警保留在 `v5-source/`、`v5-review-first-pass.json`，独立12项测试回执另录；不需要用重跑引擎掩盖这项已解释的测试文件变更。

## v4 结论与反证

**历史版本：复用墙面/挂点不能按消耗品计数的修正方向 ACCEPT；“12 个墙例均证明不中途落地恢复”的命题 REJECT。** `repetition-v4` 确有 12 个同墙/双墙、2/3/6 次墙跳、启用/禁用二段跳的真实动作链，且 12 个接收 Module 均稳定通过。四钩加四空跳另有一个稳定通过；纯四钩在第四次真实 miss，失败保留。总计 13/14 动作词实现，13/13 已物化 Module 稳定。

独立脚本 `evidence/composable-audit/repetition/review_repetition.py` 不导入作者统计函数，重新从真实接受事件/挂点状态提取词并复算输入哈希、ID、进程退出、日志及落地窗口，回执为 `v4-review.json` / `v4-review.log`，执行退出 0。这表示反证与原始数据一致，不表示反证消失。

| 发现 | 实际数据及影响 | 处理状态 |
| --- | --- | --- |
| REP-R1：同墙+二段跳中途落地补资源 | 2 次例 motion 帧86–97、3次例91–100及175–184、6次例88–100等五段均落在 launch，y=419.93。接收平台也会提前截获旧循环：2次例 Module 帧71–84、y243.96；3次例两段y235.93；6次例多段receiver与launch交替。 | 原3例不能证明连续空中恢复；v5改控制返回与接收面并在物化后重新检查，已通过，v4不覆盖。 |
| REP-R2：最小动作预算被空词回退绕过 | 原 `search.py` 若derive无词仍 `words=[()]`，请求最少6动作也可能降为空词。 | 最终源码移除回退并记录 `no_grammar_word`；不可满足预算运行及独立测试通过。 |
| REP-R3：hook 无落地统计为空集真值 | 原 probe 用 wall-attach commands 定义窗口，hook案例没有wall commands，`all(empty)`也写true。 | 独立按首末实际hook/空跳窗口复查：四钩+四空跳帧31–280在motion与Module确无grounded；最终统计器改为实际事件窗口并增加Module检查，复核通过。 |

其他9个墙例在真实帧关键区间无中途落地。所有相邻墙跳之间从前一真实贴墙位置计算的最大离墙横移均超过5wu；这证明空间分离确实发生，再次墙跳有真实wall_attach，而不是直接授予库存或循环调用API。四钩+四空跳是真正四次进入 `hook_contact_kick` 与四次受理 `air_jump`；纯四钩只有三次进入contact_kick，第4次hook_miss，不以raw hook_contact冒充成功抵达。

## 算法与搜索的可宣称范围

`contracts.py` 已移除 `walls=1`、`anchors=3` 的人工库存上限，墙跳后设置wall_ready=false，必须提出wall_separate、真实再接触才允许下一次；hook资格可由真实到达恢复。墙跳/挂点不恢复子弹这一事实继续保留。抽象wall_separate不是几何证明，compiler需真实等待、移动与重新贴墙，最终引擎回放仍是准绳。

`synthesis.py` 的same与alternating布局、墙跳握手和Router制动属于有效几何/控制策略。提高墙高、改变初始动作是允许的原型修复；修改Motor、资源或暗中重置状态则不是。本轮没有这些物理作弊。但不断扩展相同墙体和重复同一技巧本身不证明挑战的新意、压力或难度。

`repetition-search-six` 实测6条运动提案、12个几何回放均稳定，实际只有**1种六次wall_jump动作词**、6个量化几何hash、1个档案项。它证明完整grammar→primitive合成→物理接收回放流程可搜索到六次墙跳；不能称12种新玩法。该批capabilities只有move+wall_climb，普通jump禁用，支持原角色低层墙跳确实独立于普通跳。alternating双墙来自专项probe，不能假称这一批自动搜索自己选择了两种墙布局。

`max_depth`、`min_actions` 是计算预算，不是乐趣目标。当前有frontier384、depth32、plan128、probe时长等实际边界；长词可提案不等于所有物理成立，简单循环过多也可能挤掉少见动作组合。固定360帧的通用probe对长组合仍可能过早截断，专项900帧结果不应外推成任意长度Runtime支持。

后续噪声比较还有一个接口风险：alternating probe内有一个settle，materialize又添加exit/settle；现有fixed_policy在首settle处break，因此不能自动保证后一个settle的共享触发误差公平对照。本轮没有使用它发布新的paired指标；下次做容错搜索前需处理多settle策略，不能外推旧V2噪声数字。

## 源与未验范围

独立重算原Godot副本的 **870文件** 哈希，零漂移；执行 `git diff --name-only 12f6cb006d7119598e3235f4ca4f7323e4c9d092 54573a8e9400d790f58656efde2dd812cc00d8ba -- config/player_tuning.json scripts/player scripts/input scripts/combat resources/player resources/weapons scenes/player project.godot`，退出0、输出为空。结论限定该提交对与这些动作路径；不说整个仓库无变化，也不把当前工作树HEAD12f6冒充54573。

本轮已有证据是静态基础Cell、真实Motor与输入路线；没有新做移动齿轮平台、动态相位、正式荆棘伤害、能力压力区或动态敌人。后续应将“可贴墙/可钩/可落脚/危险朝向/移动轨迹/相位”作为有实际消费者的环境合同，资源验证包含每个接触与连续恢复；先做小规模动态回放，再讨论批量生成。不得以当前重复次数或接收成功率代签这些能力。

没有新公开Web；旧公开V2用旧算法，不能作为重复墙跳修复验证。审查者没有观看本轮录像或操作试玩，不签视觉、手感、人类趣味、正式游戏消费者或真机通过。
