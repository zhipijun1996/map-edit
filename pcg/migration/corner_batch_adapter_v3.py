"""New corner candidate revision: guarded vertical docking, optional 0..16px drop.

V2 prepared candidates/raw remain immutable. Runtime movement still comes from
boundary_runtime's existing real input router; no physics is implemented here.
"""
from __future__ import annotations
import copy
import subprocess
from pathlib import Path
from . import core, boundary_runtime, corner_batch_adapter as v2

SCHEMA=v2.SCHEMA
POLICY=v2.POLICY


def configuration_id(port_id,corner):
    return v2.configuration_id(port_id,corner).removesuffix('-v2')+'-v3'


def _wait(goal,after=0,timeout=360):
    return dict(op='wait',trigger=dict(after=after,state='grounded',migration_goal=list(goal),timeout=timeout))


def _vertical_actions(normal):
    down=normal[1]>0
    plan=[dict(op='drop_through'if down else'jump',trigger=dict(after=1))]
    if not down:plan.append(dict(op='jump_release',trigger=dict(after=24)))
    return plan


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
    doc['generationContract']['generation']['cornerConfiguration']['boundaryControlRevision']='goal-rectangle-vertical/v3'
    return doc,cases,records


def lower_obstructed_bottom_dock(document,input_cases,port_id):
    """Leave original roofs intact; lower only the newly introduced OWP dock."""
    doc,cases=copy.deepcopy(document),copy.deepcopy(input_cases)
    port=next(p for p in doc['generationContract']['ports']if p['id']==port_id)
    dock=next(o for o in doc['objects']if o['id']==port['support']['objectId'])
    old=v2._rect(dock);drop=0;obstructions=[]
    if port['face']=='BOTTOM':
        x=port['position'][0];floor=dock['y']
        for obj in doc['objects']:
            if obj['type']!='terrain'or obj.get('trackId'):continue
            bottom=obj['y']+obj['h']
            if obj['x']<x+14 and obj['x']+obj['w']>x-14 and floor-38<bottom<=floor:
                obstructions.append(dict(objectId=obj['id'],rect=v2._rect(obj)))
                drop=max(drop,bottom+38-floor)
    if drop>16+1e-7:raise v2.AdaptationGap('local_body_clearance_needs_dock_drop_over_16px')
    if drop:
        if dock['h']-drop<4:raise v2.AdaptationGap('local_dock_drop_would_leave_corner_block')
        dock['y']+=drop;dock['h']-=drop
        port['stagingPosition'][1]+=drop
        port['crossing_offset'][1]+=drop
        for case in cases:
            case['platforms'][dock['sourceIndex']]=v2._rect(dock)
            cp=next(p for p in case['ports']if p['id']==port_id);cp['position']=list(port['stagingPosition'])
            bp=case['block_ports'][port_id];bp['stagingPosition']=list(port['stagingPosition']);bp['crossing_offset']=list(port['crossing_offset'])
            if isinstance(bp.get('grid'),dict):bp['grid']['stagingPosition']=list(port['stagingPosition'])
        if isinstance(port.get('grid'),dict):port['grid']['stagingPosition']=list(port['stagingPosition'])
    return doc,cases,dict(pixels=drop,before=old,after=v2._rect(dock),unchangedCeilingObjects=obstructions,
                          reason='Minimum 36px body clearance plus 2px margin; only the new OWP moves, never the original roof.')


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
        adapterRevision='corner-open-v3',newDockDrop=drop,boundaryControllers=controllers)
    for row in adaptation['addedObjects']:
        obj=next(o for o in doc['objects']if o['id']==row['id']);row['rect']=v2._rect(obj)
    core.write(out/'corner-adaptation.json',adaptation)
    protocol=core.read(out/'corner-protocol.json');protocol.update(configurationId=config,
        frozenTargetDocumentSha256=core.sha(out/'module.mapnote.json'),adapterRevision='corner-open-v3',
        selection='One predeclared open-side candidate with guarded vertical docking and at most16px new-dock lowering; no holdout reselection')
    core.write(out/'corner-protocol.json',protocol)
    return {**result,'configurationId':config,'adapterRevision':'corner-open-v3','newDockDropPixels':drop['pixels']}
