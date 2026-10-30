if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core,physics
from .continue_revision062_v1 import rows,label,OUT,AUTH
from .finalize_revision062_v1 import folder_for
from .report_revision060_061_v1 import formal
GAPS={'hq07':dict(classification='验证流程／留出曝光登记缺口',reason='完整技术门槛复测通过，172例及12个同输入反例续测均有证据；但上一轮中断前R→L留出已曝光，旧守卫漏记，当前默认池不能宣称全新独立留出。',next='已补中断批次曝光登记并用真实旧raw验证守卫会阻止重复池。当前同程序换池被拒绝；保留可玩包与技术复测通过，暂不授予新独立资格，不为过认证改名、换seed或依据留出调参。'), 's04':dict(classification='输入策略与操作余量',reason='双向固定/原生包通过；最后筛选B→T轻扰动5/6、中等3/6，T→B中等3/6。漏铃、空怪伤害与越界仍存在；真实重试改善但未达门槛。',next='继续根据实际P/Q支撑、收铃后的真实停台位置与全身净空控制换乘，先稳定下段空怪处理。若仍需移铃/扩接岸，另提设计修订，不直接改方案。'), 's06':dict(classification='输入策略与操作余量',reason='真实刚性挂铃与离台射击/反冲接回双向通过；轻扰动6/6，中等B→T为0/6、T→B为2/6。射击角度与初始相位扰动导致漏铃或追台失败。',next='按实际载台相对位置安排离台、瞄准与重追；充分利用重试台。延长停留、改变速度或加平台属于设计修订，当前未实施。'), 's09':dict(classification='输入策略与狭窄时序',reason='固定双向与原生包通过；轻扰动双向均2/6，中等L→B为5/6、B→L为0/6。锯窗射击角度与空怪衔接对时序敏感。',next='稳定窗口实际高度/锯相位触发和反冲角度，保留死怪后的返回能力。若需增加净空或改变锯轨道，先走设计修订。清怪后B→L已实测成功，不能归咎于必须依赖活怪。')}

