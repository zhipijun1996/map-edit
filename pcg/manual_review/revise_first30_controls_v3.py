"""Preserve v2 diagnostics, then apply bounded parameter/control corrections."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy,shutil
from pcg.migration import core,physics
from pcg.prototype.factory.core.quality import digest
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from .first30_content_v2 import decode


def run(row):
    n=row['reviewId'];folder=core.REPO/row['outputDirectory'];backup=folder/'revisions/pre-control-v3'
    if backup.exists():raise ValueError('control_revision_already_applied')
    backup.mkdir(parents=True)
    for name in ('module.mapnote.json','cases.json','parameters.json','thumbnail.svg'):
        if(folder/name).exists():shutil.copy2(folder/name,backup/name)
    doc=core.read(folder/'module.mapnote.json');cases=core.read(folder/'cases.json')['cases']
    if n=='12':
        for o in doc['objects']:
            if o['type']=='gate':o['mechanics']['openSeconds']=.2
    content=decode(doc)
    for c in cases:
        c.update(copy.deepcopy(content));a=c['route_spec']['from_port'];z=c['route_spec']['to_port']
        c['air_port_contracts']=[{k:p[k]for k in ('id','position','stagingPosition','face','surface','permission')}for p in doc['generationContract']['ports']if p['surface']=='AIR']
        p=c['control_plan']
        if n=='06':
            if a=='B':
                suffix=p[4:]
                p=[settle(850),wait_x(856,-1),ground(),cmd('wait',8),settle(560),cmd('jump'),cmd('jump_release',8),cmd('shoot',direction=[.9886859966642595,.15]),ground(),cmd('wait',12)]+suffix
            if z=='C':next(v for v in reversed(p)if v['op']=='jump_release')['trigger']['after']=8
        if n=='07':p=[cmd('axis',value=1),wait_x(307),cmd('jump'),cmd('jump_release',20),wait_x(535),cmd('shoot',aim_cell=dict(kind='bell',id='airlock-pair')),settle(744),ground(),cmd('wait',20)]
        if n=='12':
            c['required_rewards']=[v['id']for v in content['reward_sites']if abs(v['position'][0]-c['exit_port'][0])<60 and abs(v['position'][1]-c['exit_port'][1])<20]
            if a in ('A','D')and z in ('B','C'):
                shots=[v for v in p if v['op']=='shoot'];shots[-1]['direction']=[.4358898943540673 if z=='B'else-.4358898943540673,.9]
            elif z in ('A','D'):
                x=280 if z=='A'else 1000;end=c['exit_port'][0];direction=-1 if z=='A'else 1
                p=[]
                if a not in ('A','D'):
                    if a in ('B','C'):p=[settle(640),wait_x(620 if a=='B'else 660,1 if a=='B'else-1),ground(),cmd('wait',8)]
                    else:p=[settle(640),ground(),cmd('wait',8)]
                    p += [cmd('shoot',aim_cell=dict(kind='bell',id='return-catch',receiver='access')),cmd('wait',30),ground(),cmd('wait',8)]
                p += [settle(x),wait_x(x-direction*6,direction),ground(),cmd('wait',8),cmd('jump'),settle(end),cmd('jump_release',20),ground(),cmd('wait',20)]
                c['route_spec']['require_bell']=a not in ('A','D')
        if n=='23':
            if a=='A'and z=='B':p=[cmd('axis',value=-1),wait_x(-285,-1),cmd('shoot',direction=[-1,0]),cmd('axis',9,value=1),settle(360,6)]
            elif a=='A':p=[settle(-320),wait_x(-314,-1),cmd('wait',20)]
            else:p=[cmd('axis',value=-1),cmd('jump'),cmd('jump_release',8),cmd('shoot',direction=[1,.1]),settle(-320),wait_x(-314,-1),cmd('wait',20)]
        if n=='28'and a=='B':p=[settle(700),wait_x(706,-1),ground(),cmd('wait',8),cmd('jump'),settle(152),cmd('jump_release',20),cmd('shoot',aim_cell=dict(kind='bell',id='short-bell',receiver='access')),ground(),cmd('wait',20)]
        c['control_plan']=p;c['id']+='-control-v3';c['expected_reward']=sum(v['amount']for v in content['reward_sites']if v['id']in c['required_rewards'])
    doc['generationContract']['generation']['approvedImplementation']['controlProgramsSha256']=digest([c['control_plan']for c in cases])
    core.write(folder/'module.mapnote.json',doc);core.contract(folder/'module.mapnote.json',refresh=True)
    core.write(folder/'cases.json',dict(cases=cases));core.write(folder/'parameters.json',dict(designVersion=row['designVersion'],content=content,controls=[dict(route=c['route_spec'],control_plan=c['control_plan'])for c in cases],revision=3,productionApproval=False))
    print(n,'control revision 3',flush=True)


if __name__=='__main__':
    for row in core.read('feedback/manual-review/implementation-results/first-30-v2/authorization/handoff.json')['rows']:
        if row['reviewId']in('06','07','12','23','28'):run(row)
