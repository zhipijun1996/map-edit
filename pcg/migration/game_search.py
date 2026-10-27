"""Bounded continuation for existing game inputs using native source mechanics.

Source action steps generate action hypotheses, never success certificates.
The same WorkshopEngine and current calibration/holdout policy remain in use.
"""
from __future__ import annotations
import argparse
import copy
import json
import math
from pathlib import Path
from . import core, game_adapter
from pcg.prototype.factory.core.quality import module_hash
from pcg.prototype.workshop.engine import WorkshopEngine

RUNNER_SCRIPT=core.REPO/'pcg/migration/game_search_runner.gd'
SOURCE_DEPENDENCIES=[Path(__file__),Path(game_adapter.__file__),RUNNER_SCRIPT,
    game_adapter.RUNNER_SCRIPT,core.REPO/'pcg/prototype/godot/config/foundry_capabilities.json',
    core.REPO/'pcg/prototype/godot/scripts/generation/foundry_catalog.gd']


def enriched_case(case, source):
    value=copy.deepcopy(case);raw=source['data']
    value['generation_rule']['registration_source']='pcg/migration/game_search.py'
    if source['kind']=='foundry':
        profiles=core.read(core.REPO/'library/source/config/foundry_capabilities.json')['profiles']
        profile=next(p for p in profiles if p['id']==raw['capability_profile'])
        if profile['id']not in ('base','double_jump','air_chain'):raise ValueError('unsupported_original_profile')
        value['original_tuning_profile']=dict(id=profile['id'],overrides=profile['overrides'],abilities=profile['abilities'])
        value['capabilities']=['move','jump','shot_recoil']+(['double_jump']if profile['id']!='base'else[])
        value['max_frames']=min(3600,max(1200,math.ceil(abs(value['exit_port'][0]-value['spawn'][0])/160*60)+600))
    if source['kind']=='forest':
        # An action program is a proposal, not a Cell; verify its actual actions
        # separately. Preserve unresolved real world-pickup consumers honestly.
        pending=[p for p in value.get('decoder_pending_behavior',[])if p!='action_program']
        if raw.get('reward_position'):pending.append('original_coin_note_pickup_consumer')
        value['decoder_pending_behavior']=sorted(set(pending))
        value['source_action_program']=raw.get('action_program',[])
    value['module_sha256']=module_hash(value)
    return value


def purpose(case, raw):
    outcome=game_adapter.purpose(case,raw)
    expected=case.get('original_tuning_profile')
    if expected:
        snap=raw.get('capability_snapshot',{})
        if snap.get('base_max_air_shots')!=expected['overrides'].get('max_air_shots',2):
            outcome['reasons'].append('original_profile_air_capacity_not_bound')
        if snap.get('maximum_jumps')!=expected['overrides'].get('max_jumps',1):
            outcome['reasons'].append('original_profile_jump_capacity_not_bound')
    actions=case.get('source_action_program',[])
    if any(v.get('action')in ('H','HANG')for v in actions)and raw.get('hook_contacts',0)<1:
        outcome['reasons'].append('original_hook_relation_not_executed')
    outcome['ok']=not outcome['reasons'];return outcome


def wait_x(x,direction,timeout=240):
    return dict(op='wait',trigger=dict(dynamic=dict(kind='actor_x',direction='gte'if direction>0 else'lte',value=x),timeout=timeout))


def source_step_plan(case, source, hold=12, recoil=False):
    """Translate authored takeoffs/landings, preserving every core Cell."""
    raw=source['data'];steps=raw.get('routes',{}).get('main')or raw.get('steps',[])
    if isinstance(steps,dict):steps=steps.get('steps',[])
    if not steps:return None
    plan=[];point=case['spawn'];hooks={h['id']:h['position']for h in raw.get('hook_anchors',[])}
    for step in steps:
        kind=step.get('kind',step.get('action',''));landing=step.get('landing')
        if not landing:continue
        takeoff=step.get('takeoff',point);direction=1 if landing[0]>=takeoff[0]else -1
        plan.append(dict(op='axis',trigger=dict(after=0),value=direction))
        if kind in ('walk','land'):
            plan.append(wait_x(landing[0]-direction*8,direction))
        elif kind in ('jump_gap','jump_rise','jump'):
            plan.append(wait_x(takeoff[0]-direction*8,direction))
            plan.extend([dict(op='jump',trigger=dict(after=0)),dict(op='jump_release',trigger=dict(after=hold))])
            if recoil:plan.append(dict(op='shoot',trigger=dict(after=6),direction=[-direction*.85,.5267826876]))
            plan.append(dict(op='wait',trigger=dict(after=12,state='grounded',timeout=240)))
        elif kind in ('drop','drop_through'):
            plan.append(wait_x(landing[0]-direction*8,direction))
            plan.append(dict(op='wait',trigger=dict(after=8,state='grounded',timeout=240)))
        elif kind in ('H','HANG','hook','hook_bounce','hook_hang'):
            anchor=hooks.get(step.get('anchor',step.get('hook_id')))
            if not anchor:return None
            plan.append(dict(op='grapple',trigger=dict(after=0),aim_target=anchor))
            plan.append(dict(op='wait',trigger=dict(after=18)))
        elif kind in ('R','recoil'):
            plan.append(dict(op='shoot',trigger=dict(after=0),direction=step.get('direction',[-direction,.0])))
        else:return None
        point=landing
    plan.append(dict(op='settle',trigger=dict(after=0),target_x=case['exit_port'][0],deadband=3))
    return plan


