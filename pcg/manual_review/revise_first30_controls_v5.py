"""Receiver visibility and real landing/refill routes; no design edits."""
import copy,shutil
from pcg.migration import core
from pcg.prototype.factory.core.quality import digest
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle


def run(row):
    n=row['reviewId'];folder=core.REPO/row['outputDirectory'];backup=folder/'revisions/pre-control-v5'
    if backup.exists():raise ValueError('already_revised')
    backup.mkdir(parents=True)
    for name in ('module.mapnote.json','cases.json','parameters.json','thumbnail.svg'):
        if(folder/name).exists():shutil.copy2(folder/name,backup/name)
    doc=core.read(folder/'module.mapnote.json');cases=core.read(folder/'cases.json')['cases']
    for c in cases:
        a=c['route_spec']['from_port'];z=c['route_spec']['to_port'];p=c['control_plan']
        if n=='17'and a=='C':
            p=[cmd('axis',value=-1),wait_x(1044,-1),cmd('axis',value=0),ground()]
            for i in range(16):
                block=[cmd('shoot',aim_cell=dict(kind='bell',id='return-control',target_offset=[0,12])),cmd('wait',90),cmd('axis',value=-1),wait_x(1044,-1),cmd('axis',value=0),ground()]
                for v in block:v['skip_if_carrier_running']='return-deck'
                p+=block
            p += [cmd('axis',value=-1),wait_x(1044,-1),cmd('axis',value=0),ground(),
                dict(op='wait',trigger=dict(state='carrier_x_gte',timeout=475),carrier_id='return-deck',carrier_value=850),
                cmd('axis',value=-1),cmd('jump'),cmd('jump_release',12),dict(op='wait',trigger=dict(dynamic=dict(kind='on_platform',id='return-deck'),timeout=240)),cmd('axis',value=0),
                dict(op='wait',trigger=dict(dynamic=dict(kind='actor_x',direction='lte',value=420),timeout=475)),cmd('axis',value=-1),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[.8,.6]),settle(152),ground(),cmd('wait',20)]
            c['max_frames']=3600
        if n=='23':
            if z=='B':
                p=[cmd('axis',value=-1),wait_x(-285,-1),cmd('shoot',direction=[-1,0]),cmd('axis',9,value=1),settle(100,6),wait_x(94),ground()]
                for i in range(12):
                    p.append(dict(op='shoot',trigger=dict(state='grounded_shot_ready',after=36,timeout=180,dynamic=dict(kind='actor_x',direction='gte',value=94)),
                        skip_if_enemy_dead='design-lower-entry-sentry',aim_cell=dict(kind='enemy',id='design-lower-entry-sentry'),direction=[1,0]))
                p += [settle(360),wait_x(354),ground(),cmd('wait',20)]
            elif a=='B':
                p=[cmd('axis',value=-1),cmd('jump'),cmd('jump_release',8),cmd('shoot',direction=[1,.1]),settle(-64),wait_x(-58,-1),ground(),cmd('wait',8),
                    cmd('jump'),settle(-320),cmd('jump_release',8),cmd('shoot',direction=[1,.1]),wait_x(-314,-1)]
        c['control_plan']=p;c['id']+='-control-v5'
    doc['generationContract']['generation']['approvedImplementation']['controlProgramsSha256']=digest([c['control_plan']for c in cases])
    core.write(folder/'module.mapnote.json',doc);core.contract(folder/'module.mapnote.json',refresh=True)
    core.write(folder/'cases.json',dict(cases=cases));parameters=core.read(folder/'parameters.json');parameters['controls']=[dict(route=c['route_spec'],control_plan=c['control_plan'])for c in cases];parameters['revision']=5;core.write(folder/'parameters.json',parameters)


if __name__=='__main__':
    for row in core.read('feedback/manual-review/implementation-results/first-30-v2/authorization/handoff.json')['rows']:
        if row['reviewId']in('17','23'):run(row)
