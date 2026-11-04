"""One actual canonical per approved route; diagnostic, never qualification."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import argparse
from pathlib import Path
from pcg.migration import core,physics
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose


def run(row):
    n=row['reviewId'];folder=core.REPO/row['outputDirectory']
    eng,cases,authors=physics._engine(folder,'approved-b001-first30-'+n+'-canonical-v3',physics.FULL_PROTOCOL)
    core.write(eng.out/'diagnostic-protocol.json',dict(source=physics.artifact(__file__),maximumAttempts=len(cases),
        selection='none; one unchanged authored program per declared route',holdout='NOT_RUN',technicalAdmission=False))
    rows=[]
    for i,(c,r,e)in enumerate(eng.run([physics.fresh(c,'canonical')for c in cases],'approved-canonical')):
        q=checked_purpose(authors[i],c,r);rows.append(dict(case=c,check=q,evidence=e,
            result={k:r.get(k)for k in ('ok','reason','hp','shots','jumps','ticks','plan_error','minimum_goal_distance')}))
        print(n,c['route_spec']['id'],q['ok'],q['reasons'],flush=True)
    core.write(eng.out/'canonical.json',dict(rows=rows,passed=all(v['check']['ok']for v in rows),technicalAdmission=False))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('ids',nargs='*');a=p.parse_args()
    for row in core.read('feedback/manual-review/implementation-results/first-30-v2/authorization/handoff.json')['rows']:
        if int(row['reviewId'])>5 and (not a.ids or row['reviewId']in a.ids):run(row)
