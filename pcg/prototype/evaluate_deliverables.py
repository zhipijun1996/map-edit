"""Independent perturbation and mechanic-ablation replays of actual generated Modules."""
from pathlib import Path
import json,copy,random,statistics
from experiment import Simulator,error_variant
from trajectory_synth import chain,frame_xy,normalized_fingerprint
ROOT=Path(__file__).resolve().parents[1]

def evaluate(run_name,destination='deliverables'):
    source=ROOT/'results'/run_name
    dest=ROOT/'results'/destination;dest.mkdir(parents=True,exist_ok=True)
    sim=Simulator(dest)
    entries=json.loads((source/'valid.json').read_text())
    # Choose deterministic geometry-distinct successes, not by noise success.
    selected=[];seen=set()
    for kind in ('recoil','grapple'):
        for strategy in ('A_action','B_fi_qd','C_hybrid'):
            subset=[e for e in entries if e['case']['kind']==kind and e['case']['strategy']==strategy]
            local=set()
            for e in subset:
                h=normalized_fingerprint(e['case'])
                if h in local:continue
                selected.append(e);local.add(h)
                if len(local)>=4:break
    noisy=[];noise_meta=[]
    for j,e in enumerate(selected):
        for name,timing,aim in [('exact',0,0),('mild',1,2),('moderate',3,6)]:
            for trial in range(10 if timing else 2):
                c=error_variant(e['case'],900000+j*100+trial,timing,aim)
                noisy.append(c);noise_meta.append(dict(module=e['case']['id'],kind=e['case']['kind'],strategy=e['case']['strategy'],level=name))
    rr=sim.run(noisy,'robustness')
    combined=[dict(**m,ok=r['ok'],reason=r['reason'],shots=r['shots'],grapples=r['grapples']) for m,r in zip(noise_meta,rr)]
    (dest/'robustness-table.json').write_text(json.dumps(combined,indent=2))
    # Recoil, hooks and aerial steering deletion; this tests the same program only.
    ac=[];am=[]
    for e in selected:
        for mechanism in ('shoot_release','grapple','steering'):
            if mechanism=='grapple' and e['case']['kind']!='grapple':continue
            c=copy.deepcopy(e['case']);c['id']+=f'-without-{mechanism}'
            if mechanism=='steering':c['axes']=[dict(frame=0,value=0.)]
            else:c['actions']=[a for a in c['actions'] if a['type']!=mechanism]
            ac.append(c);am.append(dict(module=e['case']['id'],kind=e['case']['kind'],removed=mechanism))
    ar=sim.run(ac,'ablations')
    (dest/'ablation-table.json').write_text(json.dumps([dict(**m,ok=r['ok'],reason=r['reason']) for m,r in zip(am,ar)],indent=2))
    # Short continuous Module from two/three independently generated motion words.
    chain_candidates=[]
    recoil=[e for e in selected if e['case']['kind']=='recoil' and e['case']['strategy']=='C_hybrid']
    for j in range(min(3,len(recoil))):
        es=[recoil[(j+i)%len(recoil)] for i in range(3)]
        c=chain([e['case'] for e in es],[e['result'] for e in es],f'continuous-recoil-{j}')
        chain_candidates.append(c)
    cr=sim.run(chain_candidates,'continuous-recoil')
    deliver=[c for c,r in zip(chain_candidates,cr) if r['ok']]
    # Grapple challenge from real physically accepted hook candidates.
    grapple=[e for e in selected if e['case']['kind']=='grapple' and e['case']['strategy']=='C_hybrid']
    if grapple:deliver.append(grapple[0]['case'])
    # Fork and reconverge: shared low ground; elevated reward reached by hook word.
    # High route program continues to drop into common exit. No reward transaction yet.
    forks=[]
    for j,e in enumerate(grapple[:3]):
        high=copy.deepcopy(e['case']);high['id']=f'multiroute-{j}-reward'
        high['platforms'][0]=[-80,438,1200,60]
        high['hazards']=[h for h in high['hazards'] if h[1]<430]
        # Keep only upper obstacle faces that cannot intersect the low main route.
        high['platforms']=[p for p in high['platforms'] if p[1]<365 or p[1]>=438]
        high['hazards']=[h for h in high['hazards'] if h[1]<365]
        high['reward_region']=high['goal'][:]
        high['trace_all']=True
        # Above the legal full-jump height; original high landing remains the reward.
        forks.append(high)
        low=copy.deepcopy(high);low['id']=f'multiroute-{j}-main';low['actions']=[]
        low['axes']=[dict(frame=0,value=1.),dict(frame=135,value=0.)]
        low['max_frames']=170;low['goal']=[630,390,140,45];low.pop('reward_region',None)
        forks.append(low)
    fr=sim.run(forks,'multiroute-initial')
    merged=[]
    for i in range(0,len(forks),2):
        high,low=forks[i:i+2];hr,lr=fr[i:i+2]
        if not (hr['ok'] and lr['ok']):continue
        high=copy.deepcopy(high)
        begin=high['max_frames']
        high['actions'].append(dict(frame=begin,type='jump',direction=[0,0]))
        high['actions'].append(dict(frame=begin+10,type='jump_release',direction=[0,0]))
        high['axes'].append(dict(frame=begin,value=1.))
        high['axes'].append(dict(frame=begin+75,value=0.))
        high['max_frames']=begin+115;high['goal']=low['goal'][:]
        merged += [high,low]
    mr=sim.run(merged,'multiroute-merge')
    for i in range(0,len(merged),2):
        region=merged[i].get('reward_region')
        visited=any(region[0]<=f['x']<=region[0]+region[2] and region[1]<=f['y']<=region[1]+region[3] and f['grounded'] for f in mr[i]['frames'])
        if mr[i]['ok'] and mr[i+1]['ok'] and visited:
            deliver+=merged[i:i+2];break
    for c in deliver:
        c['trace_all']=True
        c['title']=c['id']
    final=sim.run(deliver,'delivery-replay')
    # This is a delivery gate; failed candidates remain recorded and never enter menu.
    good=[c for c,r in zip(deliver,final) if r['ok']]
    (dest/'modules.json').write_text(json.dumps({'schema':'disordered-clock/generated-cell-modules/v1','cases':good},indent=2))
    if good:(ROOT/'prototype/godot/modules.json').write_text(json.dumps({'cases':good}))
    summary=dict(source_run=run_name,selected_modules=len(selected),robustness=[],ablations=[],delivery_modules=[dict(id=c['id'],shots=r['shots'],grapples=r['grapples'],jumps=r['jumps'],ticks=r['ticks'],final_grounded=r['frames'][-1]['grounded'],final_velocity=[r['frames'][-1]['vx'],r['frames'][-1]['vy']],reward_visited=(any(c['reward_region'][0]<=f['x']<=c['reward_region'][0]+c['reward_region'][2] and c['reward_region'][1]<=f['y']<=c['reward_region'][1]+c['reward_region'][3] and f['grounded'] for f in r['frames']) if 'reward_region' in c else None)) for c,r in zip(deliver,final) if r['ok']],simulation_cases=sim.cases,simulation_seconds=sim.seconds,
        limits=['Ablation is fixed-input, not a proof of mechanic necessity.', 'Reward is a geometric visit, no formal game reward transaction.', 'Static hazard swept-body test; no official thorn damage consumer.'])
    for kind in ('recoil','grapple'):
      for strategy in ('A_action','B_fi_qd','C_hybrid'):
       for level in ('exact','mild','moderate'):
        group=[r for r in combined if r['kind']==kind and r['strategy']==strategy and r['level']==level]
        if group:summary['robustness'].append(dict(kind=kind,strategy=strategy,level=level,success=sum(r['ok'] for r in group),n=len(group)))
    for kind in ('recoil','grapple'):
      for mech in ('shoot_release','grapple','steering'):
       group=[r for m,r in zip(am,ar) if m['kind']==kind and m['removed']==mech]
       if group:summary['ablations'].append(dict(kind=kind,removed=mech,success=sum(r['ok'] for r in group),n=len(group)))
    (dest/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))

if __name__=='__main__':
 import sys
 evaluate(sys.argv[1] if len(sys.argv)>1 else 'holdout-v2',sys.argv[2] if len(sys.argv)>2 else 'deliverables')
