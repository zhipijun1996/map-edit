# N03 开发结果：真实反向 Cell 已有小样，三口 Module 尚未成立

来源为当前 Codex 授权创意卡 `B31-N03`：向东台提供继续东岸 B，或跳离击铃让台掉头、同枪向西上反冲，由同一反向台接回并去西高岸 C。当前 **0 Module / 0 新入库 / 0 新家族成功**。两条注册规则已经用尽，不能以真反向 Cell 成功代替 Module 成功。

## 新 Cell 的实际边界

`reverse_carrier_v1.gd` 继承原 `ModuleMovingPlatform`，使用原 AnimatableBody2D、形状、碰撞、真实平台速度与承载；只更新有正负方向的 playhead。`reverse_definition_v1.gd` 调用原 Definition.at_time 的首段轨迹，新增明确的端点 hold。原平台自动往返和 start/pause 完全未改，**manual_reverse_on_hit/v1 是新 Cell**。

`reverse_latch_v1.gd` 继承原 ShotLatch，原弹丸、资格、session/epoch、冷却、事务和生命周期提交保持原组件；通过原 validated commit 的载台桥接翻转方向，不寻址/重设平台位置。不得把它标成原 start/pause。没有写人物位置、速度、枪资源或强制接地。平台和安装铃的全轨道包络需要共同预留。

32 次 Engine 调用全部保留：首8 unit输入被原静态 ModuleDefinition 拒绝（entry/exit 重合且动态台不算静态 Port），无角色轨迹；计入80预算。修正仅 dummy definition端口位于原底岸两处，unit spawn仍明确设在真实台上，**不是 Module ingress证明**。原 Cell 源未改。

修正后的8 unit场景检验中立承载、地面/空中实弹反转、空中接回、终端保持后反转、起端反转、dwell内反转、同帧重复命令、射偏：8/8有限检查通过。实际速度±120px/s，每相邻帧平台最大位移2px，所有命中提交前后位置完全相同；同帧两命令只有原冷却接受的1枪/1次翻转。原始轨迹中的部分 raw reason 是 frame_budget：这些是限定 Cell 测试，不以宽目标的 settled_goal 当 Module 准入。

只读审计 `cell-readonly-audit-v1.json` 绑定源码和原 gzip SHA；0新物理。尚未验证通用读档恢复、SceneTree暂停、破坏/卸载期间在飞弹丸、任意初相位及整图；原 `restore_motion` 不足以承诺还原新增 signed_direction，B 需要明确新 Cell 安装和状态合同。

## 三口两规则的真实失败

首规则1536×1024，A低 W anchor[0,704]、B高 E[1536,192]、C高 W[0,192]；完整 ownedcells12×8，所有高岸实际 floor224，低岸736。载台中心轨迹256→1280，y480，宽176、高20、速度140，初始中心480、向东；底岸为内部恢复，不算第四Port。

8个固定控制都在上船时撞真实台底：角色最小 centreY508，台底490，未上船；不是高度中心点通过。第二且最后规则初始台前移64到544，射击在 jump_release同刻，保持台碰撞。dy=.95两控制真实上船；dy=.98仍错过。

成功上船却落在左唇：人947.419/台1043.333，offset=-95.914。B中立随台抵达终端时人只能到1184.086，`wait_x(1240)`不可达。C确实在空中打中挂载铃让原台位置连续反向，实弹飞行13帧；由于人仍在台左唇，铃在右方，枪过横向，把人带到846，而回落时台仍1076。第一次真实着陆是原底岸，**不是反向台接回**。两个路线均未合格，未跑 noise / full / held；不删同台接回指标，不再改第三版控制。

下一设计应真正走到台中后再跳离，东向也走近出发侧，不能以中立等待的绝对 x 阈值冒充台上的相对位置。需另注册新提案及预算，不从 held 选控制。全部诊断和下一假设见 `failure-feedback-v1.json`。

## 入口与证据

```sh
python3 -m pcg.prototype.creative_batches.batch30_blockn03.request_v1
```

返回有搜索范围和具体冲突的标准 `needs_design` 响应。没有把未实现要求替换为暂停台或普通房间；没有输出把新行为错写成 start/pause 的标准 Module 文档。

可手动探索的真实 Godot 原型（界面明确标未合格，不是成功样品）：

```sh
pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 --path pcg/prototype/godot /workspace/map-edit-task-a/pcg/prototype/creative_batches/batch30_blockn03/main_v1.tscn -- --cases-json /workspace/map-edit-task-a/pcg/prototype/creative_batches/batch30_blockn03/prototype_samples.json
```

原型场景完成原 Godot `--check-only` 语法预检，未录成功视频/未编造人工观感。`prototype_samples.json` 保留未合格几何，用于手动探索；不会自动入库。

原件在 `pcg/results/workshop-batch30-blockn03-{cell-v1,cell-v2,clean-v1,clean-v2}/`，含完整输入/输出、源快照和 gzip SHA。复现用新的输出名，不覆盖原件。独立新 Cell 和 Module 总支出32/80、规则2/2，未使用 root full index15留出。人工观感/实际试玩/生产批准 UNKNOWN。
