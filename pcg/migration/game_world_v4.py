"""Original-game v4 content bindings: native pickups and fixed source profiles.

Reuses original DemoApp._commit_pickup / FoundryCatalog.apply_profile.  No
replacement grant, motion, damage, or candidate-store implementation is added.
"""
from __future__ import annotations
import argparse
import copy
import json
import shutil
from pathlib import Path
from . import core,game_adapter,game_search
from .corners import annotate
from pcg.prototype.factory.core.quality import module_hash
from pcg.prototype.workshop.engine import WorkshopEngine

RUNNER_SCRIPT=core.REPO/'pcg/migration/game_world_runner_v4.gd'
SOURCE_DEPENDENCIES=[Path(__file__),Path(game_adapter.__file__),Path(game_search.__file__),
    RUNNER_SCRIPT,game_search.RUNNER_SCRIPT,game_adapter.RUNNER_SCRIPT,
    core.REPO/'pcg/migration/runtime/original_pickups_v4.gd',
    core.REPO/'pcg/prototype/godot/config/player_tuning.json',
    core.REPO/'pcg/prototype/godot/config/foundry_capabilities.json',
    core.REPO/'pcg/prototype/godot/scripts/demo/demo_app.gd',
    core.REPO/'pcg/prototype/godot/scripts/demo/generated_demo_stage.gd',
    core.STATE/'original-pickup-v4-assets.json']


def native_fields(case,source):
    value=copy.deepcopy(case);raw=source['data']
    value['generation_rule']['registration_source']='pcg/migration/game_world_v4.py'
    if source['kind']=='foundry':
        profiles=core.read(core.REPO/'library/source/config/foundry_capabilities.json')['profiles']
        profile=next(p for p in profiles if p['id']==raw['capability_profile'])
        defaults=core.read(core.REPO/'pcg/prototype/godot/config/player_tuning.json')
        effective={key:profile['overrides'].get(key,defaults[key])for key in('max_jumps','max_air_shots')}
        value['original_tuning_profile']=dict(id=profile['id'],overrides=profile['overrides'],abilities=profile['abilities'],effectiveTuning=effective)
        value['capabilities']=['move','jump','shot_recoil']+(['double_jump']if effective['max_jumps']>1 else[])
    pickups=[];pending=[v for v in value.get('decoder_pending_behavior',[])if v not in('action_program','original_coin_note_pickup_consumer')]
    if source['kind']=='forest'and raw.get('reward_position'):
        if any(raw.get(k)for k in('choice_contract','interaction_contract','branch_reward_contract')):
            pending.append('original_branch_chest_consumer')
        else:
            point=raw['reward_position'][:];reward_id=raw.get('reward_support_id')
            index=next((i for i,p in enumerate(raw['platforms'])if p['id']==reward_id),None)
            if index is not None:point[1]+=value['platforms'][index][1]-raw['platforms'][index]['rect'][1]
            risk=raw.get('risk_reward',{})
            for kind,key,offset in [('coin','coins',0),('note','notes',20)]:
                amount=int(risk.get(key,0))
                if amount>0:pickups.append(dict(id='root_'+kind,kind=kind,amount=amount,position=[point[0]+offset,point[1]]))
            if not pickups:pending.append('source_reward_amount_not_declared')
    value['original_pickups']=pickups
    value['source_action_program']=raw.get('action_program',[])
    value['required_original_pickups']=[p['id']for p in pickups]if not raw.get('risk_reward',{}).get('optional',False)else[]
    value['decoder_pending_behavior']=sorted(set(pending))
    value.pop('module_sha256',None)
    return value


