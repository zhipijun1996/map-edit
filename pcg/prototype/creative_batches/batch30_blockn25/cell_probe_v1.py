"""Eight real original-Motor/AnimatableBody Cell cases, not Module admission."""
import json,math
from pathlib import Path
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,ground
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent
TRAJECTORY=json.loads((HERE/'trajectory-v1.json').read_text())
POINTS=TRAJECTORY['points']
DOC=json.loads((HERE/'standard-trajectory-v1.json').read_text())
SOURCE_DEPENDENCIES=[HERE/n for n in ['protocol-v1.json','loop_definition_v1.gd','install_v1.gd','runner_v1.gd','trajectory-v1.json','roundtrip_v1.mjs','standard-trajectory-v1.json']]+[ROOT/'creative-production/batch30/block-next-ideas-v5.json',ROOT/'creative-production/batch30/protocol-map-block-v10.json']

def sample(points,u):
 lengths=[math.dist(a,b)for a,b in zip(points,points[1:])];remaining=(u%1)*sum(lengths)
 for i,n in enumerate(lengths):
  if remaining<=n or i==len(lengths)-1:return[points[i][j]+(points[i+1][j]-points[i][j])*remaining/n for j in range(2)]
  remaining-=n
 raise AssertionError('closedfinitepolyline')

def cases():
 cs=[]
 for k in range(8):
  phase=[0,.25,.5,.75,0,.5,0,0][k];period=6 if k==4 else 8;pose=sample(POINTS,phase)
  c=base(f'b31-n25-cell-v1-{k}');c['platforms']=[[-512,1200,2304,64]];c['capabilities']=['move','jump','shot_recoil'];c['spawn']=[pose[0],pose[1]-30];c['entry_port']=[-400,1182];c['exit_port']=[-350,1182];c['goal']=[-512,-512,2304,1792];c['world_bounds']=[-640,-512,2560,2048]
  c['moving_platforms']=[dict(platform_id='loop-deck',trajectory_kind='closed_polyline_loop/v1',start=POINTS[0],finish=POINTS[-1],size=[160,24],travel_duration=period,dwell_duration=0,loop_period=period,loop_points=POINTS,initial_phase=phase)]
  c.update(test_kind=k,fixture_scope='Carrierunitmovinginitialspawn; staticmarkersnotportingressproof',max_frames=(period*2+2)*60,trace_all=True,control_plan=[cmd('axis',value=0)])
  if k==1:c['cell_pause_probe']=True
  if k==5:
   c['max_frames']=480;c['control_plan']+=[ground(),cmd('wait',30),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[0,1]),cmd('wait',60)]
  if k==6:
   c['platforms'].append([960,488,320,24]);c['max_frames']=240;c['control_plan']+=[ground(),cmd('wait',6),cmd('jump'),cmd('jump_release',20),cmd('wait',90)]
  if k==7:c['trajectory_document']=DOC['document']
  cs.append(c)
 return cs

