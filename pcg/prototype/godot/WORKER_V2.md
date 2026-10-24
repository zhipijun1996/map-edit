# PCG-RESEARCH-02 真实能力组合 worker

本轮新增 `capability_adapter.gd`、`runner_v2.gd`、`main_v2.gd/main_v2.tscn`、`lab_draw_v2.gd`。原Motor/Controller/Router/Traversal/资源/配置字节不修改，旧runner/main与旧模块文件保留。

## 批处理接口

```sh
Godot_v4.7.2-stable_linux.x86_64 --headless --path prototype/godot --fixed-fps 60 --script res://runner_v2.gd -- --input=/absolute/batch.json --output=/absolute/results.json
```

输入仍为 `{ "cases": [...] }`，空批次明确exit2。max_frames只接受1..3600内的有限整数，避免零帧或无界预算。每个case有platforms/hazards/hooks/spawn/goal/max_frames等旧字段，新增 `capabilities:["move","jump","shot_recoil","double_jump","grapple","wall_climb"]` 的显式子集。未知能力、重复能力、double_jump缺jump、wall_climb缺move会明确拒绝；wall_climb不要求普通jump，本轮有真实普通jump关闭仍墙跳的正例。新能力必须添加真实adapter和模型，未知能力不会被当作已实现。

平台默认不带可贴墙标记；wall_platform_indices显式列出可攀墙Cell（状态机仍要求真实侧面接触）。one_way_platform_indices（别名one_way_indices）指定单向面。两类索引均将JSON数字归一为整数键，拒绝非整数及越界索引。单向平台的形状节点按原Motor约定命名为CollisionShape2D，真实drop_through可查到。能力只改变原组件enabled/grant；不会增加跳速、反冲速度、容量或直接补资源。move缺失时研究适配器只允许Router轴0。

control_plan为顺序命令数组：

```json
[
  {"op":"axis","value":1,"noise_key":0},
  {"op":"jump","trigger":{"after":5},"noise_key":1},
  {"op":"jump_release","trigger":{"after":8},"noise_key":2},
  {"op":"grapple","aim_target":[220,250],"trigger":{"state":"airborne","min_after":4,"timeout":30},"noise_key":3},
  {"op":"jump","trigger":{"state":"hook_hang","min_after":6,"timeout":60},"noise_key":4},
  {"op":"settle","trigger":{"after":25},"noise_key":5}
]
```

所有after/min_after/timeout均相对上条实际触发帧。after=0可在同帧继续下一条（最多16条/帧）。state可为airborne/grounded/hook_hang/hook_kick/hook_contact_kick/wall_attach/wall_kick/free/descending/apex。contact_kick在当前真实Traversal中的字段名为hook_contact_kick。支持axis/jump/jump_release/shoot/grapple/wait/settle/drop_through。grapple的aim_target在真实提交时由身体中心+(0,-6)瞄准；动态方向仍交由原Router/Traversal探测碰撞。settle只用Router轴反馈接近goal中心；不搬角色、不改速度和资源。

case.noise={seed,timing_frames,aim_degrees}以noise_key生成独立稳定随机数。时机噪声加在触发阈值后clamp到>=0，状态门仍有效；瞄准误差在aim_target计算完成后旋转，绝不会被动态瞄准覆盖。fired_commands保存真实触发帧/状态/位置、最终方向、threshold、timing_error和aim_error_degrees。

旧actions/axes模式仍可回放，但其噪声加在绝对输入帧；control_plan噪声作用于顺序触发阈值。比较闭环/固定策略时，两者应使用同一命令数组和noise_key，只把状态门替换为见证间隔after，从而保持同一扰动模型。输出noise_model明确标记。仅axis命令允许timing_noise=false，固定策略尾部逐帧展开轴控制使用此标志，避免把同一尾部按帧重复施加时机噪声；动作命令仍保持相同noise_key扰动。该标志只服务固定/反馈策略的公平比较，不代表真实玩家无控制噪声。

## 结果语义

