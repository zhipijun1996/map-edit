"""Second spatial demand for the same gate-opening/return-catch family."""
import copy
from pathlib import Path
from pcg.prototype.creative_batches.batch30_blockn04 import api_v1 as source
from pcg.prototype.creative_batches.batch30_blockn04.rules_v1 import candidate as original_candidate
from pcg.prototype.creative_batches.batch30_blockpilot.rules_v1 import block_port
from pcg.map_directed.block_grid.contracts import declare,validate
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=source.RECIPES
RUNNER_SCRIPT=source.RUNNER_SCRIPT
NATIVE_SCENE=source.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(source.__file__),*source.SOURCE_DEPENDENCIES,HERE/'protocol-v1.json',HERE/'counter-expansion-v1.json']

def adapted(old,paid_C=False):
 c=copy.deepcopy(old);target=c['rule_parameters']['target'];c['interface']=1
 c['platforms'][3]=[960,480,320,96];c['platforms'][5]=[896,480,64,320]
 c['platforms'].append([1248,576,32,224])
 c['ports']=[p for p in c['ports']if p['id']!='D']
 for p in c['ports']:
  if p['id']=='C':p['position']=[1256,462]
 ports={k:copy.deepcopy(v)for k,v in c['block_ports'].items()if k!='D'}
 ports['C']=block_port('C',[9,3],'E',[1256,462])
 c['exit_port']=[24,334]if target=='B'else[1256,462];end=c['exit_port'];c['goal']=[end[0]-25,end[1]-4,50,8]
 for site in c['reward_sites']:
  if site['id']=='high-C':site.update(position=[1256,462],region=[1226,456,60,12],amount=6)
 c['expected_reward']=12 if target=='B'else 6
 if target=='C'and not paid_C:c['control_plan'][18]=cmd('wait')
 projected=declare(dict(case=c,ports=ports,functional_roles=['junction','fork'],action_clearance=c['block_reservations']),c['block_grid']['cells'])
 assert not validate(projected),validate(projected)
 c['block_grid']=projected['block_grid'];c['block_ports']=ports
 c['id']=old['id'].replace('block-n04-v1','block-n04-adapt-v1')+'-i1'
 if old.get('counterexample_kind'):
  base,kind=c['id'].split('-counter-',1);kind=kind.removesuffix('-i1');c['id']=base+'-i1-counter-'+kind
 c['rule_parameters'].update(interface=1,lower_C_paid_recoil=paid_C)
 c['layout_uid']=digest({k:c.get(k,[])for k in ['platforms','ports','latches','reward_sites','block_grid','block_ports']})
 c['generation_rule']=dict(id='batch30/N04-asymmetric-fork',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),source_contentVersion='sha256:87b8ed50f5b86fe4eafb92bc593864a15f1c59b7c99c60fae0d55f8c56460efc',parameters=dict(timer=.2,right_shore_change=128,removed_external_port='D',original_lower_D_terrain_retained=True,added_terminal_rock=[1248,576,32,224],bounded32_adapter=False,lower_C_paid_recoil=paid_C,source_physics_inherited=False),source_map_contract='6c864ae6423b6409990564371aca34a322b66253')
 c['layout_title']='穿过的门，回来接住你 / 三口错层分叉'
 s=c['map_specification'];s['id']='batch30/block-N04/asymmetric-fork';s['objective'].update(interface=1,physical_layout_sha256=c['layout_uid'],junction_role='fork',asymmetric_exit_height_difference=128,same_gameplay_family=True)
 s['ports']=dict(count=3,required_normals=[p['normal']for p in c['ports']]);s['relations']=[dict(from_port='A',to_port=k,role='main',route_id='A-to-'+k)for k in ['B','C']]
 s['risk_reward']['reward_sites']=copy.deepcopy(c['reward_sites'])
 s['return_conditions']='A->B and A->C only. Other4 ordered pairs, arbitrary-state return, boundary crossing and full Map UNKNOWN. Retained old lowerD terrain is internal recovery, not an external port.'
 return c

def candidate(target='B',paid_C=False):return adapted(original_candidate('A',target,.2),paid_C)
def layouts(recipe,interface):
 if recipe!=RECIPES[0]or interface!=1:raise ValueError('only the asymmetric three-port interface1 is registered')
 return[candidate('B'),candidate('C')]
def purpose(c,r):return source.purpose(c,r)

def alternatives(c):
 out=source.alternatives(c)
 if c['rule_parameters']['target']=='C':
  prefix=copy.deepcopy(c['control_plan'][:5]);onto=[cmd('axis',value=1),wait_x(1000),cmd('axis',value=0),ground(),cmd('wait',6),cmd('axis',value=1),cmd('jump'),cmd('jump_release',20),wait_x(1100),cmd('axis',value=0),ground(),cmd('wait',6)]
  for kind,tail in [('old-internal-D-exterior-launch',[cmd('axis',value=1),wait_x(1296),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[0,1]),settle(1256),ground(),cmd('wait',10)]),('floor-under-terminal-rock-exterior-launch',[cmd('axis',value=1),wait_x(1290),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[0,1]),settle(1256),ground(),cmd('wait',10)])]:
   v=copy.deepcopy(c);v['id']+='-counter-'+kind;v['counterexample_kind']=kind;v['control_plan']=prefix+(onto if kind.startswith('old-')else[])+tail;out.append(v)
  for kind,x,direction in [('outside-floor-angled-column-top',1290,[.25,.9682458365518543]),('inside-floor-angled-column-top',1230,[-.15,.9886859966642595])]:
   v=copy.deepcopy(c);v['id']+='-counter-'+kind;v['counterexample_kind']=kind;v['control_plan']=copy.deepcopy(prefix)+[cmd('axis',value=1),wait_x(x),cmd('axis',value=0),cmd('jump'),cmd('jump_release',24),cmd('shoot',direction=direction),settle(1256),ground(),cmd('wait',10)];out.append(v)
 return out
