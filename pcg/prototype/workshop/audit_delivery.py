"""Audit immutable artifacts using existing contract/library verification."""
import argparse,json,gzip
from .engine import ROOT
from .delivery import SELECTED
from .experiments import write
from .evidence import GEOMETRY,counter_records,geometry_key
from ..factory.core.engine import file_sha
from ..factory.core.quality import digest
from pcg.map_directed.library import verified_document

PHYSICAL=[k for k in GEOMETRY if k not in ['spawn','entry_port','exit_port','goal']]
def physical(c):return digest({k:c.get(k,[])for k in PHYSICAL})

def run(delivery='generation/workshop/v1'):
    repo=ROOT.parent;out=repo/delivery;manifest=json.loads((out/'modules/manifest.json').read_text());cases=[]
    for run,allowed in SELECTED:
        for c in json.loads((ROOT/'results'/run/'review_cases.json').read_text())['cases']:
            if not allowed or c['family']in allowed:cases.append((run,c))
    fixtures=[];seen_inputs=set()
    for name in ['workshop-transitions-holdout-v2','workshop-gate-return-window-v2','workshop-recovery-holdout-v1']:
        root=ROOT/'results'/name;cs={c['id']:c for c in json.loads((root/'cases.json').read_text())['cases']}
        summary=json.loads((root/'summary.json').read_text())
        for row in summary['rows']:
            c=cs[row['id']]
            # v2 general transitions include the old .55 second gate. Only
            # the separately rebound solved-window fixture authorizes .65.
            matched=[m for m in manifest['modules']if any(physical(raw)==physical(c)and raw['family']==m['family']for _,raw in cases if raw['family']==m['family']and ('generated-'+(raw.get('layout_uid')or raw['factory_id']))==m['id'])]
            if not matched:continue
            fingerprint=digest(c)
            if fingerprint in seen_inputs:continue
            seen_inputs.add(fingerprint)
            ev=row['evidence'];batch=next(b for b in json.loads((root/'batches.json').read_text())if b['batch']==ev['batch'])
            p=root/batch['gzip_path']
            if file_sha(p)!=batch['gzip_sha256']:raise ValueError('fixture trace drift')
            fixtures.append(dict(case_id=c['id'],contentVersions=[m['contentVersion']for m in matched],physical_geometry_sha256=physical(c),
                result='pass'if row['ok']else'failed',source_run=name,trace=dict(path=str(p.relative_to(repo)),sha256=file_sha(p),index=ev['index']),
                source_binding=dict(path=str((root/'source_binding.json').relative_to(repo)),sha256=file_sha(root/'source_binding.json')),
                scope='continuous specified policy only; general transfer/return/assembly remain UNKNOWN'))
    for m in manifest['modules']:
        doc=verified_document(out/'modules'/m['file'])
        if doc['generationContract']['contentVersion']!=m['contentVersion']or file_sha(out/'modules'/m['file'])!=m['sha256']:raise ValueError('delivery document drift')
    write(out/'continuous-evidence-bindings.json',dict(schema='pcg/scoped-continuous-evidence-bindings/v1',records=fixtures,universal_state_transfer='UNKNOWN',production_admitted=False))
    records=[r for n in ['workshop-counters-v1','workshop-counters-v2','workshop-carrier-counters-v3','workshop-gate-counters-v3','workshop-enemy-exact-counters-v1']for r in counter_records(n)]
    current={}
    for _,c in cases:
        for r in records:
            if r['geometry_sha256']==geometry_key(c):current[(r['geometry_sha256'],r['kind'])]=r
    if any(r['safe_stable']for r in current.values()):raise ValueError('selected delivery has a bound cheap-policy success')
    write(out/'counterexample-coverage.json',dict(cases=len(current),records=list(current.values()),necessity_proof=False))
    videos=json.loads((out/'videos/manifest.json').read_text())
    for clip in videos['clips']:
        if file_sha(out/'videos'/clip['file'])!=clip['sha256']:raise ValueError('video bytes drift')
    write(out/'audit.json',dict(standard_documents=len(manifest['modules']),distinct_families=len({m['family']for m in manifest['modules']}),
        exact_main_video_frames=videos['frames_exact'],bound_continuous_cases=len(fixtures),bound_counterexample_policies=len(current),
        candidate_only=True,human_video_observation='unreviewed',human_playtest='unreviewed',production_admitted=False,
        whole_map_validation='UNKNOWN; task B responsibility'))
    return out/'audit.json'

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--delivery',default='generation/workshop/v1');a=p.parse_args();print(run(a.delivery))
