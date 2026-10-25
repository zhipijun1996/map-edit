"""Bounded real local bypass probes; not a universal movement solver."""
import argparse,copy,itertools,json
from pathlib import Path
from .run import CompleteEngine
from ..director import REPO
from ..run import write
from pcg.prototype.plains.synthesis import command

def run(source,name):
 source=Path(source);out=REPO/'pcg/results'/name
 if out.exists():raise ValueError('immutable_bypass_run_exists')
 out.mkdir(parents=True);c=json.loads((source/'compiled.json').read_text());cases=[]
 # 54 common input alternatives per location: varied hold, recoil timing/aim.
 # Aim points away from the actual bell; a successful probe is a bypass ONLY
 # if the intended gate was never opened by any projectile.
 for node in ['west','ridge','arch','bell']:
  m=c['nodes'][node];raw=next(v for v in c['modules']if v['id']==node);dx,dy=raw['spec']['placement']
  start=[raw['core']['entry']['position'][0]+dx,raw['core']['entry']['position'][1]+dy]
  target=copy.deepcopy(m['core_reward_target'])
  if node=='west':target=copy.deepcopy(m['ports']['e0']['target'])
  for ordinal,(hold,delay,aim)in enumerate(itertools.product([4,12,24],[8,20,32],[[0,1],[-.8,.6],[.8,.6],[-1,0],[1,0],[0,-1]])):
   case=copy.deepcopy(c['case']);case.update(id='closed-bypass-'+node+'-'+str(ordinal),spawn=start,entry_port=start,exit_port=target['position'],goal=target['region'],extra_required=True,
    extra_script=str(Path(__file__).with_name('mechanics.gd')),r2_semantics={},valley_shop=c['case']['shop_sites'][0],r2_optional_challenges=[],map_budget_ticks=720)
   plan=[command('axis',value=1),command('jump'),command('jump_release',hold),command('shoot',max(0,delay-hold),direction=aim),command('settle',20,target_x=target['position'][0],deadband=3)]
   case['pilot_program']=[dict(id='local-probe',kind='module',target=target,control_plan=plan,budget_ticks=360)]
   cases.append(case)
 # 216 local trials, all budgets fixed before observing output.
 write(out/'protocol.json',dict(source=str(source),cases=len(cases),per_location=54,geometry_changes=0,selection='common fixed hold/aim/timing product; new explicit local starts, not whole-map route evidence'))
 write(out/'cases.json',dict(cases=cases));engine=CompleteEngine(out/'physics');engine.batch_size=12;rows=[]
 for case,r,ev in engine.run(cases,'closed-gate-bypass'):
  node=case['id'].split('-')[2];bell=next(v for v in r['plains']['bells']if v['id'].startswith(node+'/'))
  rows.append(dict(id=case['id'],node=node,arrived=r['ok'],gate_open_count=bell['open_count'],bypass=r['ok']and bell['open_count']==0,reason=r['reason'],evidence=ev))
  write(out/'summary.json',dict(cases=len(rows),bypasses=[v for v in rows if v['bypass']],rows=rows))
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--name',required=True);a=p.parse_args();print(run(a.source,a.name))
