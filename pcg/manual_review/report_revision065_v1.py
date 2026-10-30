"""Current lift completion plus the unchanged eleven prior qualified modules."""
from pcg.migration import core,physics
from .continue_revision065_lift_v1 import OUT,AUTH,ID,rows
from .run_revision066_lift_v1 import folder_for
from .report_revision060_061_v1 import formal
def main():
 row=rows()[0];f=folder_for(row);q=core.read(f/'qualification.json');assert q['passed'];audit=core.read(OUT/'verification/geometry-source-budget.json');downloads=core.read(OUT/'downloads/index.json')['rows'];films=[];technical=[]
 for name in ['lift','lift-recovery-chest']:
  p=OUT/f'videos/native-{name}-A-to-B-v1/manifest.json';m=core.read(p);r=core.read(core.resolve_artifact(m['nativeReceipt']['path']));diff=core.read(core.resolve_artifact(m['strictDiff']['path']));fields=sorted({k for d in diff['rows']for k in d['fields']});assert r['passed']and r['hp']==5 and not r['damage']and not r['returns'];assert not fields or fields==['package']
  expected=f/'playable/demo.tscn'if name=='lift'else OUT/'fixtures/missed-boarding-wait-chest-v2/playable/demo.tscn';assert m['scope']['compiledPlayableScene']==physics.artifact(expected)
  films.append(dict(name=name,movie=physics.artifact(p.parent/'native.mp4'),manifest=physics.artifact(p),receipt=m['nativeReceipt'],strict=m['strict'],reviewOnly=m['reviewOnly']));technical.append(dict(name=name,strict=m['strict'],changedFields=fields,nativePassed=True,hp=5,coins=r['coins'],actualFrames=r['actual_frames'],manifest=physics.artifact(p)))
 result=dict(schema='pcg/approved-design-implementation-result/v1',round='065+066',name='lift',reviewId=ID,moduleId=ID,designVersion=row['designVersion'],designSource=physics.artifact(row['designFile']),status='FULL_V2_VALIDATED_CANDIDATE',qualified=True,qualification=physics.artifact(f/'qualification.json'),formalAttempts=q['actualAttempts'],formalDirections=formal(q),sourceModule=physics.artifact(f/'module.mapnote.json'),parameters=physics.artifact(f/'parameters.json'),implementationProvenance=physics.artifact(f/'implementation-provenance.json'),nativePlayable=dict(scene=physics.artifact(f/'playable/demo.tscn'),manifest=physics.artifact(f/'playable/godot-package.json'),result=physics.artifact(f/'package-result.json'),actualNativeCases=2,zip=downloads[0]['file']),bonus=dict(evidence=physics.artifact(OUT/'fixtures/missed-boarding-wait-chest-v2/recovery-reward-evidence.json'),zip=downloads[1]['file'],formalQualification=False),videos=films,mainSpecificationCommit='43f1a18f',originalGamePhysicsSourceChanged=False,authorizedGeometryDelta=dict(added='relay-dock',x=0,y=544,w=64,h=12),allExistingMotionUnchanged=True,priorFailedFormalQualification=physics.artifact(core.REPO/'pcg/manual_review/implementation/revision-065-final-v1'/ID/'qualification.json'),humanPlaytest='UNKNOWN',productionApproval=False,unknown=['mirrors','closure combinations','arbitrary entry states','full Map'])
 core.write(OUT/'lift.json',result);prior=core.read('feedback/manual-review/implementation-results/revision-063-v1/index.json');complete=[r for r in prior['results']if r['qualified']]+[dict(name='lift',reviewId=ID,qualified=True,result=physics.artifact(OUT/'lift.json'))];assert len(complete)==12
 current={r['reviewId']:r for r in core.read('feedback/manual-review/implementation-handoff-v1.json')['rows']}
 for r in complete:
  d=core.read(core.resolve_artifact(r['result']['path']));assert d['designVersion']==current[r['reviewId']]['designVersion']
 core.write(OUT/'index.json',dict(schema='pcg/approved-design-implementation-index/v1',round='065+066',scope=1,qualified=1,playable=1,nativeCases=2,bonusNativeCases=1,originalTwelveTaskScope=12,originalTwelveTaskQualified=12,results=[complete[-1]],completedOriginalTwelve=complete,totalCaseConservativeUpperBound=audit['totalCaseConservativeUpperBound'],mainSpecificationCommit='43f1a18f',productionAdmitted=False))
 core.write(OUT/'verification/media-technical-audit.json',dict(passed=True,rows=technical,strictComparisonNotRelaxed=True,reviewOnlyDoesNotReplaceFormalPhysics=True))
 core.write(OUT/'verification/ai-video-observation.json',dict(observer='Codex primary agent',method='Actual view_image inspection of six representative relay/upper/exit frames from both completed native movies.',frames=physics.artifact(OUT/'verification/video-frame-selection.json'),observations=['两段影片均可见左侧中继台、四载台和三锯；中继抽帧中角色在左侧中层等候。','上层抽帧可见角色已接上L2，末帧到达上方出口；图像细节需在原片放大。','10秒等待、错过上台后回落及4币领取由原生输入、支撑与奖励回执证明，缩略图不单独授予资格。'],humanPlaytest='UNKNOWN',noQualificationFromImagesAlone=True))
 text='''# 升降井中继台完成（revision065–066）

按用户“好的，加一个中继台”，仅新增左侧中继台x0、y544、64×12px。四载台、三道横锯的轨道、速度、周期、初相位和停留均保持；原空怪、可选宝箱、顶部风铃门及顶口初始OUTPUT保留。规格已同步main `43f1a18f`。

升降井完整FULL v2通过，共167个正式案例；上行与底口恢复路线的校准、独立留出在clean/mild/moderate下均达原门槛。结合[前轮已通过的11项](../revision-063-v1/README.md)，原12项任务现全部技术验证通过。旧报告不覆盖，当前精确版本与汇总见[index.json](index.json)。人工试玩与生产批准仍UNKNOWN。

- [正常升井试玩ZIP](downloads/lift-native.zip) · [正常升井实机片](videos/native-lift-A-to-B-v1/native.mp4)
- [错过上台→中继接回→等10秒→取4币→出井试玩ZIP](downloads/lift-relay-recovery-chest.zip) · [完整实机片](videos/native-lift-recovery-chest-A-to-B-v1/native.mp4)
- [逐方向资格与参数](lift.json) · [中继恢复及原生奖励回执](fixtures/missed-boarding-wait-chest-v2/recovery-reward-evidence.json)

## 实际行为

控制先搭L1落到中继台，再独立等L2与上锯的窗口。中继站位(20,526)，真实24×36身体距中锯扫掠下沿、左侧载台外形分别有20px净空；实际10秒落稳等待、一次故意错过上台后的同世界接回均通过，无伤害或世界重置。可选宝箱由原消费者真实领取4币。

底台直接跳加一次向上反冲的12个有界尝试未到达中继台，没有使用载台；这是有限检查，不能证明所有替代路线不存在。正式反例、身体边界、机关因果和接缝按原FULL门槛执行。

## 修复与历史证据

早期固定路线成功后，严格筛选发现最后反冲在顶口旁过高；按实际发枪高度计算方向，保留原瞄准误差。首轮正式校准又发现底部发枪靠左、上台横移启动偏晚：底部站位改32px并观察下锯，登上层时先按真实身体净空横移。原5个校准失败在相同相位、敌人冷却与误差下修复通过，再按原FULL协议最多2次适应的上限预登记066续轮；065轮的1个正式候选预算不改，总病例预算5000不变，没有新的人工审批或留出调参。

一次筛选期间补TOP绑定触发源码冻结保护，已完成24例逐字节保留，只续跑未执行的2例；原错误日志、两份源码快照与谱系均保留。该v2筛选最终仍失败，最终选择v4。独立池ID文字沿用旧helper的063标签，实际首次为066冻结候选分配，绑定按完整源码/程序/输入SHA核对，未为改标签重新抽seed。

两段影片均为Godot4.7.2原生编译场景、60FPS、1倍速、结尾冻结1秒。strict=false为REVIEW_ONLY；逐字段差异保留，不放宽比较器，不替代正式物理证明。

## 复现

ZIP在仓库根目录解压，按[WORKSPACE](../../../../pcg/WORKSPACE.md)恢复官方引擎与原游戏资源。运行JSON中nativePlayable.scene：

```bash
pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 --path pcg/prototype/godot "$PWD/<scene路径>" -- --case 0
```

省略`--replay`可手动操作；加上回放实际输入；`--case 1`选择底口恢复样品。ZIP不重复包含官方引擎及原游戏资源。

[几何/源码/预算核验](verification/geometry-source-budget.json) · [正式报告原始重算](verification/full-report-rederivation.json) · [原始归档](verification/raw-archive.json) · [AI实际抽帧观察](verification/ai-video-observation.json) · [最终检查](verification/final-checks.json)

```bash
python3 pcg/tools/restore_archive.py approved-revision065-066-lift-relay-v1 --verify-parts-only
python3 pcg/tools/restore_archive.py approved-revision065-066-lift-relay-v1 --extract
python3 -m pcg.manual_review.finish_revision065_v1 verify
```

原游戏870份保护文件未改。镜像、封口组合、任意进入态和完整Map仍UNKNOWN；实现分支未整体合入main。
'''
 (OUT/'README.md').write_text(text)
 more=core.REPO/'feedback/manual-review/implementation-results/revision-066-v1';core.write(more/'index.json',dict(qualified=True,actualAttempts=167,aggregate=physics.artifact(OUT/'index.json'),sameOngoingUserTask=True,newHumanApproval=False));(more/'README.md').write_text('# 升降井控制修订续轮\n\n完整167例通过。详见[中继台总交付](../revision-065-v1/README.md)，原065失败和有界续轮授权保留。\n')
 print('R065_REPORT_ALL_ORIGINAL_TWELVE_COMPLETE',flush=True)
if __name__=='__main__':main()
