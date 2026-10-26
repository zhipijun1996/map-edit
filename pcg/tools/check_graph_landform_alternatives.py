"""Finite cheaper strategies on unchanged worlds, never an exhaustive bypass proof."""
import copy,json
from pcg.map_directed.director import REPO
from pcg.map_directed.run import write
from pcg.map_directed.graph_landforms.engine import GraphEngine
out=REPO/'pcg/results/graph-landforms-alternatives-v1'
if out.exists():raise ValueError('immutable alternatives exist')
out.mkdir();cs=json.loads((REPO/'pcg/results/graph-landforms-evaluation-v1/cases.json').read_text())['cases'];a=copy.deepcopy(cs[0]);a['id']+='-untargeted-air-shot';b=copy.deepcopy(cs[2]);b['id']+='-needle-without-recoil'
for leg in a['pilot_program']:
 if leg.get('edge_from')=='ridge':
  for op in leg.get('control_plan',[]):
   if op.get('aim_cell'):op.pop('aim_cell');op['direction']=[-.9886859966642595,.15]
for leg in b['pilot_program']:
 if leg.get('edge_to')=='cache':
  for op in leg.get('control_plan',[]):
   if op['op']=='shoot':op['op']='wait';op.pop('direction',None);op.pop('aim_cell',None)
write(out/'cases.json',dict(cases=[a,b]));write(out/'protocol.json',dict(geometry_changed=False,physics_changed=False,resources_reset=False,external_goals_unchanged=True,alternatives=['replace aimed bell shot with diagonal downward recoil shot','omit only needle-entry recoil'],scope='Two concrete input alternatives, no universal bypass impossibility claim'))
rows=[]
for c,r,e in GraphEngine(out/'physics').run([a,b],'cheaper-input-alternatives'):
 rows.append(dict(id=c['id'],physics_pass=r['ok'],expectation_met=not r['ok'],reason=r['reason'],failure=r.get('pilot',{}).get('failure'),shots=r.get('shots'),ticks=r.get('ticks'),extra=r.get('extra'),evidence=e));write(out/'rows.json',rows)
write(out/'summary.json',dict(expectations_met=all(r['expectation_met']for r in rows),rows=rows,production_admitted=False))