def purpose(case,raw):
    outcome=game_adapter.purpose(case,raw)
    profile=case.get('original_tuning_profile')
    if profile:
        snap=raw.get('capability_snapshot',{});expected=profile['effectiveTuning']
        if snap.get('base_max_air_shots')!=expected['max_air_shots']:outcome['reasons'].append('original_profile_air_capacity_not_bound')
        if snap.get('maximum_jumps')!=expected['max_jumps']:outcome['reasons'].append('original_profile_jump_capacity_not_bound')
    contacts=sum(1 for v in case.get('source_action_program',[])if v.get('action')in('H','HANG'))
    if contacts and raw.get('hook_contacts',0)<contacts:outcome['reasons'].append('original_hook_relation_not_executed')
    native=raw.get('original_pickups',{})
    claimed={p['id']for p in native.get('pickups',[])if p.get('claimed')}
    if not set(case.get('required_original_pickups',[]))<=claimed:outcome['reasons'].append('original_world_pickup_not_actually_claimed')
    if case.get('original_pickups')and (native.get('consumer')!='DemoApp._commit_pickup'or native.get('interaction_radius')!=46 or native.get('resources_reset')is not False):
        outcome['reasons'].append('original_pickup_consumer_not_bound')
    outcome['ok']=not outcome['reasons'];return outcome


def interaction_program(case,source,offset=0):
    """Place explicit original Interact inputs inside authored walk segments."""
    value=copy.deepcopy(case);pickups=value.get('original_pickups',[])
    if not pickups:return value
    direction=1 if value['exit_port'][0]>=value['spawn'][0]else -1
    target=pickups[0]['position'][0]+offset
    plan=value['control_plan'];insert=None
    for i,command in enumerate(plan):
        query=command.get('trigger',{}).get('dynamic',{})
        if query.get('kind')=='actor_x'and direction*(query['value']-target)>=0:
            insert=i;break
    if insert is None:insert=max(0,len(plan)-1)
    commands=[game_search.wait_x(target,direction)]
    commands += [dict(op='native_pickup_interact',trigger=dict(after=0 if i==0 else 1))for i in range(len(pickups))]
    value['control_plan']=plan[:insert]+commands+plan[insert:]
    value.pop('module_sha256',None);return value


def prepare_one(base,source,out,case=None):
    base=Path(base).resolve();out=Path(out).resolve()
    if out.exists():raise ValueError('original_world_prepared_destination_exists')
    shutil.copytree(base,out)
    existing=core.read(base/'cases.json')['cases'][0]
    candidate=native_fields(case or existing,source)
    candidate['module_sha256']=module_hash(candidate)
    doc=core.read(base/'module.mapnote.json');gc=doc['generationContract']
    for i,pickup in enumerate(candidate['original_pickups']):
        w,h=14,14 if pickup['kind']=='coin'else 24
        x,y=pickup['position'];identifier=doc['id']+'/original-pickup-'+pickup['id']
        doc['objects'].append(dict(id=identifier,type='reward',x=x-w/2,y=y-h/2,w=w,h=h,rotation=0,
            label='原游戏金币'if pickup['kind']=='coin'else'原游戏音符',note='Original DemoApp consumer; 46px interaction radius, no chest substitution',
            mechanics=dict(service='DemoApp._commit_pickup',kind=pickup['kind'],amount=pickup['amount'],interactionRadius=46,source=copy.deepcopy(pickup))))
        gc['space']['occupancy']['objectIds'].append(identifier)
        gc['composition']['cells'].append(dict(id=identifier,contentVersion='sha256:'+'0'*64,objectIds=[identifier]))
    if 'original_tuning_profile'in candidate:
        gc['requiredNativeProfile']=candidate['original_tuning_profile']
        gc['generation']['parameters']['original_tuning_profile']=candidate['original_tuning_profile']
    gc['requiredServices']=['run_wallet']+(['meta_progression']if any(p['kind']=='note'for p in candidate['original_pickups'])else[])
    gc['generation']['parameters']['controlPlan']=candidate['control_plan']
    gc['generation']['parameters']['nativeOriginalConsumer']=dict(source=core.relative(Path(__file__)),sha256=core.sha(__file__),pickups=candidate['original_pickups'])
    for route in gc['routes']:
        route['requiredAbilities']=candidate['capabilities'];route['capabilityRequirements']['allOf']=[v for v in candidate['capabilities']if v!='move']
        route['resourceProfile']=dict(originalNativeProfile=candidate.get('original_tuning_profile','UNKNOWN'),requiredOriginalPickups=candidate['required_original_pickups'])
    for validation in gc['validations']:
        validation.update(result='UNKNOWN',artifacts=[],method='pending_actual_original_consumer_revalidation')
        validation['capabilityConfiguration']['available']=candidate['capabilities']
    annotate(doc);core.write(out/'module.mapnote.json',doc);core.write(out/'cases.json',dict(cases=[candidate]))
    meta=core.read(out/'migration.json');meta.update(status='prepared_unverified',originalNativeConsumers=dict(profile=candidate.get('original_tuning_profile'),pickups=candidate['original_pickups']))
    core.write(out/'migration.json',meta);core.contract(out/'module.mapnote.json',refresh=True)
    return dict(id=source['id'],out=core.relative(out),status='prepared_unverified',unresolvedBehavior=candidate['decoder_pending_behavior'])


