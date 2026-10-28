from pathlib import Path
from . import rules_v2 as prior
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=prior.RECIPES
RUNNER_SCRIPT=prior.RUNNER_SCRIPT
NATIVE_SCENE=prior.NATIVE_SCENE
SOURCE_DEPENDENCIES=prior.SOURCE_DEPENDENCIES+[Path(prior.__file__),HERE/'main-solve-protocol-v3.json']
def nominal():
 p=prior.prior.nominal();p[0]=settle(650);return p

def materialize(interface=0,route='main',control=0):
 c=prior.materialize(0,route,control)
 if interface==0:
  if route=='main':c['control_plan']=nominal()
  elif route=='retry':c['control_plan'][-len(nominal()):]=nominal()
 else:
  c['spawn']=[80,182];c['entry_port']=[80,182];c['platforms']=[[-100,200,300,80],[500,500,240,100],[270,800,130,40],[250,660,20,140],[400,660,20,140],[80,440,140,40]]
  c['ports']=[dict(id='A',position=[80,182],normal=[0,-1],support_index=0),dict(id='B',position=[650,482],normal=[1,0],support_index=1)]
  c['latches'][0].update(bell=[500,820],return_access=[350,750],gate=[250,-200,20,860],paired_gate=[270,660,130,30])
  c['reward_sites'][0].update(position=[650,482],region=[620,477,60,10])
  if route=='main':c['control_plan']=nominal();target=[650,482]
  else:
   c['control_plan']=[cmd('axis',value=1),wait_x(180),cmd('jump'),cmd('jump_release',20),wait_x(440),settle(450),cmd('shoot',30+4*control,aim_cell=dict(kind='bell',id='recovery-pair')),settle(330),ground(),cmd('wait',10)];target=[330,782]
   if route=='retry':
    c['control_plan'] += [cmd('jump'),cmd('jump_release',20),cmd('shoot',aim_cell=dict(kind='bell',id='recovery-pair',receiver='access')),settle(220),ground(),cmd('wait',10),cmd('jump'),cmd('jump_release',16),cmd('shoot',direction=[0,1]),cmd('wait',14),settle(80),ground(),cmd('wait',10)]+nominal();target=[650,482]
  c['exit_port']=target;c['goal']=[target[0]-25,target[1]-4,50,8];c['max_frames']=1800;c['layout_title']='留一枪，把失误变成另一条活路 / 高口侧井'
 c['id']=c['id'].replace('v2','v3').replace('-i0-',f'-i{interface}-');c['interface']=interface;c['rule_parameters']['interface']=interface;c['generation_rule'].update(version=3,source_path=str(Path(__file__).relative_to(HERE.parents[3])))
 c['layout_uid']=digest({k:c.get(k,[])for k in ['platforms','ports','latches','reward_sites']});return c

def purpose(c,r):return prior.purpose(c,r)
