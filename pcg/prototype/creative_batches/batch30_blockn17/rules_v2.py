"""Final source rule: shorter actual projectile flight, plus true second input."""
import math
from pathlib import Path
from . import rules_v1 as source
from pcg.prototype.workshop.rules import cmd,wait_x,settle,ground
from pcg.prototype.creative_batches.batch30_blockpilot.rules_v1 import block_port
from pcg.map_directed.block_grid.contracts import declare,validate
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=source.RECIPES;RUNNER_SCRIPT=source.RUNNER_SCRIPT;NATIVE_SCENE=HERE/'main_v2.tscn'
SOURCE_DEPENDENCIES=[Path(source.__file__),*source.SOURCE_DEPENDENCIES,Path(__file__),HERE/'revision-v2.json',HERE/'main_v2.gd',HERE/'main_v2.tscn']
def candidate(target='B',control=0,interface=0,entry='A'):
 if interface not in [0,1]or entry not in (['A']if interface==0 else['A','D']):raise ValueError('outsideN17finalinterfacedomain')
 c=source.candidate(target,control);c['latches'][0]['bell'][1]=488
 if target=='B':c['control_plan'][11]=cmd('jump_release',[20,24][control]);c['control_plan'][12]=cmd('shoot',direction=[-1,0]);c['rule_parameters']['horizontal_dy']=0
 branch=c['control_plan'][8:]
 if interface==1:
  c['platforms'][2][2]=320;c['platforms'].append([800,736,352,64]);c['ports'][1]['position']=[1128,462];c['block_ports']['B']=block_port('B',[8,3],'E',[1128,462])
  dp=block_port('D',[8,5],'E',[1128,718]);c['ports'].append(dict(id='D',position=[1128,718],normal=dp['normal'],support_index=8));c['block_ports']['D']=dp
  if target=='B':
   c['exit_port']=[1128,462];c['goal']=[1121,458,14,8];branch[0]=settle(1128)
  if entry=='D':
   c['spawn']=[1128,718];c['entry_port']=[1128,718]
   c['control_plan']=[cmd('axis',value=-1),wait_x(816,-1),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[math.sqrt(1-.15**2),.15]),settle(560),wait_x(567,-1),ground(),cmd('wait',20)]+branch
  else:c['control_plan']=c['control_plan'][:8]+branch
  proj=declare(dict(case=c,ports=c['block_ports'],action_clearance=[]),[(x,y)for x in range(9)for y in range(8)]);assert not validate(proj),validate(proj);c['block_grid']=proj['block_grid']
 c['id']=f'b31-blockn17-v2-i{interface}-{entry}-{target}-c{control}';c['interface']=interface;c['route_spec']['id']=entry+'-to-'+target;c['route_spec']['from_port']=entry;c['rule_parameters'].update(interface=interface,entry=entry,short_projectile_bell488=True)
 c['native_scene']='res://prototype/creative_batches/batch30_blockn17/main_v2.tscn';c['native_block_scene']=str(NATIVE_SCENE.relative_to(HERE.parents[3]))
 c['layout_uid']=digest({k:c.get(k)for k in ['platforms','ports','latches','reward_sites','block_grid','block_ports']});c['generation_rule'].update(version=2,source_path=str(Path(__file__).relative_to(HERE.parents[3])));s=c['map_specification'];s['id']='B31-N17/'+('threeport'if interface==0 else'fourport')+'-cross-shaft-v2';s['objective']['physical_layout_sha256']=c['layout_uid'];s['ports']=dict(count=len(c['ports']),required_normals=[p['normal']for p in c['ports']]);s['relations']=[dict(from_port=a,to_port=t,role='main')for a in(['A']if interface==0 else['A','D'])for t in ['B','C']];s['space']['max_width']=1024 if interface==0 else 1152;s['space']['max_port_span_x']=s['space']['max_width'];s['return_conditions']='Onlyregisteredlowingress->B/C;otherorderedpairs/recovery/seams/fullMapUNKNOWN'
 return c
purpose=source.purpose
def support_margin(c,r):
 i=2 if c['route_spec']['to_port']=='B'else 3;rect=c['platforms'][i];f=next((f for f in r.get('frames',[])if f.get('grounded')and f.get('support_id')=='Platform'+str(i)),None)
 if not f:return dict(eligible=False,score=None)
 score=min(f['x']-12-rect[0],rect[0]+rect[2]-f['x']-12)
 return dict(eligible=purpose(c,r)['ok']and score>=0,score=score,first_target_support={k:f.get(k)for k in ['frame','x','y','support_id']})