def main():
 results=[];table=[];downloads=core.read(OUT/'downloads/index.json')['rows'];qualified=0
 for row in rows():
  n=label(row);f=folder_for(row);q=core.read(f/'qualification.json');p=f/'playable';sel=core.read(f/'selection.json');movie=next((OUT/'videos').glob('native-'+n+'-*/native.mp4'));manifest=movie.parent/'manifest.json';m=core.read(manifest);d=next(x for x in downloads if x['name']==n);count=len(core.read(p/'cases.json')['cases']);qualified+=q['passed'];screen=q.get('screen')or sel.get('screen');r=dict(schema='pcg/approved-design-implementation-result/v1',round='062',name=n,reviewId=row['reviewId'],moduleId=row['moduleId'],designVersion=row['designVersion'],designSource=physics.artifact(core.REPO/row['designFile']),status='FULL_V2_VALIDATED_CANDIDATE'if q['passed']else'TECHNICAL_GATES_PASSED_KNOWN_HOLDOUT_REPLAY'if n=='hq07'else'FIXED_NATIVE_PLAYABLE_SCREEN_UNQUALIFIED',qualified=q['passed'],qualification=physics.artifact(f/'qualification.json'),formalAttempts=q.get('actualAttempts',0),formalDirections=formal(q)if q['passed']or q.get('report')else[],sourceModule=physics.artifact(f/'module.mapnote.json'),parameters=physics.artifact(f/'parameters.json'),implementationProvenance=physics.artifact(f/'implementation-provenance.json'),selection=physics.artifact(f/'selection.json'),nativePlayable=dict(scene=physics.artifact(p/'demo.tscn'),manifest=physics.artifact(p/'godot-package.json'),result=physics.artifact(f/'package-result.json'),actualNativeCases=count,zip=d['file']),videos=[dict(movie=physics.artifact(movie),manifest=physics.artifact(manifest),receipt=m['nativeReceipt'],strict=m['strict'],reviewOnly=m['reviewOnly'])],originalGamePhysicsSourceChanged=False,designWebChanged=False,humanPlaytest='UNKNOWN',productionApproval=False,unknown=['mirror','closure combinations','arbitrary entry states','full Map'])
  if isinstance(screen,dict):r['screenEvidence']=screen;r['screen']=core.read(core.resolve_artifact(screen['path']))['counts']
  if n in GAPS:r['uncompleted']={**GAPS[n],'designImpossibleProven':False,'geometryChanged':False}
  elif not q['passed']:r['uncompleted']=dict(classification='完整验证未达标',reason='固定和筛选通过，正式校准/留出/边界/反例中仍有失败，逐方向保留于formalDirections。',designImpossibleProven=False)
  if n=='hq07':r['counterDriverContinuation']=core.read(core.resolve_artifact(q['report']['path'])).get('counterDriverContinuation');r['originalInvalidCounterAttemptsRetained']=12
  core.write(OUT/(n+'.json'),r);results.append(dict(name=n,reviewId=row['reviewId'],qualified=q['passed'],result=physics.artifact(OUT/(n+'.json'))));table.append(f"| {n} | {'完整v2通过'if q['passed']else'技术复测通过，独立资格未完成'if n=='hq07'else'双向可玩，扰动未达标'} | {count} | {r['formalAttempts']} | [证据]({n}.json) · [试玩ZIP](downloads/{d['file']['path'].rsplit('/',1)[1]}) · [短片]({core.relative(movie).split(core.relative(OUT)+'/')[1]}) |")
 audit=core.read(OUT/'verification/geometry-source-budget.json');core.write(OUT/'index.json',dict(schema='pcg/approved-design-implementation-index/v1',round='062',main=core.read(AUTH/'request.json')['main'],scope=len(results),repairs=5,newApproved=3,playable=len(results),nativeDirections=audit['nativeDirections'],qualified=qualified,results=results,productionAdmitted=False))
 text='''# 最新审批模块实现与旧失败修复（revision062）

基于main `f3aff10f229dfd461aee72650c8c40bd77affc0e`，新实现第二轮S04/S06/S09，修复HQ01/HQ03/HQ07及第二轮S10/S12。第二轮规格与旧同号模块分开记录。

'''+f'本轮8项、34个原生固定方向、8段实际影片，完整v2通过{qualified}项。原游戏870份保护文件和设计网页未改。\n\n'+'''| 规格 | 状态 | 原生方向 | 正式案例数 | 下载与证据 |
| --- | --- | --- | --- | --- |
'''+ '\n'.join(table)+'''

## 新实现与未完成项

S04采用两组原生风铃分别控制P/Q；真实事件仅影响各自载台并保留独立时钟。S06实现原生ShotLatch刚性挂在P下方64px，实际离台射击启动、反冲接回，原始28个案例逐帧偏移正确。S09保留原锯、岩面刺和原空怪；L→B真实空中命中原怪，B→L先清怪仍能返回，无自动刷怪或资源注入。

三个新模块固定双向和原生包均通过，但扰动筛选未达标，未开启独立留出，不标完整合格。具体比例、原因与后续控制建议见各JSON。有限控制失败不能证明模块无解；移动风铃、扩净空、改速度/轨道均没有擅自实施。

## 旧失败如何处理

先用上轮失败的实际校准输入、相位与噪声原样重放，8个失败均复现，再修输入策略。HQ01修Q→P落点、左岸地面反冲及顶口起跳；HQ03修右侧安全战斗站位；HQ07把实际高度并入射击触发；第二轮S10修起跳与反冲边界余量；第二轮S12修右侧登Q和从Q左侧上行。需要替换已知池的正式运行使用真实修订程序与预登记池；HQ07默认池曝光漏记单列，不宣称独立通过。全部旧失败保留，不调已观察的留出。

HQ07当前只标技术复测通过，独立资格仍未完成：发现旧守卫仅扫描完整报告，漏记上一轮中断前已完成的R→L留出。当前同一程序换独立池被守卫拒绝，未分配seed；没有强行重跑。对应规则见[物理skill](../../../../.agents/skills/pcg-physics-contract/SKILL.md)：“改名、换Route标签或只换seed不产生新独立留出”。已补充按完整批次登记曝光，并用真实旧raw做隔离回归检查。

HQ07正式反例遇到缺省direction驱动错误：已完成批次逐字节复用，仅12个完全相同的反例输入用新的观察驱动续测。原错误、实际命令、驱动源码、批次SHA和额外原始重算均独立绑定；没有新校准或留出。反例是删除指定计划动作的固定策略搜索，不能当作穷尽所有玩家操作的无解证明；实际请求均保留在raw中。

HQ09新鲜T入口首输入前受刺的冲突仍待用户确定设计修订；没有擅自改变初态权限或尖刺，上一轮单向样品及冲突证据保留在[revision060](../revision-060-v1/README.md)。

## 试玩与证据

ZIP在仓库根目录解压，按[WORKSPACE](../../../../pcg/WORKSPACE.md)恢复原项目资源；官方Godot4.7.2运行JSON的nativePlayable.scene，省略--replay为手动，加--replay回放实际输入，--case N切换方向。ZIP引用原资源和官方引擎，不重复包含。影片60FPS、1倍速、结尾冻结1秒；strict=false为REVIEW_ONLY，严格差异完整保留。

[授权和预算](authorization/request.json) · [旧失败分类](authorization/failure-triage.json) · [相同输入重跑](verification/prior-failure-replay.json) · [几何/源码/预算核验](verification/geometry-source-budget.json) · [完整报告原始重算](verification/full-report-rederivation.json) · [原始归档核验](verification/raw-archive.json) · [AI实际抽帧观察](verification/ai-video-observation.json)

```bash
python3 pcg/tools/restore_archive.py approved-revision062-implementation-v1 --verify-parts-only
python3 pcg/tools/restore_archive.py approved-revision062-implementation-v1 --extract
python3 -m pcg.manual_review.audit_revision062_v1
```

完整通过仅限精确版本及已测配置的技术候选资格，人工试玩、生产批准、镜像、封口组合、任意进入态和完整Map仍UNKNOWN。S12最后六个顶口检查仅因旧观察器0.05px高度容差失败。官方原PlayerMotor实测safe_margin=0.08；实际支撑ID、全身位于指定相邻平台、连续静止均成立，脚底偏差0.0678px在原边距内。按真实支撑只读复核后通过，原失败与六类否决测试保留，未放宽越界/健康/奖励/世界状态门槛。复核报告留在原预登记执行目录；缺失路径只读链接到同输入续跑的归档原件，另有逐项SHA清单，没有修改池预留或新增物理运行。

S12环境恢复时已完成29个封装批次及1个未封装完整批次：后者由原输出、完成标记和真实内核子进程退出码0恢复执行回执，计时UNKNOWN，未伪造计时或重跑该批。其余同输入继续，候选/协议/池/种子均未改变。

没有修改设计网页、部署或合并main。
'''
 (OUT/'README.md').write_text(text);print('062 REPORT',qualified,'of8',flush=True)
if __name__=='__main__':main()
