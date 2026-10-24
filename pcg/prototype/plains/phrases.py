"""Grow generated recoil challenges from real landing states, not authored rooms."""
import copy,itertools
from .synthesis import command,identity,crossing,shot_events

def extend_probe(base,direction,hold,delay,index):
 c=copy.deepcopy(base);c['id']=f'phrase-flight-{index}';c['family']='bell_arch_forward'if direction>0 else'bell_arch_return'
 p=c['platforms'][1];launch=p[0]+p[2]-28 if direction>0 else p[0]+28
 c['goal']=[100000,0,100,100];c['max_frames']=420;c['trace_all']=True
 c['control_plan'] += [dict(op='wait',trigger=dict(state='grounded',timeout=180)),command('settle',target_x=launch,deadband=4),dict(op='wait',trigger=dict(dynamic=dict(kind='actor_x',direction='gte'if direction>0 else'lte',value=launch-direction*5),timeout=120)),command('settle',target_x=direction*10000,deadband=4),command('jump'),command('jump_release',hold),command('shoot',delay-hold,direction=[-direction,0]),command('settle',target_x=direction*10000,deadband=4)]
 c['phrase_parameters']=dict(direction=direction,hold=hold,shot_delay=delay,launch=launch,parent_uid=identity(base),height=base['exit_port'][1])
 return c

def materialize_phrase(probe,result):
 shots=shot_events(result)
 if result.get('jumps')!=2 or len(shots)!=2:return None
 params=probe['phrase_parameters'];direction=params['direction'];height=params['height'];cross=crossing(result,height)
 if not cross:return None
 x,frame=cross
 if direction*(x-params['launch'])<150:return None
 c=copy.deepcopy(probe);c['id']+='-cells';c['trace_all']=False;c['max_frames']=720
 surface=height+18;left=x-96 if direction>0 else x-320
 receiver=len(c['platforms']);c['platforms'].append([left,surface,416,72])
 # Compute headroom from the actual second jump/shot segment. The original
 # first challenge must still work with this new geometry present (retested).
 second_jump=[f['frame']for f in result['frames']if any(a['type']=='ground_jump'for a in f.get('accepted',[]))][-1]
 flight=[f for f in result['frames']if second_jump<=f['frame']<=frame and not f['grounded']]
 bottom=min(f['y']-18 for f in flight)-32;roof_left=min(x,params['launch'])-25;roof_right=max(x,params['launch'])+25;roof=len(c['platforms']);c['platforms'].append([roof_left,bottom-28,roof_right-roof_left,28])
 c['thorns'].append(dict(surface_id='second_ceiling',platform_index=roof,face='bottom',start_offset=0,length=roof_right-roof_left,depth=12,damage=1,contact_interval=.7))
 c['saws']=[dict(source_id='phrase_gear',origin=[x+direction*110,surface-30],travel=[0,-115],radius=16,period=2.4,initial_phase=0)]
 c['exit_port']=[x+direction*250,height];c['exit_normal']=[direction,0];c['entry_normal']=[-1,0];c['goal']=[c['exit_port'][0]-36,surface-42,72,48]
 # A supported pause is a distinct stage between flight and gear timing.
 c['control_plan'][-1]=command('settle',target_x=x,deadband=6)
 c['control_plan'] += [dict(op='wait',trigger=dict(state='grounded',timeout=180)),dict(op='wait',trigger=dict(dynamic=dict(kind='saw_phase',id='phrase_gear',window=[.5,.55]),timeout=180)),command('settle',target_x=c['exit_port'][0],deadband=6)]
 c['challenge_requirements']=dict(min_ground_jumps=2,min_shots=2,min_landings=2,min_reversals=int(direction<0),min_gear_crossings=1)
 # New cells may not invalidate the already executed prefix. This is a
 # sampled geometric filter, followed by whole-episode real physics again.
 first_land=next((b['frame']for a,b in zip(result['frames'],result['frames'][1:])if not a['grounded']and b['grounded']),None)
 if first_land is None:return None
 prefix=[f for f in result['frames']if f['frame']<=first_land]
 def overlap(r,f):return r[0]<f['x']+12 and r[0]+r[2]>f['x']-12 and r[1]<f['y']+18 and r[1]+r[3]>f['y']-18
 if any(overlap(c['platforms'][i],f)for i in(receiver,roof)for f in prefix):return None
 c['synthesis']=dict(prefix_filter='sampled_prefix_body_overlap_then_whole_episode_physics',method='grow_second_flight_from_generated_landing',prefab_modules=0,landing_reference_frame=frame,parent_uid=params['parent_uid'],new_cells=['receiver','ceiling_thorns','phase_gear'],direction=direction)
 return c

def enemy_bell_gear(base,result,index,bell_position=None):
 shots=shot_events(result)
 if len(shots)!=2:return None
 c=copy.deepcopy(base);c['id']=f'enemy-bell-gear-{index}';c['family']='enemy_bell_gear';c['trace_all']=False;c['max_frames']=600
 p=c['platforms'][1];x=p[0]+p[2]/2;surface=p[1];p[2]=p[2]/2+320
 s=shots[1];bell=bell_position if bell_position is not None else[s['muzzle'][i]+s['direction'][i]*75 for i in range(2)]
 c['latches']=[dict(id='refund_bell',bell=bell,gate=[x+185,surface-180,24,180],open_seconds=4.,prompt='HIT ENEMY / REFILL / AIM BELL')]
 c['saws']=[dict(source_id='phrase_gear',origin=[x+110,surface-30],travel=[0,-115],radius=16,period=2.4,initial_phase=0)]
 c['exit_port']=[x+250,surface-18];c['goal']=[x+214,surface-42,72,48];c['entry_normal']=[-1,0];c['exit_normal']=[1,0]
 c['control_plan'] += [dict(op='wait',trigger=dict(state='grounded',timeout=180)),dict(op='wait',trigger=dict(dynamic=dict(kind='saw_phase',id='phrase_gear',window=[.5,.55]),timeout=180)),command('settle',target_x=c['exit_port'][0],deadband=6)]
 c['challenge_requirements']=dict(min_ground_jumps=1,min_shots=2,min_landings=1,min_reversals=0,min_gear_crossings=1)
 c['synthesis']=dict(method='target_switch_after_actual_air_hit_refund',prefab_modules=0,parent_uid=identity(base),new_cells=['second_shot_bell','gate','phase_gear'],bell_reference_shot=2)
 return c

def motion_proposals(bases):
 # Fixed Cartesian budget. Selection is by generated content, never holdout luck.
 bells=sorted((e for e in bases if e['case']['family']=='bell_lift'),key=lambda e:identity(e['case']))[:2]
 return [extend_probe(e['case'],direction,hold,delay,i)for i,(e,direction,hold,delay)in enumerate(itertools.product(bells,(1,-1),(6,8),(12,18)))]