def check(c,r):
 fs=r.get('frames',[]);why=[];audit=r.get('n25',{}).get('definition_audit',{});kind=c['test_kind'];period=c['moving_platforms'][0]['loop_period'];phase=c['moving_platforms'][0]['initial_phase'];length=sum(math.dist(a,b)for a,b in zip(POINTS,POINTS[1:]));speed=length/period
 if not fs:why.append('no_real_actor_frames')
 if not audit.get('valid')or audit.get('points')!=17 or audit.get('period')!=period or audit.get('period_position_error',999)>.002 or audit.get('envelope')!=[368,340,800,472]or not all(x['rejected']for x in audit.get('malformed',[])):why.append('definition_or_malformed_audit_failed')
 if r.get('hp')!=5 or r.get('returns')or any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples'])or r.get('plains',{}).get('player_damage'):why.append('original_actor_contract_violation')
 max_error=0.;max_delta=0.;last=None;previous_phase=None;wraps=0;sup=[];margins=[];max_unsupported=0;streak=0;boarded=False;phase_bins=set()
 for f in fs:
  platforms=f.get('n25',{}).get('platforms',[])
  if len(platforms)!=1:why.append('missing_real_typed_loop_carrier');continue
  p=platforms[0];expected=sample(POINTS,f['module_clock']/period+phase);max_error=max(max_error,p['position_error'],math.dist(p['actual_position'],expected))
  if abs(p['rotation'])>1e-6 or p['bell_controlled']:why.append('unexpected_rotation_or_clock_control')
  if last is not None:max_delta=max(max_delta,math.dist(last,p['actual_position']))
  last=p['actual_position'];actual_phase=f['moving_platforms'][0]['phase']
  if previous_phase is not None and previous_phase>.9 and actual_phase<.1:wraps+=1
  previous_phase=actual_phase
  supported=f.get('grounded')and f.get('support_id')=='loop-deck'
  if supported:sup.append(f);boarded=True;phase_bins.add(int(actual_phase*16)%16);streak=0
  elif boarded:streak+=1;max_unsupported=max(max_unsupported,streak)
  if boarded:margins.append(80-abs(f['x']-p['actual_position'][0])-12)
 if max_error>.002:why.append('actual_position_differs_from_closed_JS_arc_length_path')
 if max_delta>speed/60+.1:why.append('actual_loop_pose_discontinuity')
 if kind in [0,1,2,3,4,7]:
  if len(sup)/max(1,len(fs))<.9:why.append('insufficient_real_neutral_two_loop_carriage')
  if max_unsupported>6:why.append('corner_loss_exceeds_preregistered6frames')
  if not margins or min(margins)<8:why.append('standing_wholebody_deck_margin_below8px')
  if len(phase_bins)!=16 or wraps<2 or not sup or sup[-1]['module_clock']-sup[0]['module_clock']<period*2:why.append('two_full_loop_phase_coverage_missing')
 if kind==1:
  receipts=r.get('n25',{}).get('pause_receipts',[])
  if len(receipts)!=1 or not receipts[0].get('unchanged'):why.append('actual_pause_resume_not_frozen')
 if kind==5:
  shots=[f for f in fs if any(e.get('type')=='shot'for e in f.get('accepted',[]))];jump=[f for f in fs if any(e.get('type')=='ground_jump'for e in f.get('accepted',[]))]
  shot=shots[0]if shots else None;landing=next((f for f in fs if shot and f['frame']>shot['frame']and f.get('grounded')),None)
  if not jump or not shot or shot.get('grounded')or shot.get('shot_charges')!=0 or not landing or landing.get('shot_charges')!=1:why.append('actual_jump_airshot_ground_resource_chain_missing')
  if shot and landing and any(f.get('shot_charges')!=0 for f in fs if shot['frame']<=f['frame']<landing['frame']):why.append('unearned_air_resource_restore')
 if kind==6:
  head=[f for f in fs if any(t['collider']=='Platform1'and t['normal'][1]>.7 for t in f.get('n25',{}).get('contacts',[]))]
  if not head or not any(f['n25']['normal_velocity'][1]>=-.01 for f in head):why.append('original_ceiling_collision_not_observed')
  if any(f['x']+12>960 and f['x']-12<1280 and f['y']+18>488 and f['y']-18<512 for f in fs):why.append('actual_body_penetrated_ceiling')
 if kind==7 and not r.get('n25',{}).get('from_standard_document'):why.append('typed_standard_document_reload_missing')
 return dict(ok=not why,reasons=sorted(set(why)),raw_engine_reason=r.get('reason'),note='UnitchecksnotModuleadmission/portqualification',definition_audit=audit,real_frames=len(fs),supported_frames=len(sup),supported_rate=len(sup)/max(1,len(fs)),max_postboard_unsupported_frames=max_unsupported,minimum_wholebody_horizontal_margin=min(margins,default=None),phase_bins=sorted(phase_bins),actual_loop_wraps=wraps,max_expected_position_error=max_error,max_actual_step=max_delta,allowed_max_step=speed/60+.1,pause_receipts=r.get('n25',{}).get('pause_receipts',[]),shots=r.get('shots'),jumps=r.get('jumps'))

def main():
 e=WorkshopEngine(ROOT/'results/workshop-batch30-blockn25-cell-v1',extra_sources=[Path(__file__),*SOURCE_DEPENDENCIES],runner_script=HERE/'runner_v1.gd');rows=[]
 for c,r,ev in e.run(cases(),'first-eight-cell'):
  row=dict(id=c['id'],check=check(c,r),evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,passed=sum(x['check']['ok']for x in rows),rows=rows,new_modules=0,new_families=0,death_transaction='UNKNOWN',Map_shared_consumer='UNSUPPORTED_UNTIL_INSTALL'))
if __name__=='__main__':main()
