# 本轮八项修改与 Godot 证据

以授权记录中的 main 为冻结基线，在独立分支/worktree 实现；不改设计网页或870份原游戏文件。八项均有真实 Godot 无伤固定初态样品及原生加载回放。技术资格按下表逐项声明，不自动转为人工试玩或生产认可。

| 规格 | 完整技术验证 | 原生样品方向数 | 入口 |
| --- | --- | --- | --- |
| 196 | 通过 | 6 | [样品与证据](196.json) |
| 220 | 通过 | 6 | [样品与证据](220.json) |
| 42 | 未完整通过 | 6 | [样品与证据](42.json) |
| 51 | 通过 | 2 | [样品与证据](51.json) |
| 52 | 通过 | 2 | [样品与证据](52.json) |
| 50 | 通过 | 6 | [样品与证据](50.json) |
| three | 通过 | 2 | [样品与证据](three.json) |
| lift | 未完整通过 | 2 | [样品与证据](lift.json) |

196 底口改为真实64×12可穿平台；明确需要原版普通跳和蹬墙能力，下方进入不再使用非法AIR INOUT。51/52顶边和屋顶危险上移128px，下层中央地貌与危险下移64px，整体上下各增加128px；原钩和侧口不移。42/50/220保持审批地貌，修改真实输入控制。

三怪、升降井保持原3HP敌人、四台、三锯及运动/伤害参数。顶部台和箱下移32px，在出口增加原ShotLatch风铃和4秒计时门；顶口初始OUTPUT，仅出不进。实测关闭时上下两侧都不能穿门；成功样品射铃后原生起跳，从自有台越过边界，落在显式相邻模块的可穿平台。该邻台只属于测试邻居，没有编入模块。可选宝箱保留，不强迫取箱。

## 未完整通过

- 42：完整校准中 entry→exit、C→exit 的中扰动分别6/12、5/12，未达原门槛；这两路未抽取留出。其余四方向通过。固定初态六路样品不能替代这些失败；尚无几何不可行证明。
- 升降井：上升筛查1/1、4/6、3/6，内部恢复1/1、6/6、6/6。下台预测、换层和上锯净空仍需更可靠控制；没有选择正式版本或动用留出。样品保留原难度，真实清怪后同世界登顶，没有复活或补弹。

后续先改实测反馈控制；需要移台、改锯周期/敌人间距时，反馈具体冲突后再改图。本轮不追加第二份正式候选，不以换种子或降低门槛救过，遵循[工厂skill](../../../../.agents/skills/pcg-module-factory/SKILL.md)“不能事后提预算、换 seed 或放宽门槛救过”。

## 测量修订和证据范围

196原报告全部六路及接缝通过，被一条离开矩形后绕回的反例否决。保留原False报告与raw，仅按已有外部空间规则只读重分析，不把外绕认证为内部捷径。50原报告两条C接缝从可穿台顶以下2px初始化；按已有174/62夹具规则，使用互异合法起点-2、0、-4px，只补两条接缝，不重跑名义路线或留出。两项都有限定范围和拒绝篡改回归。

A→A-retry仅表示内部恢复样品；完整边界自环、镜像、部分Port封口组合、任意进入状态和整Map均UNKNOWN。220鲜活空怪命中回充的上返通过不授予死敌状态重复上返。

影片60FPS、1倍速、末尾冻结1秒，全部逐字段严格比较失败仍标REVIEW_ONLY；差异和原生trace逐片保留，不放宽比较器。三怪/升降井v1影片的Port文字曾默认显示INOUT，v3仅修正显示为冻结合同OUTPUT；旧片保留；v2录制因显示脚本解析失败中止，日志保留，v3修正后完成。AI实际检查完整影片抽帧，不能代替真人手感或人工观感。

## 复现

先按[WORKSPACE](../../../../pcg/WORKSPACE.md)恢复原游戏并安装精确官方Godot4.7.2。每项JSON链接其真实场景、原生receipt、参数和MP4；从仓库根运行：

```bash
pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 --path pcg/prototype/godot "$PWD/pcg/manual_review/implementation/revision-053-final-v1/<moduleId>/playable/demo.tscn" -- --case 0
# 省略 --replay 为手动操作；添加 --replay 重放原生输入。--case N 选择对应样品方向。
python3 pcg/tools/restore_archive.py approved-revision053-implementation-v1 --verify-parts-only
python3 pcg/tools/restore_archive.py approved-revision053-implementation-v1 --extract
python3 -m pcg.manual_review.audit_revision053_v1
```

[几何、原生包、版本预算与870原件核验](verification/geometry-source-budget.json) · [全量成功/失败raw归档](verification/raw-archive.json) · [原话与冻结预算](authorization/request.json)。npm run check通过；自动生成的设计投影已还原。新main另有六份角落审批，不擅自扩大本轮八项范围。
