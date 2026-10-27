"""Version 2 close-range clearing, original cooldown and aim-noise domains."""
from pathlib import Path
from pcg.prototype.creative_batches.enemy_world.production_v1 import specification as old_spec,purpose,alternatives
from pcg.prototype.creative_batches.enemy_world.probe_v3 import cases
from pcg.prototype.workshop.production_loop import run
from pcg.prototype.workshop.engine import ROOT

def compiler(request):
 if request.get('recipe')!='clear-sightline':return dict(status='needs_design',gaps=['unsupported relationship'],cases=[])
 s=old_spec('clear-sightline');s.update(id='creative/enemy-world/clear-sightline-v2/0');s['objective']['geometry_revision']='near-range and horizontal initial shots';cs=cases()[:4]
 for c in cs:
  c['id']=c['id'].replace('ew-near-clear','ew-clear-sightline-v2');c['trace_all']=False;c['max_frames']=420
  c['enemies'][0]['initial_idle_cooldown']=.6;c['map_specification']=s;c['idea_ids']=['enemy-world/absorber-bell','enemy-world/brace-clearance']
  c['rule_parameters']=dict(relationship=s['objective']['relationship'],ground_clearance=42,producer_task='/root/enemy_world_creator',source_type='llm_subagent_implementation')
  c['generation_rule']=dict(id='creative/enemy-world/clear-sightline',version=2,source_path=str(Path(__file__).relative_to(ROOT.parent)),parameters=c['rule_parameters'])
 return dict(status='requires_physics',specifications=[s],cases=cs)

def counters(c):
 # Reuse falsifiers with corrected output x. All remain identical geometry.
 out=alternatives(c)
 for v in out:
  for step in v['control_plan']:
   if step.get('target_x')==650:step['target_x']=450
 return out
if __name__=='__main__':
 run('workshop-creative-enemy-world-production-v2',requests=[dict(recipe='clear-sightline',interfaces=[0])],cycles=1,library_root=ROOT/'results/workshop-creative-enemy-world-library-v1',compiler=compiler,checker=purpose,counter_builder=counters,source_file=Path(__file__),extra_sources=[Path(__file__).with_name('production_v1.py'),Path(__file__).with_name('probe_v3.py')])
