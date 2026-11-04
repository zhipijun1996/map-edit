if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core,physics
from .continue_revision063_v1 import rows,label,OUT,AUTH
from .record_revision063_native_v1 import folder_for
from .report_revision060_061_v1 import formal
def active_movie(n,f):
 matches=[]
 for p in sorted((OUT/'videos').glob('native-'+n+'-*/manifest.json')):
  d=core.read(p)
  if d['scope']['compiledPlayableScene']==physics.artifact(f/'playable/demo.tscn')and d['nativeOutcomePassed']:matches.append(p)
 assert matches,(n,'no film for active playable')
 return matches[-1]
def main():
 results=[];table=[];downloads=core.read(OUT/'downloads/index.json')['rows']
 for row in rows():
  n=label(row);f=folder_for(row);q=core.read(f/'qualification.json');p=f/'playable';d=next(x for x in downloads if x['name']==n);movie=active_movie(n,f);m=core.read(movie);sel=q.get('formalSelection')or physics.artifact(f/'selection.json');s=core.read(core.resolve_artifact(sel['path']));screen=s.get('screen')
  result=dict(schema='pcg/approved-design-implementation-result/v1',round='063+064',name=n,reviewId=row['reviewId'],moduleId=row['moduleId'],designVersion=row['designVersion'],designSource=physics.artifact(core.REPO/row['designFile']),status='FULL_V2_VALIDATED_CANDIDATE'if q['passed']else'FIXED_NATIVE_PLAYABLE_SCREEN_UNQUALIFIED',qualified=q['passed'],qualification=physics.artifact(f/'qualification.json'),formalAttempts=q.get('actualAttempts',0),formalDirections=formal(q),sourceModule=physics.artifact(f/'module.mapnote.json'),parameters=physics.artifact(f/'parameters.json'),implementationProvenance=physics.artifact(f/'implementation-provenance.json'),selection=sel,nativePlayable=dict(scene=physics.artifact(p/'demo.tscn'),manifest=physics.artifact(p/'godot-package.json'),result=physics.artifact(f/'package-result.json'),actualNativeCases=len(core.read(p/'cases.json')['cases']),zip=d['file']),videos=[dict(movie=physics.artifact(movie.parent/'native.mp4'),manifest=physics.artifact(movie),receipt=m['nativeReceipt'],strict=m['strict'],reviewOnly=m['reviewOnly'])],originalGamePhysicsSourceChanged=False,mainSpecificationSync='c04fca59',humanPlaytest='UNKNOWN',productionApproval=False,unknown=['mirrors','closure combinations','arbitrary entry states','full Map'])
  screen=screen or s.get('frozenCandidate',{}).get('screen')
  if screen:result['screenEvidence']=screen;result['screen']=core.read(core.resolve_artifact(screen['path']))['counts']
  if n=='lift':
   final=core.REPO/'pcg/results/approved-r063-lift-control-screen-lift-v13/screen.json'
   result['uncompleted']=dict(classification='四载台与三锯联合时钟下的控制余量不足',reason='可交付v8固定原生通关与同世界重试通过，上行筛选轻扰动4/6、中等1/6；最后v13上行固定1/1、轻扰动0/6、中等1/6，另一个固定诊断也出现受伤和重置。未满足冻结筛选，未打开独立留出。',lastScreen=physics.artifact(final),lastScreenCounts=core.read(final)['counts'],executedSemanticCandidates=12,budgetExhausted=True,designImpossibleProven=False,geometryChanged=False,next='建议先设计审核上下两组载台的相位/停留配合，给中层交接与上层起跳各留稳定安全窗；仍保留四载台、三锯、空怪和上方可选宝箱。当前没有改周期、轨道或危险。',bonusReward=physics.artifact(OUT/'fixtures/lift-optional-chest-v1/reward-evidence.json'))
  core.write(OUT/(n+'.json'),result);results.append(dict(name=n,reviewId=row['reviewId'],qualified=q['passed'],result=physics.artifact(OUT/(n+'.json'))))
  table.append(f"| {n} | {'完整v2通过'if q['passed']else'固定可玩，扰动未过'} | {result['nativePlayable']['actualNativeCases']} | {result['formalAttempts']} | [证据]({n}.json) · [试玩ZIP](downloads/{n}-native.zip) · [短片]({core.relative(movie.parent/'native.mp4').split(core.relative(OUT)+'/')[1]}) |")
 audit=core.read(OUT/'verification/geometry-source-budget.json')
 core.write(OUT/'index.json',dict(schema='pcg/approved-design-implementation-index/v1',round='063+064',mainSpecificationCommit='c04fca59',scope=12,playable=12,nativeDirections=23,qualified=11,results=results,totalCaseConservativeUpperBound=audit['totalCaseConservativeUpperBound'],productionAdmitted=False))
 text='''# 审批修复与六个双平台交付（revision063–064）

按本次原话完成H09初始上方只出不进、第二轮S09地刺净空增加16px、HQ07/S04/S06修复及六个LT/LB双平台。12项全部有真实Godot原生可玩包，共23条固定方向；11项完整v2通过，四台三锯升降井仍未通过扰动筛选。固定通关不等于完整合格。

对应规格已提交main：`c04fca59`。42、51、52、196、三怪、升降井规格同步至已实现布局；另落实本次H09/S09修订，8份精确版本与接口矩阵均留在[规格同步回执](../../spec-sync-r063-receipt.json)。未将实现分支整体合入main，未改其他设计提案。

| 规格 | 状态 | 原生方向 | 正式案例数 | 下载与证据 |
| --- | --- | --- | --- | --- |
'''+ '\n'.join(table)+'''

## 修复及验证流程

H09 TOP初始OUTPUT，按L→T验证，不再生成非法顶口进入夹具。S09仅把下沿岩体及其上刺下移16px，矩形、端口、锯和敌人不变；按真实窗口高度射击，底部返回先起跳再移动，避免入刺。HQ07改用实际站位与支撑判断，消除近铃水平反冲和桥边战斗越界。

S04存在验证流程缺陷：分组风铃原生控制的P/Q初始停位被旧采样器错误随机化。诊断证明后冻结版本化采样修订，用原候选、原种子与全部无关扰动重验；72项比对通过，正式170例通过，没有新抽留出。历史采样函数和旧失败保留。S06顶口连续夹具第二次穿台请求早于原Motor清除前次穿台记录，增加4帧真实输入等待后，原候选及原正式输入复测176例通过。没有写入位置或资源。

六个双平台保留原冻结程序，经窄范围、预登记的v1→完整v2升级，各分配一次此前未登记的独立池；13项正反检查约束例外，普通同程序换池仍被拒绝。HQ07/S09在校准失败后使用真实修订控制，按同一用户任务、原FULL协议最多2次适应的上限预登记revision064；不是新的人类审批。旧063失败完整保留，未用留出调参。

## 升降井剩余问题

原四载台、三锯与原空怪保留，上方口初始只出不进、射铃开门；可选宝箱真实取得4币，已有完整上行取箱再出顶口的原生包和影片。当前交付v8固定通关及同世界重试成功，但上行轻扰动4/6、中等1/6。最后v13筛选仍失败，12个实际候选已用尽预设预算，未启动独立留出。不证明模块无解。

主要难点是下台→上台交接、躲中锯和上锯、到达上层起跳窗的联合时序。建议审核上下组相位与停留配合，给交接和上行各一个稳定安全窗；当前未擅自改周期、速度、轨道或危险。详见[lift.json](lift.json)、[宝箱实证](fixtures/lift-optional-chest-v1/reward-evidence.json)与[宝箱试玩ZIP](downloads/lift-optional-chest-native.zip)。

## 试玩与证据

ZIP在仓库根目录解压，按[WORKSPACE](../../../../pcg/WORKSPACE.md)恢复原游戏资源，用官方Godot4.7.2运行各JSON的nativePlayable.scene：

```bash
pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 --path pcg/prototype/godot "$PWD/<scene路径>" -- --case 0
```

省略`--replay`为手动操作，加上回放实际输入；`--case N`切换方向。ZIP引用原游戏资源与官方引擎，不重复包含。影片为实际编译场景，60FPS、1倍速，结尾冻结1秒。strict=false保留REVIEW_ONLY及逐字段差异，不以影片替代独立物理证明。S04首段AVI没有终止回执，终止原因UNKNOWN，保留但不作通过证据；当前选用已完成且场景SHA一致的v2影片。其他旧场景影片及失败也保留。

原游戏870份保护文件未改。11份通过报告均从原始数据只读重算，原始归档包含063/064所有成功、失败、零帧拒绝与源码快照。人工试玩、生产批准、镜像、封口组合、任意进入态和完整Map仍UNKNOWN。

[授权与预算](authorization/request.json) · [续轮授权](../revision-064-v1/authorization/request.json) · [源码/几何/累计预算](verification/geometry-source-budget.json) · [完整报告重算](verification/full-report-rederivation.json) · [原始归档](verification/raw-archive.json) · [AI抽帧观察](verification/ai-video-observation.json) · [最终检查](verification/final-checks.json)

```bash
python3 pcg/tools/restore_archive.py approved-revision063-064-implementation-v1 --verify-parts-only
python3 pcg/tools/restore_archive.py approved-revision063-064-implementation-v1 --extract
python3 -m pcg.manual_review.audit_revision063_v2
```
'''
 (OUT/'README.md').write_text(text)
 more=core.REPO/'feedback/manual-review/implementation-results/revision-064-v1'
 core.write(more/'index.json',dict(scope=['hq07','s09'],qualified=2,sameOngoingUserTask=True,newHumanApproval=False,aggregateIndex=physics.artifact(OUT/'index.json')))
 (more/'README.md').write_text('# HQ07/S09有界修复续轮\n\n同一用户任务内按原FULL协议适应上限完成真实控制修订；HQ07正式172例、S09正式169例均通过。旧失败、预算和池登记保留，详见[总交付](../revision-063-v1/README.md)。没有新的人工审批或设计几何修改。\n')
 print('R063_064_REPORT_11_OF_12',flush=True)
if __name__=='__main__':main()
