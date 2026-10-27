# Native Module services v5（隔离后端）

`pcg.migration.godot_package_v5`复用现有数据编译、原生执行和证据验证。公共分发已在实验静默窗口应用并冻结，见 [native-v5-public-activation-v1.json](../../pcg/migration/foundation-v1/native-v5-public-activation-v1.json)；现在由 `pcg.migration.godot_package` 按显式 v5 数据选择后端。补丁 `pcg/migration/patches/native-v5-dispatch-v1.patch` 保留应用来源，旧 v1–v4 后端及其绑定依赖没有重写。

## 精确原始 fixture

Case 仍使用四字段 `original_tuning_profile`：`id`、`overrides`、`abilities`、`effectiveTuning`。另附 `original_fixture_profile`：

```json
{
  "provider": "original_fixture/v1",
  "id": "original-fixture-1j2s",
  "source": {"path": "pcg/migration/source-resource-v9/challenge_recoil_tests.gd", "sha256": "使用 original-resource-driver-v9.json 的固定 SHA"},
  "initializer": "ChallengeRecoilTests._fixture",
  "max_jumps": 1,
  "max_air_shots": 2
}
```

支持两项精确来源：1j2s 使用上例；2j2s 使用 `branch_library_runner.gd`、`BranchLibraryRunner.fixture`、`original-fixture-2j2s`。对应 profile 的 overrides/effectiveTuning 必须正好声明这两个容量；abilities 为 move/jump/shot_recoil，2j 另含 double_jump。不替换为 2j4s air_chain，不改正式默认。

`runtime/native_profile_v5.gd.new().initialize_once(controller,profile,fixture)`只能在新角色 frame0 前调用一次。它复现原 fixture 的 tuning 变更：challenge fixture 原样 reset 一次；branch fixture 原码没有 reset，因此不增加该步骤。原地面恢复仍由原角色物理完成。`verify_existing`只核对精确身份、SHA、容量，保留当前剩余资源。Module.bind 从不初始化或回充。

## 区域宝箱 OR

Case 字段 `original_region_chests` 每项必须正好有：

```json
{"id":"cache","position":[100,200],"tier":"high","items":[],"coins":6,"reward_mode":"resources","resources":[{"kind":"coin","amount":6},{"kind":"note","amount":2}]}
```

金额、tier 和位置来自真实原始世界 `_reward`/合同；缺少金额返回缺口，不猜默认值。原始零金额保留，但不能声明为必须获得的奖励。

文档对应 reward 对象为 24×24 视觉标记，中心与 position 相同，mechanics 为：`service="DemoApp._region_interact/_claim_region_chest"`、`interactionRadius=80`、`selection="OR"`、`source=<同一宝箱数据>`。原生消费者使用真正 `PlainsRegionStage.nearby_chest`（严格距离小于80）、原 `StageRewardModal`、原 `_commit_interact/_region_interact/_claim_region_chest`、Wallet、MetaProgression。不是自动 coin pickup，也不会同时发 coin 和 note。

辅助 API 位于 `runtime/original_region_chests_v5.gd`：

- `setup(data,host,player,existing_scope,wallet,meta,shared_region_state,instance_id)`；Meta、共享 PlainsRegionState 和稳定 instance ID 必须显式提供。
- `request_interaction()`、`request_choice("coin"|"note")`、`capture()`、`snapshot()`。
- capture 在真实伤害 policy 后执行。回放动作显式记录 `native_region_interact`、`native_region_choose`（kind 字段）；可以在同一 capture 按顺序排队，因为原 modal 暂停世界时间，选择本身不推进角色物理。人工操作会看到并点击原始选择弹窗。
- `required_region_chest_choices=[{"id":"cache","kind":"coin"}]`只用于实际选择的路线，按宝箱 ID 绑定真实事件，未选择路线不能伪称领取。
- 原 UI 清空输入是原行为；回放日志 axis 记录该帧已应用的输入，另保留 `axis_after_native_interaction`，不能隐藏清空。
- 同一实例重复进入必须复用共享 state；真实领取写入原 `region_state.claimed`。外层世界快捷路服务仍是 UNKNOWN，本后端不实现 Map。

v5 Module API 在 v4 参数后追加 `native_region_state`。纯普通 pickup 仍使用原 v4 consumer；v5 后端仅添加所需语义，不改变旧包。
