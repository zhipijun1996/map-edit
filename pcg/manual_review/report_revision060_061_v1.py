import importlib
from pcg.migration import core,physics
GAPS={
 '060':{'hq01':('控制策略','T→L完整门槛未过；5个方向通过，近距离Q→P落点与左岸接回仍不稳。','先修换乘真实支撑与左岸地面反冲；不改平台轨道。'), 'hq03':('控制策略','右侧进入的两方向校准不达标；其余四向、边界与反例通过。','隔离右侧站位，避开接触后再清怪；保留原怪与岩面刺。'),'hq07':('控制／验证驱动','L→R中等扰动未达标；R→L通过。反例等待缺方向已单独修复并补测12例，原失败保留。','将实际高度条件并入射击触发，避免等待后再次延迟；不改桥和防夹。'),'hq09':('模块初始接口冲突','新鲜T入口在首个输入前被顶刺扣血；只交付L→T与收刺因果。','T初态权限或刺台需明确修订；已询问初始只出不进的方案。')},
 '061':{'s10':('控制策略','B→R校准轻扰动10/12，存在反冲越出矩形；R→B通过。','取消起跳前持续移动，留足左右反冲边界余量。'),'s12':('控制策略','12向固定样品与筛选通过，完整验证仍有上口/换乘方向未达标。','从Q左侧准备顶口起跳；按实际高度回射登Q，保留独立时钟。')}}
def formal(q):
 if q.get('routes'):routes=q['routes']
 elif q.get('report'):
  d=core.read(core.resolve_artifact(q['report']['path']));routes=d.get('routes',[])if isinstance(d,dict)else[]
 else:routes=[]
 out=[]
 for r in routes:
  a=dict(route=r['routeId'],passed=r['passed'])
  for k in ['calibration','holdout']:
   ref=r.get(k)
   if isinstance(ref,dict):
    d=core.read(core.resolve_artifact(ref['path']));a[k]=dict(evidence=ref,rates={k:v['rate']for k,v in d['stats'].items()},gate=d['quality_gate']['status'])
   else:a[k]=ref
  out.append(a)
 return out

