"""Separate implemented samples, technical scope and unresolved quality failures."""
import collections
from pcg.migration import core,physics
from .continue_revision053_v1 import rows,label,OUT,AUTH
from .finalize_revision053_v2 import folder_for

def main():
 results=[];table=[]
 for row in rows():
  n=label(row);f=folder_for(row);qfile=next(f/name for name in ['qualification-reanalyzed.json','qualification-repaired.json','qualification.json','qualification-not-run.json']if(f/name).exists());q=core.read(qfile);passed=q['passed'];videos=[]
  for p in sorted((OUT/'videos').glob(n+'-*/manifest.json')):
   if n in ['three','lift']and not p.parent.name.endswith('-v3'):continue
   m=core.read(p);videos.append(dict(movie=physics.artifact(p.parent/m['clips'][0]['file']),manifest=physics.artifact(p),strict=m.get('strict',False),reviewOnly=m.get('reviewOnly',False)))
  assert videos
  selection=core.read(f/'selection.json')if(f/'selection.json').exists()else core.read(core.REPO/row['outputDirectory']/'selection.json');screen=core.read(core.resolve_artifact(selection['screen']['path']));formal=None
  if(f/'qualification.json').exists():
   initial=core.read(f/'qualification.json');report=core.read(core.resolve_artifact(initial['report']['path']));formal=dict(originalReport=initial['report'],originalPassed=initial['passed'],attempts=report['actualAttempts'],routes=[])
   for r in report['routes']:
    item=dict(id=r['routeId'],passed=r['passed'],calibration=core.read(core.resolve_artifact(r['calibration']['path']))['stats'],holdout='NOT_RUN')
    if isinstance(r['holdout'],dict):item['holdout']=core.read(core.resolve_artifact(r['holdout']['path']))['stats']
    formal['routes'].append(item)
  r=dict(schema='pcg/approved-design-implementation-result/v1',name=n,reviewId=row['reviewId'],moduleId=row['moduleId'],designVersion=row['designVersion'],designSource=physics.artifact(core.REPO/row['designFile']),baseDesignSource=row['baseDesignSource'],status='QUALIFIED_CANDIDATE'if passed else'UNQUALIFIED_PLAYABLE_CANDIDATE',qualified=passed,qualification=physics.artifact(qfile),formal=formal,screen=screen['counts'],screenEvidence=selection['screen'],parameters=physics.artifact(f/'parameters.json'),sourceModule=physics.artifact(f/'module.mapnote.json'),nativePlayable=dict(scene=physics.artifact(f/'playable/demo.tscn'),manifest=physics.artifact(f/'playable/godot-package.json'),result=physics.artifact(f/'package-result.json'),actualNativeCases=len(core.read(f/'playback-cases.json')['cases'])),videos=videos,originalPhysicsChanged=False,designWebChanged=False,userAuthorizedGeometryChange=n in ['196','51','52','three','lift'],humanPlaytest='UNKNOWN',humanVideoObservation='UNKNOWN',productionApproval=False,designImpossible=False,movieQualificationIsAsOfCapture=True,certificationUnknown=['mirror','partial-use closure combinations','arbitrary entry states','full Map','new six approved corner configurations outside this round'])
  if n in ['three','lift']:
   r.update(userIntentDifficulty='hard; original native timings retained',humanDifficulty='UNKNOWN',topPort=dict(id='B',initialPermission='OUTPUT',surface='ONE_WAY_PLATFORM',gateOpenSeconds=4,realShotLatch=True,neighborFixture='Explicit compatible one-way neighboring deck at y-32; excluded from compiled Module'),interfaceCheck=physics.artifact(core.REPO/f'pcg/results/approved-r053-{n}-top-interface-v1/interface-checks.json'),recoveryScope='A-to-A-retry is interior recovery; complete same-Port external self-loop is UNKNOWN',optionalChest='retained on upper landing; not required to use the exit',supersededMovies='v1 overlay defaulted missing block metadata to INOUT; v3 reads actual frozen legal_port_mouths OUTPUT. Original v1 movies and strict failures retained.')
  if n=='196':r['measurementCorrection']='All six nominal routes/calibration/holdout/boundaries passed. One ordinary-jump counter left the rectangle away from its selected mouth. Readonly scope correction preserves the original refusal and treats that shortcut as an uncertified external dependency; no new trials or leave-out selection.'
  if n=='50':r['fixtureCorrection']='Two +2px C seam starts embedded feet below the native one-way top. Existing174/62 rule replaces them with distinct -4px starts; two new seam trials only, original nominal and holdout unchanged. C-to-exit demonstrated via real entry landing and six actual hook contacts; no resource grant.'
  if n=='220':r['resourceLimitation']='Fresh B/C-to-A uses real airborne enemy hits and refunds. A subsequent ascent after that enemy has died is UNKNOWN; no respawn or free ammo added.'
  if n=='42':r['uncompleted']=dict(reason='Full calibration moderate entry-to-exit6/12 and C-to-exit5/12. Their holdouts were not run. Four other directions passed; all six fixed original native demonstrations pass.',cause='Hook/recoil feedback and landing timing remain sensitive; finite failure is not proof of a geometry defect.',next='A later prospectively registered control round can use actual position/velocity, real ring contact and shore clearance; retain geometry unless a concrete conflict is found. No second formal version in this round.')
  if n=='lift':r['uncompleted']=dict(reason='Ascent screen clean1/1, mild4/6, moderate3/6; recovery1/1,6/6,6/6. No formal or holdout selected.',cause='Some initial phases miss the lower-carrier boarding forecast; others collide with G2/G3 or fail the bounded real-projectile clearing stage. The original four carrier / three saw / enemy parameters are retained.',next='Improve real support, future reachable carrier and complete swept saw-clearance feedback in a later control round. If geometry/timing needs changing, report the specific conflict for approval; do not lower difficulty silently.',sameWorldActualClearing='Fixed native ascent kills the original diver with real projectiles, then exits upward in the same world. No enemy respawn or resource reset.')
  path=OUT/(n+'.json');core.write(path,r);results.append(dict(name=n,reviewId=row['reviewId'],qualified=passed,result=physics.artifact(path)));table.append(f"| {n} | {'通过'if passed else'未完整通过'} | {r['nativePlayable']['actualNativeCases']} | [样品与证据]({n}.json) |")
 core.write(OUT/'index.json',dict(schema='pcg/approved-design-implementation-index/v1',main=core.read(AUTH/'request.json')['main'],scope=8,playable=8,qualified=sum(r['qualified']for r in results),results=results,productionAdmitted=False,scopeExpansion=False))
 text='''# 本轮八项修改与 Godot 证据

以授权记录中的 main 为冻结基线，在独立分支/worktree 实现；不改设计网页或870份原游戏文件。八项均有真实 Godot 无伤固定初态样品及原生加载回放。技术资格按下表逐项声明，不自动转为人工试玩或生产认可。

| 规格 | 完整技术验证 | 原生样品方向数 | 入口 |
| --- | --- | --- | --- |
'''+ '\n'.join(table)+'''

196 底口改为真实64×12可穿平台；明确需要原版普通跳和蹬墙能力，下方进入不再使用非法AIR INOUT。51/52顶边和屋顶危险上移128px，下层中央地貌与危险下移64px，整体上下各增加128px；原钩和侧口不移。42/50/220保持审批地貌，修改真实输入控制。

三怪、升降井保持原3HP敌人、四台、三锯及运动/伤害参数。顶部台和箱下移32px，在出口增加原ShotLatch风铃和4秒计时门；顶口初始OUTPUT，仅出不进。实测关闭时上下两侧都不能穿门；成功样品射铃后原生起跳，从自有台越过边界，落在显式相邻模块的可穿平台。该邻台只属于测试邻居，没有编入模块。可选宝箱保留，不强迫取箱。

## 未完整通过

- 42：完整校准中 entry→exit、C→exit 的中扰动分别6/12、5/12，未达原门槛；这两路未抽取留出。其余四方向通过。固定初态六路样品不能替代这些失败；尚无几何不可行证明。
- 升降井：上升筛查1/1、4/6、3/6，内部恢复1/1、6/6、6/6。下台预测、换层和上锯净空仍需更可靠控制；没有选择正式版本或动用留出。样品保留原难度，真实清怪后同世界登顶，没有复活或补弹。

后续先改实测反馈控制；需要移台、改锯周期/敌人间距时，反馈具体冲突后再改图。本轮不追加第二份正式候选，不以换种子或降低门槛救过，遵循[工厂skill](../../../../.agents/skills/pcg-module-factory/SKILL.md)“不能事后提预算、换 seed 或放宽门槛救过”。

## 测量修订和证据范围

196原报告全部六路及接缝通过，被一条离开矩形后绕回的反例否决。保留原False报告与raw，仅按已有外部空间规则只读重分析，不把外绕认证为内部捷径。50原报告两条C接缝从可穿台顶以下2px初始化；按已有174/62夹具规则，使用互异合法起点-2、0、-4px，只补两条接缝，不重跑名义路线或留出。两项都有限定范围和拒绝篡改回归。

A→A-retry仅表示内部恢复样品；完整边界自环、镜像、部分Port封口组合、任意进入状态和整Map均UNKNOWN。220鲜活空怪命中回充的上返通过不授予死敌状态重复上返。

影片60FPS、1倍速、末尾冻结1秒，全部逐字段严格比较失败仍标REVIEW_ONLY；差异和原生trace逐片保留，不放宽比较器。三怪/升降井v1影片的Port文字曾默认显示INOUT，v3仅修正显示为冻结合同OUTPUT；旧片保留。AI实际检查完整影片抽帧，不能代替真人手感或人工观感。

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
'''
 (OUT/'README.md').write_text(text)
 print('REVISION053_REPORT',sum(r['qualified']for r in results),'/8',flush=True)
if __name__=='__main__':main()
