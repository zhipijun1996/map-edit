"""Second bounded calibration probes, unchanged approved Cell geometry."""
import copy
from pcg.migration import core,physics
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
for row in core.read('feedback/manual-review/implementation-results/batch-001/authorization/handoff-v1.json')['rows']:
 if row['reviewId']not in ['03','05']:continue
 folder=core.REPO/row['outputDirectory'];cs=core.read(folder/'cases.json')['cases'];base=cs[0];probes=[]
 if row['reviewId']=='03':
  for hold in [8,12,20]:
   for dy in [.4,.55]:
    for after in [0,10]:
     c=copy.deepcopy(base);c['id']+=f'-tiny-h{hold}-dy{dy}-a{after}'
     p=copy.deepcopy(c['control_plan'][:7]);p[5]['target_x']=128
     p += [ground(),cmd('wait',12),settle(488),cmd('jump'),cmd('jump_release',hold),cmd('shoot',after,direction=[-(1-dy*dy)**.5,dy]),ground(),cmd('wait',20)]
     c['control_plan']=p;probes.append(c)
 else:
  for stop in [720,736,744]:
   c=copy.deepcopy(base);c['id']+=f'-combat-stop{stop}';p=copy.deepcopy(c['control_plan'][:10]);p[8]['target_x']=stop;p+=[wait_x(stop-6),ground(),cmd('wait',4)]
   for n in range(3):
    p += [cmd('shoot',aim_cell=dict(kind='enemy',id='human-f02-high-sentry'),direction=[1,0]),cmd('wait',22),wait_x(stop-6),ground(),cmd('wait',8)]
   p += [settle(1000),wait_x(994),ground(),cmd('wait',20)];c['control_plan']=p;probes.append(c)
 eng,_,authors=physics._engine(folder,'approved-b001-'+row['reviewId']+'-repair2',physics.FULL_PROTOCOL);checks=[]
 core.write(eng.out/'protocol.json',dict(maximumControlAttempts=80,probes=len(probes),selection='first strict passing case in declared order',geometryChanges=0,holdout='NOT_RUN',source=physics.artifact(__file__)))
 for c,r,e in eng.run([physics.fresh(c,'repair2')for c in probes],'control-repair'):
  chk=checked_purpose(authors[0],c,r);checks.append(dict(case=c,check=chk,evidence=e));print(row['reviewId'],c['id'],chk['ok'],chk['reasons'],flush=True)
 core.write(eng.out/'repair-check.json',dict(rows=checks))
