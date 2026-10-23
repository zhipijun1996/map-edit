# PCG-RESEARCH-02 能力组合合同与独立反证审计

审计角色：只读能力合同与反证，未修改生成器、worker或游戏源。源码冻结为 `gunman-rush@12f6cb006d7119598e3235f4ca4f7323e4c9d092`，Godot4.7.2。原字节与逐文件SHA在 `evidence/composable-audit/index.json`。本阶段是代码事实审计，尚未签署新算法的运行结果、趣味、设备或生产准入。

## 一、必须纠正的恢复语义

**钩索接触和蹬墙恢复额外空跳/钩索资格，不恢复射击次数。**

`TraversalAbility.restore_air_actions()` 只在已启用double时调用 `JumpAbility.restore_air_jump()`，并在hook启用时清 `hook_used`。它没有 `ActionResources.grant_shot`。所以纯 `shot→hook→shot` 或 `shot→wallkick→shot` 若全程不落地、不真实命中，在当前一发基础配置中不合法。

射击次数在真实落地时由 `ActionResources.reset()` 恢复；真实空中命中经 `PlayerController.on_projectile_hit→ShotEnergyPolicy.on_hit→queue_grant(1)` 在后续Controller帧提交一次限额补弹。`restore_air_actions`被命中路径调用，是另一独立效果，不能把二者合并为一个“所有资源恢复”。钩索对敌人伤害的 `on_grapple_damage`只记战斗能量，不是补弹路径。

当前 `enable_shot_energy()` 默认读取 `resources/player/demo_ui_01/time_energy_v2.tres`，`shooting_consumes_energy=false`。旧 `plains_shot_energy.tres` 与部分fixture仍有历史耗能；不得因为类名/旧测试把当前射击写成固定扣20。

## 二、实际能力表

| 能力ID/建议语义 | 真正运行入口/前置条件 | 消耗/恢复 | 生成器注意 |
|---|---|---|---|
| move | InputRouter轴→Controller→Motor.step；ground/air acceleration由真实tuning读取 | 无独立次数；仍受锁定、墙面和能力速度覆盖 | 无move的实验必须禁止轴意图，不能把`axis=0`等同角色不会被反冲/拉近移动 |
| jump | JumpAbility.enabled、请求/缓冲窗口、used_jumps小于当前flight cap；地面/coyote与空跳由真实used_jumps处理 | 普通起跳占第1资格；落地重置；走下平台过coyote会把used设1 | 不从“有jump token”猜当前是否可跳；缓存grounded与接受顺序影响同帧 |
| shot_recoil | ShootAbility.enabled、武器未占用、有效非零方向、cooldown≤0、余弹>0、Controller非traversal.busy；RecoilAbility.enabled决定位移 | 当前空中一发；地面延后结算pending_ground_shots；落地/真实空中命中恢复；一般hook/wall不补弹 | `shooting`与`recoil`是可区分组件；当前组合ID把它们作为一个受支持原语需明示 |
| double_jump | Traversal.grant('double_jump')设capacity_floor=2；JumpAbility.enabled且原tuning.max_jumps>0 | 第二跳占资格；真实接触/墙跳/命中在double启用时可令used_jumps=1 | 高于基础能力的合法授予，不应覆写tuning.max_jumps。grant发生在空中时_air_max保守裁剪，不能凭grant制造即刻多跳 |
| grapple | grant('grapple')；state free/hook_hang或合法尾段、未消耗H、有效方向、真实ShapeCast命中group grapple_target | 发射置hook_used；miss不恢复；落地、成功挂点/弹起到达、wallkick/真实空中命中可恢复H | 当前实际range231wu，不是Definition脚本默认460。hook_contact只是射线命中/开始pull；真正到达hang/contact_kick才是相应恢复点 |
| wall_climb | grant('wall_climb')；不在地面、Motor.is_on_wall、没有recoil burst；真实接触墙面必须group wall_climbable；normal.x * axis < -0.1 | wall_jump须state wall_attach和wall_ready；离墙lock约0.12秒，至少5wu分离后允许再次贴墙；恢复额外跳和H | 墙跳不是任意空中jump，不得仅摆一个墙矩形就宣称可蹬。tag、方向、碰撞法线与分离状态都要进证据 |

