"""Bounded calibration-only repairs; actual router inputs, unchanged design/physics."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import argparse
import copy
import math
from pcg.migration import core, physics
from pcg.prototype.workshop.rules import cmd, wait_x, ground, settle
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose

ROWS=core.read(core.REPO/'feedback/manual-review/implementation-results/first-30-v2/authorization/handoff.json')['rows']


def variants(n,base):
    out=[]
    if n=='01':
        for pause in (8,16,24):
            c=copy.deepcopy(base);c['control_plan'][11:11]=[ground(),cmd('wait',pause)]
            c['id']+='-reground-'+str(pause);out.append(c)
    elif n=='02':
        for dy,hold in ((.92,20),(.96,20),(.92,24),(.96,24),(.90,16),(.94,16)):
            c=copy.deepcopy(base);c['control_plan'][28]['trigger']['after']=hold
            c['control_plan'][29]['direction']=[-math.sqrt(1-dy*dy),dy]
            c['id']+=f'-crest-{dy}-{hold}';out.append(c)
    else:
        # Kill the diver from the full original A bank with accepted ground
        # shots; a fixed-direction recoil crosses to the existing tiny perch.
        for entry_dy in (.30,.45):
            for reverse_after in (15,18,21):
                c=copy.deepcopy(base);p=[settle(-144),wait_x(-150),ground(),cmd('wait',8)]
                for shot in range(3):
                    p += [cmd('shoot',aim_cell=dict(kind='enemy',id='review-gap-diver'),direction=[1,-.5]),cmd('wait',22),ground(),wait_x(-150),cmd('wait',8)]
                p += [settle(128),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[-math.sqrt(1-entry_dy*entry_dy),entry_dy]),ground(),cmd('wait',12)]
                # Every cycle really jumps, fires at the guard, waits for the
                # original projectile refund, reverses recoil and lands/refills.
                for cycle in range(3):
                    p += [cmd('jump'),cmd('jump_release',20),cmd('shoot',aim_cell=dict(kind='enemy',id='review-cache-sentry'),direction=[1,0]),
                          cmd('shoot',reverse_after,direction=[-.99498743710662,-.1]),ground(),cmd('wait',12)]
                p += [settle(488),wait_x(140),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[-.916515138991168,.4]),ground(),cmd('wait',20)]
                c.update(control_plan=p,max_frames=2400);c['id']+=f'-clear-guards-{entry_dy}-{reverse_after}';out.append(c)
    return out


def run(n):
    row=next(r for r in ROWS if r['reviewId']==n);folder=core.REPO/row['outputDirectory']
    route={'01':'D-to-C','02':'reward-outbound','03':'high-investment'}[n]
    base=next(c for c in core.read(folder/'cases.json')['cases'] if c['route_spec']['id']==route)
    cases=variants(n,base)
    eng,_,authors=physics._engine(folder,'approved-b001-'+n+'-repair-v5',physics.FULL_PROTOCOL)
    author=next(a for a in authors if a is not None)
    core.write(eng.out/'repair-protocol.json',dict(source=physics.artifact(__file__),
        geometryChanges=False,enemyChanges=False,canonicalCandidates=len(cases),
        maximumMildScreens=len(cases),trialsPerScreen=6,maximumAttempts=len(cases)*7,
        selection='first canonical pass with at least 5 of 6 mild calibration trials',
        calibrationSeed=2810285100,holdout='NOT_RUN',qualityGateUnchanged=True))
    checks=[];passing=[]
    for c,r,e in eng.run([physics.fresh(c,'v5-canonical') for c in cases],'repair-canonical'):
        check=checked_purpose(author,c,r);checks.append(dict(case=c,check=check,evidence=e))
        print(n,c['id'],check['ok'],check['reasons'],flush=True)
        if check['ok']:passing.append(c)
    selected=None;screens=[]
    for base in passing:
        expanded=[instantiate(base,2810285100,'mild',i) for i in range(6)];observed=[]
        for c,r,e in eng.run(expanded,'repair-mild-screen'):
            check=checked_purpose(author,c,r);observed.append(dict(check=check,evidence=e))
        successes=sum(r['check']['ok'] for r in observed);screens.append(dict(case=base,passed=successes,trials=6,rows=observed))
        print(n,'mild',base['id'],successes,'/6',flush=True)
        if successes>=5:
            selected=base;break
    core.write(eng.out/'repair-check.json',dict(rows=checks,screens=screens,selected=selected,technicalAdmission=False,actualAttempts=eng.sim.cases))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('ids',nargs='+',choices=['01','02','03'])
    for n in parser.parse_args().ids:run(n)
