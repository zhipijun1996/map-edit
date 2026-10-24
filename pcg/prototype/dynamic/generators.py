"""Parameterized primitive synthesis. Families are design hypotheses, not Module banks."""
from pathlib import Path
import sys,copy,random,math
COMP=Path(__file__).resolve().parents[1]/'composable'
sys.path.insert(0,str(COMP))
from contracts import Grammar,Registry
from synthesis import compile_probe,materialize,command,gated

def actual_word(result):
 out=[];previous='free'
 for f in result.get('frames',[]):
  state=f['traversal_state']
  if state=='hook_hang' and previous!='hook_hang':out.append('hook_hang')
  elif state=='hook_contact_kick' and previous!='hook_contact_kick':out.append('hook_bounce')
  for e in f.get('accepted',[]):
   if e['type'] in ('ground_jump','air_jump','anchor_jump','wall_jump'):out.append(e['type'])
   elif e['type']=='shot':out.append('recoil')
   elif e['type']=='traversal' and e['state']=='wall_kick':out.append('wall_jump')
  previous=state
 return tuple(out)

def dynamic(op,kind,after=0,timeout=600,**kwargs):
 query=kwargs.pop('query',{});return dict(op=op,trigger=dict(dynamic=dict(kind=kind,**query),min_after=after,timeout=timeout),**kwargs)

def ports(case,probe=False):
 c=copy.deepcopy(case);c['entry_port']=c['spawn'][:]
 c['exit_port']=[c['platforms'][0][0]+40,c['platforms'][0][1]-18] if probe else [c['goal'][0]+c['goal'][2]/2,c['goal'][1]+c['goal'][3]/2]
 c['world_bounds']=[-5000,-5000,15000,15000]
 c.setdefault('moving_platforms',[]);c.setdefault('saws',[]);c.setdefault('thorns',[])
 return c

def motion_proposals(seed=740100,count=4,*,families=None,available_capabilities=None,max_depth=12,min_actions=4):
 out=[]
 for family,caps in [('thorn_wall',['move','jump','double_jump','wall_climb']),('hook_saw',['move','jump','double_jump','grapple'])]:
  if families is not None and family not in families:continue
  if available_capabilities is not None and not set(caps)<=set(available_capabilities):continue
  words=Grammar(caps).derive(seed,limit=180,max_depth=max_depth,min_actions=min_actions)
  words=[w for w in words if w.count('wall_jump')>=2 and w.count('air_jump')>=2] if family=='thorn_wall' else [w for w in words if w[0]=='hook_hang' and sum(x.startswith('hook_') for x in w)>=2 and 'air_jump'in w]
  for wi,word in enumerate(words[:count]):
   for vi in range(2):
    layout='alternating' if family=='thorn_wall' and vi%2 else 'same'
    c=compile_probe(word,caps,seed+wi*50+vi+(10000 if family=='hook_saw' else 0),wall_layout=layout)
    if available_capabilities is not None:
     c['proposal_capability_contract']=copy.deepcopy(c['capability_contract'])
     c['capabilities']=list(available_capabilities)
     c['capability_contract']=Registry().snapshot(c['capabilities'])
    c=ports(c,probe=True);c.update(id=f'{family}-p{wi}-v{vi}',family=family,max_frames=900,trace_all=True)
    out.append(c)
 return out

def merge(intervals):
 result=[]
 for lo,hi in sorted(intervals):
  if result and lo<=result[-1][1]:result[-1][1]=max(hi,result[-1][1])
  else:result.append([lo,hi])
 return result

def pressure_floor(c):
 top=max(620,c['spawn'][1]+200,c['goal'][1]+220)
 low=min(c['spawn'][0],c['goal'][0])-380;high=max(c['spawn'][0],c['goal'][0]+c['goal'][2])+380
 index=len(c['platforms']);c['platforms'].append([low,top,high-low,48])
 c['thorns'].append(dict(surface_id='pressure_floor',platform_index=index,face='top',start_offset=0,length=high-low,depth=20,damage=1,contact_interval=.7))

