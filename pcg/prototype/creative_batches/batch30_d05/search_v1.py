"""Equal mild screen and explicit strong cheap policies on frozen first geometry."""
import argparse,copy,json,math
from pathlib import Path
from . import rules_v1 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.rules import cmd,settle,wait_x,ground
from pcg.prototype.workshop.evaluate import instantiate
HERE=Path(__file__).parent

def alternatives(c):
 out=[]
 def add(label,p):
  v=copy.deepcopy(c);v['id']+='-counter-'+label;v['counterexample_kind']=label;v['control_plan']=p;out.append(v)
 board=copy.deepcopy(c['control_plan'][:5]);depart=copy.deepcopy(c['control_plan'][:7]);final=copy.deepcopy(c['control_plan'][10:])
 for hold in [8,16,24]:
  for dy in [.2,.6,.8660254037844386]:add(f'parked-direct-{hold}-{dy}',depart+[cmd('jump'),cmd('jump_release',hold),cmd('shoot',6,direction=[-math.sqrt(1-dy*dy),dy]),settle(1320)])
  add('ordinary-jump-'+str(hold),depart+[cmd('jump'),cmd('jump_release',hold),settle(1320)])
 for delay in [30,90]:add('ground-start-passive-'+str(delay),board+[cmd('shoot',aim_cell=dict(kind='bell',id='catch-bell')),cmd('axis',value=0),cmd('wait',delay),settle(1320)])
 for x in [490,550,640,680]:add('ground-start-direct-'+str(x),board+[cmd('shoot',aim_cell=dict(kind='bell',id='catch-bell')),cmd('axis',value=1),wait_x(x),cmd('jump'),cmd('jump_release',24),cmd('shoot',6,direction=[-.8,.6]),settle(1320)])
 for mode in ['pause-air','recoil-only']:
  p=board+[cmd('shoot',aim_cell=dict(kind='bell',id='catch-bell'))]+copy.deepcopy(c['control_plan'][5:])
  if mode=='recoil-only':p[10]=cmd('shoot',direction=[-.8,.6])
  add('ground-start-catch-'+mode,p)
 p=copy.deepcopy(c['control_plan']);p[9]=cmd('wait');add('omit-start-shot',p)
 p=copy.deepcopy(c['control_plan']);p[17]=cmd('wait',6);add('omit-final-shot',p)
 add('continuous-air-no-catch',copy.deepcopy(c['control_plan'][:10])+[cmd('shoot',24,direction=[-.8,.6]),settle(1320)])
 add('floor-then-right-bank',[cmd('axis',value=1),wait_x(550),cmd('axis',value=0),ground(),cmd('wait',8),cmd('axis',value=1),wait_x(1150),cmd('jump'),cmd('jump_release',24),cmd('shoot',6,direction=[-.5,math.sqrt(.75)]),settle(1320)])
 for stop in [710,740,760]:
  for dy in [.7,.8660254037844386]:add(f'roof-rest-{stop}-{dy}',copy.deepcopy(c['control_plan'][:10])+[wait_x(stop),cmd('axis',value=0),ground(),cmd('wait',6),cmd('axis',value=1),cmd('jump'),cmd('jump_release',24),cmd('shoot',6,direction=[-math.sqrt(1-dy*dy),dy]),settle(1320)])
 return out

def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--counters',action='store_true');a=p.parse_args();e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(rules.__file__)]+rules.SOURCE_DEPENDENCIES,runner_script=rules.RUNNER_SCRIPT);rows=[]
 cs=alternatives(rules.candidate(0,0))if a.counters else[instantiate(rules.candidate(0,k),261027303,'mild',i)for k in range(4)for i in range(6)]
 for c,r,b in e.run(cs,'cheap-counter'if a.counters else'equal-mild-screen'):
  q=rules.purpose(c,r);same=bool(r.get('ok'))and r.get('workshop',{}).get('coins',0)>=12;fs=r.get('frames',[]);roof=any(f.get('grounded')and f.get('support_id')=='Platform2'for f in fs)
  row=dict(case=c,result=r,purpose=q,evidence=b,same_external_outcome=same,roof_ground=roof);rows.append(row)
  print(json.dumps(dict(id=c['id'],same_external_outcome=same,purpose=q,frames=len(fs),roof_ground=roof,shots=r.get('shots'),last=[fs[-1].get('x'),fs[-1].get('y'),fs[-1].get('support_id')]if fs else None)),flush=True)
 write(e.out/'summary.json',dict(actual_cases=e.sim.cases,purpose_pass=sum(x['purpose']['ok']for x in rows),same_outcome_successes=[x['case']['id']for x in rows if x['same_external_outcome']],rows=rows))
if __name__=='__main__':main()
