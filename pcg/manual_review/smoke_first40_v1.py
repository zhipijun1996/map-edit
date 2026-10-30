"""One actual diagnostic per authored Route; never an independent certificate."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import argparse
from pcg.migration import core,physics
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose

def run(row,version):
    n=row['reviewId'];folder=core.REPO/row['outputDirectory'];eng,cases,authors=physics._engine(folder,'approved-b040-'+n+'-canonical-'+version,physics.FULL_PROTOCOL)
    core.write(eng.out/'protocol.json',dict(maximumAttempts=len(cases),newIndependentHoldout=False,purpose='one authored control per route; diagnostic only'))
    checks=[]
    try:
        for i,(c,r,e)in enumerate(eng.run([physics.fresh(c,'canonical-'+version)for c in cases],'canonical-'+version)):
            q=checked_purpose(authors[i],c,r);checks.append(dict(case=c,check=q,evidence=e));print(n,c['route_spec']['id'],q['ok'],q['reasons'],flush=True)
        core.write(eng.out/'canonical.json',dict(rows=checks,passed=all(v['check']['ok']for v in checks)))
    except Exception as ex:
        core.write(eng.out/'interruption.json',dict(error=str(ex)));print(n,type(ex).__name__,str(ex),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--version',required=True);p.add_argument('ids',nargs='+');a=p.parse_args()
    for row in core.read('feedback/manual-review/implementation-results/first-40-v1/authorization/handoff.json')['rows']:
        if row['reviewId']in a.ids:run(row,a.version)
