"""Paired perturbation tests and bounded shortcut search on fixed geometry.
The latter can find counterexamples; its failures never prove ability necessity.
"""
from pathlib import Path
import argparse,copy,json,random,collections,time,math
from simulator import ROOT,Simulator
from synthesis import command,gated,fixed_policy,actual_word,behavioral_descriptor

def alternatives(case,seed=817):
    """No supplied module/policy: cheap input families on the candidate's Cells."""
    rng=random.Random(seed);caps=set(case['capabilities']);out=[]
    goal_x=case['goal'][0]+case['goal'][2]/2
    sign=1 if goal_x>case['spawn'][0] else -1
    for jump_at in (5,10,16):
        for kind in ('walk','jump','double','recoil','jump_recoil','hook','wall'):
            if kind=='double' and 'double_jump'not in caps:continue
            if 'recoil'in kind and 'shot_recoil'not in caps:continue
            if kind=='hook' and ('grapple'not in caps or not case['hooks']):continue
            if kind=='wall' and 'wall_climb'not in caps:continue
            plan=[command('axis',value=sign)]
            if kind in ('jump','double','jump_recoil','hook') and 'jump'in caps:
                plan += [command('jump',after=jump_at),command('jump_release',after=10)]
            if kind=='double':plan += [command('jump',after=16),command('jump_release',after=10)]
            if 'recoil'in kind:plan.append(command('shoot',after=jump_at,direction=[-sign*.75,.66]))
            if kind=='hook':
                h=case['hooks'][0];plan += [command('grapple',after=8,aim_target=[h['x'],h['y']]),gated('jump','hook_hang',min_after=3,timeout=70),command('jump_release',after=10)]
            if kind=='wall':
                walls=[case['platforms'][int(i)] for i in case.get('wall_platform_indices',[])]
                if not walls:continue
                approach=1 if walls[0][0]>case['spawn'][0] else -1
                plan[0]['value']=approach
                plan += [gated('jump','wall_attach',min_after=2,timeout=100),gated('axis','wall_kick',min_after=1,timeout=12,value=sign),command('jump_release',after=8)]
            plan.append(command('settle',after=5,target_x=goal_x,deadband=6))
            c=copy.deepcopy(case);c['id']+=f'-shortcut-{kind}-{jump_at}';c['control_plan']=plan;c['max_frames']=min(480,max(220,case['max_frames']));c['trace_all']=False
            c['alternative_family']=kind;out.append(c)
    # Direct action removal retains other controls; this can expose decorative actions.
    for index,step in enumerate(case['control_plan']):
        if step['op']not in ('jump','shoot','grapple'):continue
        c=copy.deepcopy(case);c['id']+=f'-omit-{index}';c['control_plan'][index]['op']='wait';c['alternative_family']='omit_'+step['op'];out.append(c)
    return out

def lower_mechanical_cost(reference,alternative):
    """Strict partial order, not a claim about human difficulty or fun."""
    def cost(result):
        w=actual_word(result);used=set()
        for action,cap in [('air_jump','double_jump'),('recoil','shot_recoil'),('hook_hang','grapple'),('hook_bounce','grapple'),('wall_jump','wall_climb')]:
            if action in w:used.add(cap)
        return used,len(w)
    before,n=cost(reference);after,m=cost(alternative)
    return after<before or (after==before and m<n)

def separate_counterexample(case,intended,alternative):
    """Add small hazardous primitive Cells away from the intended swept body tube."""
    reference=intended['frames'];points=alternative['frames'];rects=[]
    for f in points[::3]:
        x,y=round(f['x']/4)*4,round(f['y']/4)*4
        # Reference segment bounding boxes conservatively protect the whole body.
        rect=[x-8,y-12,16,24]
        def overlaps(a,b):return a[0]<=b[0]+b[2] and b[0]<=a[0]+a[2] and a[1]<=b[1]+b[3] and b[1]<=a[1]+a[3]
        protected=False
        for p,q in zip(reference,reference[1:]):
            tube=[min(p['x'],q['x'])-20,min(p['y'],q['y'])-26,abs(p['x']-q['x'])+40,abs(p['y']-q['y'])+52]
            if overlaps(rect,tube):protected=True;break
        if protected or any(abs(x-h['x'])<30 and abs(y-h['y'])<30 for h in case['hooks']):continue
        if any(abs(x-r[0])<60 and abs(y-r[1])<60 for r in rects):continue
        rects.append(rect)
        if len(rects)>=3:break
    if not rects:return None
    c=copy.deepcopy(case);c['id']+='-refined';c['hazards']+=rects
    c['synthesis']['counterexample_cells']=rects
    return c

def select_diverse(entries,n=16):
    # Coverage first; never count geometric hashes as new action experiences.
    chosen=[];seen=set()
    for combo in range(16):
        group=[e for e in entries if e['case']['combo_index']==combo]
        if group:
            group.sort(key=lambda e:(len(e['actual_word']),e['case']['id']))
            e=group[0];chosen.append(e);seen.add(e['case']['id'])
    for e in sorted(entries,key=lambda e:(-len(e['actual_word']),e['case']['id'])):
        if len(chosen)>=n:break
        if e['case']['id']not in seen:chosen.append(e);seen.add(e['case']['id'])
    return chosen[:n]

