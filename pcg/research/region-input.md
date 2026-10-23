# 区域输入驱动的生成原型

本原型让区域特色进入候选的机制、运动方向和实际几何约束。入口为 [`prototype/dynamic/regions.py`](../prototype/dynamic/regions.py)，两个输入示例为 [`sky_islands.research.json`](../regions/sky_islands.research.json) 和 [`mushroom_caverns.proposed.json`](../regions/mushroom_caverns.proposed.json)。它们都是研究配置，不能用作正式区域 Bible、美术准入或人工验收。

浮岛会实际拆分长墙、移除不属于该区域的已知压力 Cells，并拒绝仍然过宽、过高或方向错误的候选。仅改区域名、颜色或几何标签不能通过检查。变换后旧物理回执全部失效，必须重新运行真实 Godot 角色；`check_candidate(...) == []` 仅表示通过提案筛选。

## 使用接口

从仓库根目录启动 Python，并把 `prototype/dynamic` 放到模块搜索路径前面：

```python
import sys
sys.path.insert(0, "prototype/dynamic")
from regions import (
    prepare_regions, filter_families, transform_candidate, check_candidate,
)

# 由本次 run 的实际解锁状态提供，不能为满足区域要求而自动补全。
available = ["move", "jump", "double_jump", "wall_climb", "grapple", "shot_recoil"]
spec = prepare_regions("regions/sky_islands.research.json", available)
families = filter_families(spec, ["thorn_wall", "hook_chain", "carrier_double"])

# case 是原始候选；frames 必须来自同一候选的真实参考运动。
regional = transform_candidate(case, reference_frames, spec)
violations = check_candidate(regional, spec)
if not violations:
    # 接入 runner_v3：重新物理验证、误差扰动、能力消融和轨迹比较。
    enqueue_real_godot_validation(regional)
```

最后一行是调用方接入点，并非本模块提供的函数。变换不会修改输入对象、玩家轨迹、角色资源或候选的 `capabilities`。调用方不能把另一条轨迹套在候选上，再沿用旧通关结论。

| 接口 | 返回及失败方式 |
| --- | --- |
| `prepare_regions(path, availablecaps, runtime=True)` | 读取 JSON、验证字段及能力，返回包含 hash 的 prepared spec；不支持的运行输入抛 `RegionSpecError`。 |
| `validate_region_spec(authored, availablecaps, runtime=True)` | 相同验证，用于内存中的作者输入。 |
| `filter_families(spec, families=None)` | 与显式 `generator_families` 求交集。候选仍须经过几何检查，族名不是区域符合证据。 |
| `transform_candidate(case, reference_frames, spec)` | 返回复制后的候选；无法安全转译时抛 `RegionTransformError`，不能静默放行。 |
| `check_candidate(case, spec)` | 返回 `{code, path, ...details}` 违规列表；空列表没有物理可行、趣味或最低能力证明含义。 |

`runtime_eligible` 仅表示允许进入本研究提案管线，不表示已可部署到正式游戏。当前只接受 `research_only` / `proposed` 状态，尚未提供“正式批准”状态。

## 输入字段

未知字段会拒绝，避免拼写错误悄悄变成无效配置。

| 字段 | 定义 |
| --- | --- |
| `schema` | 固定 `pcg/region-spec/v1`。 |
| `version`, `id`, `status` | 正整数版本、小写下划线 ID、`research_only` 或 `proposed`。 |
| `name`, `description` | 可读说明，无几何验证效力。 |
| `mechanisms.allowed` | 实际消费者允许生成的机制 ID。 |
| `mechanisms.required` | 候选实际对象中必须存在；必须是 allowed 的子集。存在机制对象不等于玩家实际使用了它。 |
| `mechanisms.forbidden` | 不允许的机制 ID，不能与 allowed 相交；未列入 allowed 的实际机制同样拒绝。 |
| `capabilities.requires` | 进入该区域的最低已解锁能力。不会由生成器授予。 |
| `capabilities.preferred_challenge_capabilities` | 希望探索的能力，属于搜索偏好，既不授予也不要求每段使用。 |
| `traversal.allow_repetition` | 当前要求 true；动作和能力可重复。实际重复次数仍受角色真实资源与状态约束。 |
| `traversal.must_use_all_available` | 必须为 false。可用能力集合与某段挑战的使用子集分开。 |
| `traversal.min_actions`, `max_depth` | 动作提案预算，满足 `1 <= min_actions <= max_depth <= 32`；调用生成器须消费它们，本过滤器不把长度标签当作真实动作执行证明。 |
| `traversal.preferred_actions` | 已注册动作规则 ID 的偏好列表；研究配置不能用未实现动作。 |
| `geometry.direction` | any / upward / horizontal。upward 要求出口中心高于出生点；horizontal 要求水平位移不少于垂直位移。 |
| `geometry.min_goal_rise` | 显式设置时要求 `spawn.y - goal_center.y` 不小于该值；未设置不限制升降。 |
| `geometry.small_rock.width`, `.height` | 各为正数 `[min,max]`；约束实际静态矩形。 |
| `geometry.max_contiguous_height` | 限制连续攀爬面；紧贴矩形合成同一连续墙，不能通过切标签逃过限制。 |
| `geometry.min_vertical_gap` | 有水平重叠的相邻墙岩块最小竖向间隔。 |
| `geometry.port_support_exceptions` | `{max_width,max_height}`；仅实际支撑出生点或出口中心的台面可豁免 small_rock 尺寸，仍须满足例外上限。伪造 entry_port 标签无效。 |
| `transform.split_climb_walls` | 按真实参考轨迹接触区间拆长墙；必须具有 small_rock 约束。 |
| `transform.remove_pressure_floor` | 显式删除已知 pressure_floor 的刺及其非端口 host，避免遗留宽大底板。 |
| `transform.remove_forbidden_pressure_cells` | 当区域禁止 thorns 时，显式转译当前生成器的独立 flight_pressure Cells；识别和拒绝边界见下文。 |
| `transform.contact_padding`, `contact_x_tolerance` | 接触区间保护 padding 和面接触 x 容差，世界坐标单位。 |
| `generator_families` | 允许的提案族 ID，精确匹配；暂时沿用 thorn_wall 等构造族名不代表允许刺。 |
| `motifs` | 设计意图标签，不代替任何实际几何检查。 |

