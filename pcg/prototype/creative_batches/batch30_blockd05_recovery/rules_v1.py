"""Independent input-only rescue on the exact admitted D05 Block worlds."""
import copy,json
from pathlib import Path
from pcg.prototype.creative_batches.batch30_blockd05 import api_v1 as core
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.map_directed.block_grid.contracts import raster
HERE=Path(__file__).parent
REPO=HERE.parents[3]
PROTOCOL=json.loads((HERE/'protocol-v1.json').read_text())
VERSIONS={int(i):v for i,v in PROTOCOL['source_versions'].items()}
RUNNER_SCRIPT=core.RUNNER_SCRIPT
SOURCE_DEPENDENCIES=[Path(core.__file__),*core.SOURCE_DEPENDENCIES,HERE/'protocol-v1.json']
for version in VERSIONS.values():
 root=REPO/'pcg/map_directed/library/candidates'/version.removeprefix('sha256:')
 SOURCE_DEPENDENCIES += [root/'record.json',root/'cases.json',root/'module.mapnote.json']
PHYSICAL_KEYS=['platforms','moving_platforms','latches','reward_sites','ports','block_grid','block_ports','block_reservations','capabilities','spawn','entry_port','exit_port','goal']

def fixture(interface=0,control=0):
 c=core.layouts(core.RECIPES[0],interface)[0]
 version=VERSIONS[interface];folder=REPO/'pcg/map_directed/library/candidates'/version.removeprefix('sha256:')
 stored=json.loads((folder/'cases.json').read_text())['cases'][0]
 assert all(c[k]==stored[k]for k in PHYSICAL_KEYS),'immutable admitted world drift'
 option=PROTOCOL['controls'][control];x=option['floor_takeoff_x']
 p=copy.deepcopy(c['control_plan'][:9])+[cmd('shoot',direction=[0,1]),cmd('axis',value=1),wait_x(850),cmd('axis',value=0),ground(),cmd('wait',6)]
 p += [settle(x),wait_x(x+7,-1),ground(),cmd('wait',8),cmd('axis',value=0),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[0,1]),cmd('wait',option['turn_left_after_shot']),cmd('axis',value=-1),wait_x(380,-1),cmd('axis',value=0),ground(),cmd('wait',6)]
 p += [settle(-104),wait_x(-97,-1),ground(),cmd('wait',10)]+copy.deepcopy(c['control_plan'])
 c['control_plan']=p;c['id']=f'b30-block-d05-independent-recovery-v1-i{interface}-c{control}';c['max_frames']=2600
 c['validation_fixture']=dict(kind='missed_bell_right_side_original_deck_recovery',module_enrollment=False,source_contentVersion=version,source_case_id=stored['id'],control=control,floor_takeoff_x=x,turn_left_after_shot=option['turn_left_after_shot'],source_physical_geometry_unchanged=True,source_ownership_unchanged=True,scope='Initially parked carrier, unstarted missed shot only')
 return c

def purpose(c,r):
 fs=r.get('frames',[]);why=[];shots=[f for f in fs if any(e.get('type')=='shot'for e in f.get('accepted',[]))];toggles=[e for e in r.get('workshop',{}).get('events',[])if e.get('type')=='carrier_toggle'];first=shots[0]if shots else None
 floor=next((f for f in fs if first and f['frame']>first['frame']and f.get('grounded')and f.get('support_id')=='Platform3'),None)
 toggle=toggles[0]if toggles else None
 parked=[f for f in fs if floor and f['frame']>floor['frame']and f.get('grounded')and f.get('support_id')=='catch-deck'and(not toggle or f['frame']<toggle['frame'])]
 returned=[f for f in fs if parked and f['frame']>parked[0]['frame']and f.get('grounded')and f.get('support_id')=='Platform0'and abs(f['x']+104)<7 and(not toggle or f['frame']<toggle['frame'])]
 if not r.get('ok'):why.append(r.get('reason','unstable'))
 if not floor:why.append('no_actual_wrong_shot_floor_landing')
 if not parked:why.append('no_actual_original_parked_deck_recovery_landing')
 if not returned:why.append('no_actual_internal_A_dock_return_before_retry')
 if not(toggle and toggle.get('running')and toggle.get('airborne')and returned and toggle['frame']>returned[0]['frame']):why.append('initial_wrong_shot_started_carrier_or_missing_actual_retry')
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage')or r.get('returns'):why.append('harm_or_world_reset')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 owned=set(map(tuple,c['block_grid']['cells']));outside=[f['frame']for f in fs if not raster([f['x']-12,f['y']-18,24,36])<=owned]
 if outside:why.append('actual_body_left_frozen_block_reservation')
 retry=None
 if returned:
  tail=copy.deepcopy(r);tail['frames']=[f for f in fs if f['frame']>=returned[0]['frame']]
  tail['workshop']['events']=[e for e in tail['workshop'].get('events',[])if e.get('frame',-1)>=returned[0]['frame']]
  retry=core.purpose(c,tail)
  if not retry['ok']:why.append('actual_nominal_retry_catch_or_reward_failed')
 return dict(ok=not why,reasons=why,causal=dict(first_wrong_shot_frame=first['frame']if first else None,actual_floor_frame=floor['frame']if floor else None,parked_deck_recovery_frames=[f['frame']for f in parked],actual_A_dock_frames=[f['frame']for f in returned],first_carrier_toggle=toggle,retry_core=retry,unreserved_body_frames=outside[:16],source_contentVersion=c['validation_fixture']['source_contentVersion']),behavior={k:r.get(k)for k in ['shots','jumps','ticks']})
