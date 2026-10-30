"""Finish the cropped upper jump; preserve bridge state in an explicit real loop."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy,shutil
from pcg.migration import core
from pcg.prototype.factory.core.quality import digest
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle


def revise06(row):
    folder=core.REPO/row['outputDirectory'];backup=folder/'revisions/pre-control-v6';backup.mkdir(parents=True)
    for name in ('cases.json','module.mapnote.json','parameters.json','thumbnail.svg'):shutil.copy2(folder/name,backup/name)
    cases=core.read(folder/'cases.json')['cases']
    for c in cases:
        if c['route_spec']['to_port']!='C':continue
        p=c['control_plan'];start=max(i for i,v in enumerate(p)if v['op']=='settle'and v['target_x']==24)
        c['control_plan']=p[:start]+[settle(356),wait_x(362,-1),ground(),cmd('wait',8),cmd('jump'),settle(24),
            dict(op='jump_release',trigger=dict(dynamic=dict(kind='actor_y',direction='lte',value=156),timeout=90)),ground(),cmd('wait',20)]
        c['id']+='-control-v6'
    doc=core.read(folder/'module.mapnote.json');doc['generationContract']['generation']['approvedImplementation']['controlProgramsSha256']=digest([c['control_plan']for c in cases])
    core.write(folder/'module.mapnote.json',doc);core.contract(folder/'module.mapnote.json',refresh=True);core.write(folder/'cases.json',dict(cases=cases))


def loop17(row):
    folder=core.REPO/row['outputDirectory'];out=core.read(folder/'cases.json')['cases'][0];c=copy.deepcopy(out)
    p=copy.deepcopy(c['control_plan'])+[settle(1044),wait_x(1050,-1),ground(),cmd('wait',8),cmd('jump'),settle(768),cmd('jump_release',12),
        dict(op='wait',trigger=dict(dynamic=dict(kind='on_platform',id='return-deck'),timeout=240)),wait_x(774,-1),ground()]
    for _ in range(8):
        block=[dict(op='axis',value=-1,cancel_settle=True,trigger=dict(after=0)),cmd('jump'),cmd('jump_release',20),cmd('shoot',aim_cell=dict(kind='bell',id='return-control',target_offset=[0,-10])),
            dict(op='axis',value=0,cancel_settle=True,trigger=dict(after=0)),dict(op='wait',trigger=dict(dynamic=dict(kind='on_platform',id='return-deck'),timeout=240)),
            cmd('wait',20),settle(768),wait_x(774,-1)]
        for v in block:v['skip_if_carrier_running']='return-deck'
        p+=block
    p += [dict(op='axis',value=0,cancel_settle=True,trigger=dict(after=0)),dict(op='wait',trigger=dict(dynamic=dict(kind='on_platform',id='return-deck'),timeout=240)),
        dict(op='wait',trigger=dict(dynamic=dict(kind='actor_x',direction='lte',value=420),timeout=475)),cmd('axis',value=-1),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[.8,.6]),settle(152),ground(),cmd('wait',20)]
    assert len(p)<=128,len(p)
    c.update(id='approved-first30-17-same-world-A-C-A-v6',control_plan=p,max_frames=3600,exit_port=[152,420],goal=[145,416,14,8],fixture_kind='same-world-A-C-A')
    c['route_spec']=dict(id='A-C-A-earned-return',from_port='A',to_port='A',role='return',require_bell=True)
    c['approved_first30']['conditionalReturn']=dict(fromPort='C',toPort='A',requires='Actual A-to-C approach leaves the original bridge parked on the reward side; no world rebuild or state injection',freshCQualification=False)
    core.write(folder/'same-world-return-cases.json',dict(cases=[c],scope='earned C-to-A return within actual A-C-A; fresh C remains UNKNOWN'))
    return folder


if __name__=='__main__':
    for row in core.read('feedback/manual-review/implementation-results/first-30-v2/authorization/handoff.json')['rows']:
        if row['reviewId']=='06':revise06(row)
        if row['reviewId']=='17':loop17(row)
