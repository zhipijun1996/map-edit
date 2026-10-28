import copy
from pcg.migration import core,physics
from pcg.manual_review.implement_approved_batch001 import case_for,mirror_plan,source_folder
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
q=core.read('feedback/manual-review/implementation-results/batch-001/authorization/handoff-v1.json')
for row in q['rows']:
 if row['reviewId'] not in ['01','03','05']:continue
 folder=core.REPO/row['outputDirectory'];cs=core.read(folder/'cases.json')['cases'];selected=[]
 if row['reviewId']=='01':
  originals=core.read(source_folder(row)/'cases.json')['cases'];targets=core.read(core.REPO/row['designFile'])['intendedRoutes']
  for c in cs:
   if c['route_spec']['from_port']not in ['B','C']:continue
   target=next(r for r in targets if r['id']==c['route_spec']['id']);c['control_plan']=case_for(originals,target)['control_plan'];selected.append(c)
 elif row['reviewId']=='03':
  c=cs[0];p=copy.deepcopy(c['control_plan'][:7]);p[5]['target_x']=128
  p += [ground(),cmd('wait',12)]
  p += [cmd('shoot',0 if n==0 else 22,aim_cell=dict(kind='enemy',id='review-gap-diver'),direction=[-1,0])for n in range(3)]
  p += [cmd('wait',12)]
  p += [cmd('shoot',0 if n==0 else 22,aim_cell=dict(kind='enemy',id='review-cache-sentry'),direction=[1,-.5])for n in range(3)]
  p += [cmd('wait',12),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[-.55,.8351646544245033]),settle(488),ground(),cmd('wait',20)]
  c['control_plan']=p;selected=[c]
 else:
  c=cs[0];p=copy.deepcopy(c['control_plan']);p[8]['target_x']=700;p=p[:10]
  p += [cmd('wait',4)]
  p += [cmd('shoot',0 if n==0 else 22,aim_cell=dict(kind='enemy',id='human-f02-high-sentry'),direction=[1,0])for n in range(3)]
  p += [cmd('wait',12),settle(1000),wait_x(994),ground(),cmd('wait',20)];c['control_plan']=p;selected=[c]
 eng,_,authors=physics._engine(folder,'approved-b001-'+row['reviewId']+'-repair1',physics.FULL_PROTOCOL);author=authors[0];checks=[]
 core.write(eng.out/'protocol.json',dict(purpose='calibration-only control repair',geometryChanges=0,maximumControlAttempts=80,selection='first safe strict passing program; no holdout exposure'))
 for c,r,e in eng.run([physics.fresh(c,'repair1')for c in selected],'control-repair'):
  chk=checked_purpose(author,c,r);checks.append(dict(case=c,check=chk,evidence=e));print(row['reviewId'],c['route_spec']['id'],chk['ok'],chk['reasons'],flush=True)
 core.write(eng.out/'repair-check.json',dict(rows=checks))
