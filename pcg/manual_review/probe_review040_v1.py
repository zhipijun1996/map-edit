"""Bounded clean diagnostic, not a qualifier or independent holdout."""
import argparse
from pcg.migration import core,physics
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
AUTH=core.REPO/'feedback/manual-review/implementation-results/review-040-v1/authorization'
def run(row,version):
    folder=core.REPO/row['outputDirectory'];n=row['reviewId'];eng,cases,authors=physics._engine(folder,'approved-r040-'+n+'-canonical-'+version,physics.FULL_PROTOCOL);checks=[];playback=[]
    for i,(c,r,e)in enumerate(eng.run([physics.fresh(c,'clean-diagnostic-'+version)for c in cases],'clean-diagnostic')):
        q=checked_purpose(authors[i],c,r);checks.append(dict(case=c,check=q,evidence=e));print(n,c['route_spec']['id'],q['ok'],q['reasons'],flush=True)
        if q['ok']:playback.append(physics._recording(c,r))
    core.write(eng.out/'canonical.json',dict(rows=checks,passed=len(playback)==len(cases),orchestration=physics.artifact(__file__),independentHoldout=False));core.write(eng.out/'playback-cases.json',dict(cases=playback))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--version',required=True);p.add_argument('ids',nargs='+');a=p.parse_args()
    for row in core.read(AUTH/'handoff.json')['rows']:
        if row['reviewId']in a.ids:run(row,a.version)
