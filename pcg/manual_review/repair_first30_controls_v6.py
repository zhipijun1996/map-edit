"""Second bounded repair: staged guard hop and observed real refund readiness."""
import argparse,copy
from pcg.migration import core,physics
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
from .repair_first30_controls_v5 import ROWS


def run(n):
    row=next(r for r in ROWS if r['reviewId']==n);folder=core.REPO/row['outputDirectory']
    cases=core.read(folder/'cases.json')['cases'];base=copy.deepcopy(cases[0]);probes=[]
    if n=='02':
        for landing,hold in ((1072,6),(1080,6),(1088,6),(1072,8),(1080,8),(1088,8)):
            c=copy.deepcopy(base);p=c['control_plan'][:26]
            p += [settle(landing),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[-.5,.8660254037844386]),wait_x(landing-6),ground(),cmd('wait',6),
                  settle(1184),cmd('jump'),cmd('jump_release',hold),ground(),cmd('wait',8),settle(1512),wait_x(1506),ground(),cmd('wait',20)]
            c['control_plan']=p;c['id']+=f'-staged-crest-{landing}-{hold}';probes.append(c)
    else:
        selected=core.read(core.REPO/'pcg/results/approved-b001-03-repair-v5/repair-check.json')['selected']
        for reverse_delay in (0,2,4):
            c=copy.deepcopy(selected)
            for v in c['control_plan']:
                if v['op']=='shoot'and v.get('direction')==[-.99498743710662,-.1]:
                    v['trigger']=dict(state='shot_ready',after=reverse_delay,timeout=60)
            c['id']+=f'-observed-refund-{reverse_delay}';probes.append(c)
    # All cases use one unchanged original-physics runner, with additive
    # observation conditions only. No resources or actor motion are assigned.
    bound_folder=core.REPO/'pcg/manual_review/implementation/first-30-v2-control-probes'/row['moduleId']
    for c in cases:c['generation_rule']['registration_source']='pcg/manual_review/approved_r'+n+'_v2.py'
    core.write(bound_folder/'cases.json',dict(cases=cases))
    eng,_,authors=physics._engine(bound_folder,'approved-b001-'+n+'-repair-v6',physics.FULL_PROTOCOL);author=authors[0]
    core.write(eng.out/'repair-protocol.json',dict(source=physics.artifact(__file__),maximumAttempts=len(probes)*7,
        levels='canonical then six moderate calibration probes',selection='first canonical pass with at least 5/6 moderate',
        calibrationSeed=2810286100,geometryChanges=False,holdout='NOT_RUN'))
    rows=[];passing=[]
    for base in probes:base['generation_rule']['registration_source']='pcg/manual_review/approved_r'+n+'_v2.py'
    for c,r,e in eng.run([physics.fresh(c,'canonical')for c in probes],'repair-canonical'):
        q=checked_purpose(author,c,r);rows.append(dict(case=c,check=q,evidence=e));print(n,c['id'],q['ok'],q['reasons'],flush=True)
        if q['ok']:passing.append(c)
    screens=[];selected=None
    for base in passing:
        observed=[]
        for c,r,e in eng.run([instantiate(base,2810286100,'moderate',i)for i in range(6)],'repair-moderate-screen'):
            q=checked_purpose(author,c,r);observed.append(dict(check=q,evidence=e))
        passed=sum(v['check']['ok']for v in observed);screens.append(dict(case=base,rows=observed,passed=passed,trials=6));print(n,'moderate',passed,'/6',flush=True)
        if passed>=5:selected=base;break
    core.write(eng.out/'repair-check.json',dict(rows=rows,screens=screens,selected=selected,technicalAdmission=False,actualAttempts=eng.sim.cases))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('ids',nargs='+',choices=['02','03'])
    for n in p.parse_args().ids:run(n)
