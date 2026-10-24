"""Pressure relations are placed from measured shots/flight, never prefab rooms."""
import copy,itertools,math
from ..factory.core.quality import digest
CAPS=['move','jump','shot_recoil']

def identity(c):return digest({k:v for k,v in c.items()if k not in('id','family','synthesis','title','review_alias','module_sha256','factory_id','factory_evidence','recorded_frames','witness','metadata')})
def command(op,after=0,**kw):return dict(op=op,trigger=dict(after=after),**kw)
def probe(family,index,hold,shot,aim,second=None):
 p=[command('axis',value=1),command('jump'),command('jump_release',hold),command('shoot',max(0,shot-hold),direction=aim)]
 if family=='low_arch':p.insert(1,dict(op='wait',trigger=dict(dynamic=dict(kind='actor_x',direction='gte',value=205),timeout=100)))
 if second:p.append(command('shoot',second,direction=[-1,.05]))
 return dict(id=f'{family}-probe{index}',family=family,capabilities=CAPS[:],platforms=[[-120,438,360,60]],spawn=[80,420],goal=[100000,0,100,100],entry_port=[80,420],exit_port=[120,420],world_bounds=[-5000,-5000,15000,15000],control_plan=p,max_frames=160,trace_all=True,one_way_platform_indices=[],hazards=[],thorns=[],saws=[],moving_platforms=[],hooks=[],latches=[],enemies=[])
def proposals():
 out=[]
 for hold,shot,x in itertools.product((8,12),(18,26,34),(-.25,-.5)):
  y=math.sqrt(1-x*x);out.append(probe('bell_lift',len(out),hold,shot,[x,y]))
 for hold,shot,y in itertools.product((6,8),(12,18,24),(0,.08)):
  out.append(probe('low_arch',len(out),hold,shot,[-math.sqrt(1-y*y),y]))
 for hold,shot,delay in itertools.product((8,12),(16,24,32),(18,24)):
  out.append(probe('enemy_refund',len(out),hold,shot,[-.45,math.sqrt(1-.45**2)],delay))
 return out
def shot_events(result):return [e for e in result.get('plains',{}).get('events',[])if e['type']=='shot_origin']
def enemy_materialize(case,result):
 shots=shot_events(result)
 if not shots:return None
 e=shots[0];mx,my=e['muzzle'];dx,dy=e['direction']
 if dy<=0 or my>=422:return None
 x=mx+dx*(422-my)/dy
 if not -85<=x<=212 or abs(x-80)<32:return None
 c=copy.deepcopy(case);c['id']+='-real-enemy';c['enemies']=[dict(id='ammo_sentry',definition='plains_sentry',position=[x,422])]
 return c
def crossing(result,height):
 shots=shot_events(result)
 if not shots:return None
 after=shots[-1]['frame']+5
 for a,b in zip(result['frames'],result['frames'][1:]):
  if b['frame']<=after or b.get('returns',0):continue
  if not b['grounded']and b['vy']>0 and a['y']<=height<b['y']:
   t=(height-a['y'])/(b['y']-a['y']);return a['x']+(b['x']-a['x'])*t,b['frame']
 return None
def materialize(case,result):
 family=case['family'];shots=shot_events(result)
 if result.get('jumps')!=1 or len(shots)!=(2 if family=='enemy_refund'else 1):return []
 out=[]
 for height in ((240,280)if family=='bell_lift'else(420,)):
  cross=crossing(result,height)
  if not cross:continue
  x,frame=cross
  if x<315:continue
  c=copy.deepcopy(case);c['id']+=f'-land{height}';c['trace_all']=False;c['max_frames']=480
  surface=height+18;width=192 if family=='bell_lift'else 176
  c['platforms'] += [[x-width/2,surface,width,72],[-350,620,max(x+700,1600),48]]
  c['goal']=[x-56,surface-42,112,48];c['exit_port']=[x,surface-18]
  c['thorns']=[dict(surface_id='pit_pressure',platform_index=2,face='top',start_offset=0,length=c['platforms'][2][2],depth=20,damage=1,contact_interval=.7)]
  c['control_plan'].append(command('settle',6,target_x=x,deadband=6))
  if family=='bell_lift':
   s=shots[0];bell=[s['muzzle'][i]+s['direction'][i]*85 for i in range(2)]
   c['latches']=[dict(id='lift_bell',bell=bell,gate=[x+28,surface-180,24,180],open_seconds=1.6,prompt='SHOOT DOWN / LIFT + OPEN')]
   c['goal'][0]=x+28;c['goal'][2]=width/2-30;c['exit_port'][0]=x+width/2-26;c['control_plan'][-1]['target_x']=c['exit_port'][0]
  elif family=='low_arch':
   flight=[f for f in result['frames']if not f['grounded']and f['frame']<=frame]
   bottom=min(f['y']-18 for f in flight)-30
   c['platforms'].append([155,bottom-28,max(180,x-155),28]);c['thorns'].append(dict(surface_id='ceiling_pressure',platform_index=3,face='bottom',start_offset=0,length=c['platforms'][3][2],depth=12,damage=1,contact_interval=.7))
   # Separate the flight and timing decisions with a real supported recovery
   # band. The gear still uses original motion/damage, after the landing.
   c['platforms'][1][2]=width/2+320
   c['saws']=[dict(source_id='landing_gear',origin=[x+110,surface-30],travel=[0,-115],radius=16,period=2.4,initial_phase=0)]
   c['exit_port'][0]=x+250;c['goal'][0]=x+214;c['goal'][2]=72
   c['control_plan'] += [dict(op='wait',trigger=dict(state='grounded',timeout=150)),dict(op='wait',trigger=dict(dynamic=dict(kind='saw_phase',id='landing_gear',window=[.5,.55]),timeout=180)),command('settle',target_x=c['exit_port'][0],deadband=6)]
  c['synthesis']=dict(method='decision_relations+actual_flight+original_cells',prefab_modules=0,landing_reference_frame=frame,decision_hypothesis=family)
  out.append(c)
 return out
