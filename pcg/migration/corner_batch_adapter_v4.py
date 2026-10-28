"""V4 fills only native-long-plan corner bindings; frozen v2/v3 stay unchanged."""
from __future__ import annotations
import copy
import subprocess
from pathlib import Path
from . import core, boundary_runtime_extended as boundary_runtime
from . import corner_batch_adapter as v2, corner_batch_adapter_v3 as v3

SCHEMA=v2.SCHEMA
POLICY=v2.POLICY
_wait=v3._wait
_vertical_actions=v3._vertical_actions
lower_obstructed_bottom_dock=v3.lower_obstructed_bottom_dock
SOURCE_DEPENDENCIES=[Path(v2.__file__),Path(v3.__file__),Path(boundary_runtime.__file__)]


def configuration_id(port_id,corner):
    return v2.configuration_id(port_id,corner).removesuffix('-v2')+'-v4'


def bind_vertical_controls(document,input_cases,port_id):
    """Use real goal rectangles, never target_x +/- a guessed settle deadband."""
    doc,cases=copy.deepcopy(document),copy.deepcopy(input_cases)
    port=next(p for p in doc['generationContract']['ports']if p['id']==port_id)
    x,y=port['stagingPosition'];inside=[x-6,y-5,12,10]
    if port['normal'][0]:raise v2.AdaptationGap('vertical_controller_requires_vertical_corner')
    for case in cases:
        plans=case.setdefault('migration_boundary_plans',{}).setdefault(port_id,{})
        route=case['route_spec']
        if route['to_port']==port_id:
            # Canonical actions retain their exact coordinates/parameters. Wait
            # for their actual accepted terminal goal, then walk to the new dock.
            # A real settle(deadband=4) may stop at target-3.41; hardcoding +/-3
            # incorrectly times out despite a valid stable original goal.
            plan=copy.deepcopy(case['control_plan'])
            plan += [_wait(case['goal']),dict(op='settle',trigger=dict(after=0),target_x=x,deadband=2),_wait(inside)]
            plan += _vertical_actions(port['normal'])
            plans['egress']=plan
        if route['from_port']==port_id:
            # Cross at the actual anchor before moving sideways toward the
            # original starting pose. Early sideways steering can violate the
            # complete-body aperture even though the original spawn is reachable.
            plan=[dict(op='settle',trigger=dict(after=0),target_x=x,deadband=2)]
            plan+=_vertical_actions([0,-port['normal'][1]])
            plan += [_wait(inside),dict(op='settle',trigger=dict(after=0),target_x=case['spawn'][0],deadband=2)]
            plans['ingress']=plan
    doc,cases,records=boundary_runtime.bind(doc,cases)
    doc['generationContract']['generation']['cornerConfiguration']['boundaryControlRevision']='goal-rectangle-vertical/v4-native-budget'
    return doc,cases,records

def prepare(source,out,port_id,corner):
    source,out=Path(source).resolve(),Path(out).resolve()
    result=v2.prepare(source,out,port_id,corner)
    doc=core.read(out/'module.mapnote.json');cases=core.read(out/'cases.json')['cases']
    doc,cases,drop=lower_obstructed_bottom_dock(doc,cases,port_id)
    doc,cases,controllers=bind_vertical_controls(doc,cases,port_id)
    config=configuration_id(port_id,corner)
    doc['generationContract']['generation']['cornerConfiguration']['id']=config
    meta=core.read(out/'migration.json');meta['cornerConfiguration']['id']=config
    core.write(out/'module.mapnote.json',doc);core.write(out/'cases.json',dict(cases=cases));core.write(out/'migration.json',meta)
    script="""import fs from 'node:fs';import {canonical,sha256} from './module-contract.js';const p=process.argv[1],d=JSON.parse(fs.readFileSync(p));for(const c of d.generationContract.composition.cells){const os=c.objectIds.map(id=>d.objects.find(o=>o.id===id));c.contentVersion='sha256:'+sha256(canonical(os.length===1?os[0]:os));}fs.writeFileSync(p,JSON.stringify(d,null,2)+'\\n');"""
    subprocess.run(['node','--input-type=module','-e',script,str(out/'module.mapnote.json')],cwd=core.REPO,check=True)
    core.contract(out/'module.mapnote.json',refresh=True)
    doc=core.read(out/'module.mapnote.json');adaptation=core.read(out/'corner-adaptation.json')
    adaptation.update(configurationId=config,targetDocumentSha256=core.sha(out/'module.mapnote.json'),
        targetPort=next(p for p in doc['generationContract']['ports']if p['id']==port_id),
        adapterRevision='corner-open-v4',newDockDrop=drop,boundaryControllers=controllers)
    for row in adaptation['addedObjects']:
        obj=next(o for o in doc['objects']if o['id']==row['id']);row['rect']=v2._rect(obj)
    core.write(out/'corner-adaptation.json',adaptation)
    protocol=core.read(out/'corner-protocol.json');protocol.update(configurationId=config,
        frozenTargetDocumentSha256=core.sha(out/'module.mapnote.json'),adapterRevision='corner-open-v4',
        selection='One predeclared open-side candidate with guarded vertical docking and at most16px new-dock lowering; no holdout reselection')
    core.write(out/'corner-protocol.json',protocol)
    return {**result,'configurationId':config,'adapterRevision':'corner-open-v4','newDockDropPixels':drop['pixels']}
