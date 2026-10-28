"""Correct runner binding and state-trigger validation for bounded repair: staged guard hop and observed real refund readiness."""
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
        for landing,height in ((1088,42),(1080,42),(1088,48),(1080,48)):
            c=copy.deepcopy(base);p=c['control_plan'][:26]
            p += [settle(landing),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[-.5,.8660254037844386]),wait_x(landing-6),ground(),cmd('wait',8),
                  cmd('jump'),settle(1184),dict(op='jump_release',trigger=dict(dynamic=dict(kind='actor_y',direction='lte',value=height),timeout=90)),ground(),cmd('wait',8),
                  settle(1512),wait_x(1506),ground(),cmd('wait',20)]
            c['control_plan']=p;c['id']+=f'-observed-crest-head-{landing}-{height}';probes.append(c)
    else:
        high=core.read(core.REPO/'pcg/results/approved-b001-03-repair-v11/repair-check.json')['selected']
        low=copy.deepcopy(cases[1]);low['control_plan']=copy.deepcopy(high['control_plan'][:-6])+[cmd('jump'),settle(488),dict(op='shoot',trigger=dict(state='apex',timeout=90),direction=[-1,0]),cmd('jump_release'),ground(),cmd('wait',20)]
        low['id']+='-cleared-low-apex';low['max_frames']=2400;probes=[low]
    # All cases use one unchanged original-physics runner, with additive
    # observation conditions only. No resources or actor motion are assigned.
    bound_folder=core.REPO/'pcg/manual_review/implementation/first-30-v2-control-probes'/row['moduleId']
    for c in cases:c['generation_rule']['registration_source']='pcg/manual_review/approved_r'+n+'_v4.py'
    core.write(bound_folder/'cases.json',dict(cases=cases))
    eng,_,authors=physics._engine(bound_folder,'approved-b001-'+n+'-repair-v13',physics.FULL_PROTOCOL);author=authors[0]
    core.write(eng.out/'repair-protocol.json',dict(source=physics.artifact(__file__),maximumAttempts=len(probes)*7,
        levels='canonical then six moderate calibration probes',selection='first canonical pass with at least 5/6 moderate',
        calibrationSeed=2810286100,geometryChanges=False,holdout='NOT_RUN'))
    rows=[];passing=[]
    for base in probes:base['generation_rule']['registration_source']='pcg/manual_review/approved_r'+n+'_v4.py'
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
