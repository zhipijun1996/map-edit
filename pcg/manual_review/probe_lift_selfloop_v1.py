"""Full-body same-Port ingress/retry/egress in one original live world."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core,physics
from .lift_idea_v1 import rows
from .finalize_lift_v1 import folder_for
from .probe_ideas_recovery_v1 import build_loop,observe_loop

def main():
    folder=folder_for(rows()[0]);eng,cases,_=physics._engine(folder,'approved-lift-selfloop-v1',physics.FULL_PROTOCOL)
    case=build_loop(next(c for c in cases if c['route_spec']['id']=='A-to-A-retry'),core.read(folder/'module.mapnote.json'))
    results=[]
    for c,r,e in eng.run([case],'full-port-selfloop'):
        check=observe_loop(c,r)
        stable=len({f['actor_epoch']for f in r['frames']})==1 and not r['returns']
        check.update(sameActorAndWorld=stable)
        check['passed']=bool(r['ok'] and r['hp']==5 and stable and check['sequence']==['outside','inside','outside'] and all(v['aperture']for v in check['crossing']) and all(b['module_clock']>a['module_clock']for a,b in zip(r['frames'],r['frames'][1:])))
        results.append(dict(check=check,evidence=e));print(check,flush=True)
    core.write(eng.out/'selfloop-checks.json',dict(rows=results,simulationTrials=1,independentHoldout=False))
if __name__=='__main__':main()