def main():
 for version in ['060','061']:
  scope=importlib.import_module('pcg.manual_review.continue_revision'+version+'_v1');final=importlib.import_module('pcg.manual_review.finalize_revision'+version+'_v1');results=[];table=[];downloads=core.read(scope.OUT/'downloads/index.json')['rows']
  for row in scope.rows():
   n=scope.label(row);f=final.folder_for(row);q=core.read(f/'qualification.json');p=f/('playable-presentation-v2'if version=='060'and n=='hq09'else'playable');selection=core.read(f/'selection.json')if(f/'selection.json').exists()else{};manifest=sorted((scope.OUT/'videos').glob('native-'+n+'-*/manifest.json'))[-1];m=core.read(manifest);d=next(d for d in downloads if d['name']==n);status='FULL_V2_VALIDATED_CANDIDATE'if q['passed']else'PARTIAL_PLAYABLE_DESIGN_CONFLICT'if n=='hq09'else'UNQUALIFIED_PLAYABLE_CANDIDATE';movie=manifest.parent/'native.mp4';r=dict(schema='pcg/approved-design-implementation-result/v1',round=version,name=n,reviewId=row['reviewId'],moduleId=row['moduleId'],designVersion=row['designVersion'],designSource=physics.artifact(core.REPO/row['designFile']),status=status,qualified=q['passed'],qualification=physics.artifact(f/'qualification.json'),formalAttempts=q.get('actualAttempts',0),formalDirections=formal(q),selection=physics.artifact(f/'selection.json')if selection else'NOT_SELECTED_FRESH_TOP_CONFLICT',sourceModule=physics.artifact(f/'module.mapnote.json'),parameters=physics.artifact(f/'parameters.json'),implementationProvenance=physics.artifact(f/'implementation-provenance.json'),nativePlayable=dict(scene=physics.artifact(p/'demo.tscn'),manifest=physics.artifact(p/'godot-package.json'),result=physics.artifact(f/('package-result-presentation-v2.json'if p.name=='playable-presentation-v2'else'package-result.json')),actualNativeCases=len(core.read(p/'cases.json')['cases']),zip=d['file']),videos=[dict(movie=physics.artifact(movie),manifest=physics.artifact(manifest),receipt=m['nativeReceipt'],strict=m['strict'],reviewOnly=m['reviewOnly'])],originalGamePhysicsSourceChanged=False,designWebChanged=False,humanPlaytest='UNKNOWN',productionApproval=False,unknown=['mirror','closure combinations','arbitrary entry states','full Map'])
   if selection:r['screen']=core.read(core.resolve_artifact(selection['screen']['path']))['counts'];r['screenEvidence']=selection['screen']
   if n in GAPS[version]:
    kind,reason,nextstep=GAPS[version][n];r['uncompleted']=dict(classification=kind,reason=reason,next=nextstep,designImpossibleProven=False)
   core.write(scope.OUT/(n+'.json'),r);results.append(dict(name=n,reviewId=row['reviewId'],qualified=q['passed'],result=physics.artifact(scope.OUT/(n+'.json'))));table.append(f"| {n} | {'完整v2通过'if q['passed']else'初态冲突／仅单向样品'if n=='hq09'else'可玩，完整验证未过'} | {r['nativePlayable']['actualNativeCases']} | {r['formalAttempts']} | [证据]({n}.json) · [试玩ZIP](downloads/{n}-native.zip) · [短片]({core.relative(movie).split(core.relative(scope.OUT)+'/')[1]}) |")
  qualified=sum(r['qualified']for r in results);audit=core.read(scope.OUT/'verification/geometry-source-budget.json');core.write(scope.OUT/'index.json',dict(schema='pcg/approved-design-implementation-index/v1',round=version,main=core.read(scope.AUTH/'request.json')['main'],latestSync='f3aff10f229dfd461aee72650c8c40bd77affc0e',scope=len(results),playable=len(results),nativeDirections=audit['nativeDirections'],qualified=qualified,results=results,productionAdmitted=False))
  intro='授权修复HQ01/HQ02/S12，并实现新批HQ03/HQ07/HQ08/HQ09。HQ02中台宽64→112、旧S12原生载台改可穿已按授权实施；其余设计几何与轨道不改。'if version=='060'else'实现已批准的第二轮S02/S07/S08/S10/S11/S12/S13，均与旧同号规格分开。S04/S06/S09后来在main获准，按最新请求进入下一轮。'
  text=f'''# 审批实现与真实 Godot 证据（revision{version}）

{intro}

本轮7项均有可玩包，固定方向{audit['nativeDirections']}条，完整v2通过{qualified}项。原游戏870份保护文件未变；设计网页未修改。所有通过、失败、零帧拒绝、引擎中断和源码快照均保留。

| 规格 | 状态 | 原生方向 | 正式案例数 | 下载与证据 |
| --- | --- | --- | --- | --- |
'''+ '\n'.join(table)+'''

完整通过是当前精确版本及已测路线的技术候选资格，不是人工试玩或生产批准。固定样品成功不代表全部扰动通过；未过项按JSON逐方向说明，不归咎为已证明的几何无解。

## 试玩

下载ZIP后在本仓库根目录解压，按[WORKSPACE](../../../../pcg/WORKSPACE.md)恢复原项目资源。用官方Godot4.7.2打开JSON的nativePlayable.scene：

```bash
pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 --path pcg/prototype/godot "$PWD/<scene路径>" -- --case 0
```

省略`--replay`为手动操作，加上则回放真实记录输入；`--case N`切换已包含的方向。ZIP不重复打包官方引擎或原游戏资源。影片为实际编译场景、60FPS、1倍速，结尾全世界冻结1秒。strict=false的影片明确为REVIEW_ONLY，全部严格差异保留；不放宽比较器。

## 证据与限制

[授权与预算](authorization/request.json) · [几何/源码/预算核验](verification/geometry-source-budget.json) · [原始归档核验](verification/raw-archive.json) · [原始完整报告重算](verification/full-report-rederivation.json) · [AI抽帧观察](verification/ai-video-observation.json)

'''
  if version=='060':text+='HQ02已有真实敌弹先发射、再被P原生圆形扫掠消解的回执，余寿0.4667秒；没有改敌弹速度或寿命。HQ08只在原生实际落地支撑后启动，不以进入触发图框替代。HQ09用原PlayerProjectile的terrain_impacted与spent证明挡弹，真实玩家有10帧穿过挡板；L来向发出真实机关子弹、收回两侧刺，顶口平台保留。HQ09顶刺方向的第二版仅改_draw，原表现和影片保留。\n\nHQ01正式运行遇到原引擎signal11：完成批次逐字节复用，只续跑相同输入，未换候选/池/种子。完整结果仍False。HQ07反例驱动读取不存在direction的问题已独立补测12例，原校准失败不因此变True。\n'
  else:text+='S11新增精确顺时针椭圆运动定义，复用原ModuleMovingPlatform与角色物理，非直线或折线近似；真实承载、周期与9类非法定义拒绝均有证据。S13为同一L口的实际取奖自返回；额外外部L→取奖→外部L实测中，第13帧完整进入、第65帧真实取得4币、第152帧完整退出。通用单次出界观察器不接受先入后出的顺序，保留原False并按自返回合同只读复核，未重跑物理。\n'
  text+=f'''\n```bash
python3 pcg/tools/restore_archive.py approved-revision{version}-implementation-v1 --verify-parts-only
python3 pcg/tools/restore_archive.py approved-revision{version}-implementation-v1 --extract
python3 -m pcg.manual_review.audit_revision060_061_v1
```

镜像、封口组合、任意进入态与完整Map仍UNKNOWN。没有部署设计网页、合并main或授予生产批准。
'''
  (scope.OUT/'README.md').write_text(text);print(version,'REPORT',qualified,'of7',flush=True)
if __name__=='__main__':main()