def run(args):
    source=ROOT/'results'/args.source;out=ROOT/'results'/args.name;sim=Simulator(out);start=time.perf_counter()
    entries=select_diverse(json.loads((source/'archive.json').read_text()),args.modules)
    # Shortcut discovery and refinement use calibration only, before noise holdout.
    alts=[];owners=[]
    for i,e in enumerate(entries):
        cases=alternatives(e['case']);alts+=cases;owners += [i]*len(cases)
    ars=sim.run(alts,'00-shortcut-search');found=collections.defaultdict(list);other_routes=0
    for i,c,r in zip(owners,alts,ars):
        if r['ok']:
            if lower_mechanical_cost(entries[i]['result'],r):found[i].append((c,r))
            else:other_routes+=1
    refined=[];refined_owners=[]
    for i,solutions in found.items():
        e=entries[i];c=separate_counterexample(e['case'],e['result'],solutions[0][1])
        if c:refined.append(c);refined_owners.append(i)
    rrs=sim.run(refined,'01-refinement-witness')
    accepted=[]
    for i,c,r in zip(refined_owners,refined,rrs):
        if r['ok'] and actual_word(r)==tuple(entries[i]['actual_word']):
            entries[i]=dict(case=c,result=r,actual_word=list(actual_word(r)),descriptor=list(behavioral_descriptor(r)))
            accepted.append(i)
    alts2=[];owners2=[]
    for i in accepted:
        cs=alternatives(entries[i]['case']);alts2+=cs;owners2 += [i]*len(cs)
    ar2=sim.run(alts2,'02-refined-shortcut-search');remaining=collections.Counter(i for i,r in zip(owners2,ar2) if r['ok'] and lower_mechanical_cost(entries[i]['result'],r))
    # Exact same geometry, noise seed, command keys and magnitudes for both policies.
    noise_cases=[];labels=[]
    for i,e in enumerate(entries):
        for policy,base in [('feedback',e['case']),('fixed',fixed_policy(e['case'],e['result']))]:
            for level,timing,angle in [('clean',0,0),('mild',1,2),('moderate',3,6)]:
                count=1 if level=='clean' else args.trials
                for trial in range(count):
                    c=copy.deepcopy(base);c['id']+=f'-{policy}-{level}-{trial}'
                    c['noise']=dict(seed=args.seed+trial,timing_frames=timing,aim_degrees=angle)
                    noise_cases.append(c);labels.append(dict(module=i,policy=policy,level=level,trial=trial))
    rs=sim.run(noise_cases,'03-paired-noise-holdout');pooled={};by_module=[]
    for policy in ('feedback','fixed'):
        for level in ('clean','mild','moderate'):
            rows=[r for l,r in zip(labels,rs) if l['policy']==policy and l['level']==level]
            pooled[policy+'/'+level]=dict(success=sum(r['ok'] for r in rows),trials=len(rows))
    for i,e in enumerate(entries):
        scores={}
        for policy in ('feedback','fixed'):
            for level in ('clean','mild','moderate'):
                rr=[r for l,r in zip(labels,rs) if l['module']==i and l['policy']==policy and l['level']==level]
                scores[policy+'/'+level]=dict(success=sum(r['ok'] for r in rr),trials=len(rr))
        by_module.append(dict(id=e['case']['id'],combo=e['case']['combo_index'],word=e['actual_word'],capabilities=e['case']['capabilities'],original_shortcuts=len(found[i]),refined=i in accepted,remaining_shortcuts=remaining[i] if i in accepted else len(found[i]),scores=scores))
    summary=dict(schema='pcg/composable-evaluation/v2',source=args.source,holdout_seed=args.seed,modules=by_module,pooled=pooled,
        shortcut_trials=len(alts)+len(alts2),other_successful_routes_preserved=other_routes,shortcut_cost='strict subset of actually used optional capabilities, or same set with fewer accepted critical actions',original_modules_with_shortcuts=sum(bool(x) for x in found.values()),refinements_attempted=len(refined),refinements_preserving_witness=len(accepted),
        modules_without_discovered_shortcuts=sum(x['remaining_shortcuts']==0 for x in by_module),
        noise_trials=len(noise_cases),physics_cases=sim.cases,wall_seconds=time.perf_counter()-start,
        limits=['Shortcut search is bounded; no discovered shortcut is not a proof of necessity.','Paired perturbation measures this automated policy, not human success or fun.','Holdout noise is not used to change geometry or policies.'])
    (out/'summary.json').write_text(json.dumps(summary,indent=2));(out/'selected.json').write_text(json.dumps(entries));(out/'noise-labels.json').write_text(json.dumps(labels))
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',default='composable-search-v2');p.add_argument('--name',default='composable-evaluation-v2');p.add_argument('--modules',type=int,default=16);p.add_argument('--trials',type=int,default=12);p.add_argument('--seed',type=int,default=171031);run(p.parse_args())
