"""Validation-only real-death and closed-window return witnesses; no Module count."""
import argparse,copy,json
from pathlib import Path
from . import api_v1 as api
from .repair_v4 import compact
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
HERE=Path(__file__).parent
def rest():return [cmd('axis',value=0),ground(),cmd('wait',8)]
def dead_fixture(control=0):
 c=api.layouts(api.RECIPES[0],0)[1];prep,gap=[(18,18),(20,18),(18,20),(20,20)][control]
 before=[cmd('shoot',aim_cell=dict(kind='bell',id='window-path-pair')),cmd('wait',prep),cmd('shoot',aim_cell=dict(kind='enemy',id='window-sentry')),cmd('wait',gap),cmd('shoot',aim_cell=dict(kind='enemy',id='window-sentry')),cmd('axis',value=0),cmd('wait',4),cmd('jump'),cmd('jump_release',8),cmd('shoot',6,aim_cell=dict(kind='enemy',id='window-sentry')),cmd('wait',35),cmd('axis',value=-1),wait_x(80,-1),*rest(),cmd('shoot',aim_cell=dict(kind='bell',id='window-path-pair')),cmd('wait',15)]
 c['id']+=f'-real-ground-clear-c{control}';c['control_plan']=before+c['control_plan'];c['max_frames']=2200;c['validation_fixture']=dict(kind='actual3HPclear_then_same_world_staged',no_module_enrollment=True,control=control)
 return c
def guard_fixture(after_exchange=False):
 c=api.layouts(api.RECIPES[0],0)[0];source=copy.deepcopy(c['control_plan']);c['id']+='-guard-'+('actual-return'if after_exchange else'initial')
 c['goal']=[55,416,50,8]
 c['control_plan']=(source[:-1]+[wait_x(450),*rest(),cmd('axis',value=-1),wait_x(80,-1),*rest(),cmd('wait',120),settle(80,6)]if after_exchange else[cmd('shoot',aim_cell=dict(kind='enemy',id='window-sentry')),cmd('wait',120),settle(80,6)])
 c['max_frames']=1800;c['validation_fixture']=dict(kind='actual_closed_window_guard_return'if after_exchange else'actual_closed_window_guard_initial',no_module_enrollment=True,definition_marker='B',actual_goal='originalA')
 return c
def dead_check(c,r):
 q=api.purpose(c,r);dead=any(e.get('dead')for e in r.get('plains',{}).get('enemies',[]));q['causal']['actual_enemy_dead']=dead
 if not dead:q['reasons'].append('enemy_not_really_dead')
 q['ok']=not q['reasons'];return q
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args()
 engine=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),HERE/'verification-protocol-v3.json',HERE/'repair_v4.py',Path(api.__file__),*api.SOURCE_DEPENDENCIES],runner_script=api.RUNNER_SCRIPT);rows=[];clean=[]
 for c,r,e in engine.run([dead_fixture(k)for k in range(4)],'real-clear-clean'):
  q=dead_check(c,r);rows.append(compact(c,r,e,q))
  if q['ok']:clean.append(c)
  print(json.dumps(dict(id=c['id'],ok=q['ok'],why=q['reasons'],hp=r.get('hp'),enemy=r.get('plains',{}).get('enemies'),last={k:r.get('frames',[{}])[-1].get(k)for k in ['x','y','support_id']})),flush=True)
 selected=clean[:1];write(engine.out/'selection-before-mild.json',dict(ids=[c['id']for c in selected],holdout_used=False))
 for c,r,e in engine.run([instantiate(c,261031101,'mild',k)for c in selected for k in range(6)],'real-clear-mild'):
  q=dead_check(c,r);rows.append(compact(c,r,e,q));print(json.dumps(dict(id=c['id'],ok=q['ok'],why=q['reasons'])),flush=True)
 for c,r,e in engine.run([guard_fixture(v)for v in [False,True]],'closed-guard-return'):
  expected=2 if 'actual-return'in c['id']else 3;enemies=r.get('plains',{}).get('enemies',[]);hp=enemies[0]['hp']if enemies else None;good=bool(r.get('ok'))and r.get('hp')==5 and hp==expected and not r.get('returns');q=dict(ok=good,reasons=[]if good else['closed_guard_return_failed'],causal=dict(actual_enemy_hp=hp,expected_enemy_hp=expected,actual_player_hp=r.get('hp'),protected_ground_frames=sum(f.get('grounded')and f.get('support_id')=='Platform0'for f in r.get('frames',[]))),behavior=dict(shots=r.get('shots'),jumps=r.get('jumps')))
  rows.append(compact(c,r,e,q));print(json.dumps(dict(id=c['id'],ok=good,why=q['reasons'],hp=r.get('hp'))),flush=True)
 write(engine.out/'validation-results.json',rows);print(json.dumps(dict(actual_cases=engine.sim.cases,total=208+engine.sim.cases)),flush=True)
if __name__=='__main__':main()
