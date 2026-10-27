"""Fresh outer control cycle; unchanged previous physical Cell/world."""
import copy
from pathlib import Path
from pcg.prototype.creative_batches.batch30_blockn03 import rules_v2 as source
from pcg.prototype.workshop.rules import cmd
HERE=Path(__file__).parent
RECIPES=source.RECIPES
RUNNER_SCRIPT=source.RUNNER_SCRIPT
NATIVE_SCENE=HERE.parent/'batch30_blockn03/main_v1.tscn'
SOURCE_DEPENDENCIES=[*source.SOURCE_DEPENDENCIES,Path(__file__),HERE/'protocol-v1.json',HERE/'phase-and-policy-clarification-v1.json']
CONTROLS=[(20,16),(20,24),(24,16),(24,24)]

def candidate(target='B',control=0):
 if target not in ['B','C']or control not in range(4):raise ValueError('outside registered cycle2')
 c=source.module_candidate(target,0);walk,brake=CONTROLS[control];c['id']=f'b31-block-n03-cycle2-i0-{target.lower()}-c{control}'
 c['control_plan'][7:7]=[cmd('axis',value=1),cmd('wait',walk),cmd('axis',value=0)]
 if target=='C':
  i=next(i for i,s in enumerate(c['control_plan'])if s['op']=='shoot'and s.get('aim_cell',{}).get('id')=='reverse-bell')
  assert c['control_plan'][i+1]['op']=='axis'
  c['control_plan'][i+1:i+2]=[cmd('axis',value=1),cmd('wait',brake),cmd('axis',value=0)]
  for s in c['control_plan']:
   d=s.get('trigger',{}).get('dynamic',{})
   if d.get('kind')=='actor_x'and d.get('value')==300:s['trigger']['timeout']=600
 c['rule_parameters'].update(control=control,outer_cycle=2,center_walk_frames=walk,air_right_brake_frames=brake,physical_geometry_and_Cell_unchanged=True)
 c['generation_rule']=dict(id='B31-N03/cycle2-center-before-intercept',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'],parent_closed_cycle='batch30_blockn03/failure-feedback-v1.json',source_map_contract='6c864ae6423b6409990564371aca34a322b66253',new_cell_required=True)
 return c


def purpose(c,r):return source.purpose(c,r)
