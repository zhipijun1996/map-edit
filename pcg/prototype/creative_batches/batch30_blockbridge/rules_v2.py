"""Same physical bridge adaptation, explicit bounded recovery ownership/control."""
import copy,json
from pathlib import Path
from . import rules_v1 as old
from pcg.map_directed.block_grid.contracts import raster,connected
from pcg.prototype.creative_batches.batch30_c01 import verify_v1 as original_recovery
from pcg.prototype.workshop.rules import cmd,wait_x,ground
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=old.RECIPES;RUNNER_SCRIPT=old.RUNNER_SCRIPT;NATIVE_SCENE=old.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(old.__file__),*old.SOURCE_DEPENDENCIES,HERE/'protocol-v2.json',HERE/'source-recovery-reservation-v1.json',Path(original_recovery.__file__)]
SEED=json.loads((HERE/'source-recovery-reservation-v1.json').read_text())
def candidate(interface=0,control=0):
 c=old.candidate(interface,control);forbidden={(p['grid']['cell'][0]+p['normal'][0],p['grid']['cell'][1]+p['normal'][1])for p in c['block_ports'].values()}
 body=set(map(tuple,SEED['interfaces'][str(interface)]['source_body_cells']))-forbidden;extra=set(map(tuple,SEED['interfaces'][str(interface)]['owner_margin_cells']))-forbidden
 cells=set(map(tuple,c['block_grid']['cells']))|body|extra
 if not connected(cells):raise ValueError('needs_design: recovery reservation disconnected')
 c['block_grid']['cells']=sorted(map(list,cells));c['block_grid']['recovery_scope']='Oldsample-seeded ownership with newrealrearm insideboundary; exactnewfixture stillrequired'
 c['block_reservations']+=old.rows(body);c['id']=c['id'].replace('blockbridge-v1','blockbridge-v2')
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','latches','reward_sites','block_ports','block_grid']})
 c['generation_rule'].update(version=2,source_path=str(Path(__file__).relative_to(HERE.parents[3])))
 c['map_specification']=old.specification(interface,c)
 return c

def purpose(c,r):return old.purpose(c,r)

def recovery(interface,control=0):
 c=candidate(interface,0);source=copy.deepcopy(c['control_plan'])
 rest=lambda:[cmd('axis',value=0),ground(),cmd('wait',8)]
 first_fail=source[:10]+[cmd('wait',8),*rest()]
 rearm=[180,170,180,170][control];slow=[-.25,-.25,-.4,-.4][control]
 stairs=[cmd('axis',value=-1),wait_x(180,-1),*rest(),cmd('axis',value=-1),cmd('jump'),cmd('jump_release',16),cmd('shoot',6,direction=[.2,(.96)**.5]),wait_x(0,-1),*rest(),cmd('axis',value=1),cmd('jump'),cmd('jump_release',16),cmd('shoot',6,direction=[-.4,(.84)**.5]),wait_x(180),*rest(),cmd('axis',value=1),wait_x(300),cmd('axis',value=-1),cmd('jump'),cmd('jump_release',20),cmd('shoot',0,direction=[.3,(.91)**.5]),wait_x(80,-1),*rest(),cmd('axis',value=1),wait_x(rearm),*rest(),cmd('shoot',aim_cell=dict(kind='bell',id='bridge-pair')),cmd('wait',35),cmd('axis',value=slow),wait_x(24,-1),*rest()]
 c['control_plan']=first_fail+stairs+source;c['id']+=f'-recovery-r{control}';c['max_frames']=2600
 c['validation_fixture']=dict(kind='new_block_same_world_failure_retry',control=control,actual_rearm_x=rearm,dock_return_axis=slow,no_module_enrollment=True,no_reset=True)
 return c

def recovery_purpose(c,r):
 q=original_recovery.recovery_purpose(c,r);cells=set(map(tuple,c['block_grid']['cells']));fs=r.get('frames',[]);outside=[f['frame']for f in fs if not raster([f['x']-12,f['y']-18,24,36])<=cells]
 # Require a supported real dock return after the first deliberate floor fall.
 first=q.get('causal',{}).get('first_landing');dock=[f for f in fs if first and f['frame']>first['frame']and f.get('grounded')and abs(f['x']-24)<=8 and abs(f['y']-334)<1]
 if outside:q['reasons'].append('actual_recovery_body_outside_frozen_ownership')
 if not dock:q['reasons'].append('real_return_to_new_A_dock_missing')
 q['causal'].update(outside_body_frames=outside[:12],outside_count=len(outside),actual_A_dock_frames=[f['frame']for f in dock][:12]);q['ok']=not q['reasons'];return q
