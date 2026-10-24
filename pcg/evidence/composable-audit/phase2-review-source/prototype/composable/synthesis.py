"""Compile typed action words into input policies and parameterized primitive Cells."""
from __future__ import annotations
import copy,random,math,json,hashlib
from contracts import Registry,Grammar

def command(op,after=0,**kwargs):return dict(op=op,trigger=dict(after=after),**kwargs)
def gated(op,state,min_after=0,timeout=100,**kwargs):return dict(op=op,trigger=dict(state=state,min_after=min_after,timeout=timeout),**kwargs)

def compile_probe(word,caps,seed):
    caps=Registry().resolve(list(caps));Grammar(caps).validate_word(word)
    r=random.Random(seed);spawn=[80,420];platforms=[[-120,438,260,60]];hooks=[];wall_indices=[]
    hooks_before_wall=word[:word.index('wall_contact')].count('hook_hang')+word[:word.index('wall_contact')].count('hook_bounce') if 'wall_contact'in word else 0
    if 'wall_contact'in word:
        wall_x=195+145*hooks_before_wall
        wall_y=170-100*hooks_before_wall
        platforms.append([wall_x,wall_y,32,650]);wall_indices=[1]
    plan=[command('axis',value=1. if 'move'in caps else 0.)]
    # Hook affordances are individual anchors, positioned from relational offsets.
    hook_count=0;travel=1
    for index,op in enumerate(word):
        wait=r.randint(8,16)
        if op=='ground_jump':
            plan += [gated('jump','grounded',min_after=5),command('jump_release',after=r.randint(8,12))]
        elif op=='air_jump':
            plan += [gated('jump','airborne',min_after=wait+4),command('jump_release',after=r.randint(8,12))]
        elif op=='anchor_jump':
            plan += [gated('jump','hook_hang',min_after=r.randint(2,5)),command('jump_release',after=r.randint(8,12))]
        elif op=='recoil':
            theta=r.uniform(.28,1.08)
            plan.append(command('shoot',after=wait,direction=[-travel*math.cos(theta),math.sin(theta)]))
        elif op.startswith('hook_'):
            x=(210+hook_count*r.randint(125,155) if travel>0 else platforms[1][0]-130-(hook_count-hooks_before_wall)*110) if 'move'in caps else 80
            y=230-hook_count*r.randint(65,100)+r.randint(-12,12)
            hooks.append(dict(x=x,y=y,kind='hang' if op=='hook_hang' else 'bounce'))
            hook_count+=1
            plan += [command('grapple',after=wait,aim_target=[x,y])]
            if op=='hook_hang':plan.append(gated('wait','hook_hang',min_after=1,timeout=85))
            else:plan.append(gated('wait','free',min_after=25,timeout=95))
        elif op=='wall_contact':plan.append(gated('wait','wall_attach',min_after=3,timeout=110))
        elif op=='wall_jump':
            plan.append(gated('jump','wall_attach',min_after=r.randint(2,5)))
            travel=-1
            # Keep pressure into the wall on the jump frame; changing axis in the
            # same tick detaches before Traversal consumes the jump request.
            plan.append(command('axis',after=1,value=-1.))
            plan.append(command('jump_release',after=8))
    for i,c in enumerate(plan):c['noise_key']=f'word/{i}'
    case=dict(schema='pcg/candidate-module/v2',id=f'probe-{seed}',capabilities=sorted(caps),capability_contract=Registry().snapshot(caps),seed=seed,word=list(word),
        platforms=platforms,hazards=[],wall_platform_indices=wall_indices,hooks=hooks,spawn=spawn,goal=[5000,-500,40,40],
        control_plan=plan,max_frames=360,trace_all=True,settle_frames=6,
        synthesis=dict(method='typed_action_graph+real_motion',authored_modules=0))
    return case

def last_mechanic_frame(result):
    xs=[c['frame'] for c in result.get('fired_commands',[]) if c['op'] not in ('axis','settle','wait','jump_release')]
    return max(xs,default=0)

