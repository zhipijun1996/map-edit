# 最新审批实现与旧失败修复（revision059）

基于 main `7106d08c`，在独立分支/worktree实现。设计网页、审批几何、轨道和原游戏870份文件均未修改。本轮7项、31个固定初态原生通行样品；HQ03新修订和HQ06–HQ10未审批，不实施。先前六个连接件沿用旧证据，不改种子重抽留出。

| 规格 | 验证状态 | 原生方向 | 场景、参数和证据 |
| --- | --- | --- | --- |
| s02 | 完整v2通过 | 2 | [s02.json](s02.json) |
| s11 | 完整v2通过 | 6 | [s11.json](s11.json) |
| s12 | 可玩，未完整认证 | 12 | [s12.json](s12.json) |
| hq01 | 可玩，未完整认证 | 6 | [hq01.json](hq01.json) |
| hq02 | 可玩，未完整认证 | 2 | [hq02.json](hq02.json) |
| hq04 | 完整v2通过 | 1 | [hq04.json](hq04.json) |
| hq05 | 完整v2通过（反例空间复核） | 2 | [hq05.json](hq05.json) |

S02、S11已修复并完成真正独立的新程序FULL_v2验证，分别169与363个Godot案例。S02先使用审批的中途落脚台，再观察真实支撑登台，底口先保持完整身体竖直过口；S11下口出发会实际射中底铃，三个访问铃实射都只切换同一组一次。

HQ01新增同一事件原子控制两原生载台的Cell，保留独立时钟；六向样品可玩，但随机冻结构型筛查未过。HQ02双向样品可玩，上行筛查全过；返程少数相位实际受伤，且尚无已发射原生敌弹被P消解的正向回执，不能宣称核心拦弹玩法完成。中台最右完整身体中心(116,338)到哨兵(320,308)约206px，超过原180px激活范围。若要求站在中台引怪，可审阅延长中台右端的建议，本轮没有自行改动。

HQ04使用原SimpleRoomReward成功事务切换原防夹互补门，金币4；真实外部L→取宝→低路→外部L同世界闭环、重复领取、保存恢复和原生包重进均通过。HQ05补全门4秒、炮台冷却0.6秒、延迟0.05秒、机关弹720px/s/寿命1秒；真实父弹被吸收并发出不同身份的子弹，使用原PlayerProjectile扫掠。父子因果、固定方向、重复/错误会话/错误目标/自触发拒绝与无额外反冲/返弹检查通过。原正式报告因一条越出合法顶口的外部反例为False；按既有完整身体空间规则只读复核后通过，保留原False、所有raw及复核链，不新增物理或留出。

S12新版12向固定样品通过，随机相位仍会出现实体载台挡头、丢失支撑、反冲越界及清怪等待超时，未启动正式/留出。先改实际支撑、净空反馈与刹车；若需改轨迹、相位或单向属性，先反馈设计冲突。有限控制失败不是几何不可实现的证明。

## 试玩与影片

每项JSON的nativePlayable.scene可直接启动：

```bash
pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 --path pcg/prototype/godot "$PWD/<nativePlayable.scene.path>" -- --case 0
# --case N 选择方向；添加 --replay 自动回放，省略则手动试玩。
```

按[WORKSPACE](../../../../pcg/WORKSPACE.md)恢复精确原游戏资源，使用官方Godot4.7.2。当前影片均直接录制实际编译场景、60FPS、结尾1秒冻结。S12和HQ05严格帧比较仍保留REVIEW_ONLY；差异仅为事件来源/父因果串中的运行时对象ID，角色、载台与HP帧一致，不放宽比较器。人工试玩与生产准入仍UNKNOWN/False。失败录像、所有引擎成功/失败输出与来源快照保留。

[授权、排除项与预算](authorization/request.json) · [几何、原件、预算核验](verification/geometry-source-budget.json) · [AI影片观察](verification/ai-video-observation.json) · [原始归档核验](verification/raw-archive.json)

```bash
python3 pcg/tools/restore_archive.py approved-revision059-implementation-v1 --verify-parts-only
python3 pcg/tools/restore_archive.py approved-revision059-implementation-v1 --extract
python3 -m pcg.manual_review.audit_revision059_v1
```

没有部署网页、合并main或授予生产认可。
