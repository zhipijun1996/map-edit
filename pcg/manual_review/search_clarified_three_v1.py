"""Bounded native control domain; first passing screen wins; no holdout here."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import argparse,copy,itertools
from pcg.migration import core,physics,godot_package
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
from pcg.prototype.workshop.rules import cmd
from pcg.manual_review.prepare_review029_v1 import at,end
from pcg.manual_review.repair_review029_v2 import axis
from pcg.manual_review.repair_clarified_three_v1 import OUT,AUTH,WORK,rows

def programs(n,base):
 if n=='171':
  # Native cooldown is 15 ticks. Observe readiness rather than serial waits.
  for target,offset in [(476,0),(480,0),(488,0),(476,-3),(480,-3),(488,-3)]:
   plans=[]
   for c in base:
    right=c['route_spec']['from_port']=='entry';x=target if right else 1024-target;first='design-ambush-left'if right else'design-ambush-right';second='design-ambush-right'if right else'design-ambush-left'
    p=at(x,420)+[axis(0),cmd('wait',3)]
    for _ in range(3):
     for enemy in [first,second]:p+=[dict(op='shoot',aim_cell=dict(kind='enemy',id=enemy,body_offset=[0,offset]),trigger=dict(state='shot_ready',timeout=150))]
    p+=end(616 if right else 408,420);plans.append(p)
   yield dict(startX=target,enemyBodyOffsetY=offset),plans
 elif n=='175':
  for hold,release_x in [(8,1415),(10,1415),(8,1440),(10,1440),(6,1415),(12,1415)]:
   c=base[0];p=copy.deepcopy(c['control_plan']);i=next(i for i,v in enumerate(p)if v.get('trigger',{}).get('dynamic',{}).get('kind')=='platform_phase'and v['trigger']['dynamic']['window']==[.27,.29]);j=next(j for j in range(i,len(p))if p[j].get('carrier_value')==1430)
   p[i:j+1]=[axis(0),cmd('jump'),cmd('jump_release',hold),dict(op='wait',trigger=dict(dynamic=dict(kind='on_platform',id='key-carrier'),timeout=180)),axis(0),dict(op='wait',trigger=dict(state='carrier_x_gte',timeout=900),carrier_id='key-carrier',carrier_value=release_x)]
   yield dict(boardJumpHold=hold,finalDepartureX=release_x),[p]
 else:yield dict(surfaceOnly=True),[c['control_plan']for c in base]

def run(row):
 n=row['reviewId'];folder=core.REPO/row['outputDirectory'];base=core.read(folder/'cases.json')['cases'];domain=list(programs(n,base));assert len(domain)<=(1 if n=='174'else 6)
 plan_path=OUT/'development'/(n+'-domain.json');assert not plan_path.exists();core.write(plan_path,dict(candidates=[dict(parameters=p,programs=cs)for p,cs in domain],maximumAttempts=len(domain)*13*len(base),selection='first passing 1 clean +6 mild +6 moderate screen; moderate>=5, mild6/6; no holdout'))
 for k,(params,plans)in enumerate(domain):
  candidate=folder/('search/candidate-'+str(k));cs=copy.deepcopy(base)
  for i,c in enumerate(cs):c.update(id='clarified-'+n+'-candidate-'+str(k)+'-'+str(i),control_plan=plans[i])
  doc=godot_package.bind_case_behavior(core.read(folder/'module.mapnote.json'),cs);core.write(candidate/'module.mapnote.json',doc);core.contract(candidate/'module.mapnote.json',refresh=True);core.write(candidate/'cases.json',dict(cases=cs));eng,actual,authors=physics._engine(candidate,'approved-c3-'+n+'-screen-'+str(k),physics.FULL_PROTOCOL)
  inputs=[];labels={};counts=[dict(clean=0,mild=0,moderate=0)for c in cs];checks=[]
  for i,c in enumerate(actual):
   for level,total in [('clean',1),('mild',6),('moderate',6)]:
    for j in range(total):
     v=instantiate(physics.fresh(c,'bounded-screen'),271029031,level,j);inputs.append(v);labels[v['id']]=(i,level)
  for c,r,e in eng.run(inputs,'bounded-screen'):
   i,level=labels[c['id']];q=checked_purpose(authors[i],c,r);counts[i][level]+=q['ok'];checks.append(dict(route=cs[i]['route_spec']['id'],level=level,check=q,evidence=e))
  passed=all(v['clean']==1 and v['mild']==6 and v['moderate']>=5 for v in counts);core.write(eng.out/'screen.json',dict(passed=passed,counts=counts,parameters=params,rows=checks,sourceCases=physics.artifact(candidate/'cases.json')));print(n,k,passed,counts,flush=True)
  if passed:
   core.write(folder/'history/before-selection-cases.json',dict(cases=base));core.write(folder/'cases.json',dict(cases=cs));core.write(folder/'module.mapnote.json',doc);core.contract(folder/'module.mapnote.json',refresh=True);core.write(folder/'selection.json',dict(candidate=k,parameters=params,screen=physics.artifact(eng.out/'screen.json'),unchangedThresholds=True));return
 core.write(folder/'selection.json',dict(passed=False,reason='bounded domain exhausted',candidates=len(domain)))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('ids',nargs='+');a=p.parse_args()
 for r in rows():
  if r['reviewId']in a.ids:run(r)
