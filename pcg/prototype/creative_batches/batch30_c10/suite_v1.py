"""Final frozen C10 world probes, bounded counters and preselected noise."""
import argparse,copy,json,math
from pathlib import Path
from . import rules_v3 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.rules import cmd,settle,wait_x,ground
HERE=Path(__file__).parent

def alternatives(c):
 out=[];target=c['exit_port'][0]
 def add(label,p):
  v=copy.deepcopy(c);v['id']+='-counter-'+label;v['counterexample_kind']=label;v['control_plan']=p;out.append(v)
 if c['rule_parameters']['route']=='main':
  for hold in [0,8,16,24,28]:
   p=[settle(650),wait_x(180)]
   if hold:p += [cmd('jump'),cmd('jump_release',hold)]
   add('ordinary-'+str(hold),p+[ground(),cmd('wait',10)])
  for hold in [8,16,24,28]:
   for dy in [.15,.7,.99]:add(f'paid-recoil-{hold}-{dy}',[settle(650),wait_x(180),cmd('jump'),cmd('jump_release',hold),cmd('shoot',direction=[-math.sqrt(1-dy*dy),dy]),ground(),cmd('wait',10)])
  for hold in [0,20]:
   p=[cmd('shoot',aim_cell=dict(kind='bell',id='recovery-pair')),settle(650),wait_x(180)]
   if hold:p += [cmd('jump'),cmd('jump_release',hold)]
   add('preopen-'+str(hold),p+[ground(),cmd('wait',10)])
 else:
  source=copy.deepcopy(c['control_plan']);ix=next(i for i,v in enumerate(source)if v['op']=='shoot')
  p=copy.deepcopy(source);p[ix]=cmd('wait',source[ix]['trigger']['after']);add('omit-correction',p)
  for delay in [0,4,8,12,16,20]:
   p=copy.deepcopy(source);p[ix]['trigger']['after']=delay;add('correction-window-'+str(delay),p)
  for dy in [0,.2,.8]:
   p=copy.deepcopy(source);p[ix].pop('aim_cell',None);p[ix]['direction']=[math.sqrt(1-dy*dy),dy];add('recoil-miss-receiver-'+str(dy),p)
  for x in [80,180]:
   for hold in [0,20]:
    p=[settle(x),cmd('wait',24),cmd('shoot',aim_cell=dict(kind='bell',id='recovery-pair')),settle(330)]
    if hold:p += [cmd('jump'),cmd('jump_release',hold)]
    add(f'ground-preopen-{x}-{hold}',p+[ground(),cmd('wait',10)])
  for dy in [-.2,-.6,-.9]:add('spent-air-charge-'+str(dy),[cmd('axis',value=1),wait_x(180),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[-math.sqrt(1-dy*dy),dy]),cmd('shoot',18,aim_cell=dict(kind='bell',id='recovery-pair')),settle(330),ground(),cmd('wait',10)])
  p=copy.deepcopy(source);p[2]=cmd('wait');p[3]=cmd('wait',20);add('omit-entry-jump',p)
 return out

def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--route',choices=['main','recovery','retry'],required=True);p.add_argument('--mode',choices=['clean','noise','counters'],required=True);a=p.parse_args();c=rules.materialize(0,a.route,0)
 cs=[c]if a.mode=='clean'else[instantiate(c,261039109,level,i)for level in ['mild','moderate']for i in range(6)]if a.mode=='noise'else alternatives(c)
 e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(rules.__file__)]+rules.SOURCE_DEPENDENCIES,runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run(cs,a.mode):
  q=rules.purpose(c,r);last=r.get('frames',[{}])[-1];row=dict(id=c['id'],counter_kind=c.get('counterexample_kind'),purpose=q,result={k:r.get(k)for k in ['ok','reason','hp','shots','jumps']},last={k:last.get(k)for k in ['frame','x','y','support_id']},evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'probe-results.json',rows);write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,purpose_passed=sum(x['purpose']['ok']for x in rows)))
if __name__=='__main__':main()
