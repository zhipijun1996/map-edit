"""Close the real lower-mouth landing bypass found by v4 counters."""
import importlib.util
from pathlib import Path
OWN=Path(__file__);PRIOR=OWN.with_name('production-v4.py');s=importlib.util.spec_from_file_location('wallslide_v4',PRIOR);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
from pcg.prototype.workshop.production_loop import run
ROOT=m.ROOT;ADAPTER=m.ADAPTER

def compiler(request):
 response=m.compiler(request)
 for c in response['cases']:
  c['id']=c['id'].replace('-v4-','-v5-');c['thorns'].append(dict(surface_id='lower-mouth-no-perch',platform_index=3,face='top',start_offset=0,length=20,depth=8));c['generation_rule']['version']=5;c['rule_parameters']['v4_counterexample_repair']='Lower mouth top was an actual unintended landing/recharge step; add original top-face thorn to match guarded mouth claim.'
 return response
purpose=m.purpose
alternatives=m.alternatives
if __name__=='__main__':
 run('workshop-creative-jump-wall-production-v5',[dict(recipe=m.FAMILY,interfaces=[0])],cycles=1,library_root=ROOT/'results/workshop-creative-jump-wall-library-v1',compiler=compiler,checker=purpose,counter_builder=alternatives,source_file=OWN,extra_sources=[PRIOR,ADAPTER],runner_script=ADAPTER)
