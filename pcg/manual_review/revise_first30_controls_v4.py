"""Real height feedback, original upper receiver API and same-world carrier timing."""
import copy,shutil
from pcg.migration import core
from pcg.prototype.factory.core.quality import digest
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from .first30_content_v2 import decode


def run(row):
    n=row['reviewId'];folder=core.REPO/row['outputDirectory'];backup=folder/'revisions/pre-control-v4'
    if backup.exists():raise ValueError('already_revised')
    backup.mkdir(parents=True)
    for name in ('module.mapnote.json','cases.json','parameters.json','thumbnail.svg'):
        if(folder/name).exists():shutil.copy2(folder/name,backup/name)
    doc=core.read(folder/'module.mapnote.json');cases=core.read(folder/'cases.json')['cases']
    if n=='12':
        next(o for o in doc['objects']if o['id']=='design-upper-return-bell')['mechanics']['returnSideOnly']=False
    content=decode(doc)
    for c in cases:
        c.update(copy.deepcopy(content));a=c['route_spec']['from_port'];z=c['route_spec']['to_port'];p=c['control_plan']
        if n=='06':
            if a=='B':
                source=core.read((core.REPO/row['sourceModule']['file']).parent/'cases.json')['cases']
                p=[settle(850),wait_x(856,-1),ground(),cmd('shoot',aim_cell=dict(kind='bell',id='upper-route-gears')),cmd('wait',36),settle(850),wait_x(856,-1),ground(),
                   cmd('jump'),settle(688),cmd('jump_release',20),ground(),cmd('wait',12)]
                p += copy.deepcopy(source[1]['control_plan'][14:])if z=='C'else[settle(430),wait_x(436,-1),ground(),settle(24),wait_x(30,-1),ground(),cmd('wait',20)]
            if z=='C':
                last=next(v for v in reversed(p)if v['op']=='jump_release');last['trigger']=dict(dynamic=dict(kind='actor_y',direction='lte',value=162),timeout=90)
        if n=='12':
            if a in('B','C','E')and z in('B','C'):
                launch=420 if z=='B'else 860;direction=-1 if z=='B'else 1;end=c['exit_port'][0]
                p=[settle(launch),wait_x(launch-direction*6,direction),ground(),cmd('wait',8),cmd('jump'),settle(end),cmd('jump_release',20),
                   cmd('shoot',direction=[.4358898943540673 if z=='B'else-.4358898943540673,.9]),ground(),cmd('wait',20)]
            for v in p:
                if v.get('trigger',{}).get('dynamic',{}).get('kind')=='actor_x':v['trigger']['timeout']=475
        if n=='17':
            if a=='A':
                p[1]['trigger']['after']=135
            else:
                p=[cmd('axis',value=-1),wait_x(1044,-1),cmd('axis',value=0),ground(),cmd('wait',8),cmd('shoot',aim_cell=dict(kind='bell',id='return-control')),cmd('wait',215),
                   cmd('axis',value=-1),cmd('jump'),cmd('jump_release',12),dict(op='wait',trigger=dict(dynamic=dict(kind='on_platform',id='return-deck'),timeout=240)),cmd('axis',value=0),
                   dict(op='wait',trigger=dict(dynamic=dict(kind='actor_x',direction='lte',value=360),timeout=475)),cmd('axis',value=-1),cmd('jump'),cmd('jump_release',20),
                   cmd('shoot',direction=[.8,.6]),settle(152),ground(),cmd('wait',20)]
        if n=='23'and z=='C':p=[v for v in p if not(v['op']=='wait'and v.get('trigger',{}).get('after')==20)]
        if n=='28'and a=='B':
            p=[settle(600),wait_x(606,-1),ground(),cmd('wait',8),cmd('shoot',aim_cell=dict(kind='bell',id='short-bell',receiver='access')),
               dict(op='jump',trigger=dict(state='grounded_shot_ready',after=15,timeout=90)),settle(152),cmd('jump_release',8),cmd('shoot',direction=[.916515138991168,.4]),ground(),cmd('wait',20)]
        c['control_plan']=p;c['id']+='-control-v4'
    doc['generationContract']['generation']['approvedImplementation']['controlProgramsSha256']=digest([c['control_plan']for c in cases])
    core.write(folder/'module.mapnote.json',doc);core.contract(folder/'module.mapnote.json',refresh=True)
    core.write(folder/'cases.json',dict(cases=cases));core.write(folder/'parameters.json',dict(designVersion=row['designVersion'],content=content,controls=[dict(route=c['route_spec'],control_plan=c['control_plan'])for c in cases],revision=4,productionApproval=False))


if __name__=='__main__':
    for row in core.read('feedback/manual-review/implementation-results/first-30-v2/authorization/handoff.json')['rows']:
        if row['reviewId']in('06','12','17','23','28'):run(row)
