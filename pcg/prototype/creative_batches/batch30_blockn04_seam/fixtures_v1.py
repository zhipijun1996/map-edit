"""Exact fixed two-module union and real-input join; not a Map generator."""
import copy,json
from pathlib import Path
from . import audit_v1 as audit
from pcg.prototype.creative_batches.batch30_blockn04 import api_v1 as original_n04
from pcg.prototype.creative_batches.batch30_seams.fixtures_v1 import translated,rectangle,point
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.map_directed.block_grid.contracts import declare,validate,raster
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RUNNER_SCRIPT=HERE/'runner_v1.gd'
NATIVE_SCENE=HERE/'main_v1.tscn'
SOURCE_DEPENDENCIES=[Path(audit.__file__),Path(original_n04.__file__),*original_n04.SOURCE_DEPENDENCIES,HERE/'protocol-v1.json',HERE/'static-placement-v1.json',HERE/'observe_v1.gd',HERE/'runner_v1.gd',HERE/'main_v1.gd',HERE/'main_v1.tscn',Path(translated.__code__.co_filename)]
for n in ['record.json','cases.json','module.mapnote.json']:SOURCE_DEPENDENCIES.append(audit.ROOT/'map_directed/library/candidates'/audit.VERSION/n)

def scoped(c,label):
 c=copy.deepcopy(c)
 for l in c['latches']:l['id']=label+'/'+l['id']
 for s in c['reward_sites']:s['id']=label+'/'+s['id']
 for q in c['control_plan']:
  if q.get('aim_cell',{}).get('id')=='return-catch':q['aim_cell']['id']=label+'/return-catch'
 c['required_rewards']=[label+'/'+x for x in c['required_rewards']]
 return c

def translated_grid(c,delta):
 c=copy.deepcopy(c);dx,dy=[int(v/128)for v in delta]
 c['block_grid']['cells']=[[x+dx,y+dy]for x,y in c['block_grid']['cells']]
 c['block_reservations']=[rectangle(r,delta)for r in c['block_reservations']]
 for p in c['block_ports'].values():
  p['position']=point(p['position'],delta);p['stagingPosition']=point(p['stagingPosition'],delta)
  p['grid']['cell']=[p['grid']['cell'][0]+dx,p['grid']['cell'][1]+dy];p['grid']['stagingPosition']=point(p['grid']['stagingPosition'],delta);p['aperture']=rectangle(p['aperture'],delta)
 c['block_grid']['port_bindings']=[dict(port_id=k,**copy.deepcopy(p['grid']))for k,p in c['block_ports'].items()]
 return c

