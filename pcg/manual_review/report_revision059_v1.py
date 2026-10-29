from pcg.migration import core,physics
from .continue_revision059_v1 import rows,label,OUT,AUTH
from .finalize_revision059_v1 import folder_for
from .report_revision058_v1 import formal_summary
GAPS={
'hq01':dict(reason='Six fixed native directions pass; independent initial P/Q phases fail the all-route screen.',cause='The input program still assumes the illustrated frozen stair pose. A real group shot preserves both original independent clocks, so another phase can park P/Q outside the demonstrated transfer window.',next='Build a state-driven start/board/park/transfer program for alternative frozen poses; if a pose cannot meet real clearance, return exact trace before changing approved tracks/phases.',designDefectProven=False),
'hq02':dict(reason='Upward screen passes all13, but downward screen fails clean1 and mild1 from real player damage. The moving-platform interception intent has no positive native projectile-disposal receipt.',cause='The illustrated full-body middle dock is outside the original sentry activation range; the canonical first fired seed follows an earlier steep locked aim and does not produce a proven P interception. Real native fire/telegraph cancellation was observed and retained.',measurement=dict(originalActivationRange=180,middlePlatform=[64,356,64,12],fullBodyMiddleRightmostCenter=[116,338],sentryCenter=[320,308],minimumDistance=((320-116)**2+30**2)**.5),next='First revise the lure/jump/board inputs to preserve a shot after actual fire. If the middle dock must initiate the shot while standing, consider extending its right edge so a fully supported player can enter180px activation range; this is a design proposal only, not applied. Keep original sentry/projectile parameters.',designDefectProven=False),
's12':dict(reason='All12 fixed native demonstrations pass; the randomized screen is not all-route passing, so no formal/holdout was started.',cause='The Q transfer improves left-side TOP access, but right-to-T and bottom boarding still lose support or hit a solid carrier at some phases; some recoil paths leave the legal rectangle and the high-shore clearing guard can time out.',next='Use actual support and swept ceiling clearance, earlier braking, and adaptive takeoff timing. If relative carrier paths/phases or one-way attributes must change, submit exact conflicting traces for review first.',designDefectProven=False)}
def main():
 result_rows=[];table=[]
 for row in rows():
  n=label(row);f=folder_for(row);hq=n.startswith('hq');p=f/('playable-final-v2'if hq else'playable');qp=next(f/name for name in ['qualification-reobserved.json','qualification.json','qualification-not-run.json']if(f/name).exists());q=core.read(qp);full=q['passed'];selection=core.read(f/'selection.json');screen=core.read(core.resolve_artifact(selection['screen']['path']));movies=sorted((OUT/'videos').glob('native-'+n+'-*/manifest.json'));current=[v for v in movies if core.read(v).get('nativeOutcomePassed')];v=max(current,key=lambda v:v.parent.name);movie=core.read(v);assert movie['nativeOutcomePassed'];vid=dict(movie=physics.artifact(v.parent/'native.mp4'),manifest=physics.artifact(v),receipt=movie['nativeReceipt'],strict=movie['strict'],reviewOnly=movie['reviewOnly'],nativeOutcomePassed=True)
  package_result=f/('package-result-final-v2.json'if hq else'package-result.json');formal=core.REPO/f'pcg/results/approved-r059-{n}-qualified-final-v1/migration-physics.json'
  status='FULL_V2_VALIDATED_WITH_COUNTER_SCOPE_REANALYSIS'if n=='hq05'and full else'FULL_V2_VALIDATED_CANDIDATE'if full else'UNQUALIFIED_PLAYABLE_CANDIDATE'
  r=dict(schema='pcg/approved-design-implementation-result/v1',name=n,reviewId=row['reviewId'],moduleId=row['moduleId'],designVersion=row['designVersion'],designSource=physics.artifact(core.REPO/row['designFile']),baseDesignSource=row['baseDesignSource'],status=status,qualified=bool(full),qualification=physics.artifact(qp),validationScope='FULL_v2_with_original_raw_counter_scope_reanalysis'if n=='hq05'and full else'FULL_v2'if full else'fixed_native_samples_only',formal=formal_summary(formal),screen=screen['counts'],screenEvidence=selection['screen'],parameters=physics.artifact(f/'parameters.json'),sourceModule=physics.artifact(f/'module.mapnote.json'),implementationProvenance=physics.artifact(f/'implementation-provenance.json'),nativePlayable=dict(scene=physics.artifact(p/'demo.tscn'),manifest=physics.artifact(p/'godot-package.json'),result=physics.artifact(package_result),actualNativeCases=len(core.read(p/'cases.json')['cases'])),videos=[vid],originalPhysicsChanged=False,designWebChanged=False,humanPlaytest='UNKNOWN',productionApproval=False,designImpossible=False,certificationUnknown=['mirror','partial-port closure combinations','arbitrary entry states','full Map'])
  if n in GAPS:r['uncompleted']=GAPS[n]
  if n=='s02':r['repair']=dict(before='Previous up route failed finite full-ride safe-window calibration.',after='Native jump/recoil to the approved middle ledge, actual support-based carrier boarding, then top disembark; complete FULL_v2 passed169 attempts.',bottomIngress='Original jump stays vertically aligned through the complete64px aperture before moving to internal350 dock; Port remains320,640.')
  if n=='s11':r['repair']=dict(before='Bottom receiver wrongly applied right-side-only eligibility; previous formal did not certify corrected runtime.',after='Bottom actual shot accepted by the same original complementary group; all6 routes FULL_v2 passed363 attempts.',threeReceiverShots=physics.artifact(core.REPO/'pcg/results/approved-r059-s11-three-access-v1/access-checks.json'))
  if n=='hq04':r['mechanism']=dict(actualOriginalService='SimpleRoomReward',coins=4,onlySuccessfulUniqueCommit=True,originalNativePairAntiCrush=True,idempotentSaveAndSameRunReentry=True,sameWorldExternalLRewardL=physics.artifact(OUT/'verification/hq04-reward-loop.json'),nativeReentry=physics.artifact(OUT/'verification/hq04-native-reentry.json'))
  if n=='hq05':r['mechanism']=dict(gateSeconds=4,turretCooldown=.6,childDelay=.05,childSpeed=720,childLifetime=1,originalProjectileSweep=True,fixedDirection=[.4472135954999579,-.8944271909999159],newChildIdentityWithRealParent=True,extraPlayerRecoil=False,ammoRefund=False,actualGuardChecks=physics.artifact(OUT/'verification/hq05-turret-guards.json'),counterErratum=physics.artifact(OUT/'verification/hq05-counter-scope-reobserved.json'),returnPlan='Drop through top deck to the closed gate, then shoot the return receiver upward. Jump from catch deck only after actual child projectile opens gate.')
  core.write(OUT/(n+'.json'),r);result_rows.append(dict(name=n,reviewId=row['reviewId'],qualified=full,result=physics.artifact(OUT/(n+'.json'))));table.append(f"| {n} | {'完整v2通过（反例空间复核）'if n=='hq05'and full else'完整v2通过'if full else'可玩，未完整认证'} | {r['nativePlayable']['actualNativeCases']} | [{n}.json]({n}.json) |")
 core.write(OUT/'index.json',dict(schema='pcg/approved-design-implementation-index/v1',main=core.read(AUTH/'request.json')['main'],scope=7,playable=7,nativeDirections=31,qualified=sum(v['qualified']for v in result_rows),unqualifiedCurrentCandidates=3,results=result_rows,legacyCarryWithoutNewHoldout=physics.artifact(AUTH/'legacy-connectors.json'),productionAdmitted=False))
 text='''# 最新审批实现与旧失败修复（revision059）

基于 main `7106d08c`，在独立分支/worktree实现。设计网页、审批几何、轨道和原游戏870份文件均未修改。本轮7项、31个固定初态原生通行样品；HQ03新修订和HQ06–HQ10未审批，不实施。先前六个连接件沿用旧证据，不改种子重抽留出。

| 规格 | 验证状态 | 原生方向 | 场景、参数和证据 |
| --- | --- | --- | --- |
'''+ '\n'.join(table)+'''

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
'''
 (OUT/'README.md').write_text(text);print('REPORT_7_NATIVE_31_DIRECTIONS_FULL_V2',sum(v['qualified']for v in result_rows))
if __name__=='__main__':main()
