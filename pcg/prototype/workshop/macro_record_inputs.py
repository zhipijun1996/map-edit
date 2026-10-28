"""One fixed infrastructure replay per selected film, with no candidate search.

The original batch observer picks the first slide collision at a two-collider
seam. Compare a fresh one-case process with the native process WITHOUT dropping
support_id or any other comparison field. Original discrepancies remain stored.
"""
import argparse,copy,json
from .engine import ROOT,WorkshopEngine
from .experiments import write
from .macro import purpose
from .macro_retry import check
from .record import KEYS
from ..factory.core.quality import module_hash,PUBLIC_HASH_EXCLUDED
from pcg.contract.export import collect

def run(name):
    sources=['workshop-macro-holdout-v2','workshop-macro-retry-held-v2'];selected=[]
    for source in sources:
        for row in collect(ROOT/'results'/source/'review_cases.json',ROOT/'results'/source):
            c=row['case']
            if c['family']!='gate-brake-return':continue
            if source==sources[0]and c['route_spec']['id']=='loop'or source==sources[1]and c['rule_parameters']['variant']==0:
                selected.append((c,row['result'],source))
    assert len(selected)==3
    engine=WorkshopEngine(ROOT/'results'/name,batch_size=1)
    write(engine.out/'protocol.json',dict(scope='one fixed fresh-process observation replay per published film; all original geometry, inputs, IDs and seeds unchanged',maximum_cases=3,maximum_retries=0,field_exclusions=[],purpose='diagnose first slide-collision observation at static seams; no candidate or holdout selection'))
    bases=[{k:copy.deepcopy(v)for k,v in c.items()if k not in PUBLIC_HASH_EXCLUDED}for c,_,_ in selected];reviews=[];rows=[]
    for (c,r,e),(original,old,source)in zip(engine.run(bases,'fresh-process'),selected):
        assert module_hash(c)==original['module_sha256'];p=check(c,r)if c.get('retry_fixture')else purpose(c,r);assert p['ok'],p
        differences=[]
        assert len(old['frames'])==len(r['frames'])
        for a,b in zip(old['frames'],r['frames']):
            changed=[k for k in KEYS if a[k]!=b[k]]
            if changed:differences.append(dict(frame=a['frame'],fields=changed,old_support=a['support_id'],fresh_support=b['support_id']))
            assert all(k=='support_id'for k in changed),differences[-1:]
            assert a['plains']==b['plains']and a['workshop']==b['workshop']
        native=ROOT/'results/workshop-macro-media-v2'/('M03'if c.get('retry_fixture')else'M01'if c['rule_parameters']['variant']==0 else'M02')/'gate-brake-return.trace.json'
        nf=json.loads(native.read_text())['frames'];native_diff=[]
        for a,b in zip(nf,r['frames']):
            changed=[k for k in KEYS if a[k]!=b[k]]
            if changed:native_diff.append(dict(frame=a['frame'],fields=changed))
        frozen=copy.deepcopy(original);frozen['factory_evidence']=e;assert module_hash(frozen)==original['module_sha256'];reviews.append(frozen)
        rows.append(dict(id=c['id'],source_run=source,moduleSha256=original['module_sha256'],purpose=p,original_batch_differences=differences,native_all_fields_exact=not native_diff and len(nf)==len(r['frames']),native_differences=native_diff,evidence=e))
    write(engine.out/'review_cases.json',dict(cases=reviews));write(engine.out/'rows.json',rows)
    write(engine.out/'summary.json',dict(cases=3,all_native_fields_exact=all(r['native_all_fields_exact']for r in rows),all_passed_purpose=all(r['purpose']['ok']for r in rows),candidate_changes=0))
    print(json.dumps([dict(id=r['id'],native_exact=r['native_all_fields_exact'],diff=len(r['native_differences']))for r in rows]))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();run(a.name)
