"""Fixed control probes: clear the guard with real jumping, retain every failure."""
import copy
from pcg.migration import core,physics
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
for row in core.read('feedback/manual-review/implementation-handoff-v1.json')['rows']:
 if row['reviewId']not in ['03','05']:continue
 folder=core.REPO/row['outputDirectory'];base=core.read(folder/'cases.json')['cases'][0];probes=[]
 if row['reviewId']=='03':
  for launch in [136,140,144]:
   for dy in [.5,.52,.54]:
    c=copy.deepcopy(base);c['id']+=f'-edge{launch}-dy{dy}';p=copy.deepcopy(c['control_plan'][:7]);p[5]['target_x']=128
    p += [ground(),cmd('wait',12),settle(488),wait_x(launch),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[-(1-dy*dy)**.5,dy]),ground(),cmd('wait',20)]
    c['control_plan']=p;probes.append(c)
 else:
  for launch in [680,700,720]:
   for hold in [12,20]:
    c=copy.deepcopy(base);c['id']+=f'-guard-hop{launch}-h{hold}';p=copy.deepcopy(c['control_plan'][:10]);p += [wait_x(launch),cmd('jump'),cmd('jump_release',hold),ground(),cmd('wait',20)];c['control_plan']=p;probes.append(c)
 eng,_,authors=physics._engine(folder,'approved-b001-'+row['reviewId']+'-repair3',physics.FULL_PROTOCOL);checks=[]
 core.write(eng.out/'protocol.json',dict(maximumControlAttempts=80,probes=len(probes),selection='first strict passing case in declared order',geometryChanges=0,holdout='NOT_RUN',source=physics.artifact(__file__)))
 for c,r,e in eng.run([physics.fresh(c,'repair3')for c in probes],'control-repair'):
  chk=checked_purpose(authors[0],c,r);checks.append(dict(case=c,check=chk,evidence=e));print(row['reviewId'],c['id'],chk['ok'],chk['reasons'],flush=True)
 core.write(eng.out/'repair-check.json',dict(rows=checks))
