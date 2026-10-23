"""Action-first Cell synthesis. No authored terrain/module library.
Motion traces are sampled from the pinned real Godot controller, not integrated here.
"""
from __future__ import annotations
import copy, math, random, hashlib, json
from dataclasses import dataclass

@dataclass
class Primitive:
    seed:int
    kind:str
    program:dict
    trace:list
    duration:int
    end:tuple
    landed_frame:int


def action(frame, typ, direction=(0,0)):
    return dict(frame=int(frame),type=typ,direction=list(direction))


def proposal(seed:int, kind:str)->dict:
    """Sample a typed action word. Coordinates are only primitive Cells/anchors."""
    r=random.Random(seed)
    spawn=[80,420]
    fire=r.randint(13,23)
    stop=r.randint(38,48)
    theta=r.uniform(.20,.68)
    actions=[action(5,'jump'),action(r.randint(13,18),'jump_release')]
    hooks=[]
    if kind=='recoil':
        actions.append(action(fire,'shoot_release',(-math.cos(theta),math.sin(theta))))
    elif kind=='grapple':
        # Real hang anchor. Aim is derived from the measured flight in calibration.
        hooks=[dict(x=r.randint(195,225),y=r.randint(235,270),kind='hang')]
        actions += [action(r.randint(10,15),'grapple',(.72,-.69)), action(r.randint(44,49),'jump'),
                    action(r.randint(53,59),'jump_release'), action(r.randint(57,63),'shoot_release',(-.98,.20))]
        stop=r.randint(77,86)
    return dict(id=f'probe-{kind}-{seed}',seed=seed,kind=kind,spawn=spawn,
                platforms=[[-80,438,220,60]],hazards=[],hooks=hooks,
                goal=[3000,-500,20,20],actions=sorted(actions,key=lambda a:a['frame']),
                axes=[dict(frame=0,value=1.0),dict(frame=stop-r.randint(2,5),value=-1.0),dict(frame=stop,value=0.0)],
                max_frames=stop+35,trace_all=True,profile='grapple' if kind=='grapple' else 'base')


def frame_xy(f):
    if 'position' in f:return f['position']
    return [f['x'],f['y']]

def materialize(probe:dict, result:dict, width:int=80, clearance:int=30, cp:bool=False)->dict|None:
    """Place a receiving support on the descending real trajectory.
    Add attached hazard faces outside the swept body corridor. Final candidate must
    be replayed: inverse construction itself never grants feasibility.
    """
    frames=result.get('frames',[])
    if not frames:return None
    pts=[frame_xy(f) for f in frames]
    r=random.Random(probe['seed']+991)
    last_action=max(a['frame'] for a in probe['actions'])
    stop=probe['axes'][-1]['frame']
    # Prefer a raised landing, requiring recoil/hook to reach its height.
    target_y=420-r.randint(160,235) if probe['kind']=='grapple' else 420-r.randint(30,85)
    crossing=None
    for i in range(max(last_action+8,stop-8),len(pts)-1):
        if pts[i][1]<=target_y<pts[i+1][1] and pts[i][0]>205:
            crossing=i+1;break
    if crossing is None:return None
    endx,endy=pts[crossing]
    # Shared domain for every policy, including the non-solver baselines.
    # v1 applied this margin only inside CP; retain v1 as an unfair pilot.
    if width<48 or round(endx-width/2)<165:return None
    if cp:
        from ortools.sat.python import cp_model
        model=cp_model.CpModel()
        left=model.new_int_var(round(endx-width+24),round(endx-24),'landing_left')
        w=model.new_int_var(width,width,'landing_width')
        model.add(left>=165)
        model.add(left+12<=round(endx))
        model.add(left+w-12>=round(endx))
        center_error=model.new_int_var(0,width,'center_error')
        model.add_abs_equality(center_error,2*left+width-2*round(endx))
        model.minimize(center_error)
        solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=.03;solver.parameters.num_search_workers=1
        status=solver.solve(model)
        if status not in (cp_model.OPTIMAL,cp_model.FEASIBLE):return None
        landing_left=solver.value(left)
    else:landing_left=round(endx-width/2)
    out=copy.deepcopy(probe)
    out['id']=probe['id'].replace('probe','module')
    out['platforms'].append([landing_left,target_y+18,width,80])
    # Wide lethal floor is a hazard Cell; supports carry attached spikes on undersides.
    out['hazards']=[[140,600,max(200,landing_left+width-140),40]]
    out['goal']=[landing_left+8,target_y-25,width-16,45]
    out['axes']=copy.deepcopy(probe['axes'])
    out['max_frames']=crossing+24
    # Trajectory-adjacent thorn faces create alternating clearance demands.
    for frac,side in [(.40,-1),(.68,1)]:
        x=140+(landing_left-140)*frac
        if x<155 or x>landing_left-30:continue
        # Every visit to this x-band contributes, including hook return/release.
        # Checking one local trace sample was insufficient: retained calibration-v1.
        band=[p[1] for p in pts[:crossing+1] if abs(p[0]-x)<34]
        if not band:continue
        yy=min(band)-18-clearance-36 if side<0 else max(band)+18+clearance
        block=[round(x-16),round(yy),32,36]
        if any(abs(h['x']-x)<40 and abs(h['y']-yy)<60 for h in probe.get('hooks',[])):continue
        out['platforms'].append(block)
        out['hazards'].append([block[0],block[1]+(30 if side<0 else -6),32,12])
    out['synthesis']={'method':'trace_to_support_and_clearance','cp_sat':cp,'landing_frame':crossing,
                      'landing_width':width,'clearance':clearance,'template_modules':0}
    return out


