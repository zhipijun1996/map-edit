from pathlib import Path
from . import rules_v1 as prior
from pcg.prototype.workshop.rules import wait_x,settle,reward
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=prior.RECIPES
RUNNER_SCRIPT=prior.RUNNER_SCRIPT
NATIVE_SCENE=prior.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(prior.__file__),*prior.SOURCE_DEPENDENCIES,HERE/'protocol-v2.json']
def candidate(interface=0,control=0):
 if interface not in[0,1]:raise ValueError('Outside registered descendingcarrier spaces')
 c=prior.candidate(0,control)
 if interface==0:return c
 c['id']=f'b30-c11-v2-i1-c{control}'
 c['platforms'][0]=[-80,230,320,100];c['platforms'][1]=[870,430,220,100];c['platforms'][2]=[500,20,180,410];c['platforms'][-1]=[270,60,30,190]
 c['moving_platforms'][0].update(start=[360,310],finish=[720,730],size=[240,20],travel_duration=3.5)
 c['latches'][0]['bell']=[520,260];c['thorns'][0]['length']=410
 retreat,advance=[(305,470),(305,490),(325,470),(325,490)][control]
 c['control_plan'][6]=wait_x(retreat,-1);c['control_plan'][8]=wait_x(advance);c['control_plan'][10]=wait_x(720);c['control_plan'][-1]=settle(980,6)
 c.update(spawn=[80,212],entry_port=[80,212],exit_port=[980,412],goal=[955,408,50,8],interface=1)
 c['ports']=[dict(id='A',position=[80,212],normal=[-1,0],support_index=0),dict(id='B',position=[980,412],normal=[1,0],support_index=1)]
 c['reward_sites']=[];reward(c,980,412,8)
 c['rule_parameters'].update(interface=1,control=control,retreat_x=retreat,forward_read_x=advance,roof=[500,20,180,410],receiver=[870,430,220,100],carrier_drop=420,departure_x=720,near_shore_tooth=[270,60,30,190],spatial_adaptation='narrower240deck, steeper420drop, changed tooth/roof and nearer higher-relative receiver')
 c['layout_title']='下沉渡台：先退后抢 / 陡降侧岸'
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','moving_platforms','latches','reward_sites','thorns']})
 c['generation_rule']=dict(id='batch30/C11',version=2,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'])
 return c
purpose=prior.purpose
