"""Real canonical replays and native packages; no holdout reruns or promotion."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import argparse,copy
from pcg.migration import core,physics,godot_package
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose


def folder_for(row):
    n=row['reviewId']
    if n=='01':return core.REPO/'pcg/manual_review/implementation/first-30-v2'/row['moduleId']
    if n in('02','03'):return core.REPO/'pcg/manual_review/implementation/first-30-v4'/row['moduleId']
    return core.REPO/row['outputDirectory']


def run(row):
    folder=folder_for(row);n=row['reviewId']
    eng,cases,authors=physics._engine(folder,'approved-b001-first30-'+n+'-delivery-canonical-v7',physics.FULL_PROTOCOL)
    core.write(eng.out/'delivery-protocol.json',dict(source=physics.artifact(__file__),maximumAttempts=len(cases),purpose='native frozen replay input',newIndependentHoldout=False))
    checks=[];recorded=[]
    for i,(c,r,e)in enumerate(eng.run([physics.fresh(c,'delivery-canonical')for c in cases],'native-delivery-canonical')):
        q=checked_purpose(authors[i],c,r);checks.append(dict(case=c,check=q,evidence=e))
        print(n,c['route_spec']['id'],q['ok'],q['reasons'],flush=True)
        if q['ok']:recorded.append(physics._recording(c,r))
    core.write(eng.out/'canonical.json',dict(rows=checks,passed=all(v['check']['ok']for v in checks)))
    if len(recorded)!=len(cases):return
    core.write(folder/'playback-cases.json',dict(cases=recorded));out=folder/'playable'
    godot_package.compile_package(folder/'module.mapnote.json',folder/'playback-cases.json',out,stable_id=row['moduleId'])
    result=godot_package.run_package_validation(out);core.write(folder/'package-result.json',result)
    print(n,'native',result['passed'],len(recorded),'routes',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('ids',nargs='+');a=p.parse_args()
    for row in core.read('feedback/manual-review/implementation-results/first-30-v2/authorization/handoff.json')['rows']:
        if row['reviewId']in a.ids:run(row)