def wall_thorns(c,result):
 fs=result['frames'];wallframes=[f for f in fs if any(e['type']=='wall_jump' for e in f['accepted'])]
 if not wallframes:return
 lo=min(f['y'] for f in wallframes)-40;hi=max(f['y'] for f in wallframes)+40
 for index in c.get('wall_platform_indices',[]):
  p=c['platforms'][index];right=index==c['wall_platform_indices'][0];face='left' if right else 'right';edge=p[0] if right else p[0]+p[2]
  protected=[]
  for f in fs:
   if abs(f['x']-edge)<=32:protected.append([f['y']-27,f['y']+27])
  cursor=max(lo,p[1]);end=min(hi,p[1]+p[3]);holes=[]
  for a,b in merge(protected):
   if a>cursor:holes.append((cursor,min(a,end)))
   cursor=max(cursor,b)
   if cursor>=end:break
  if cursor<end:holes.append((cursor,end))
  for j,(a,b) in enumerate(holes):
   if b-a<26:continue
   length=min(88,b-a-8);start=a+4
   c['thorns'].append(dict(surface_id=f'wall_pressure_{index}_{j}',platform_index=index,face=face,start_offset=start-p[1],length=length,depth=8,damage=1,contact_interval=.7))

def pressure_surfaces(c,frames,clearance=20):
 """Fit real thorn-host Cells beside the whole protected motion tube."""
 def overlap(a,b):return a[0]<b[0]+b[2] and b[0]<a[0]+a[2] and a[1]<b[1]+b[3] and b[1]<a[1]+a[3]
 tubes=[[min(a['x'],b['x'])-20,min(a['y'],b['y'])-26,abs(a['x']-b['x'])+40,abs(a['y']-b['y'])+52] for a,b in zip(frames,frames[1:])]
 added=[];goal=c['goal'];protected_ports=[[c['spawn'][0]-32,c['spawn'][1]-38,64,76],[goal[0]-12,goal[1]-12,goal[2]+24,goal[3]+24]]
 sample=frames[12::7]
 for f in sample:
  if f['grounded'] or f['traversal_state']not in ('free','wall_kick'):continue
  for face in ('top','bottom'):
   x=round(f['x']/4)*4-20
   if face=='top':hazard=[x,f['y']+18+clearance,40,20];host=[x,hazard[1]+20,40,24]
   else:hazard=[x,f['y']-18-clearance-20,40,20];host=[x,hazard[1]-24,40,24]
   if any(overlap(hazard,t) or overlap(host,t) for t in tubes+protected_ports):continue
   if any(overlap(host,p) or overlap(hazard,p) for p in c['platforms']):continue
   if any(abs(x-a[0])+abs(hazard[1]-a[1])<90 for a in added):continue
   index=len(c['platforms']);c['platforms'].append(host);added.append(hazard)
   c['thorns'].append(dict(surface_id='flight_pressure_'+str(len(added)),platform_index=index,face=face,start_offset=0,length=40,depth=20,damage=1,contact_interval=.7))
   break
  if len(added)>=3:break

def turn_into_modules(probes,results):
 modules=[];reasons=[]
 for p,r in zip(probes,results):
  intended=tuple(x for x in p['word'] if x not in ('wall_contact','wall_separate'))
  if r.get('rejected') or not r.get('plan_completed') or actual_word(r)!=intended:
   reasons.append(dict(id=p['id'],reason='motion_word_not_executed',actual=list(actual_word(r))));continue
  c=materialize(p,r,width=160 if p['family']=='thorn_wall' else 112,clearance=44)
  if c is None:reasons.append(dict(id=p['id'],reason='no_unintercepting_receiver'));continue
  c=ports(c);c.update(id=p['id'].replace('-p','-m'),trace_all=False,max_frames=max(450,c['max_frames']))
  c['hazards']=[];c['thorns']=[];pressure_floor(c)
  if p['family']=='thorn_wall':
   wall_thorns(c,r)
   pressure_surfaces(c,r['frames'][:c['synthesis']['landing_probe_frame']+1])
  c['design_hypothesis']='Choose safe contact bands and use restored air actions' if p['family']=='thorn_wall' else 'Wait at a visible safe anchor and cross a moving hazard window'
  c['reference_frames']=r['frames'][:c['synthesis']['landing_probe_frame']+1]
  modules.append(c)
 return modules,reasons