def fixture(control=0):
 if control not in [0,1]:raise ValueError('outside frozen seam controller domain')
 local,source_binding=audit.source();left,placed,placement=audit.audit()
 assert placement['accepted']
 left=scoped(left,'left');right=scoped(translated_grid(placed,audit.DELTA),'right')
 c=copy.deepcopy(left)
 for k in ['factory_id','factory_evidence','recorded_frames','module_sha256','validation_summary','review_alias','noise','map_specification']:c.pop(k,None)
 n=len(left['platforms']);c['platforms']=copy.deepcopy(left['platforms']+right['platforms'])
 for field in ['latches','reward_sites','moving_platforms']:c[field]=copy.deepcopy(left[field]+right[field])
 c['ports']=[];ports={}
 for label,part,keys,offset in [('L',left,['A','B','D'],0),('R',right,['B','C','D'],n)]:
  for key in keys:
   raw=copy.deepcopy(next(p for p in part['ports']if p['id']==key));raw['id']=label+'-'+key;raw['support_index']+=offset;c['ports'].append(raw)
   p=copy.deepcopy(part['block_ports'][key]);p['id']=raw['id'];ports[raw['id']]=p
 c['spawn']=left['spawn'][:];c['entry_port']=left['entry_port'][:];c['exit_port']=right['exit_port'][:];x,y=c['exit_port'];c['goal']=[x-25,y-4,50,8];c['settle_frames']=12
 c['required_rewards']=['left/high-C','right/high-C'];c['expected_reward']=24;c['max_frames']=3000
 c['route_spec']=dict(id='exact-N04-left-C-right-A-C',from_port='L-A',to_port='R-C',role='fixture',via_ports=[],required_rewards=c['required_rewards'])
 if control==0:
  first=copy.deepcopy(left['control_plan'][:-3])+[cmd('axis',value=1),wait_x(1253),cmd('axis',value=0),ground(),cmd('wait',20)]
  bridge=[cmd('axis',value=1),wait_x(1301),cmd('axis',value=0),ground(),cmd('wait',20)]
  second=copy.deepcopy(right['control_plan'])
 else:
  first=copy.deepcopy(left['control_plan'])+[cmd('wait',20)]
  bridge=[settle(1304),wait_x(1297),ground(),cmd('wait',20)]
  second=copy.deepcopy(right['control_plan'])
  for index,target in [(0,1920),(2,1920),(10,2140),(12,2140),(15,2536)]:second[index]=settle(target)
  second[1]=wait_x(1913);second[11]=wait_x(2133)
 c['control_plan']=first+bridge+second
 c['world_bounds']=[-1200,-1384,5280,2784]
 cells=set(map(tuple,left['block_grid']['cells']))|set(map(tuple,right['block_grid']['cells']))
 reservations=left['block_reservations']+right['block_reservations']
 projected=declare(dict(case=c,ports=ports,functional_roles=['exact_continuity_fixture'],action_clearance=reservations),cells)
 assert not validate(projected),validate(projected)
 c['block_grid']=projected['block_grid'];c['block_ports']=ports;c['block_reservations']=reservations
 c['family']='exact-N04-block-continuity';c['id']=f'b30-N04-exact-seam-v1-c{control}';c['native_scene']=str(NATIVE_SCENE)
 c['seam_specimen']=dict(source_contentVersion='sha256:'+audit.VERSION,source_binding=source_binding,source_local_case=local,source_left_case=left,source_right_case=right,source_right_raw_case=placed,translation_right=audit.DELTA,seam_anchor=[1280,320],left_dock=[1256,334],right_dock=[1304,334],final_dock=[2536,-50],right_platform_offset=n,control=control,added_platforms=0,removed_platforms=0,all_original_entities_preserved=True,placement_audit=placement,internal_connection=dict(from_component='left',from_port='C',to_component='right',to_port='A'),external_ports=list(ports))
 c['seam_specimen']['fixture_version']='sha256:'+digest(dict(source='sha256:'+audit.VERSION,translation=audit.DELTA,platforms=c['platforms'],latches=c['latches'],rewards=c['reward_sites'],owned=c['block_grid'],control=c['control_plan']))
 assert c['platforms']==left['platforms']+right['platforms']
 return c

def stable_groups(fs,target,support):
 groups=[];run=[]
 for f in fs:
  good=f.get('grounded')and f.get('support_id')==support and abs(f['x']-target[0])<=7 and abs(f['y']-target[1])<=1 and abs(f.get('vx',999))<=1
  if good:run.append(f)
  else:
   if len(run)>=12:groups.append(run)
   run=[]
 if len(run)>=12:groups.append(run)
 return groups

def local_result(raw,label,delta,first,last,offset):
 r=copy.deepcopy(raw);r['frames']=[f for f in r['frames']if first<=f['frame']<=last]
 for f in r['frames']:
  f['x']-=delta[0];f['y']-=delta[1];f['n04']=f.get('n04_seam',{}).get(label+'/return-catch',{})
  if f.get('support_id')==label+'_return_catch_gate':f['support_id']='n04_return_catch_gate'
  elif str(f.get('support_id','')).startswith('Platform'):
   index=int(f['support_id'].removeprefix('Platform'))
   if index>=offset:f['support_id']='Platform'+str(index-offset)
 r['plains']['events']=[dict(e,id='return-catch')if e.get('id')==label+'/return-catch'else e for e in r.get('plains',{}).get('events',[])if first<=e.get('frame',-1)<=last and('id'not in e or e.get('id')==label+'/return-catch')]
 events=[dict(e,id=e['id'].removeprefix(label+'/'))for e in r.get('workshop',{}).get('events',[])if str(e.get('id','')).startswith(label+'/')and first<=e.get('frame',-1)<=last]
 r['workshop']['events']=events;r['workshop']['coins']=sum(e.get('amount',0)for e in events if e.get('type')=='chest_claim'and e.get('accepted'))
 return r