def hazard_plan(case, hold=12, recoil=False):
    direction=1 if case['exit_port'][0]>=case['spawn'][0]else -1
    plan=[dict(op='axis',trigger=dict(after=0),value=direction)]
    crossings=[]
    for thorn in case.get('thorns',[]):
        face=thorn.get('face');face=['top','left','right','bottom'][face]if isinstance(face,int)else face
        if face!='top':continue
        p=case['platforms'][thorn['platform_index']]
        left=p[0]+thorn['start_offset'];right=left+thorn['length']
        if min(case['spawn'][0],case['exit_port'][0])<left<max(case['spawn'][0],case['exit_port'][0]):
            crossings.append((left-52 if direction>0 else right+52,None))
    for saw in case.get('saws',[]):
        x,y=saw['origin']
        if min(case['spawn'][0],case['exit_port'][0])<x<max(case['spawn'][0],case['exit_port'][0]):
            crossings.append((x-direction*(saw['radius']+70),saw))
    for x,saw in sorted(crossings,key=lambda item:direction*item[0]):
        plan.append(wait_x(x,direction))
        if saw and saw.get('travel',[0,0])[1]:
            safe=[.20,.25]if saw['travel'][1]<0 else[.70,.75]
            plan.extend([dict(op='axis',trigger=dict(after=0),value=0),
                dict(op='wait',trigger=dict(dynamic=dict(kind='saw_phase',id=saw['source_id'],window=safe),timeout=240)),
                dict(op='axis',trigger=dict(after=0),value=direction)])
        plan.extend([dict(op='jump',trigger=dict(after=0)),dict(op='jump_release',trigger=dict(after=hold))])
        if recoil:plan.append(dict(op='shoot',trigger=dict(after=6),direction=[-direction*.85,.5267826876]))
        plan.append(dict(op='wait',trigger=dict(after=12,state='grounded',timeout=240)))
    plan.append(dict(op='settle',trigger=dict(after=0),target_x=case['exit_port'][0],deadband=3))
    return plan if crossings else None


def proposals(case, source):
    base=enriched_case(case,source);values=game_adapter.policy_candidates(base)
    for hold,recoil in ((8,False),(12,False),(12,True)):
        plan=source_step_plan(base,source,hold,recoil)if source['kind']=='forest'else hazard_plan(base,hold,recoil)
        if plan:
            value=copy.deepcopy(base);value['id']+=f'-authored-step-h{hold}-r{int(recoil)}';value['control_plan']=plan;values.append(value)
    # Every proposal is data, never a replacement room or a pass label.
    for value in values:
        value.pop('module_sha256',None);value['module_sha256']=module_hash(value)
    return values


def discover(prepared,name,exclude=None,include=None):
    prepared=Path(prepared).resolve();manifest=core.read(prepared/'manifest.json')
    sources={r['id']:r for r in game_adapter.source_entries()}
    plans=[]
    for row in manifest['rows']:
        if row['status']!='prepared_unverified'or row['id']in(exclude or[]):continue
        if include and row['id']not in include:continue
        case=core.read(core.REPO/row['prepared']/'cases.json')['cases'][0]
        plans += [(row['id'],value)for value in proposals(case,sources[row['id']])]
    run=core.REPO/'pcg/results'/core.safe_id(name)
    engine=WorkshopEngine(run,batch_size=12,extra_sources=SOURCE_DEPENDENCIES,runner_script=RUNNER_SCRIPT)
    core.write(run/'protocol.json',dict(schema='pcg/original-game-continuation-discovery/v1',
        sourceManifest=dict(path=core.relative(prepared/'manifest.json'),sha256=core.sha(prepared/'manifest.json')),
        maximumAttempts=len(plans),programsPerSourceMaximum=7,
        selection='first clean success; no holdout feedback; all failures retained',
        purpose='original actions, resources and world consequences',
        qualityPolicy='unchanged factory regular; discovery alone is not admission'))
    original={c['id']:identifier for identifier,c in plans};rows=[]
    for case,raw,evidence in engine.run([c for _,c in plans],'native-original-continuation'):
        check=purpose(case,raw)
        rows.append(dict(moduleId=original[case['id']],case=case,passed=check['ok'],check=check,
            evidence=evidence,actualResult=dict(ok=raw.get('ok'),reason=raw.get('reason'),hp=raw.get('hp'),
                hooks=raw.get('hook_contacts',0),shots=raw.get('shots'),jumps=raw.get('jumps'),
                capabilitySnapshot=raw.get('capability_snapshot'),frames=len(raw.get('frames',[])))))
    selected={}
    for row in rows:
        if row['passed']and row['moduleId']not in selected:selected[row['moduleId']]=row
    report=dict(schema='pcg/original-game-policy-discovery-results/v1',actualAttempts=engine.sim.cases,
        checkedSources=len({r['moduleId']for r in rows}),cleanSuccessSources=len(selected),
        geometricalSuccessSources=len({r['moduleId']for r in rows if r['actualResult']['ok']}),
        certifiedModules=0,selected=selected,rows=rows)
    core.write(run/'discovery.json',report)
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--prepared',required=True)
    parser.add_argument('--name',required=True);parser.add_argument('--exclude-selected')
    parser.add_argument('--include',nargs='*');args=parser.parse_args()
    excludes=set(core.read(args.exclude_selected)['selected'])if args.exclude_selected else set()
    result=discover(args.prepared,args.name,excludes,args.include)
    print(json.dumps({k:v for k,v in result.items()if k not in('rows','selected')},indent=2))
