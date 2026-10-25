"""v6 repairs independently phased transfer and roof bypass, retains all v3 failures."""
import copy
from pathlib import Path
from pcg.prototype.creative_batches.machinery.probe_v5 import candidates as repaired
from pcg.prototype.creative_batches.machinery.production_v3 import purpose,alternatives,specification as old_spec
from pcg.prototype.workshop.production_loop import run
from pcg.prototype.workshop.engine import ROOT
RECIPES=['carrier-rendezvous','saw-pursuit']
def compiler(request):
 recipe=request['recipe'];s=old_spec(recipe);s['id']='creative-machinery/v6/'+recipe
 cs=repaired(recipe)
 for c in cs:
  c['trace_all']=False;c['production_recipe']=recipe;c['parent_family']='moving_platform'if recipe!='saw-pursuit'else'dynamic_saw';c['rule_parameters']=dict(relationship=recipe,source_task='/root/machinery_creator',revision='independent platform phase rendezvous or real thorn roof blocks bypass',human_fun='unreviewed');c['generation_rule']=dict(id='creative-machinery/'+recipe,version=6,source_type='llm_subagent_proposal',source_task='/root/machinery_creator',parameters=c['rule_parameters']);c['map_specification']=s;c['idea_ids']=['machinery/'+recipe]
 return dict(status='requires_physics',specifications=[s],cases=cs)
if __name__=='__main__':
 run('workshop-creative-machinery-production-v6',requests=[dict(recipe=r)for r in RECIPES],cycles=2,library_root=ROOT/'results/workshop-creative-machinery-library-v6',compiler=compiler,checker=purpose,counter_builder=alternatives,source_file=Path(__file__),extra_sources=[p for p in Path(__file__).parent.glob('*.py')if p!=Path(__file__)])
