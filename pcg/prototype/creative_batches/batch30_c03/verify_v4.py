import argparse,json
from pathlib import Path
from . import api_v1 as api
from .repair_v4 import compact
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.workshop.rules import cmd,settle
HERE=Path(__file__).parent
def dead_purpose(c,r):
 q=api.purpose(c,r);dead=any(e.get('dead')for e in r.get('plains',{}).get('enemies',[]));q['causal']['actual_enemy_dead']=dead
 if not dead:q['reasons'].append('enemy_not_really_dead')
 q['ok']=not q['reasons'];return q
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args()
 engine=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),HERE/'repair_v4.py',HERE/'verification-protocol-v2.json',Path(api.__file__),*api.SOURCE_DEPENDENCIES],runner_script=api.RUNNER_SCRIPT);rows=[]
 dead=api.dead_fixture();good=False
 for c,r,e in engine.run([dead],'actual-death-clean'):
  q=dead_purpose(c,r);good=q['ok'];rows.append(compact(c,r,e,q));print(json.dumps(dict(id=c['id'],ok=q['ok'],why=q['reasons'],enemies=r.get('plains',{}).get('enemies'))),flush=True)
 if good:
  for c,r,e in engine.run([instantiate(dead,261031101,l,k)for l in ['mild','moderate']for k in range(6)],'actual-death-perturb'):
   q=dead_purpose(c,r);rows.append(compact(c,r,e,q));print(json.dumps(dict(id=c['id'],ok=q['ok'],why=q['reasons'])),flush=True)
 windows=[api.rules.closed_window_fixture(after_exchange=v)for v in [False,True]]
 windows[1]['control_plan'][-7:-7]=[cmd('wait',120)]
 for c,r,e in engine.run(windows,'actual-closed-window'):
  expected=2 if 'after-return'in c['id'] else 3;enemies=r.get('plains',{}).get('enemies',[]);hp=enemies[0]['hp']if enemies else None;q=dict(ok=bool(r.get('ok'))and r.get('hp')==5 and hp==expected,reasons=[],causal=dict(expected_enemy_hp=expected,actual_enemy_hp=hp,player_hp=r.get('hp'),extra_protected_wait_ticks=120 if 'after-return'in c['id']else 0))
  if not q['ok']:q['reasons'].append('closed_window_or_return_not_demonstrated')
  rows.append(compact(c,r,e,q));print(json.dumps(dict(id=c['id'],ok=q['ok'],why=q['reasons'],enemy_hp=hp)),flush=True)
 danger=api.layouts(api.RECIPES[0],0)[0];danger['id']+='-counter-open-window-standing-threat';danger['goal']=[55,416,50,8];danger['control_plan']=[cmd('shoot',aim_cell=dict(kind='bell',id='window-path-pair')),cmd('axis',value=0),cmd('wait',120),settle(80,6)]
 for c,r,e in engine.run([danger],'open-window-threat'):
  harmed=r.get('hp',5)<5 or bool(r.get('plains',{}).get('player_damage'));q=dict(ok=False,reasons=['observed_player_harm'if harmed else'threat_contrast_not_demonstrated'],causal=dict(open_window_actual_harmed=harmed,player_hp=r.get('hp'),experiment_is_not_playable_success=True));rows.append(compact(c,r,e,q));print(json.dumps(dict(id=c['id'],safe=r.get('ok'),hp=r.get('hp'),threat_demonstrated=harmed)),flush=True)
 case=api.layouts(api.RECIPES[0],0)[0];kinds={'initial-open-path-one-shot-16-1.0-0','borrow-twice-overtop-different-world-18','borrow-twice-overtop-different-world-24','borrow-twice-overtop-different-world-35'}
 for c,r,e in engine.run([v for v in api.alternatives(case)if v['counterexample_kind']in kinds],'exact-low-cost'):
  q=api.purpose(c,r);world=api.required_world_outcome(c,r);goal_only=bool(r.get('ok'))and r.get('hp')==5 and r.get('workshop',{}).get('coins',0)>=12 and not r.get('returns')and not any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']);same=goal_only and world['ok'];row=compact(c,r,e,q);row.update(goal_only_outcome=goal_only,same_required_world_outcome=same,potential_low_cost_world_open_counter=goal_only and not world['ok']and r.get('shots',0)<=3 and r.get('jumps',0)<=1,world_outcome=world,costs=dict(nominal_probe=dict(shots=3,jumps=1,source='workshop-batch30-c03-screen-v3 i0-air-c1'),alternative={k:r.get(k)for k in ['shots','jumps','ticks']}));rows.append(row);print(json.dumps(dict(id=c['id'],goal_only=goal_only,same_world=same,shots=r.get('shots'),jumps=r.get('jumps'),ticks=r.get('ticks'),purpose=q['ok'],min_y=min((f['y']for f in r.get('frames',[])),default=None))),flush=True)
 write(engine.out/'verification-results.json',rows);print(json.dumps(dict(actual_cases=engine.sim.cases,previous_cases=200,total_probe_cases=200+engine.sim.cases)),flush=True)
if __name__=='__main__':main()
