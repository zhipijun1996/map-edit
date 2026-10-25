"""Keep original port hazard margin while closing the left safe-body bypass."""
from pathlib import Path
from pcg.prototype.creative_batches.enemy_world.production_v4 import compiler as previous,purpose,alternatives
from pcg.prototype.workshop.production_loop import run
from pcg.prototype.workshop.engine import ROOT
HERE=Path(__file__).parent

def compiler(request):
 response=previous(request)
 if response['status']!='requires_physics':return response
 response['specifications'][0]['id']='creative/enemy-world/displace-landing-v5/0'
 for c in response['cases']:
  c['id']=c['id'].replace('-v4-','-v5-');c['thorns'][0]['length']=18
  c['generation_rule']['version']=5;c['generation_rule']['source_path']=str(Path(__file__).relative_to(ROOT.parent))
  c['rule_parameters']['physical_landing_constraint']='left body must clear thorn edge x188 (center>=200), unpushed enemy225 allows only center<=199; no safe gap until original enemy moves'
 return response
if __name__=='__main__':
 run('workshop-creative-enemy-world-production-v5',requests=[dict(recipe='displace-landing',interfaces=[0])],cycles=1,library_root=ROOT/'results/workshop-creative-enemy-world-library-v1',compiler=compiler,checker=purpose,counter_builder=alternatives,source_file=Path(__file__),extra_sources=[HERE/'production_v4.py',HERE/'production_v3.py',HERE/'probe_v4.py',HERE/'runner_v1.gd'],runner_script=HERE/'runner_v1.gd')
