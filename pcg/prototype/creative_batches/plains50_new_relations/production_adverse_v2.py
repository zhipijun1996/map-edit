"""Second geometry revision: wider demanded receiving shore, same quality gate."""
import copy,argparse
from pathlib import Path
from pcg.prototype.creative_batches.plains50_new_relations.production_resources_v1 import compiler as old_compiler,purpose,alternatives
from pcg.prototype.workshop.production_loop import run
HERE=Path(__file__).parent

def compiler(request):
 response=old_compiler(dict(recipe='adverse-refund-reversal'));sources=[c for c in response['cases']if c['map_specification']['id'].endswith('/1')]
 # Preserve upper port/elevation; adapt the larger receiving footprint, not the
 # admission rate. Prefer22 ticks from calibration's delayed-hit evidence.
 ss=[];cs=[]
 for c in sorted(sources,key=lambda c:0 if c['control_plan'][5]['trigger']['after']==22 else 1):
  d=copy.deepcopy(c);d['id']=d['id'].replace('p50-','p50-r2-');d['platforms'][1][0]=240;d['platforms'][1][2]=245
  d['rule_parameters']['receiving_footprint']=[240,118,245,80];d['rule_parameters']['revision_reason']='previous high-port calibration moderate7/12, enlarged receiving footprint as explicit new space demand'
  s=copy.deepcopy(d['map_specification']);s['id']='plains50-new/adverse-refund-reversal/1-wide';s['objective']=d['rule_parameters'];d['map_specification']=s;d['generation_rule']['version']=2;d['generation_rule']['parameters']=d['rule_parameters'];cs.append(d)
  if not ss:ss.append(s)
 return dict(status='requires_physics',specifications=ss,cases=cs)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--name',default='workshop-plains50-new-adverse-production-v2');a=p.parse_args()
 run(a.name,requests=[dict(recipe='adverse-refund-reversal')],cycles=1,compiler=compiler,checker=purpose,counter_builder=alternatives,source_file=Path(__file__),extra_sources=[HERE/'production_resources_v1.py',HERE/'probe_v3.py',HERE/'production_v1.py'])
