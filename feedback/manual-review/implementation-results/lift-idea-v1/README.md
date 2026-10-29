# 四台升降、三道横锯：实现与未通过项

按 main `11f35799` 新增的精确审批 `16d930fb67a6…` 独立登记本轮。四台、三锯、空怪、两口、原版物理及审批运动参数均实现；不改变设计网页。**可玩候选三路固定初态实测与原生回放通过，但未认证。**

| 路线 | 固定原初态示范 | 固定随机初相筛查 clean / 轻 / 中 |
| --- | --- | --- |
| A→B 上升 | HP5、无重置通过 | 0/1、0/6、1/6，失败 |
| B→A 返回 | HP5、无重置通过 | 1/1、6/6、6/6 |
| A→A 底台恢复 | HP5、无重置通过 | 1/1、6/6、6/6 |

协议的 clean 也随机化载台、锯与敌人的初始动态状态；“固定初态示范”不能冒充该筛查。完整底口 A→A 另用真实邻台，从外部穿入、内部起跳回落、再完整退出，同一角色 epoch / 世界时钟连续，通过；没有把内部虚拟 marker 当真实 Port 自环。

12 个语义控制版本已用完，未满足选择条件，因此没有正式版本或留出。后续仍需改进原控制对实体台侧面/底部、换乘距离、第三锯及空怪的预测和反馈；失败不能推成设计不可行证明。原有 [Module 工厂 skill](../../../../.agents/skills/pcg-module-factory/SKILL.md) 要求“不能事后提预算、换 seed 或放宽门槛救过”。本轮不通过改锯周期、移台或治疗补弹来救过。设计修改须重新审批。

## 参数和实际消费者

两固定可穿台仅在底部 y864、顶部 y32，实际站立中心846/14；审批图的832 staging 原意保留在授权源。四个移动台为原 `ModuleMovingPlatform` 实体碰撞，原矩形 Shape，未增加下穿或隐身重生：

| 台 | 中心起终点 y | 单程 / 停顿（秒） | 初相 |
| --- | --- | --- | --- |
| L1 x104 | 784→512 | 3.0 / 0.35 | 0.09701492537313433 |
| R1 x280 | 784→512 | 3.6 / 0.5 | 0.21463414634146344 |
| L2 x104 | 448→128 | 2.8 / 0.4 | 0.28125 |
| R2 x280 | 448→128 | 4.0 / 0.45 | 0.11797752808988764 |

三锯是原 `ModuleSawDefinition`，圆半径24、中心x64–320，y688/464/240，周期2.8/3.7/4.6秒、初相0.15/0.85/0.5。图中 `hazard/gears` 语义在消费者副本映射为原锯子，没把运动齿轮当静态矩形。四台 source `designMotion` 精确解码，无参数更改。空怪仍为原 `plains_diver`、3 HP、巡航/俯冲/伤害均真实。可选宝箱为原奖励消费者4币，不是上升必需条件。

[完整参数](../../../../pcg/manual_review/implementation/lift-idea-final-v1/idea-96ba6bf1-9b60-470a-9128-54ae7ea44af3/parameters.json) · [几何/参数/12版预算审计](verification/geometry-and-budget.json) · [870份原游戏文件核验](verification/source-audit.json)。

## 敌人死亡和失败恢复

20次真实地面射击只打到空怪剩1HP，原失败保留。30次的独立补测在1073帧观察到真实死亡；之后底口撤离和重新进入仍死亡，没有自动复活。沿冻结上升控制再试，在G2发生真实伤害、触发原生角色返回（epoch 1→2）；这是失败，并非同角色无重置通过。死敌主路没有通过，死敌返程尚未实测，其他解UNKNOWN。4800帧夹具被原Harness拒绝的原件也保留，后续新夹具修为原上限3600，没有修改引擎。

补做前三份规格登记预算内的4个反例：两怪/三怪各“省最后一枪”“重复用第一怪”。本次均未找到到岸解，全部保留；这只是有限搜索，不证明相应动作绝对必要。前三份正式校准和留出字节没有改变。

## 样品与复现

[结果和两个 MP4 入口](lift.json)。两片60 FPS、1倍速、末尾冻结1秒；严格比较为 REVIEW_ONLY，失败及逐字段差异全部保留。AI仅实际查看6张解码帧；底台等待明显，是当前控制的体验限制。真人手感、人工观感、生产认可UNKNOWN。

先按 [WORKSPACE](../../../../pcg/WORKSPACE.md) 恢复原游戏、安装精确官方 Godot4.7.2，再从仓库根运行：

```bash
pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 --path pcg/prototype/godot "$PWD/pcg/manual_review/implementation/lift-idea-final-v1/idea-96ba6bf1-9b60-470a-9128-54ae7ea44af3/playable/demo.tscn" -- --case 0
# --case 0 / 1 / 2 = 上升 / 返回 / 恢复；添加 --replay 重放原生示范。
python3 pcg/tools/restore_archive.py approved-lift-idea-implementation-v1 --verify-parts-only
python3 pcg/tools/restore_archive.py approved-lift-idea-implementation-v1 --extract
python3 -m pcg.manual_review.audit_lift_v1
```

编译使用显式 `pcg.migration.lift_runtime_v1`；所有成功、失败、输入、执行日志和冻结源在 [raw归档](../../../../pcg/archives/approved-lift-idea-implementation-v1/manifest.json)，原生包及回放receipt直接入仓库。`npm run check`通过，自动生成的设计投影已还原。

截至冻结 main：86份已审批中78份在各自声明条件下技术合格；旧6项和新增三怪/本升降井共8项未完整通过。本次4份新规格均有实现和可玩候选，环岛/两怪通过正式验证；不自动转为生产认可。六份双平台角落图仍未审批，本轮不实施。
