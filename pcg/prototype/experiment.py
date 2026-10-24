#!/usr/bin/env python3
"""Equal-proposal-budget pilot. All success comes from real Godot replay.
A/B/C here are explicitly restricted ablations, not reproductions of full papers.
"""
from pathlib import Path
import argparse, copy, json, time, subprocess, random, statistics, hashlib, resource
from trajectory_synth import proposal,materialize,descriptor,normalized_fingerprint,chain,frame_xy
ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/'toolchain/Godot_v4.7.2-stable_linux.x86_64'
GODOT=ROOT/'prototype/godot'

class Simulator:
    def __init__(self,out):self.out=out;self.calls=0;self.cases=0;self.seconds=0
    def run(self,cases,label):
        if not cases:return []
        self.calls+=1;self.cases+=len(cases)
        inp=self.out/f'{label}.input.json';out=self.out/f'{label}.output.json';log=self.out/f'{label}.log'
        inp.write_text(json.dumps({'cases':cases}))
        cmd=[str(ENGINE),'--headless','--path',str(GODOT),'--fixed-fps','60','--script','res://runner.gd','--',f'--input={inp}',f'--output={out}']
        start=time.perf_counter()
        usage_before=resource.getrusage(resource.RUSAGE_CHILDREN)
        with log.open('w') as f:p=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=180)
        batch_seconds=time.perf_counter()-start
        self.seconds+=batch_seconds
        usage=resource.getrusage(resource.RUSAGE_CHILDREN)
        (self.out/f'{label}.execution.json').write_text(json.dumps(dict(command=cmd,exit_code=p.returncode,wall_seconds=batch_seconds,child_cpu_seconds=(usage.ru_utime+usage.ru_stime-usage_before.ru_utime-usage_before.ru_stime),children_peak_rss_kib=usage.ru_maxrss),indent=2))
        if p.returncode or not out.exists():raise RuntimeError(f'Godot failed {p.returncode}; see {log}')
        data=json.loads(out.read_text())
        if isinstance(data,list):results=data
        else:results=data.get('results',data.get('cases',[]))
        if len(results)!=len(cases):raise RuntimeError(f'Incomplete batch {label}: {len(results)}/{len(cases)}')
        return results


def error_variant(case,seed,jitter,aim_degrees):
    r=random.Random(seed);c=copy.deepcopy(case)
    c['id']+=f'-error-{seed}'
    for a in c['actions']:
        a['frame']=max(0,a['frame']+r.randint(-jitter,jitter))
        if a['type'] in ('shoot_release','grapple'):
            import math
            x,y=a['direction'];t=math.radians(r.uniform(-aim_degrees,aim_degrees))
            a['direction']=[x*math.cos(t)-y*math.sin(t),x*math.sin(t)+y*math.cos(t)]
    c['actions'].sort(key=lambda a:a['frame'])
    return c


def run(args):
    out=ROOT/'results'/args.name;out.mkdir(parents=True,exist_ok=True)
    sim=Simulator(out);start=time.perf_counter()
    stats=[];all_kept=[];archive=[]
    # Shared motion sample corpus is charged once and reported separately.
    probes=[proposal(args.seed+i,kind) for kind in ('recoil','grapple') for i in range(args.samples)]
    pres=sim.run(probes,'00-probes')
    corpus=list(zip(probes,pres))
    for kind in ('recoil','grapple'):
        bank=[(c,r) for c,r in corpus if c['kind']==kind]
        for strategy in ('A_action','B_fi_qd','C_hybrid'):
            rng=random.Random(args.seed);feasible={};infeasible={};pairs=[];elapsed=time.perf_counter()
            # Same real proposal budget and sample corpus for every variant.
            for generation in range(args.generations):
                candidates=[]
                for j in range(args.samples):
                    probe,res=bank[j]
                    width=rng.choice([48,64,80,96,112]);clearance=rng.choice([12,20,28,40])
                    if strategy!='A_action' and generation and (feasible or infeasible):
                        # Two archives, feasible quality vs infeasible progress pressure.
                        pool=list(feasible.values()) if feasible and (rng.random()<.5 or not infeasible) else list(infeasible.values())
                        parent=rng.choice(pool)[0];width=max(40,min(120,parent['synthesis']['landing_width']+rng.choice([-16,0,16])))
                        clearance=max(8,min(48,parent['synthesis']['clearance']+rng.choice([-8,0,8])))
                    c=materialize(probe,res,width,clearance,strategy=='C_hybrid')
                    if c:
                        c['id']+=f'-{strategy}-g{generation}-j{j}';c['strategy']=strategy;candidates.append(c)
                results=sim.run(candidates,f'{kind}-{strategy}-g{generation}')
                for c,r in zip(candidates,results):
                    pairs.append((c,r));d=descriptor(r)
                    # Progress is a search hint; never a proof of infeasibility.
                    progress=max((frame_xy(f)[0] for f in r.get('frames',[])),default=0)
                    q=1.0-len(r.get('frames',[]))/1000
                    ok=r.get('ok',False)
                    score=q if ok else progress
                    target=feasible if ok else infeasible
                    if d not in target or score>target[d][2]:target[d]=(c,r,score)
            kept=[(c,r) for c,r in pairs if r.get('ok',False)]
            unique={normalized_fingerprint(c) for c,r in kept}
            row=dict(kind=kind,strategy=strategy,proposal_budget=args.samples*args.generations,evaluated=len(pairs),feasible=len(kept),feasible_fraction=len(kept)/len(pairs) if pairs else 0,
                archive_cells=len(feasible),infeasible_archive_cells=len(infeasible),unique_geometry=len(unique),
                repeated_geometry_fraction=1-len(unique)/len(kept) if kept else None,
                seconds=time.perf_counter()-elapsed,seconds_per_valid=(time.perf_counter()-elapsed)/len(kept) if kept else None,
                human_fun='unverified',difficulty_control='unverified',runtime='desktop_headless_only')
            stats.append(row);all_kept += [(c,r) for c,r in kept]
            archive += [dict(case=c,result=r,behavior=list(d)) for d,(c,r,_) in feasible.items()]
    (out/'summary.json').write_text(json.dumps(dict(schema='gunman-pcg-pilot/v1',seed=args.seed,samples=args.samples,generations=args.generations,
        source_commit='12f6cb006d7119598e3235f4ca4f7323e4c9d092',engine=subprocess.check_output([str(ENGINE),'--version'],text=True).strip(),
        rows=stats,simulation_calls=sim.calls,simulation_cases=sim.cases,simulation_seconds=sim.seconds,
        wall_seconds=time.perf_counter()-start,parent_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,children_peak_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
        notes=['Restricted proposal-policy pilot; not full A*, Tanagra, FI-MAP-Elites reproduction.',
               'Sampling corpus cost is separate; all candidates need independent real replay.',
               'No human ratings collected; success is a witness, search failure is not unreachability.']),indent=2))
    (out/'archive.json').write_text(json.dumps(archive))
    (out/'valid.json').write_text(json.dumps([dict(case=c,result=r) for c,r in all_kept]))
    print(json.dumps(stats,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--samples',type=int,default=16);p.add_argument('--generations',type=int,default=2);p.add_argument('--seed',type=int,default=481516);p.add_argument('--name',default='pilot-v1');run(p.parse_args())
