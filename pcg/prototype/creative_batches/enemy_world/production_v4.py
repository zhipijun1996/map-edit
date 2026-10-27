"""Physical thorn-edge landing repair; previous broad floor remains archived."""
from pathlib import Path
from pcg.prototype.creative_batches.enemy_world.production_v3 import compiler as previous,purpose,alternatives as old_alts
from pcg.prototype.workshop.production_loop import run
from pcg.prototype.workshop.engine import ROOT
HERE=Path(__file__).parent

def compiler(request):
 response=previous(request)
 if response['status']!='requires_physics':return response
 s=response['specifications'][0];s['id']='creative/enemy-world/displace-landing-v4/0';s['objective']['physical_repair']='real left top thorns leave only a body-sized safe landing beside actual enemy'
 for c in response['cases']:
  c['id']=c['id'].replace('-v3-','-v4-');c['platforms'][1]=[170,438,570,100]
  c['thorns']=[dict(surface_id='landing-left-thorns',platform_index=1,face='top',start_offset=0,length=26,depth=12)]
  c['exit_port']=[210,420];c['goal']=[208,416,8,8];c['reward_sites'][0]['position']=[210,420]
  c['control_plan'][-1]['target_x']=210;c['control_plan'][-1]['deadband']=1
  c['generation_rule']['version']=4;c['generation_rule']['source_path']=str(Path(__file__).relative_to(ROOT.parent))
  c['rule_parameters']['physical_landing_constraint']='left body must clear thorn edge x196; unpushed enemy body starts x211'
 return response

def alternatives(c):
 out=old_alts(c)
 for v in out:
  for step in v['control_plan']:
   if step.get('target_x')==208:step['target_x']=210;step['deadband']=1
 return out
if __name__=='__main__':
 run('workshop-creative-enemy-world-production-v4',requests=[dict(recipe='displace-landing',interfaces=[0])],cycles=1,library_root=ROOT/'results/workshop-creative-enemy-world-library-v1',compiler=compiler,checker=purpose,counter_builder=alternatives,source_file=Path(__file__),extra_sources=[HERE/'production_v3.py',HERE/'probe_v4.py',HERE/'runner_v1.gd'],runner_script=HERE/'runner_v1.gd')