def purpose(c,raw):
 from pcg.prototype.creative_batches.junctions.landing_buffer_v1 import classify
 r,interpretation=classify(c,raw);fs=r.get('frames',[]);meta=c['seam_specimen'];why=[]
 left_groups=stable_groups(fs,[1256,334],'Platform3');right_groups=stable_groups(fs,[1304,334],'Platform7')
 left_group=left_groups[0]if left_groups else[];right_group=right_groups[0]if right_groups else[]
 if not left_group:why.append('left_original_C_dock_not_supported_stable12')
 if not right_group:why.append('right_original_A_dock_not_supported_stable12')
 left_end=left_group[-1]['frame']if left_group else -1;right_start=right_group[0]['frame']if right_group else 999999
 l=local_result(r,'left',[0,0],0,left_end,0);rr=local_result(r,'right',audit.DELTA,right_start,999999,7)
 ql=original_n04.purpose(meta['source_local_case'],l);qr=original_n04.purpose(meta['source_local_case'],rr)
 if not ql['ok']:why += ['left/'+x for x in ql['reasons']]
 if not qr['ok']:why += ['right/'+x for x in qr['reasons']]
 cross=[f for f in fs if left_end<f['frame']<right_start and f['x']-12<1280<f['x']+12]
 complete=[f for f in fs if f['frame']>left_end and f['x']-12>=1280 and f['x']<=1311 and f.get('grounded')and abs(f['y']-334)<=1]
 if not cross or not complete or any(not f.get('grounded')or abs(f['y']-334)>1 for f in cross):why.append('full_body_supported_seam_crossing_missing')
 owned=set(map(tuple,c['block_grid']['cells']));outside=[f['frame']for f in fs if not raster([f['x']-12,f['y']-18,24,36])<=owned]
 if outside:why.append('actual_body_outside_exact_union_ownership')
 claims=[e for e in r.get('workshop',{}).get('events',[])if e.get('type')=='chest_claim'and e.get('accepted')]
 if sorted(e['id']for e in claims)!=sorted(c['required_rewards'])or r.get('workshop',{}).get('coins')!=24:why.append('two_actual_unique_C_chests_not_exact24')
 if not r.get('ok'):why.append(r.get('reason','not_stable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage')or r.get('returns'):why.append('harm_reset_or_teleport')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 initial=fs[0].get('n04_seam',{})if fs else{}
 if any(initial.get(k,{}).get('open',True)or initial.get(k,{}).get('collision_layer')!=1 for k in ['left/return-catch','right/return-catch']):why.append('both_original_gates_not_initially_closed')
 sampled=[{k:f.get(k)for k in ['frame','x','y','vx','grounded','support_id','shot_charges','shot_cooldown','jumps_used','energy','hp']}for f in right_group[:12]]
 return dict(ok=not why,reasons=why,causal=dict(left_core=ql,right_core=qr,left_dock_stable_frames=len(left_group),right_dock_stable_frames=len(right_group),seam_straddling_frames=[f['frame']for f in cross],complete_body_crossing_frames=[f['frame']for f in complete],observed_right_ingress=sampled,claims=claims,outside_body_frames=outside[:16],single_world=True,added_platforms=0,removed_platforms=0,source_geometry_exact_union=True,observer_interpretation=interpretation),behavior={k:r.get(k)for k in ['shots','jumps','ticks']})