def shift_case(case,dx,dy):
    c=copy.deepcopy(case)
    c['spawn']=[c['spawn'][0]+dx,c['spawn'][1]+dy]
    for key in ('platforms','hazards'):
        c[key]=[[x+dx,y+dy,w,h] for x,y,w,h in c[key]]
    c['goal']=[c['goal'][0]+dx,c['goal'][1]+dy,*c['goal'][2:]]
    c['hooks']=[dict(h,x=h['x']+dx,y=h['y']+dy) for h in c.get('hooks',[])]
    return c


def chain(cases, results, ident):
    """Compile action words into one Module with continuous state, never teleporting.
    The new seam must pass another full replay; individual proofs are insufficient.
    """
    merged=copy.deepcopy(cases[0]);merged['id']=ident
    time=0
    for i,(c,res) in enumerate(zip(cases,results)):
        if i:
            previous=frame_xy(results[i-1]['frames'][-1])
            # accumulated endpoint is read from transformed preceding trace
            dx=last_end[0]-c['spawn'][0];dy=last_end[1]-c['spawn'][1]
            c=shift_case(c,dx,dy)
            for key in ('platforms','hazards','hooks'):merged[key]+=c.get(key,[])
            merged['actions'] += [dict(a,frame=a['frame']+time) for a in c['actions']]
            merged['axes'] += [dict(a,frame=a['frame']+time) for a in c['axes']]
            merged['goal']=c['goal']
        else:dx=dy=0
        last_end=frame_xy(res['frames'][-1]);last_end=[last_end[0]+dx,last_end[1]+dy]
        time+=len(res['frames'])
    merged['max_frames']=time
    merged['synthesis']=dict(merged['synthesis'],word_count=len(cases),method='continuous_action_grammar')
    return merged


def descriptor(result):
    fs=result.get('frames',[])
    if not fs:return (0,0)
    pts=[frame_xy(f) for f in fs]
    events=[e for f in fs for e in f.get('accepted',[])]
    shots=[e for e in events if e.get('type')=='shot']
    angle=math.atan2(shots[0]['direction'][1],-shots[0]['direction'][0]) if shots else 0
    airborne=sum(not f.get('grounded',False) for f in fs)/len(fs)
    # Four recoil aim bands x five actual airborne-time bands; kind separated.
    return (min(3,max(0,int(angle/.20))),min(4,int(airborne*5)))



def normalized_fingerprint(case):
    x,y=case['spawn']
    geometry=[(round((a-x)/16),round((b-y)/16),round(w/16),round(h/16)) for a,b,w,h in case['platforms']]
    return hashlib.sha256(json.dumps(sorted(geometry)).encode()).hexdigest()[:16]
