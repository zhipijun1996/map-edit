"""Bounded control-only repair over immutable v5 Cells and world geometry."""
import copy,math
from pathlib import Path
from . import rules_v5 as old
HERE=Path(__file__).parent
RECIPES=old.RECIPES
RETURN_CONTROLS=[(545,.35),(560,.35),(545,.5),(560,.5)]
SOURCE_DEPENDENCIES=[Path(old.__file__),HERE/'protocol-v1.json',HERE/'protocol-v2.json',HERE.parents[2]/'creative-production/batch30/protocol-v3.json']

def materialize(interface=0,park='middle',route='outbound',control=None,return_control=0):
 if control is None:control=0 if interface==0 else 3
 c=copy.deepcopy(old.materialize(interface,park,route,control));takeoff,dy=RETURN_CONTROLS[return_control]
 if route=='return-middle':
  for command in c['control_plan']:
   query=command.get('trigger',{}).get('dynamic',{})
   if query.get('kind')=='actor_x'and query.get('value')==490+interface*15:query['value']=takeoff
  shots=[q for q in c['control_plan']if q['op']=='shoot'];shots[-1]['direction']=[math.sqrt(1-dy*dy),dy]
 c['id']=c['id'].replace('v5','v6')+'-r'+str(return_control);c['rule_parameters']['return_control']=dict(index=return_control,takeoff_x=takeoff,shot_dy=dy)
 c['generation_rule']=dict(id='batch30/D04',version=6,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'],geometry_source=str(Path(old.__file__).relative_to(HERE.parents[3])),geometry_unchanged=True)
 return c
