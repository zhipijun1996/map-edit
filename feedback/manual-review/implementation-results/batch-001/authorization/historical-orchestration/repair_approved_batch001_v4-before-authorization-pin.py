"""Last bounded parameter hypotheses; no approved design or threshold changes."""
import copy
from pcg.migration import core,physics
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
from pcg.prototype.workshop.evaluate import instantiate
for row in core.read(core.REPO/'feedback/manual-review/implementation-handoff-v1.json')['rows']:
 if row['reviewId']not in ['02','03']:continue
 folder=core.REPO/row['outputDirectory'];base=core.read(folder/'physics-input-cases.json')['cases'][0];probes=[]
 if row['reviewId']=='02':
  for launch in [944,960,976]:
   c=copy.deepcopy(base);c['id']+=f'-third-launch{launch}'
   for command in c['control_plan']:
    if command.get('target_x')==928:command['target_x']=launch
    d=command.get('trigger',{}).get('dynamic',{})
    if d.get('kind')=='actor_x' and d.get('value')==922:d['value']=launch-6
   probes.append(c)
 else:
  for launch in [136,144]:
   for dy in [.85,.92]:
    for after in [14,18,22]:
     c=copy.deepcopy(base);c['id']+=f'-late-vertical{launch}-dy{dy}-a{after}'
     p=copy.deepcopy(c['control_plan'][:7]);p[5]['target_x']=128
     p += [ground(),cmd('wait',12),settle(488),wait_x(launch),cmd('jump'),cmd('jump_release',8),cmd('shoot',after,direction=[-(1-dy*dy)**.5,dy]),ground(),cmd('wait',20)]
     c['control_plan']=p;probes.append(c)
 eng,_,authors=physics._engine(folder,'approved-b001-'+row['reviewId']+'-repair4',physics.FULL_PROTOCOL);checks=[]
 core.write(eng.out/'protocol.json',dict(maximumControlAttempts=80,canonicalProbes=len(probes),geometryChanges=0,holdout='NOT_RUN',
  selection='02: greatest min(mild,moderate) 6-trial screen rate, then fewest canonical ticks, then declared order; 03: first strict passing new program only. Not formal quality or independent holdout.',source=physics.artifact(__file__)))
 for c,r,e in eng.run([physics.fresh(c,'repair4')for c in probes],'control-repair'):
  chk=checked_purpose(authors[0],c,r);checks.append(dict(case=c,check=chk,evidence=e,ticks=r['ticks']));print(row['reviewId'],c['id'],chk['ok'],chk['reasons'],flush=True)
 core.write(eng.out/'repair-check.json',dict(rows=checks))
 if row['reviewId']=='02':
  screened=[]
  for i,v in enumerate(checks):
   if not v['check']['ok']:continue
   c=v['case'];samples=[instantiate(c,2810282041+i*1009,level,j)for level in ['mild','moderate']for j in range(6)];out=[]
   for value,raw,e in eng.run(samples,'screen-noise'):
    chk=checked_purpose(authors[0],value,raw);out.append(dict(id=value['id'],check=chk,evidence=e))
   rates={level:sum(v['check']['ok']for v in out if '-'+level+'-'in v['id'])/6 for level in ['mild','moderate']}
   screened.append(dict(case=c,canonical=v,rates=rates,observations=out));print('02 screen',i,rates,flush=True)
  core.write(eng.out/'screens.json',dict(rows=screened))