ok要求：全过程安全、计划全部完成、无trigger超时/配置错误，最后连续至少6帧角色落地、|vx|/|vy|<=1且中心在goal内。trace_all=true继续完整预算，并以末帧稳定状态判定，途中到达后离开不算成功。旧actions/axes全部输入结束前也不会提前结束正例。

frames保留原请求、真实接受事件、位置/速度/grounded、资源及新增hook_used/wall_ready/can_air_jump/shot_cooldown。原jump事件外增加ground_jump/air_jump/anchor_jump；墙跳根据真实Traversal wall_kick记录，不能靠JumpAbility.jumped计墙跳。hook_contact只取实际抓取信号；raw hook_contact表示真实接触，不保证已经抵达挂点。实际动作word须从frames的hook_hang/hook_contact_kick进入状态判别，不可把raw计数直接当成功抵达。钩索与墙跳可恢复额外跳/hook资格，绝不补shot_charges；只有原落地/命中消费者允许的资源变化会发生。

仍只验证StaticBody平台、真实钩点及完整身体对静态危险包络的保守扫掠；没有正式荆棘伤害/奖励交易/敌人/存档消费者。物理通过不签人工趣味或设备体验。

## 可玩入口

`main_v2.tscn`读取modules_v2.json。Replay读recorded_frames中的真实axis/requested（也可用展开actions/axes），不是浏览器在线搜索。手动模式用原键鼠和Controller；同样要求6帧稳定出口，奖励路先访问奖励位置。window.__pcgLabStateV2暴露能力、接受事件计数、稳定帧和状态，只读，不决定玩法。

## 初次冒烟

results/worker-v2-contract/worker_v2_smoke_input/output.json、worker_v2_smoke.log保留11-case实际运行：稳定入口、非法能力/噪声拒绝、真实墙跳、普通jump关闭时墙跳，以及同seed噪声重跑逐帧完全一致。该冒烟不是全部能力组合覆盖；后续候选/消融/噪声/浏览器需按最终生成源独立验证。

显式JSON浮点索引回归：原p-c8-w0-v0现在真实wall_attach 316帧、wall_jump 1次；该控制尚未稳定完成，仍报告frame_budget。worker_v2_oneway_input/output.json证明one_way_indices=[0.0]通过原Router drop_through、落在下层平台并稳定成功；worker_v2_empty_input.json明确exit2。

UI headless解析与实际启动通过；无move候选经真实KeyboardMouseAdapter按D后Router轴为1，20真实帧后axis=0、dx=0，未被Controller重新覆盖。144字长title的下拉宽755，保留回放按钮；镜头增加纵向跟随以覆盖高出口/墙跳。证据ui-no-move.log；临时夹具已移出Godot导出目录，均保存在results/worker-v2-contract。

## 研究录像入口

movie_v2.tscn从正式modules_v2.json按combo_index=3/4/7/11/14/15各选首个候选，以真实recorded_frames或展开actions/axes回放。每段稳定成功或明确失败后停留30帧，输出MOVIE_V2_SEGMENT（id、安全、连续稳定帧、真实接受事件、能力），全部结束输出MOVIE_V2_COMPLETE后退出。场景切换重新实例化原物理夹具，不在段内跳位或修改速度/物理。录像只证明已记录的输入能回放，不能代替人工趣味评测。

```sh
Godot_v4.7.2-stable_linux.x86_64 --path prototype/godot --fixed-fps 60 --write-movie /absolute/research-v2.avi res://movie_v2.tscn
```

lab_draw_v2对高低出口及向左墙跳出口双向追踪镜头；main_v2仍是正式可玩入口。正式20候选中6段代表真实录制完成，headless和原生录制逐段id/事件/帧数/安全与稳定结果完全一致。delivery/composable-v2/modules.mp4为1280×720、60FPS、13.13秒，recording-results.json保存分段对照；全部6段真实连续稳定6帧。combo4双钩显示“容错待优化”，录像不据此宣称稳健或趣味性。