实际源码位置：[授予与hook资格](https://github.com/zhipijun1996/gunman-rush/blob/12f6cb006d7119598e3235f4ca4f7323e4c9d092/scripts/player/traversal_ability.gd#L45)、[wall_jump](https://github.com/zhipijun1996/gunman-rush/blob/12f6cb006d7119598e3235f4ca4f7323e4c9d092/scripts/player/traversal_ability.gd#L102)、[真实到达与挂点跳](https://github.com/zhipijun1996/gunman-rush/blob/12f6cb006d7119598e3235f4ca4f7323e4c9d092/scripts/player/traversal_ability.gd#L224)、[恢复](https://github.com/zhipijun1996/gunman-rush/blob/12f6cb006d7119598e3235f4ca4f7323e4c9d092/scripts/player/traversal_ability.gd#L315)、[跳跃](https://github.com/zhipijun1996/gunman-rush/blob/12f6cb006d7119598e3235f4ca4f7323e4c9d092/scripts/player/jump_ability.gd#L46)、[射击](https://github.com/zhipijun1996/gunman-rush/blob/12f6cb006d7119598e3235f4ca4f7323e4c9d092/scripts/combat/shoot_ability.gd#L74)、[真实命中补弹](https://github.com/zhipijun1996/gunman-rush/blob/12f6cb006d7119598e3235f4ca4f7323e4c9d092/scripts/combat/shot_energy_policy.gd#L49)。

## 三、事件不能只按按钮名分类

- `wall_jump()`不发 `JumpAbility.jumped`，它通过Traversal的`wall_kick`转移可观测。只计jump信号会漏墙跳。
- `jump_from_anchor()`发jumped时Traversal仍为hook_hang，之后才设hook_kick。它使用第二跳速度，并令used_jumps至少1；不消费一个新的普通地面跳，也不等于普通double_jump。
- 普通空跳可根据请求前ground/coyote、used_jumps与请求后接受状态分类；只有used_jumps=2并不足以解释是否来自恢复后的空跳，恢复来源要保留。
- 同帧Controller先处理jump，再处理shoot；后者取消jump ascent，Motor shot burst把普通竖速度清零。`jump+shot`两条接受事件不证明两者都有实际位移贡献。
- 第二跳会清正在进行的recoil burst；射击会取消跳跃hold/ascent。因此 `jump→shot→double` 与 `jump→double→shot` 可能确实不同，但要看真实速度/轨迹与删动作反证，不能仅把按钮重排计成新玩法。
- 成功目标应以稳定末态为准：中心在出口集合、完整身体安全、连续若干帧落地且速度低、剩余资格合法；“某帧曾到过”不保证可交接。

## 四、可执行组合与初始几何建议

以下引用原生测试的输入/接触结构，不代表新候选已经通过：

1. **H→H连续挂点**：原 `tests/grapple_feel_runner.gd` 的 hanging_rehook 使用spawn(0,182)、floor(-200,200,500,30)、hang A(100,50)、B(250,35)。真实等待hook_hang后再向B发H；没有落地。旧挂点会从探针例外中排除，适合验证新动作链的非落地恢复。
2. **起跳→H→挂点跳→反冲**：将第一钩点放在本次真实飞行中可见/可达位置；只有达到hook_hang后触发jump，再在合法非busy状态射击。此组合只有一发，符合当前弹药。
3. **起跳→二段跳→反冲** 与 **起跳→反冲→二段跳**：在同一个能力/入口快照下采样两种真实动作词，用不同落点高度、返向修正与删动作搜索确认用途。不得为维持原始反冲时长跳过真实clear_recoil行为。
4. **墙贴附→wallkick→反冲/二段跳**：原测试用spawn(260,650)、墙(280,-3000,45,3700)、axis+1约0.15秒接触→wall_attach→Router jump。可缩小墙到模块所需尺寸；保持axis+1会在实际分离后回到同墙，适合重复wallkick但需防无限攀爬廉价解。
5. **H→挂点跳→H**：新H在手动挂点跳尾段可受控打断；应验证原Router TTL/epoch，不能刷新旧请求时间戳模拟接受。动态目标仍需相位/目标活性，当前静态挂点样本不能外推。

特别警告：`tests/actor_actions_runner.gd.fixture()`明确把 `max_air_shots=2` 并绑定历史能量定义。其几何/输入可作参考，不能复制资源参数到当前生成器。`wall_jump()`底层本身没有读 `JumpAbility.enabled`；若生成器规定wall_climb必须同时有jump，这是生成策略政策，而非原API绝对依赖。

## 五、任意组合支持的准确边界

“能力集合不再硬编码成base/double/hook几个profile”是可以实现的扩展；“任意未来能力自动获得准确物理模型和高质量关卡”目前没有证据。

每项能力插件最低合同应包含：稳定ID与版本、实际授予/撤销适配器、前置条件与互斥、真实输入绑定、可观察状态/接受事件、资格消耗与各真实恢复来源、环境affordance、依赖Definition与核心源SHA、可采样的前后状态域以及正/负例。未注册ID、未知规则、互斥或缺前置一律拒绝/unknown；不能回落all profile偷偷授予更多能力。武器模式/等级也属于快照，因为同一shot的距离、占用状态、伤害与资源规则会变化。

对四种可选能力的16个子集逐项验证，可证明该有限集合的组合路径覆盖。若move/jump固定存在，则不能把结果写成全部64子集。具有能力不代表生成关卡强制需要该能力；最低能力要求只能由反证搜索与设计声明共同建立。

## 六、替代解与鲁棒性反证

推荐在同几何/入口快照下按成本从低到高搜索：纯移动、早/晚单跳、满跳/最短跳、普通跳+反冲、单钩点直达、二段跳绕行、同墙重复wallkick、从奖励台边缘取巧。把动作数/风险/时间作为搜索顺序，不能用“本见证删动作失败”替代重新规划。运动状态去重至少含位置/速度、跳/射/钩资格、冷却、Traversal阶段与目标；没有完整物理快照时从起点重播前缀更诚实，不能只恢复Motor位置。

反馈控制方案必须由Router轴/动作执行，不设置角色状态。按当前真实位置瞄准 `aim_target` 有助容错，但旧误差注入若只旋转`direction`会被该自动瞄准覆盖，造成虚假100%。正确做法是在最终瞄准向量提交前注入角误差；触发时机/观测延迟也要明确。固定程序和闭环策略应共享同几何、同噪声序列，避免把加宽落点和控制器收益混为一谈。

档案质量应避免单纯奖励短/窄/动作数。token或事件signature覆盖只是行为代理，尚不代表观察、承诺、恢复、失败学习或奖励选择真正不同；趣味仍需真人。连续安全通过和噪声曲线可作为工程门槛，不代签G5。

## 七、后续独立审查待办

新worker/DSL/搜索冻结后复核：未知能力拒绝、无多授予、hook/wall不补弹、非法第三跳/第二发被拒、H miss不恢复、wall tag/方向反例、事件触发timeout、稳定出口、真实最终误差注入、同源同噪声对照、动作分类与实际计数、费用/重复输入口径以及全部失败原件。当前本文件仅接受上述源码事实；运行结果、泛化和用户体验保持未验证。
