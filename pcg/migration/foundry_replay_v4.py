"""Reuse the original Foundry's actual input recordings, with new evidence.

Old manifest/basis identities remain immutable history. No recorded position is
used as movement; the same native Harness executes axis/actions and perturbations.
"""
from __future__ import annotations
import argparse
import copy
import json
from pathlib import Path
from . import core,game_adapter,game_world_v4
from pcg.prototype.factory.core.quality import module_hash
from pcg.prototype.workshop.engine import WorkshopEngine

RUNNER_SCRIPT=core.REPO/'pcg/migration/foundry_replay_runner_v4.gd'
SOURCE_DEPENDENCIES=[Path(__file__),RUNNER_SCRIPT,*game_world_v4.SOURCE_DEPENDENCIES,
    core.STATE/'original-foundry-replays-v1.json']


def purpose(case,raw):return game_world_v4.purpose(case,raw)


def replay_case(case,source,warmup=0):
    index=core.read(core.STATE/'original-foundry-replays-v1.json')
    name=source['data']['id']+'.json'
    binding=next(r for r in index['files']if r['name']==name)
    path=core.REPO/binding['imported']
    if core.sha(path)!=binding['sha256']:raise ValueError('changed_original_recording')
    recording=core.read(path)
    if recording['manifest_hash']!=source['data']['hash']or recording['basis']!=source['data']['basis']:
        raise ValueError('original_recording_bound_to_different_manifest')
    value=game_world_v4.native_fields(case,source)
    # Separate original Module instances scoped identical authored hazard IDs.
    # The atomic imported composite needs that same scope made explicit.
    resources={r['id']:r for r in game_adapter.source_entries()if r['kind']=='resource'}
    ranges=[];cursor=0
    for component,node in enumerate(source['data']['nodes']):
        count=len(resources[node['module_id']]['data']['platforms'])
        ranges.append((cursor,cursor+count,component));cursor+=count
    scoped=[]
    for thorn in value.get('thorns',[]):
        part=next(component for low,high,component in ranges if low<=thorn['platform_index']<high)
        prefix=f'part{part}/';before=thorn['surface_id']
        if not before.startswith(prefix):thorn['surface_id']=prefix+before
        scoped.append(dict(platformIndex=thorn['platform_index'],before=before,after=thorn['surface_id']))
    value['original_component_hazard_scopes']=scoped
    value['original_replay_frame_count']=len(recording['frames'])
    value['axes']=[];value['actions']=[];previous_axis=None
    for index,frame in enumerate(recording['frames']):
        if frame['axis']!=previous_axis:
            value['axes'].append(dict(frame=index,value=frame['axis'],noise_key=index*31))
            previous_axis=frame['axis']
        for ai,action in enumerate(frame['actions']):
            value['actions'].append(dict(frame=index,type=action['type'],direction=copy.deepcopy(action['direction']),noise_key=index*31+ai+1))
    value['original_replay_source']=dict(path=binding['imported'],sha256=binding['sha256'],
        sourceManifestHash=recording['manifest_hash'],sourceBasis=recording['basis'],
        oldRecordingIsNewCertification=False,posesUsedAsMovement=False)
    value['generation_rule']['registration_source']='pcg/migration/foundry_replay_v4.py'
    value['warmup_frames']=warmup;value['max_frames']=min(3600,len(recording['frames'])+480)
    value['control_plan']=[dict(op='settle',trigger=dict(after=0),target_x=value['exit_port'][0],deadband=3)]
    value['id']+=f'-original-input-w{warmup}'
    value.pop('module_sha256',None);value['module_sha256']=module_hash(value)
    return value


def discover(prepared,name):
    manifest=core.read(Path(prepared)/'manifest.json');sources={r['id']:r for r in game_adapter.source_entries()}
    plans=[]
    for row in manifest['rows']:
        if row['kind']!='foundry'or row['status']!='prepared_unverified':continue
        case=core.read(core.REPO/row['prepared']/'cases.json')['cases'][0]
        plans.extend((row['id'],replay_case(case,sources[row['id']],warmup))for warmup in(0,4))
    run=core.REPO/'pcg/results'/core.safe_id(name)
    engine=WorkshopEngine(run,batch_size=12,extra_sources=SOURCE_DEPENDENCIES,runner_script=RUNNER_SCRIPT)
    core.write(run/'protocol.json',dict(schema='pcg/original-foundry-replay-discovery/v4',
        maximumAttempts=len(plans),sourceCount=len(plans)//2,programs='original axis/action streams, warmup0or4',
        selection='first clean original-input replay; independent calibration/holdout remain required',
        noPoseAssignment=True,originalBasisNeverRelabelled=True,noise='existing timing_error and disturbed_direction on actual source events'))
    source_ids={c['id']:identifier for identifier,c in plans};rows=[]
    for case,raw,evidence in engine.run([c for _,c in plans],'original-foundry-input-streams'):
        check=purpose(case,raw);rows.append(dict(moduleId=source_ids[case['id']],case=case,passed=check['ok'],check=check,evidence=evidence,
            actualResult=dict(ok=raw.get('ok'),reason=raw.get('reason'),hp=raw.get('hp'),frames=len(raw.get('frames',[])),
                final=(raw.get('frames') or [{}])[-1],capabilitySnapshot=raw.get('capability_snapshot'))))
    selected={}
    for row in rows:
        if row['passed']and row['moduleId']not in selected:selected[row['moduleId']]=row
    report=dict(schema='pcg/original-game-policy-discovery-results/v1',actualAttempts=engine.sim.cases,
        checkedSources=len({r['moduleId']for r in rows}),cleanSuccessSources=len(selected),selected=selected,rows=rows,
        certifiedModules=0)
    core.write(run/'discovery.json',report);return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--prepared',required=True);parser.add_argument('--name',required=True)
    args=parser.parse_args();r=discover(args.prepared,args.name)
    print(json.dumps({k:v for k,v in r.items()if k not in('rows','selected')},indent=2))
