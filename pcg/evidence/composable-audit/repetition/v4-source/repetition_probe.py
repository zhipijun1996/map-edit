"""Regression probes for reusable wall/anchor affordances and restored air jumps.
Motion acceptance and a settled Module are reported separately.
"""
import copy,json,hashlib,subprocess
from pathlib import Path
from contracts import Grammar
from synthesis import compile_probe,materialize,actual_word
from search import expected_word
from simulator import ROOT,Simulator

def run(name):
    out=ROOT/'results'/name;sim=Simulator(out);cases=[]
    for layout in ('same','alternating'):
        for n in (2,3,6):
            for double in (False,True):
                caps=['move','jump','wall_climb']+(['double_jump'] if double else [])
                word=[]
                for i in range(n):
                    if i:word.append('wall_separate')
                    word+=['wall_contact','wall_jump']+(['air_jump'] if double else [])
                c=compile_probe(word,caps,730010+len(cases),wall_layout=layout)
                c.update(id=f'wall-{layout}-{n}-double-{int(double)}',max_frames=900)
                cases.append(c)
    for double in (False,True):
        word=(['hook_bounce','air_jump'] if double else ['hook_bounce'])*4
        caps=['move','jump','grapple']+(['double_jump'] if double else [])
        c=compile_probe(word,caps,730100+len(cases));c.update(id='four-hooks-double-'+str(int(double)),max_frames=900);cases.append(c)
    rs=sim.run(cases,'00-motion');receivers=[];motion=[]
    for c,r in zip(cases,rs):
        intended=actual_word(r)==expected_word(c['word']) and r['plan_completed']
        jumps=[f for f in r['frames'] if any(e['type']=='wall_jump' for e in f['accepted'])]
        commands=[f for f in r['fired_commands'] if f['op']=='jump' and f['state']=='wall_attach']
        separations=[]
        for a,b in zip(commands,commands[1:]):
            span=[f for f in r['frames'] if a['frame']<=f['frame']<=b['frame']]
            separations.append(max(abs(f['x']-a['position'][0]) for f in span))
        wall_sides=[round(f['position'][0],1) for f in commands]
        in_air=all(not f['grounded'] for f in r['frames'] if commands and commands[0]['frame']<=f['frame']<=commands[-1]['frame'])
        motion.append(dict(id=c['id'],word=list(actual_word(r)),intended_word_executed=intended,wall_jumps=len(jumps),air_jumps=r.get('air_jumps',0),wall_contact_x=wall_sides,separation_distances=separations,no_intermediate_grounding=in_air,reason=r['reason']))
        if intended:
            g=materialize(c,r,width=160,clearance=44)
            if g:g.update(id=c['id']+'-module');receivers.append(g)
    grs=sim.run(receivers,'01-modules');byid={r['id']:r for r in grs}
    for row in motion:
        r=byid.get(row['id']+'-module');row['settled_module']=bool(r and r['ok']);row['module_reason']=r['reason'] if r else 'not_materialized'
    # The physical source itself is not patched to obtain these trajectories.
    provenance=json.loads((ROOT/'prototype/godot/source_provenance.json').read_text())
    drift=[name for name,h in provenance['files'].items() if hashlib.sha256((ROOT/'prototype/godot'/name).read_bytes()).hexdigest()!=h]
    game=Path('/workspace/gunman-rush-latest');latest='54573a8e9400d790f58656efde2dd812cc00d8ba'
    paths=['config/player_tuning.json','scripts/player','scripts/input','scripts/combat','resources/player','resources/weapons','scenes/player','project.godot']
    changed=subprocess.check_output(['git','diff','--name-only',provenance['commit'],latest,'--',*paths],cwd=game,text=True).splitlines()
    summary=dict(schema='pcg/repetition-regression/v3',motion_cases=len(cases),intended_motion_success=sum(r['intended_word_executed'] for r in motion),module_candidates=len(receivers),settled_modules=sum(r['ok'] for r in grs),physics_cases=sim.cases,physics_source=provenance['commit'],latest_development_checked=latest,changed_motion_sources=changed,original_source_drift=drift,results=motion,limits=['Static primitive fixtures; no moving hazards/platforms or production damage.','Repetitions are not proof of interesting or difficult play.','No new public Web build; immutable V2 remains the old algorithm.'])
    (out/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
    if drift or changed:raise SystemExit('Motion source differs')
if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--name',default='repetition-v4');run(parser.parse_args().name)