def discover(prepared, prior_discovery, out, name, ids=None):
    manifest=core.read(Path(prepared)/'manifest.json');sources={r['id']:r for r in game_adapter.source_entries()}
    old=core.read(prior_discovery);first={}
    for row in old['rows']:
        if row['actualResult']['ok']and row['moduleId']not in first:first[row['moduleId']]=row['case']
    out=Path(out).resolve();out.mkdir(parents=True,exist_ok=False);rows=[];plans=[]
    for entry in manifest['rows']:
        if entry['id']not in first or ids and entry['id']not in ids:continue
        source=sources[entry['id']]
        if source['kind']!='forest':continue
        folder=core.REPO/entry['prepared'];target=out/folder.name
        candidate=native_fields(first[entry['id']],source)
        if candidate['decoder_pending_behavior']:continue
        candidate=interaction_program(candidate,source)
        row=prepare_one(folder,source,target,candidate);rows.append(row)
        for offset in(-16,0,16):
            # Start again from the frozen source-guided movement program rather
            # than inserting a second interaction sequence into the previous.
            value=native_fields(first[entry['id']],source);value=interaction_program(value,source,offset)
            value['id']+=f'-native-pickup-{offset}';value['module_sha256']=module_hash(value)
            plans.append((entry['id'],value))
    run=core.REPO/'pcg/results'/core.safe_id(name)
    engine=WorkshopEngine(run,batch_size=12,extra_sources=SOURCE_DEPENDENCIES,runner_script=RUNNER_SCRIPT)
    core.write(run/'protocol.json',dict(schema='pcg/original-game-world-consumer-discovery/v4',maximumAttempts=len(plans),
        selection='first source movement program with successful explicit native interaction; calibration/holdout independent',
        baselineMovement='prior clean discovery only; no holdout used',originalConsumer='DemoApp._commit_pickup',interactionRadius=46,
        noNewResourceMechanism=True))
    source_ids={c['id']:identifier for identifier,c in plans};results=[]
    for case,raw,evidence in engine.run([c for _,c in plans],'original-world-pickup-programs'):
        check=purpose(case,raw);results.append(dict(moduleId=source_ids[case['id']],case=case,passed=check['ok'],check=check,evidence=evidence,
            actualResult=dict(ok=raw.get('ok'),reason=raw.get('reason'),hp=raw.get('hp'),originalPickups=raw.get('original_pickups'))))
    selected={}
    for row in results:
        if row['passed']and row['moduleId']not in selected:selected[row['moduleId']]=row
    report=dict(schema='pcg/original-game-policy-discovery-results/v1',actualAttempts=engine.sim.cases,checkedSources=len(rows),
        cleanSuccessSources=len(selected),selected=selected,rows=results,certifiedModules=0)
    core.write(run/'discovery.json',report);core.write(out/'manifest.json',dict(rows=rows,actualAttempts=engine.sim.cases,selected=list(selected)))
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--prepared',required=True)
    parser.add_argument('--prior',required=True);parser.add_argument('--out',required=True);parser.add_argument('--name',required=True)
    parser.add_argument('--ids',nargs='*');args=parser.parse_args()
    r=discover(args.prepared,args.prior,args.out,args.name,args.ids)
    print(json.dumps({k:v for k,v in r.items()if k not in('rows','selected')},indent=2))
