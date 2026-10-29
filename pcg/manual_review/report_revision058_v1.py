"""Publish native samples while keeping full-v2, legacy and failed candidates distinct."""
from pcg.migration import core,physics
from .continue_revision058_v1 import rows,label,OUT,AUTH
from .finalize_revision058_v1 import folder_for

def formal_summary(path,current=True):
 if not path.exists():return None
 d=core.read(path);rs=[]
 for r in d['routes']:
  v=dict(id=r['routeId'],passed=r['passed'],calibration=core.read(core.resolve_artifact(r['calibration']['path']))['stats'],holdout='NOT_RUN')
  if isinstance(r['holdout'],dict):v['holdout']=core.read(core.resolve_artifact(r['holdout']['path']))['stats']
  rs.append(v)
 return dict(originalReport=physics.artifact(path),originalPassed=d['passed'],appliesToCurrentRuntime=current,attempts=d['actualAttempts'],routes=rs)
def main():
 results=[];table=[]
 for row in rows():
  n=label(row);f=folder_for(row);legacy=n.startswith(('lt-','lb-'));qp=next(f/k for k in ['qualification-reanalyzed.json','qualification-supplemented.json','qualification.json','qualification-not-run.json']if(f/k).exists());q=core.read(qp);full=q['passed']and not legacy;scoped=q['passed'];v=next((OUT/'videos').glob('native-'+n+'-*/manifest.json'));m=core.read(v);assert m['nativeOutcomePassed'];vid=dict(movie=physics.artifact(v.parent/m['clips'][0]['file']),manifest=physics.artifact(v),receipt=m['nativeReceipt'],strict=m['strict'],reviewOnly=m['reviewOnly'],nativeOutcomePassed=True)
  select=core.read(f/'selection.json');screen=core.read(core.resolve_artifact(select['screen']['path']));formal=core.REPO/f'pcg/results/approved-r058-{n}-qualified-final-v1/migration-physics.json'
  r=dict(schema='pcg/approved-design-implementation-result/v1',name=n,reviewId=row['reviewId'],moduleId=row['moduleId'],designVersion=row['designVersion'],designSource=physics.artifact(core.REPO/row['designFile']),baseDesignSource=row['baseDesignSource'],status='FULL_V2_VALIDATED_CANDIDATE'if full else'LEGACY_V1_SUPPLEMENTED_CANDIDATE'if legacy and scoped else'UNQUALIFIED_PLAYABLE_CANDIDATE',qualified=bool(full),validationPassedWithinDeclaredScope=bool(scoped),qualification=physics.artifact(qp),validationScope='FULL_v2'if full else'legacy_v1_seeds_plus_full_seam_and_counter_coverage'if legacy else'fixed_native_samples_only',formal=formal_summary(formal,n!='s11'),screen=screen['counts'],screenEvidence=select['screen'],parameters=physics.artifact(f/'parameters.json'),sourceModule=physics.artifact(f/'module.mapnote.json'),implementationProvenance=physics.artifact(f/'implementation-provenance.json'),nativePlayable=dict(scene=physics.artifact(f/'playable/demo.tscn'),manifest=physics.artifact(f/'playable/godot-package.json'),result=physics.artifact(f/'package-result.json'),actualNativeCases=len(core.read(f/'playback-cases.json')['cases'])),videos=[vid],originalPhysicsChanged=False,designWebChanged=False,userAuthorizedGeometryChange=n=='42',humanPlaytest='UNKNOWN',humanVideoObservation='UNKNOWN',productionApproval=False,designImpossible=False,certificationUnknown=['mirror','partial-port closure combinations','same-Port external self-loops','arbitrary entry states','full Map'])
  if legacy:r['protocolLimitation']=dict(reason='Initial formal helper selected historical default v1 rather than preregistered FULL_v2. Its independent seeds remain unchanged; no second holdout was drawn. Missing continuous-entry and counter checks were added within the original32-fixture budget.',fullV2Qualification='UNKNOWN',cause='workflow/default-protocol selection error, not a demonstrated Module defect',next='Future prospectively registered FULL_v2 round; helper now explicitly pins FULL_v2 and asserts its schema before creating Engine.')
  if n=='42':r['geometryChange']=dict(oldRightShore=[336,0,176,24],newRightShore=[304,0,208,24],oldGap=80,newGap=48,hookAndTopRewardAndPortsUnchanged=True,allSixDirectionsPassed=True)
  if n=='s02':r['uncompleted']=dict(reason='B-to-T full calibration clean9/12,mild8/12,moderate10/12; its independent holdout NOT_RUN. T-to-B passed.',cause='Read-only carrier/saw forecast can wait beyond its finite2400-frame window at some initial phases. Finite failed control is not proof of impossible geometry.',next='Improve the finite safe boarding and disembark controller in a later prospective round; preserve the approved P/G motion unless a precise conflict is reviewed.',internalBottomDock=[350,590],logicalBottomPort=[320,640],dockReason='Original ModuleDefinition rejects the canonical320 standing anchor inside the full solid-ferry envelope; a30px internal staging offset uses the same approved support and Port.',bottomIngressCorrection=physics.artifact(OUT/'verification/s02-bottom-fixture-v2.json'))
  if n=='s07':r['parametersCompleted']=dict(initialGate='closed',openSeconds=.12,originalAntiCrush=True,returnReceiverAnySide=True,actualAscent='walk off approved hood roof, fire back through its right opening, land on reclosed gate, then ordinary jump to TOP',humanTimingDifficulty='UNKNOWN',observationCorrection='Explicit neighboring one-way deck caught the successful ascent before an internal14px dock wait. Only terminal observation reanalysed from original raw; full-body/aperture/health/outcomes unchanged.')
  if n=='s11':r['uncompleted']=dict(reason='Bottom receiver wrong right-side-only predicate corrected after original formal. Corrected candidate passes six-direction13-trial screens, six native replays and all three real receiver shots, but does not inherit old formal admission.',cause='implementation binding defect, now fixed with original ShotLatch.add_access_bell(...,false,false); geometry unchanged',next='Future independently registered formal round for corrected runtime; one formal version per specification budget retained.',receiverVerification=physics.artifact(OUT/'verification/s11-three-receivers.json'))
  if n=='s12':r['uncompleted']=dict(reason='All12 fixed native demonstrations pass after real enemy death, but final phase/noise screen is not all-route passing; formal and holdout NOT_RUN.',cause='P/Q solid bodies can cancel a jump from below or displace its rider. Some TOP transfer/control branches also time out. No change to approved motion/collision and no proof of global impossibility.',next='First use actual support/ceiling contact and swept carrier forecast to avoid blocked takeoffs. If that remains insufficient, review relative phase/path clearance or a one-way platform change before altering design.',deadEnemyDemonstrations=physics.artifact(OUT/'verification/s12-dead-enemy-samples.json'),boundedStop=physics.artifact(AUTH/'s12-final-control-stop.json'))
  core.write(OUT/(n+'.json'),r);results.append(dict(name=n,reviewId=row['reviewId'],qualified=full,validationPassedWithinDeclaredScope=scoped,result=physics.artifact(OUT/(n+'.json'))));title='完整v2通过'if full else'v1及补测通过；v2未认证'if legacy else'可玩；未完整认证';table.append(f"| {n} | {title} | {r['nativePlayable']['actualNativeCases']} | [场景、影片、参数与证据]({n}.json) |")
 core.write(OUT/'index.json',dict(schema='pcg/approved-design-implementation-index/v1',main=core.read(AUTH/'request.json')['main'],scope=13,playable=13,nativeDirections=44,qualified=sum(r['qualified']for r in results),legacyV1WithFullCoverageSupplement=6,unqualifiedCurrentCandidates=3,results=results,productionAdmitted=False,scopeExpansion=False))
 (OUT/'README.md').write_text('''# 42 与十二份新审批规格：可玩样品和证据

基于授权记录中最新main，在独立分支/worktree实现。13项均有真实编译Module场景、参数、44个固定初态原生通行样品，以及直接录制编译场景的13段60FPS影片。原游戏870份文件和设计网页不变。

| 规格 | 验证范围 | 原生方向数 | 入口 |
| --- | --- | --- | --- |
'''+ '\n'.join(table)+'''

## 42 的授权调整

右岸由x336/宽176改为x304/宽208，缺口80→48px。钩点、上层奖励、三个Port不动；六个方向完整v2通过。其它十二份规格保持审批几何与运动轨迹。

S02底口仍是(320,640)，内部Dock设为(350,590)，避开原生定义禁止的载台全行程锚点重叠；不是移动Port。补充接缝样品先竖直跳到完整身体进入边界，再向内部Dock移动。S07未知开门时间补为0.12秒，保留原防夹和可重开；实测利用原铃罩顶和重新闭合的门落脚上返。S11初始B门开/A门关，三个访问铃属于同一原生互补组，底铃用any-side访问，右铃保留右侧访问限制。S12保留P/Q两实体载台及原3HP空怪，固定样品均由真实弹丸清怪后在同一世界继续通行，不复活或补弹。

## 未完整认证和原因

- **六个双平台连接件**：旧默认协议选择是本轮流程错误。原v1独立留出通过，随后补齐连续进入、反例和顶口观察器核对；旧种子没有改、没有再次抽留出，不能据此声称按预登记FULL_v2种子完成认证。执行器现已显式固定v2并在创建Engine前断言。不是已证明的Module缺陷。
- **S02**：上行校准9/12、8/12、10/12，前两档未达原门槛，故该路没有抽取留出。部分初始相位在有限时间内等不到预测安全的乘台窗口；需要后续改进控制，尚不能归因为几何不可行。下行通过，底口完整身体接缝补测通过。
- **S11修正版**：补充射击发现底铃误用了仅右侧限制，已修复。修正版六向筛查、六向原生回放及三铃实射均通过；旧版正式报告绑定旧运行时，不转移给修正版。本轮不追加第二份正式版本。
- **S12**：固定初态12向和敌死后样品全部通过；不同相位下P/Q可能挡住起跳或使角色失去载台支撑，最终筛查未全过，未启动正式/留出。先改实际支撑、头顶接触和换台反馈；如需改相位、轨迹净空或可穿属性，反馈后再改设计。本轮没有自行调整这些方案。

S07原正式报告四条顶口接缝被内部落地等待误报：真实相邻台已经接住角色。原raw和False报告保留，只读重算实际连续站稳、完整身体过口、64px净空、无伤和目标结果，并有52项正反例回归。

## 试玩与录像

从仓库根运行对应JSON的nativePlayable.scene：

```bash
pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 --path pcg/prototype/godot "$PWD/<nativePlayable.scene.path>" -- --case 0
# 添加 --replay 重放；省略则手动操作。--case N 选择其它方向。
```

按[WORKSPACE](../../../../pcg/WORKSPACE.md)恢复原游戏资源并使用精确官方Godot4.7.2。每项JSON链接当前原生场景、载入回执、参数、成功到达终点的原生影片及严格比较结果。13段当前影片直接使用编译场景，原生回执确认HP5/无重置/目标站稳；镜头和结尾1秒冻结不改运动。早期工坊录像、失败回放和比较差异原样保留，不作为成功影片或技术认证。影片不能替代人工试玩；镜像、部分Port封口、自环、任意进入状态和整Map仍UNKNOWN。

## 原始成功/失败证据

全部90,422份引擎raw、日志和冻结来源在8段SHA校验归档中；不同阶段的拒绝、失败和旧S11样品也保留。原生包回执和影片回执直接提交。恢复：

```bash
python3 pcg/tools/restore_archive.py approved-revision058-implementation-v1 --verify-parts-only
python3 pcg/tools/restore_archive.py approved-revision058-implementation-v1 --extract
python3 -m pcg.manual_review.audit_revision058_v1
python3 -m pcg.manual_review.test_revision058_measurements_v1
```

[原话与预算](authorization/request.json) · [几何/870原件/原生包/预算核验](verification/geometry-source-budget.json) · [测量回归](verification/measurement-regressions.json) · [原始归档核验](verification/raw-archive.json)。npm run check通过，自动生成设计投影已还原。没有部署网页、合并main或授予生产认可。
''')
 print('REPORT_13_NATIVE_44_DIRECTIONS_FULL_V2',sum(r['qualified']for r in results))
if __name__=='__main__':main()