当前真实机制白名单为 `static_terrain`、`one_way`、`wall_climb_surface`、`grapple_anchor`、`thorns`、`moving_platform`、`moving_saw`。消费者映射分别使用 platforms、one_way indices、wall indices、hooks、thorns、moving_platforms、saws。只写一个 `mechanisms` 声明而没有对象，会报 `claimed_mechanism_has_no_consumer`。未承载在真实 host 上的旧 `hazards` 包络也不合格。

## 浮岛转译的边界

示例要求向上至少 120 wu，岩块宽高各 32–160 wu，连续攀爬面至多 180 wu，岩块竖向至少分开 24 wu。出生与出口实际支撑台可至多 360×180 wu。允许蹬墙、二段跳、钩索和反冲任意重复组合的探索，但不会强制单个模块同时用尽四种能力；齿轮、移动平台与刺在这个研究配置中禁止。

长墙只保留真实参考轨迹 wall_attach / wall_kick / accepted wall_jump 所需要的接触带。角色碰撞体尺寸从受保护的真实 `player.tscn` 读取，当前为 24×36 wu，并记录源 SHA；不另设一套角色参数。小岩块保留真实接触 X，加入角色半高和 contact_padding 后合并保护区间。如果一个不能切断的保护带超出 160 wu，变换会拒绝，不会擅自剪断运动所依赖的墙。

独立压力 Cell 删除是显式的研究区域转译。当前仅识别 `generators.pressure_surfaces` 的 `flight_pressure_<正整数>` 标识，以及宽40×高24 host、top/bottom 刺面、offset0、length40、depth20的完整签名。host 若同时为墙、one-way、实际端口支撑、参考轨迹中的 grounded 支撑，或挂有另一个刺对象，会拒绝删除。签名不同也拒绝。`pressure_unknown` 等未知对象会保留并导致区域违规，不能任意删刺后宣称符合。`pressure_floor` 使用独立开关和实际端口保护；已替换长墙上的旧刺随原 host 删除，必须通过新物理重验确认安全。

删除和拆分后会重建 wall indices、one-way indices 和剩余刺的 host indices，记录每个旧 platform index 对应的新索引列表。变换记录能区分 pressure_floor host 删除、独立 flight_pressure host 删除、长墙拆分和旧 host 刺删除。

## 蕈灯地穴暂不可运行

`mushroom_caverns.proposed.json` 明确声明 `bounce_mushroom` 和 `spore_current`。两者尚无游戏消费者、真实运动和测试接口，默认执行：

```python
prepare_regions("regions/mushroom_caverns.proposed.json", available)
# RegionSpecError:
# runtime_region_rejected:proposed/unimplemented=bounce_mushroom,spore_current
```

`runtime=False` 只允许编辑器展示提案与 `unimplemented_mechanisms`。该对象仍不能交给 filter/transform 当作运行输入。把钩点、移动平台或已有反冲改名为“弹射蘑菇”不会实现该机制；应先实现蘑菇触发、冲量、再次触发/能力恢复策略、冷却和真实 Godot 自动测试，再更新机制白名单与消费者验证。

## 回执、验证与后续接入

`profile_sha256` 是作者输入的规范化 JSON hash，不含本次 actor 可用能力；`source_sha256` 是原始配置文件字节 hash。prepared 对象被修改后会拒绝继续使用，必须重新准备。候选 `region_profile` 记录版本、hash、实际可用能力、意图动作的使用子集、真实碰撞体源 hash、索引映射和全部变换，始终标记 `formal_region_approval=false`、`validation_status=requires_real_physics_revalidation`。

意图动作子集不能当作最低能力证明：额外解锁能力是否形成捷径、每项动作是否真有必要，都需要真实重放和能力消融。区域提案过滤通过后，继续现有动态管线的真实物理验证、操作误差扰动、动态相位扫描、探索多样性评价，再进入人类试玩。没有这些证据不能称“区域生成质量已达标”。

Map Notes 可先导入上述 schema，用明确的 research/proposed 标记展示机制、能力条件、尺寸范围和拒绝原因。保存配置即产生新 profile hash；预览必须引用这个 hash 对应的新生成/物理回执，不能继承旧模块结果。尚未实现编辑器集成。

验证命令：`python3 -m unittest discover -s prototype/dynamic -p test_regions.py -v`，当前 20 项通过。测试涵盖能力不偷授、不强制全部用尽、实际岩块几何、端口例外、连续墙识别、压力 host 精确识别与共享角色保护、索引重映射、方向检查、配置变更检测及蘑菇运行拒绝。本项工作未启动 Godot，未自行签发物理成功回执。
