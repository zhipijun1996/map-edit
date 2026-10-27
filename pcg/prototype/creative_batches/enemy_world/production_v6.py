"""Restore robust settling and accept either genuine displacement direction."""
from pathlib import Path
from pcg.prototype.creative_batches.enemy_world.production_v5 import compiler as previous
from pcg.prototype.creative_batches.enemy_world.production_v3 import alternatives
from pcg.prototype.workshop.evaluate import purpose as original_purpose
from pcg.prototype.workshop.production_loop import run
from pcg.prototype.workshop.engine import ROOT
HERE=Path(__file__).parent

def compiler(request):
 response=previous(request)
 if response['status']!='requires_physics':return response
 response['specifications'][0]['id']='creative/enemy-world/displace-landing-v6/0'
 for c in response['cases']:
  c['id']=c['id'].replace('-v5-','-v6-');c['exit_port']=[208,420];c['goal']=[200,416,15,8]
  c['control_plan'][-1]['target_x']=208;c['control_plan'][-1]['deadband']=4
  c['generation_rule']['version']=6;c['generation_rule']['source_path']=str(Path(__file__).relative_to(ROOT.parent))
 return response

def purpose(c,r):
 p=original_purpose(c,r);fs=r.get('frames',[]);events=r.get('plains',{}).get('events',[])
 hits=[e for e in events if e['type']=='damage'and e.get('target')=='occupant']
 moved=any(f.get('plains',{}).get('enemies')and abs(f['plains']['enemies'][0]['x']-225)>=8 for f in fs)
 dead=any(e['type']=='enemy_defeated'and e['id']=='occupant'for e in events)
 body_clear=any(f['grounded']and f['y']>400 and (f['plains']['enemies'][0]['dead']or abs(f['x']-f['plains']['enemies'][0]['x'])>=26) for f in fs if f.get('plains',{}).get('enemies'))
 relation=bool(hits and (moved or dead)and body_clear)
 p['causal'].update(enemy_body_displaced=moved,enemy_defeated=dead,actual_body_clear_at_lower_landing=body_clear,enemy_initial_x=225,body_half_width_sum=26,damage_target_id='occupant',either_displacement_direction_accepted=True)
 if not relation:p['reasons'].append('enemy_occupancy_not_actually_changed')
 p['ok']=not p['reasons'];return p
if __name__=='__main__':
 run('workshop-creative-enemy-world-production-v6',requests=[dict(recipe='displace-landing',interfaces=[0])],cycles=1,library_root=ROOT/'results/workshop-creative-enemy-world-library-v1',compiler=compiler,checker=purpose,counter_builder=alternatives,source_file=Path(__file__),extra_sources=[HERE/('production_v'+str(v)+'.py')for v in [3,4,5]]+[HERE/'probe_v4.py',HERE/'runner_v1.gd'],runner_script=HERE/'runner_v1.gd')
