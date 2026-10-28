"""N06 second interface: same real central choice from two low shores."""
import copy,json,math
from pathlib import Path
from pcg.prototype.creative_batches.batch30_blockn06_repair import api_v1 as parent
from pcg.prototype.creative_batches.batch30_blockpilot.rules_v1 import block_port
from pcg.map_directed.block_grid.contracts import raster,declare,validate
from pcg.prototype.factory.core.quality import digest
from pcg.prototype.workshop.rules import cmd,wait_x,ground
HERE=Path(__file__).parent
RECIPES=parent.RECIPES
RUNNER_SCRIPT=parent.RUNNER_SCRIPT
NATIVE_SCENE=parent.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(parent.__file__),*parent.SOURCE_DEPENDENCIES,Path(__file__),HERE/'protocol-v1.json',HERE/'demand-v1.json',HERE.parent/'batch30_blockpilot/rules_v1.py',HERE.parents[2]/'map_directed/block_grid/contracts.py',HERE.parents[2]/'creative-production/batch30/map-constraint-source-v2/source-index.json']

def candidate(entry='A',target='B',control=1):
 if entry not in ['A','D']or target not in ['B','C']or control not in [0,1]:raise ValueError('outside registered4port domain')
 if entry=='A'and control!=1:raise ValueError('A preserves frozenparent selectedcontrol1')
 c=parent.rules.candidate(target,1);c['platforms'][1]=[480,608,320,64];c['platforms'].append([1024,736,256,64])
 dock=[1256,718];c['ports'].append(dict(id='D',position=dock,normal=[1,0],support_index=9));c['block_ports']['D']=block_port('D',[9,5],'E',dock)
 if entry=='D':
  dx=[.7,.75][control];dy=math.sqrt(1-dx*dx)
  prefix=[cmd('axis',value=-1),wait_x(1055,-1),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[dx,dy]),wait_x(670,-1),cmd('axis',value=0),ground(),cmd('wait',8)]
  c['control_plan']=prefix+copy.deepcopy(c['control_plan'][9:]);c['spawn']=dock[:];c['entry_port']=dock[:]
 c['id']=f'b31-blockn06-four-v1-{entry}-{target}-c{control}';c['route_spec'].update(id=entry+'-to-'+target,from_port=entry,to_port=target,via_ports=[],require_bell=target=='C',required_rewards=[])
 c['rule_parameters'].update(control=control,entry=entry,target=target,new_interface='fourport-two-ingress',shared_choice_M=c['platforms'][1][:],new_gameplay_family=False)
 c['generation_rule']=dict(id='B31-N06/fourport-interface',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=dict(control=control,entry=entry,target=target,parent_rule='batch30_blockn06_repair',M_right_extension=64,D_bank=[1024,736,256,64],retained_recovery_platform_indices=[6,7,8],deleted_entities=[],no_inherited_physics=True),source_map_contract='6c864ae6423b6409990564371aca34a322b66253')
 c['layout_title']='中庭双翼换桥 / 东西低入口四口'
 proj=declare(dict(case=c,ports=c['block_ports'],action_clearance=c['block_reservations']),c['block_grid']['cells']);errors=validate(proj)
 if errors:raise ValueError(errors)
 c['block_grid']=proj['block_grid'];c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','latches','reward_sites','block_grid','block_ports']})
 s=c['map_specification'];s['id']='B31-N06/fourport-two-low-ingress';s['source_type']='explicit_model_authored_interface_demand_notactualMap';s['ports']=dict(count=4,required_normals=[p['normal']for p in c['ports']]);s['relations']=[dict(from_port=e,to_port=t,role='main',route_id=e+'-to-'+t)for e in ['A','D']for t in ['B','C']]
 s['objective'].update(physical_layout_sha256=c['layout_uid'],junction_role='interchange_two_ingress_to_two_high_choices',new_gameplay_family=False,new_requirement_source='demand-v1.json');s['resource_state']['entry']='Either supportedA orD dock, originalresources, samephysicalentities andoriginalpairedv3 leftsolid/rightabsent initialstate'
 s['return_conditions']='OnlyA/D->B/Cregistered4directions; other8orderedpairsUNKNOWN. Retainedoriginalfloor/stairs do not certify recovery/return/assembly/fullMap.'
 return c


def purpose(c,r):
 q=parent.purpose(c,r);outside=[];owned=set(map(tuple,c['block_grid']['cells']));fs=r.get('frames',[])
 for a,b in zip(fs,fs[1:]):
  if not raster([min(a['x'],b['x'])-12,min(a['y'],b['y'])-18,abs(a['x']-b['x'])+24,abs(a['y']-b['y'])+36])<=owned:outside.append(b['frame'])
 q['causal']['outside_body_sweep_frames']=outside[:20]
 if outside:q['reasons'].append('actual_body_sweep_outside_frozen_ownership')
 q['ok']=not q['reasons'];return q


def support_margin(c,r):
 m=parent.rules.support_margin(c,r);m['eligible']=m['eligible']and m.get('score',-1)>=0
 return m
