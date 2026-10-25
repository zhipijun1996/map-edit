"""Content experiment entrypoints. No topology, Map assembly or new Harness."""
import argparse,copy,json,subprocess,time
from pathlib import Path
from .engine import WorkshopEngine,ROOT,HERE
from .rules import FAMILIES,candidates,specifications,generate
from .evaluate import purpose,evaluate
from .counterexamples import alternatives
from .evidence import counter_records,geometry_key
from ..factory.core.quality import module_hash,digest,gate,POLICY
from ..factory.core.engine import file_sha
from pcg.contract.export import collect
from pcg.map_directed.library import CandidateLibrary

REPO=ROOT.parent
def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def source_cases(families):
    specs=[s for s in specifications()if s['required_family']in families];cases=[]
    for spec in specs:
        response=generate(spec)
        if response['status']!='requires_physics':raise ValueError(response)
        for c in response['cases']:
            c['map_specification']=spec
            c['idea_ids']=[{'thorn-slot':'human-A1-thorn-slot','chase-landing':'human-A2-chase-landing','timed-cache':'human-A3-short-gate'}.get(c['family'],'codex-'+c['family']+'-v1')]
            cases.append(c)
    return specs,cases

def counter_run(name,families,requested=None):
    engine=WorkshopEngine(ROOT/'results'/name);specs,bases=requested if requested is not None else source_cases(families);rows=[]
    cs=[c for base in bases for c in alternatives(base)]
    write(engine.out/'protocol.json',dict(scope='counterexample search only',maximum_cases=len(cs),source_protocol=json.loads((HERE/'protocol.json').read_text()),necessity_proof=False))
    for c,r,e in engine.run(cs,'counterexample'):
        # This intentionally ignores requested action words and purpose: a cheap
        # safe stable arrival refutes the proposal even if no shot was executed.
        row=dict(id=c['id'],base_id=c['id'].split('-counter-')[0],kind=c['counterexample_kind'],safe_stable=bool(r['ok']),reason=r['reason'],actual_shots=r.get('shots'),actual_reward=r.get('workshop',{}).get('coins'),evidence=e)
        rows.append(row);write(engine.out/'counterexamples.json',rows)
        if row['safe_stable']:print(json.dumps(row),flush=True)
    write(engine.out/'summary.json',dict(cases=len(rows),cheap_successes=[r for r in rows if r['safe_stable']],all_failures_preserved=True,necessity_proof=False))
    print(engine.out,flush=True);return engine.out

def produce(name,families,counters,requested=None):
    out=ROOT/'results'/name;engine=WorkshopEngine(out);protocol=json.loads((HERE/'protocol.json').read_text());specs,bases=requested if requested is not None else source_cases(families)
    write(out/'protocol.json',dict(protocol,holdout_seed=protocol['holdout_seed'],families=families,selection_frozen_before_holdout=True))
    write(out/'challenge-specifications.json',specs);write(out/'candidates.json',dict(cases=bases))
    entries=evaluate(engine,bases,protocol['holdout_seed'],12,'holdout')
    counter_runs=counters.split(',')
    counter_rows=[r for run in counter_runs for r in counter_records(run)];reviews=[];enrolled=[]
    write(out/'bound-counterexamples.json',counter_rows)
    for e in entries:
        base=e['case'];bound=[r for r in counter_rows if r['base_id']==base['id']and r['geometry_sha256']==geometry_key(base)]
        if len(bound)<18:raise ValueError('counterexample_geometry_coverage_missing/'+base['id'])
        shortcut=any(r['safe_stable']for r in bound)
        e['quality_gate']=gate(e['stats'],shortcut,bool(base.get('moving_platforms')or base.get('enemies')))
        if not e['witness']or e['quality_gate']['status']!='awaiting_human_review':continue
        w=e['witness'];c=copy.deepcopy(w['case']);c['factory_id']=digest(base);c['factory_evidence']=w['evidence']
        c['recorded_frames']=[dict(frame=f['frame'],axis=f['axis'],requested=f['requested'])for f in w['result']['frames']]
        c['validation_summary']=e['stats'];c['module_sha256']=module_hash(c)
        c['review_alias']=base['id'];reviews.append(c)
    write(out/'evaluations.json',entries);write(out/'review_cases.json',dict(cases=reviews))
    if reviews:
        rows=collect(out/'review_cases.json',out)
        for row in rows:
            row['workshopPurpose']=purpose(row['case'],row['result'])
            if row['case'].get('ports'):row['routePurpose']=row['workshopPurpose']
        bundle=dict(rows=rows,sourceCommit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip())
        write(out/'source-bundle.json',bundle)
        subprocess.run(['node',str(HERE/'export.mjs'),str(out/'source-bundle.json'),str(out/'modules')],check=True,cwd=REPO)
        library=CandidateLibrary(out/'library');manifest=json.loads((out/'modules/manifest.json').read_text())
        for c in reviews:
            if c.get('ports'):continue # multi-route catalog remains scoped, no single-route enrollment lie
            doc=out/'modules'/('generated-'+c['factory_id']+'.mapnote.json')
            entry=next(e for e in entries if digest(e['case'])==c['factory_id'])
            artifacts=[dict(path=str(p.relative_to(REPO)),sha256=file_sha(p))for p in [out/'evaluations.json',out/'protocol.json',out/'bound-counterexamples.json']]
            record=library.enroll(c,doc,entry['quality_gate'],artifacts);enrolled.append(record)
        # Reconstruct the library object and read disk records/documents/physics.
        # Queries use existing CandidateLibrary.find; this is not a cache count.
        reloaded=CandidateLibrary(out/'library');queries=[]
        for spec in specs:
            query=copy.deepcopy(spec);query['relations']=[dict(**r,**{'from':r['from_port'],'to':r['to_port']})for r in spec['relations']]
            matches=reloaded.find(query)if spec['ports']['count']==2 else[]
            queries.append(dict(specification=spec['id'],matches=[m['record']['contentVersion']for m in matches],generator_called=False,storage='CandidateLibrary candidates on disk',production_admitted=False))
        write(out/'retrieval.json',queries)
    passedfamilies=[]
    for f in families:
        selected=[e for e in entries if e['case']['family']==f]
        if all(e['quality_gate']['status']=='awaiting_human_review'for e in selected):passedfamilies.append(f)
    write(out/'summary.json',dict(families_requested=families,technical_families=passedfamilies,technical_candidates=len(reviews),enrolled_single_route_candidates=len(enrolled),physics_cases=engine.sim.cases,human_video_observation='unreviewed',human_playtest='unreviewed',production_admitted=False,whole_map='UNKNOWN',counterexample_scope='finite policies; no proof of necessity'))
    print(out,flush=True);return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['counters','produce']);p.add_argument('--name',required=True);p.add_argument('--families',nargs='+',choices=FAMILIES,default=list(FAMILIES));p.add_argument('--counters');a=p.parse_args()
    if a.stage=='counters':counter_run(a.name,a.families)
    else:
        if not a.counters:p.error('produce requires --counters')
        produce(a.name,a.families,a.counters)