def materialize(probe,result,width=144,clearance=40):
    fs=result.get('frames',[])
    if not fs or result.get('plan_error') or not result.get('plan_completed'):return None
    last=last_mechanic_frame(result)
    # Receive the real descending trajectory shortly after the whole action word.
    choices=[]
    for i,f in enumerate(fs):
        if not last+8<=i<=last+65:continue
        if f['vy']<130 or f['traversal_state']!='free' or f['grounded']:continue
        if 'move'in probe['capabilities'] and abs(f['x']-probe['spawn'][0])<150 and probe['spawn'][1]-f['y']<100:continue
        if f['y']>probe['spawn'][1]+100:continue
        # A wall is an actual blocking Cell; receiving support cannot live inside it.
        if any(p[0]-24<=f['x']<=p[0]+p[2]+24 and p[1]-20<=f['y']<=p[1]+p[3]+20 for j,p in enumerate(probe['platforms']) if j in probe.get('wall_platform_indices',[])):continue
        choices.append((i,f))
    if not choices:return None
    i,f=choices[min(7,len(choices)-1)]
    x=round(f['x']/4)*4;y=round(f['y']/4)*4
    c=copy.deepcopy(probe);c['id']=f'module-{probe["seed"]}-w{width}-c{clearance}'
    left=x-width/2;top=y+18
    launch=probe['platforms'][0]
    if left<launch[0]+launch[2]+24 and left+width>launch[0]-24 and top>launch[1]-64:return None
    landing_index=len(c['platforms']);c['platforms'].append([left,top,width,72])
    # One-way receiver prevents invalidating ascent where the projected path revisits x.
    c['one_way_platform_indices']=[landing_index]
    c['goal']=[left+24,y-24,width-48,48]
    c['control_plan'].append(command('settle',after=5,deadband=6,target_x=x,noise_key='exit/settle'))
    c['max_frames']=min(480,i+100);c['trace_all']=False
    # Protect the complete body tube on every visit to each candidate x-band.
    pts=fs[:i+1]
    if 'move'in probe['capabilities']:
        floor_y=max(600,round(max(v['y'] for v in pts)+160))
        c['hazards']=[[140,floor_y,max(80,left+width-140),24]]
        lo=probe['platforms'][0][0]+probe['platforms'][0][2]+48;hi=left-50
        if hi>lo:
            for j,frac in enumerate((.25,.60)):
                bx=lo+(hi-lo)*frac
                band=[v['y'] for v in pts if abs(v['x']-bx)<=36]
                if not band:continue
                by=min(band)-18-clearance-32 if j%2==0 else max(band)+18+clearance
                rect=[round(bx-14),round(by),28,32]
                if any(abs(h['x']-bx)<48 and abs(h['y']-by)<64 for h in c['hooks']):continue
                if any(jj in c.get('wall_platform_indices',[]) and abs(p[0]-bx)<60 for jj,p in enumerate(c['platforms'])):continue
                c['platforms'].append(rect)
                c['hazards'].append([rect[0],rect[1]+(26 if j%2==0 else -6),28,12])
    c['synthesis'].update(landing_width=width,clearance=clearance,landing_probe_frame=i,landing_center=[x,y],policy='state_gates+router_feedback')
    return c

def actual_word(result):
    out=[];previous_state='free'
    for f in result.get('frames',[]):
        state=f.get('traversal_state','free')
        if state=='hook_hang' and previous_state!='hook_hang':out.append('hook_hang')
        elif state=='hook_contact_kick' and previous_state!='hook_contact_kick':out.append('hook_bounce')
        for e in f.get('accepted',[]):
            typ=e['type']
            if typ in ('ground_jump','air_jump','anchor_jump','wall_jump'):out.append(typ)
            elif typ=='shot':out.append('recoil')
        previous_state=state
    return tuple(out)

def behavioral_descriptor(result):
    w=actual_word(result)
    returns=sum(1 for a,b in zip(result.get('frames',[]),result.get('frames',[])[1:]) if a['vx']>5 and b['vx']< -5)
    return (w.count('air_jump'),w.count('wall_jump'),min(3,w.count('hook_hang')+w.count('hook_bounce')),w.count('recoil'),min(3,returns))

def fingerprint(case):
    sx,sy=case['spawn']
    arr=[]
    for key in ('platforms','hazards'):
        arr.append(sorted([round((x-sx)/8),round((y-sy)/8),round(w/8),round(h/8)] for x,y,w,h in case[key]))
    arr.append(sorted((round((h['x']-sx)/8),round((h['y']-sy)/8),h['kind']) for h in case['hooks']))
    return hashlib.sha256(json.dumps(arr).encode()).hexdigest()[:20]

def fixed_policy(case,result):
    """Same sequential noise-key model as adaptive policy, with state/aim feedback removed."""
    c=copy.deepcopy(case);c['id']+='-open-loop';plan=[];prev=0
    for event in result['fired_commands']:
        idx=event['index'];original=case['control_plan'][idx];step=copy.deepcopy(original)
        step['trigger']={'after':event['frame']-prev};prev=event['frame']
        if 'aim_target'in step:step.pop('aim_target');step['direction']=event['direction']
        if step['op']=='settle':
            # Replace the feedback tail with the exact clean executed Router inputs.
            step['op']='axis';step['value']=result['frames'][event['frame']]['axis']
            plan.append(step)
            last_value=step['value'];last_frame=event['frame']
            for f in result['frames'][event['frame']+1:]:
                if f['axis']!=last_value:
                    plan.append(command('axis',after=f['frame']-last_frame,value=f['axis'],noise_key='fixed/axis/'+str(f['frame']),timing_noise=False))
                    last_value=f['axis'];last_frame=f['frame']
            break
        plan.append(step)
    c['control_plan']=plan
    return c

def replay_case(case,result):
    c=copy.deepcopy(case);c.pop('control_plan',None);c.pop('noise',None);c['actions']=[];c['axes']=[]
    old=None
    for f in result['frames']:
        if f['axis']!=old:c['axes'].append(dict(frame=f['frame'],value=f['axis']));old=f['axis']
        for a in f['requested']:
            c['actions'].append(dict(frame=f['frame'],type=a['type'],direction=a.get('direction',[0,0])))
    c['max_frames']=len(result['frames'])+12
    return c
