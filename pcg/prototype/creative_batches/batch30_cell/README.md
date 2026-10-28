# 单风铃互斥双门 Cell

最终运行版本：`runner_v3.gd` / `main_v3.tscn`。这是一个新增机制Cell，未入Module库，不增加本批30个Module计数。原角色、弹丸、资源、ShotLatch和共享Harness均未改动。

## 配置

继续使用原case.latches，每项可添加：

```json
{
  "id":"pair-a",
  "bell":[180,350],
  "gate":[450,250,24,188],
  "paired_gate":[850,250,24,188],
  "initial_open":"A",
  "open_seconds":0
}
```

`gate`是A门，`paired_gate`是B门。`initial_open`只接受A/B；真实弹丸击中同一个原接收器后交换两门，重复命中能交换回来。可用原`return_access`加同机关的另一接收器，但不会自动使射线或反向路线可用。`aim_cell={kind:"bell",id:"pair-a"}`仍使用原枪口迭代瞄准，照常叠加实际噪声。

调用WorkshopEngine时，`runner_script=HERE/'runner_v3.gd'`；`extra_sources`至少包含`pair_latch_v1.gd`、`pair_latch_v2.gd`、`pair_latch_v3.gd`、`runtime_v3.gd`、`runner_v3.gd`、`main_v3.gd`、`main_v3.tscn`及protocol。v3继承v2的真实敌人防夹与v1接收器/事务逻辑，不能漏绑基类。

## 互斥与防夹

A/B是实际StaticBody2D+RectangleShape2D；每次切换在原deferred提交中一次完成，两门实际collision_layer及shape.disabled同步互补。没有一帧允许两门同时打开。

若拟关闭的门与真实角色/敌人身体重叠，则**整次请求拒绝**，保持原一开一关，不等角色进去后强行夹门。v1有24×36角色AABB+6单位余量，v2另用Godot PhysicsDirectSpaceState2D.intersect_shape查询闭门矩形grow6，过滤实际CharacterBody2D。敌人中心在门外、身体边缘伸入仍会阻止关闭；不挪敌人、不造成伤害。玩家需移开再射，关门请求不会排队偷偷生效。

原ShotLatch的射击身份、session/health/lifetime epoch、事件去重、音效和冷却继续复用。blocked不增加switch_count，原射击资源照常消耗。`motion_mode=true`仅借原接收器重复注册门控，重写提交与绘制；不代表此Cell有移动平台或自动停靠。

## 状态与验证

每帧及最终`workshop.paired_gates[]`记录：`id,open_a,open_b,gate_a_layer,gate_b_layer,gate_a_disabled,gate_b_disabled,switch_count,blocked_count,events`。切换事件记录frame/open/airborne；阻挡事件记录closing、真实碰撞blockers类别与位置。`plains.bells[]`仍给原接收器open_count，不能只看该计数推断哪扇门可走。

v2防夹覆盖真实原EnemyActor（存活HP3且未受门伤害）、玩家、两初态切换往返、原投射物空中命中、真实通门/堵门对照、独立输入扰动、重复送达/旧health epoch/取消pending/取消接收器/失效lifetime。故障注入脚本只用于Cell测试，不是生产控制策略。

旧探针错误也保留：v1四件entry=exit被原Definition拒绝；一件空中测试恰在要关闭门内，Cell正确拒绝；另一件B门对照的起点已在门后，修正输入后重新通过。没有改门槛或删除这些失败。

v1/v2/v3各一段原生60Hz演示，均124帧与原物理见证严格逐字段一致；只演示Cell两次切换，不是人工试玩或生产准入。目录：`generation/workshop/batch30-cell-v{1,2,3}/native-two-swaps/`。源码、完整运行/失败/预算见`receipt-v3.json`。

原生Cell消费者对非pair case也可复用，过滤pair项再接回原world；不建立另一份物理。不得因门互斥就给Module填`no_path`或声称单向；路线、资源状态、接缝与返回仍须逐案原Godot验证。

## V3最后加固

v1/v2所有观测物理帧均一开一关；v3额外将deferred事务内部赋值改为先关闭目标门、后打开旧门，任何内部步骤也不出现双开，中间双关不跨物理帧。没有增加挂铃/自动行为。最终117 Harness案例（含旧拒绝与输入错误）+3原生回放=120次实际调用，未超预声明预算。
