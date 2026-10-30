"""Publishable result records; qualification, demonstrations and approval stay separate."""
import json
import subprocess
from pcg.migration import core, physics
from .new_ideas_v1 import rows, label, OUT, AUTH
from .finalize_ideas_v1 import folder_for

def main():
    results=[]
    for row in rows():
        name=label(row);f=folder_for(row);passed=name!='enemies-3'
        videos=[]
        for p in sorted((OUT/'videos').glob(name+'-*/manifest.json')):
            manifest=core.read(p)
            videos.append(dict(movie=physics.artifact(p.parent/manifest['clips'][0]['file']),manifest=physics.artifact(p),strict=False,reviewOnly=True))
        qualification=physics.artifact(f/('qualification-reanalyzed.json'if name=='orbit'else'qualification.json'if passed else'qualification-not-run.json'))
        record=dict(schema='pcg/approved-design-implementation-result/v1',reviewId=row['reviewId'],moduleId=row['moduleId'],name=name,designVersion=row['designVersion'],designSource=physics.artifact(core.REPO/row['designFile']),status='QUALIFIED_CANDIDATE'if passed else'UNQUALIFIED_PLAYABLE_CANDIDATE',qualified=passed,qualification=qualification,sourceModule=physics.artifact(f/'module.mapnote.json'),parameters=physics.artifact(f/'parameters.json'),nativePlayable=dict(scene=physics.artifact(f/'playable/demo.tscn'),manifest=physics.artifact(f/'playable/godot-package.json'),result=physics.artifact(f/'package-result.json'),actualNativeCases=6 if name=='orbit'else 3),videos=videos,humanPlaytest='UNKNOWN',humanVideoObservation='UNKNOWN',productionApproval=False,approvedGeometryChanged=False)
        if name=='enemies-3':
            record['uncompleted']=dict(route='A-to-B',screen=dict(clean='0/1',mild='2/6',moderate='5/6'),reason='Nominal zero-noise and original native replay pass. Random idle pose, attack/recovery timing, recoil and TOP mouth alignment still fail the fixed screening gates. Twelve executed semantic versions exhausted; no formal/holdout selected.',designImpossible=False,suggestedNextSteps=['后续新预算中改进真实位置/速度/命中反馈控制；先固定攻击落点和顶口对齐，再作新校准。','若要改变几何，应另行审批敌人间距或顶口接岸布局；当前没有几何不可行证明，不能直接认定必须改图。'])
        if name!='orbit':
            record['persistentEnemyLimitation']='Real ground shots kill the first diver. It remains dead after exiting/reentering A in the same active world; this frozen ascent then times out. Alternative dead-enemy ascent UNKNOWN. No automatic respawn, healing or resource reset added.'
        if name=='orbit':
            record['counterInterpretation']='Two ordinary-jump counters leave the exact Module beyond the selected TOP aperture. Original failures/raw retained; readonly reanalysis marks external-space dependence UNKNOWN, not an internally certified shortcut. All nominal calibration/holdout and boundary gates unchanged.'
        path=OUT/(name+'.json');core.write(path,record);results.append(dict(name=name,reviewId=row['reviewId'],qualified=passed,result=physics.artifact(path)))
    core.write(OUT/'index.json',dict(schema='pcg/approved-design-implementation-index/v1',baseMain=core.read(AUTH/'request.json')['main'],scope=3,qualified=2,playable=3,results=results,families=2,variantsAreNotSeparateFamilies=True,formalPhysicsAttempts=742,aggregateAtFrozenHandoff=dict(qualified=78,total=85,oldUnresolved=['42','50','51','52','196','220'],newUnqualified=['enemies-3']),productionAdmitted=False))
    readme='''# 新创意实现与真实 Godot 证据 v1

本轮精确冻结 main `54b02eef` 的三份已审批规格；两种敌人数量属于同一玩法家族。设计网页、地貌、敌人位置和原游戏物理均未改。原 82 项的结论保留；此冻结范围累计 78/85 通过，旧 42/50/51/52/196/220 未在本轮重试。

| 规格 | 技术结果 | 可玩样品 / 证据 |
| --- | --- | --- |
| 环岛（三口六向） | 六向校准、留出、30 个边界探针通过；498 次正式实测 | [结果](orbit.json) |
| 两怪连续上升 | 上升、返回、恢复校准及留出，18 个边界探针通过；244 次正式实测 | [结果](enemies-2.json) |
| 三怪连续上升 | 三路零噪声及原生回放通过；上升筛查未通过，未用正式留出 | [结果](enemies-3.json) |

三怪最终筛查：上升 clean 0/1、轻扰动 2/6、中扰动 5/6；返回和恢复各 1/1、6/6、6/6。原版敌人游荡初始位置、俯冲/恢复位移和反冲使顶口对齐仍不稳定。12 个已执行语义版本达到登记上限，未换种子或放宽门槛；这不是设计不可行证明。后续可在新授权预算中改进实测反馈控制，若改敌人间距/顶口布局须另行审批。

环岛原始报告的两个反例越过顶部合法口之外的 Module 外空间。保留原始失败，用原 498 次 raw 只读重分析为“外部空间依赖、UNKNOWN”；不认证为内部捷径，不改名义控制或门槛。见 [22 项回归](counter-scope-regression.json)。

补充实际验证：两种敌人数规格均在同一世界完成 A 外→完整进入→内部恢复→A 完整退出；角色 epoch、世界时钟连续，无重置。第一怪被真实击杀后，退出再进入仍死亡，现有上升控制超时；死敌状态的其他玩家解仍 UNKNOWN，没有自动补怪或治疗。环形 Cell 四个初相各连续运行两圈，真实承载、无旋转；同铃真实启／停／再启／再停。原观察器把空列表误比零、以及采样时钟的一帧次序问题保留，均只读重分析，未重跑留出。见 [补测](extra-fixtures-reanalyzed.json) 与 [启停](loop-toggle-reanalyzed.json)。23 次额外夹具调用（含 4 次定义拒绝）在预登记 48 次内。

参数均绑定原版 Cell：闭合 17 点轨迹 / 4 秒；原 ModuleMovingPlatform 与 ShotLatch；原 plains_diver 巡航、俯冲、3 HP、碰撞、弹药命中返还。底台真实站立点由顶面减原身体半高 18px 得到；原图中的 staging 意图留在授权原件。可选宝箱采用原奖励消费者、4 币；图标大小映射到无碰撞的原 36×36 奖励消费者，中心不变，未改变审批对象。未要求强取可选奖励。

顶部 ONE_WAY 台面在 y32，实际站立中心 y14，身体有 4px 穿过边界。夹具明确邻模块台面 y−96，先通过自有顶台再完整进入；出口从真实内部口完成原路线后起跳。保留原完整 24×36 身体、顺序、口宽和安全门槛。这是明确邻居配置的验证，不能推断任意邻模块安全。

6 段 MP4 均 60 FPS、1 倍速、末尾冻结 1 秒；[抽帧审阅](verification/ai-video-observation.json)。严格比较均为 REVIEW_ONLY，仅原 `workshop` 字典不同；所有被比较的位置、速度、生命、支撑和敌人事件一致。逐字段失败原件和 trace 保留。仅 AI 实际查看 18 张解码帧，人工观感、手感和生产认可 UNKNOWN。

## 运行可玩候选

先按 [WORKSPACE](../../../../pcg/WORKSPACE.md) 恢复 870 个原游戏文件并安装精确官方 Godot 4.7.2；原件 SHA 全部通过。

```bash
python3 pcg/tools/restore_archive.py godot-runtime-v1 --extract
pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 --headless --editor --path pcg/prototype/godot --quit
# 从仓库根运行；--case 选择相应 cases.json 中的路线，省略 --replay 即真实操作。
pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 --path pcg/prototype/godot "$PWD/pcg/manual_review/implementation/new-ideas-final-v1/idea-orbit-choice-001/playable/demo.tscn" -- --case 0
```

两怪、三怪对应 `new-ideas-final-v1/idea-0363f85c-16c0-4b5f-b3b0-461335608db7-enemies-2` / `-enemies-3`；各有三路。编译入口显式使用 `pcg.migration.ideas_runtime_v2`，不会冒充旧通用编译器自动支持新 Cell。

[原始归档清单](../../../../pcg/archives/approved-new-ideas-implementation-v1/manifest.json) 保存全部本轮成功、失败、源快照、执行命令和 raw；可核验后恢复：

```bash
python3 pcg/tools/restore_archive.py approved-new-ideas-implementation-v1 --verify-parts-only
python3 pcg/tools/restore_archive.py approved-new-ideas-implementation-v1 --extract
python3 -m pcg.manual_review.audit_ideas_v1
```

`npm run check` 通过；其自动生成的设计投影已还原。没有改正式准入、没有自动合并或发布设计页。
'''
    (OUT/'README.md').write_text(readme)
if __name__=='__main__':main()