def saw_variants(module,periods=(2.4,3.2)):
 c=copy.deepcopy(module);fs=c.pop('reference_frames');first=c['hooks'][0];goalx=c['goal'][0]+c['goal'][2]/2
 # Choose a point in the actually traversed band, away from safe ports and first hang.
 lo=first['x']+45;hi=goalx-100
 points=[f for f in fs if lo<f['x']<hi and f['traversal_state'] in ('free','hook_pull','hook_kick')]
 if not points:return []
 p=min(points,key=lambda f:abs(f['x']-(first['x']+60)));x=p['x'];near=[f['y'] for f in fs if abs(f['x']-x)<20];y=(min(near)+max(near))/2
 out=[]
 for period in periods:
  for window in (.0,.125,.25,.375,.5,.625,.75,.875):
   v=copy.deepcopy(c);v['saws']=[dict(source_id='crossing_saw',origin=[x,y],travel=[0,110],radius=18,period=period,initial_phase=0,damage=1,contact_interval=.7)]
   # Gate the last departure from a safe first hang. Bounce-only chains wait at entry.
   plan=v['control_plan'];insert=1
   hang_indices=[i for i,s in enumerate(plan) if s.get('trigger',{}).get('state')=='hook_hang' and s['op']=='wait']
   if hang_indices:insert=hang_indices[0]+1
   plan.insert(insert,dynamic('wait','saw_phase',timeout=math.ceil(period*60)+100,query=dict(id='crossing_saw',window=[window,min(.999,window+.075)]),noise_key='dynamic/saw_window'))
   v.update(id=c['id']+f'-s{period}-t{window}',window_start=window)
   out.append(v)
 return out

def ferry_candidates(seed=740800,variants=6):
 rng=random.Random(seed);out=[]
 for vi in range(variants):
  finish=rng.choice((560,620,680));dwell=rng.choice((.8,1.,1.2));travel=rng.choice((1.8,2.2,2.6));width=rng.choice((104,120,136))
  receiver_left=finish+rng.choice((245,265,285));top=438-rng.choice((32,48,64));gx=receiver_left+80
  for method in ('double','recoil'):
   caps=['move','jump']+(['double_jump'] if method=='double' else ['shot_recoil'])
   plan=[command('axis',value=1),dynamic('wait','actor_x',query=dict(direction='gte',value=210),timeout=100),command('axis',value=0),dynamic('wait','platform_phase',query=dict(id='carrier',window=[0,.025]),timeout=math.ceil((travel+dwell)*120)+100),command('axis',value=1),command('jump'),command('jump_release',after=10),dynamic('wait','on_platform',query=dict(id='carrier'),timeout=110),command('axis',value=0),dynamic('wait','platform_phase',query=dict(id='carrier',window=[.5,.525]),timeout=math.ceil((travel+dwell)*120)+100),command('axis',value=1),command('jump'),command('jump_release',after=10)]
   if method=='double':plan += [gated('jump','airborne',min_after=12),command('jump_release',after=12)]
   else:plan += [command('shoot',after=5,direction=[-.84,.54])]
   plan.append(command('settle',after=6,target_x=gx,deadband=6))
   for j,s in enumerate(plan):s.setdefault('noise_key',f'ferry/{j}')
   c=dict(schema='pcg/dynamic-candidate/v3',id=f'ferry-v{vi}-{method}',family='carrier_'+method,capabilities=caps,platforms=[[-120,438,360,60],[receiver_left,top,160,72]],one_way_platform_indices=[],wall_platform_indices=[],spawn=[80,420],goal=[gx-56,top-42,112,48],hooks=[],hazards=[],thorns=[],saws=[],moving_platforms=[dict(platform_id='carrier',start=[300,438],finish=[finish,438],size=[width,20],travel_duration=travel,dwell_duration=dwell,initial_phase=0)],control_plan=plan,max_frames=1300,trace_all=False,settle_frames=6,seed=seed+vi,word=['ground_jump','ground_jump','air_jump'] if method=='double' else ['ground_jump','ground_jump','recoil'],design_hypothesis='Board and coast with zero axis; choose a departure window and use a distinct aerial correction')
   c=ports(c);pressure_floor(c);out.append(c)
 return out

def with_phases(case,phases):
 out=[]
 for phase in phases:
  c=copy.deepcopy(case);c['id']+=f'-phase{phase}'
  for obj in c['moving_platforms']+c['saws']:obj['initial_phase']=phase
  c['initial_phase_label']=phase;out.append(c)
 return out
