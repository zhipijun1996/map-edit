"""Actual EnemyActor collision-shape anti-pinch cases for V2."""
import argparse,json
from pathlib import Path
from . import probe_v1 as old,probe_v2 as fixed
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.rules import cmd,settle
HERE=Path(__file__).parent
SOURCES=[Path(__file__),Path(old.__file__),Path(fixed.__file__)]+old.SOURCE_DEPENDENCIES+[HERE/n for n in ['pair_latch_v2.gd','runtime_v2.gd','runner_v2.gd','main_v2.gd','main_v2.tscn']]

def cases():
 out=[]
 for label,initial,x,expect in [('enemy-in-A','A',460,True),('enemy-outside','A',650,False),('enemy-in-B','B',860,True),('enemy-body-edge','A',486,True)]:
  c=fixed.cases()[0];c['id']='pair-cell-'+label+'-v2';c['latches'][0]['initial_open']=initial
  c['enemies']=[dict(id='sentinel',definition='plains_sentry',position=[x,422],initial_idle_cooldown=1.5)]
  c['control_plan']=[cmd('shoot',aim_cell=dict(kind='bell',id='pair')),cmd('wait',15),settle(120)];c['expect_enemy_block']=expect;out.append(c)
 return out

def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=SOURCES,runner_script=HERE/'runner_v2.gd');rows=[]
 for c,r,b in e.run(cases(),'real-enemy-antipinch'):
  ps=r.get('workshop',{}).get('paired_gates',[{}])[0];es=r.get('plains',{}).get('enemies',[]);blocked=ps.get('blocked_count')==1;expected=c['expect_enemy_block'];events=[v for v in ps.get('events',[])if v['type']=='pair_switch_blocked'];reasons=[]
  if not r.get('ok'):reasons.append(r.get('reason'))
  if blocked!=expected or ps.get('switch_count')!=(0 if expected else 1):reasons.append('wrong-atomic-outcome')
  if not es or es[0].get('hp')!=3 or es[0].get('dead'):reasons.append('enemy-was-harmed')
  if expected and not any(a['kind']=='enemy'for event in events for a in event.get('blockers',[])):reasons.append('actual-enemy-shape-not-reported')
  fs=r.get('frames',[])
  if any(p['open_a']==p['open_b']or p['gate_a_layer']==p['gate_b_layer']or p['gate_a_disabled']==p['gate_b_disabled']for f in fs for p in f.get('workshop',{}).get('paired_gates',[])):reasons.append('complementarity-lost')
  if c['id'].endswith('body-edge-v2')and expected:
   # Its centre is outside A while the full original enemy shape overlaps.
   xs=[a['position'][0]for event in events for a in event.get('blockers',[])if a['kind']=='enemy']
   if not xs or not all(x>474 for x in xs):reasons.append('edge-probe-centre-not-outside')
  check=dict(ok=not reasons,reasons=reasons,final_pair=ps,enemy=es,frame_count=len(fs));rows.append(dict(case=c,result=r,check=check,evidence=b));print(json.dumps(dict(id=c['id'],check=check)),flush=True)
 write(e.out/'summary.json',dict(actual_cases=e.sim.cases,passed=sum(x['check']['ok']for x in rows),rows=rows))
if __name__=='__main__':main()
