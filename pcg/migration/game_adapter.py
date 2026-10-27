"""Decode the finite original-game archive into exact, unverified migration inputs.

This uses original evaluated dictionaries, never editor proxy rectangles.  It
creates no physics certificate and does not grant production/human approval.
python3 -m pcg.migration.game_adapter --out .cache/migration/game-inputs-v1
"""
from __future__ import annotations
import argparse
import copy
import json
import math
import re
import subprocess
from collections import Counter
from pathlib import Path
from . import core
from pcg.prototype.factory.core.quality import digest, module_hash

COMMIT = '879b39eaa869be70cb799dedd1bb6ffc35e0b92f'
RUNNER_SCRIPT = core.REPO/'pcg/migration/game_runner.gd'
SOURCE_DEPENDENCIES = [Path(__file__), core.REPO/'pcg/migration/game_document.mjs', RUNNER_SCRIPT]


def source_entries():
    """All finite registered inputs; 177 references are not 177 families."""
    imported=core.read(core.STATE/'game-source-import.json')
    by_path={r['originalPath']:r for r in imported['files']}
    rows=[]
    for item in core.read(core.REPO/'library/catalog.json')['modules']:
        path=core.REPO/item['file'].removeprefix('./')
        doc=core.read(path); source=doc['source']; raw=source['original']
        pinned=by_path.get(source['path'])
        if pinned:
            live=core.REPO/pinned['path']
            if core.sha(live)!=pinned['sha256']:raise ValueError('changed_import:'+str(live))
        if source['kind']=='foundry':
            batch=core.read(core.REPO/pinned['path'])
            exact=[v.get('manifest',v)for v in batch.get('accepted',[])+batch.get('itineraries',[])]
            matches=[v for v in exact if v.get('id')==raw.get('id')]
            if len(matches)!=1:raise ValueError('missing_current_foundry_manifest:'+raw.get('id',''))
            raw=matches[0]
        rows.append(dict(id=item['id'],kind=source['kind'],title=doc['title'],
            sourcePath=source['path'],sourceDocument=core.relative(path),
            sourceDocumentSha256=core.sha(path),sourceCommit=COMMIT if pinned else source['commit'],
            sourceArtifact=copy.deepcopy(pinned),method=source.get('method'),
            arguments=source.get('arguments',[]),data=copy.deepcopy(raw)))
    return rows


def support_index(platforms, point):
    near=[(abs(point[1]+18-r[1]),i)for i,r in enumerate(platforms)
          if r[0]-1e-5<=point[0]<=r[0]+r[2]+1e-5]
    return min(near)[1] if near and min(near)[0]<2 else None


def original_ports(raw):
    out=[]; seen={}
    for role, ports in [('entry',[raw['entry_port']]+raw.get('entry_ports',[])),
                        ('exit',[raw['exit_port']]+raw.get('exit_ports',[]))]:
        for p in ports:
            key=(p['port_id'],tuple(p['position']))
            if key in seen:
                seen[key]['sourceRoles'].append(role);continue
            direction=p.get('direction',[1,0]);normal=[-v for v in direction]if role=='entry'else direction[:]
            value=dict(id=p['port_id'],position=p['position'][:],normal=normal,
                       sourceRoles=[role],sourcePort=copy.deepcopy(p))
            ix=support_index(raw['platforms'],p['position'])
            if ix is not None:value['support_index']=ix
            if any(q['id']==value['id']for q in out):value['id']+='-'+role
            out.append(value);seen[key]=value
    return out


def latch_config(module_id):
    modules=core.read(core.REPO/'library/source/config/plains_shot_latches.json')['modules']
    if module_id not in modules:return []
    value=copy.deepcopy(modules[module_id]);value.update(id='windchime_'+module_id,
        open_seconds=value.get('open_seconds',0),prompt=value.get('prompt',''))
    if value.get('actuator_id'):value['ferry_id']=value['actuator_id']
    return [value]


def base_case(identifier,platforms,spawn,goal,bounds):
    return dict(id='game-'+identifier,family='original-game-'+identifier,
        capabilities=['move','jump','shot_recoil'],platforms=copy.deepcopy(platforms),
        spawn=spawn[:],entry_port=spawn[:],exit_port=goal[:],
        goal=[goal[0]-12,goal[1]-4,24,8],world_bounds=copy.deepcopy(bounds),
        one_way_platform_indices=[],wall_platform_indices=[],hazards=[],thorns=[],
        saws=[],moving_platforms=[],hooks=[],latches=[],enemies=[],
        control_plan=[dict(op='settle',trigger=dict(after=0),target_x=goal[0],deadband=3)],
        max_frames=1200,trace_all=False,settle_frames=12,
        generation_rule=dict(registration_source='pcg/migration/game_adapter.py',
            status='decoded_original_no_physics_approval'),
        challenge_requirements=dict(min_shots=0,min_ground_jumps=0),
        route_spec=dict(id='main',from_port='entry',to_port='exit',role='main',
                        require_bell=False,via_ports=[]))


def resource_case(row):
    raw=row['data']; a=raw['entry_port']; b=raw['exit_port']
    case=base_case(row['id'],raw['platforms'],a['position'],b['position'],raw['world_bounds'])
    for destination,source in [('one_way_platform_indices','one_way_platform_indices'),
       ('hazards','danger_bounds'),('thorns','surface_thorns'),('saws','saws'),('moving_platforms','ferries')]:
        case[destination]=copy.deepcopy(raw.get(source,[]))
    case['ports']=original_ports(raw)
    case['entry_normal']=[-v for v in a['direction']];case['exit_normal']=b['direction'][:]
    case['route_spec'].update(from_port=case['ports'][0]['id'],
        to_port=next(p['id']for p in case['ports']if p['position']==b['position']and'exit'in p['sourceRoles']))
    case['latches']=latch_config(row['id'])
    case['source_external_latches']=copy.deepcopy(case['latches'])
    case['route_spec']['require_bell']=bool(case['latches'])
    case['source_tuning_constraints']={key:copy.deepcopy(value)for key,value in raw.items()
        if key.startswith(('min_','minimum_','maximum_','requires_'))}
    if raw.get('min_jumps',0)>1:case['capabilities'].append('double_jump')
    case['source_identity']=dict(sourceCommit=row['sourceCommit'],sourceArtifact=row['sourceArtifact'],
        originalDictionarySha256=digest(raw),adapterVersion=1)
    case['module_sha256']=module_hash(case)
    return case


def forest_case(row):
    raw=row['data'];ps=raw.get('platforms',[])
    if not ps:raise ValueError('original_forest_has_no_platforms')
    platforms=[p['rect']for p in ps];spawn=raw['spawn'];goal=raw['goal']
    ext=[r for r in platforms]+raw.get('dangers',[])
    x=min(r[0]for r in ext);y=min(r[1]for r in ext)-256
    right=max(r[0]+r[2]for r in ext);bottom=max(r[1]+r[3]for r in ext)+128
    case=base_case(row['id'],platforms,spawn,goal,[x,y,right-x,bottom-y])
    case['one_way_platform_indices']=[i for i,p in enumerate(ps)if p.get('one_way')]
    case['hazards']=copy.deepcopy(raw.get('dangers',[]))
    case['hooks']=[dict(x=h['position'][0],y=h['position'][1],kind='hang'if h.get('hang_enabled')else'bounce',
                        source_id=h['id'])for h in raw.get('hook_anchors',[])]
    if case['hooks']:case['capabilities'].append('grapple')
    case['source_behavior']=copy.deepcopy({k:v for k,v in raw.items()if k not in ('platforms','dangers')})
    ports=[dict(id='entry',position=spawn[:],normal=[-1,0],sourceRoles=['entry'])]
    for key,port in raw.get('ports',{}).items():
        if port['position']==spawn:continue
        normal=port.get('normal') or port.get('direction') or [1,0]
        ports.append(dict(id=key,position=port['position'][:],normal=normal,sourceRoles=['exit'],sourcePort=port))
    if not any(p['position']==goal for p in ports):ports.append(dict(id='exit',position=goal[:],normal=[1,0],sourceRoles=['exit']))
    for port in ports:
        ix=support_index(platforms,port['position'])
        if ix is not None:port['support_index']=ix
    case['ports']=ports
    case['route_spec'].update(to_port=next(p['id']for p in ports if p['position']==goal))
    case['source_identity']=dict(sourceCommit=row['sourceCommit'],sourceArtifact=row['sourceArtifact'],
        originalDictionarySha256=digest(raw),adapterVersion=1)
    # Preserve unsupported source behavior explicitly: no proxy enemy/reward.
    nonempty=[k for k in ('enemies','rewards','reward','switches','action_program')if raw.get(k)]
    case['decoder_pending_behavior']=nonempty
    case['module_sha256']=module_hash(case)
    return case


def foundry_case(row,resources):
    """Flatten exact existing component placements, preserving native Cells.

    This is one atomic Module interface for a historical composite, not a new
    map generator or a claim of certified component seam composition.
    """
    raw=row['data'];parts=[]
    for i,node in enumerate(raw['nodes']):
        part=resource_case(resources[node['module_id']]);dx,dy=node['offset']
        prefix=f"part{i}/";phase=(node.get('phase_index',0)*.25)%1
        for r in part['platforms']+part['hazards']:r[0]+=dx;r[1]+=dy
        for key in ('spawn','entry_port','exit_port'):
            part[key][0]+=dx;part[key][1]+=dy
        part['goal'][0]+=dx;part['goal'][1]+=dy
        for spec in part['moving_platforms']:
            for key in ('start','finish'):spec[key][0]+=dx;spec[key][1]+=dy
            spec['platform_id']=prefix+spec['platform_id']
            spec['initial_phase']=(spec.get('initial_phase',0)+phase)%1
        for spec in part['saws']:
            spec['origin'][0]+=dx;spec['origin'][1]+=dy
            spec['source_id']=prefix+spec['source_id']
            spec['initial_phase']=(spec.get('initial_phase',0)+phase)%1
        for spec in part['latches']:
            spec['id']=prefix+spec['id'];spec['bell'][0]+=dx;spec['bell'][1]+=dy
            spec['gate'][0]+=dx;spec['gate'][1]+=dy
            if spec.get('sequence_gate'):spec['sequence_gate'][0]+=dx;spec['sequence_gate'][1]+=dy
            if spec.get('ferry_id'):spec['ferry_id']=prefix+spec['ferry_id']
        parts.append(part)
    all_rects=[r for part in parts for r in part['platforms']+part['hazards']]
    x=min(r[0]for r in all_rects);y=min(r[1]for r in all_rects)-256
    right=max(r[0]+r[2]for r in all_rects);bottom=max(r[1]+r[3]for r in all_rects)+128
    result=base_case(row['id'],[],parts[0]['spawn'],parts[-1]['exit_port'],[x,y,right-x,bottom-y])
    for part in parts:
        offset=len(result['platforms']);result['platforms']+=part['platforms']
        result['one_way_platform_indices'] += [offset+i for i in part['one_way_platform_indices']]
        for thorn in part['thorns']:thorn['platform_index']+=offset
        for key in ('hazards','thorns','saws','moving_platforms','hooks','latches','enemies'):result[key]+=part[key]
    result['ports']=[dict(id='entry',position=result['spawn'][:],normal=parts[0]['entry_normal'],sourceRoles=['entry']),
                      dict(id='exit',position=result['exit_port'][:],normal=parts[-1]['exit_normal'],sourceRoles=['exit'])]
    for p in result['ports']:
        ix=support_index(result['platforms'],p['position'])
        if ix is not None:p['support_index']=ix
    result['entry_normal']=parts[0]['entry_normal'];result['exit_normal']=parts[-1]['exit_normal']
    result['route_spec']['require_bell']=bool(result['latches'])
    result['source_components']=[dict(moduleId=n['module_id'],offset=n['offset'],phaseIndex=n.get('phase_index',0),
        sourceDictionarySha256=digest(resources[n['module_id']]['data']))for n in raw['nodes']]
    result['source_identity']=dict(sourceCommit=row['sourceCommit'],originalDictionarySha256=digest(raw),
        sourceArtifact=row['sourceArtifact'],representation='atomic_module_from_exact_original_composite')
    result['decoder_pending_behavior']=[]
    result['module_sha256']=module_hash(result)
    return result


def policy_candidates(case):
    """Finite geometry-guided action hypotheses; only Godot decides success."""
    source=next((p for p in case['ports']if p['id']==case['route_spec']['from_port']),None)
    target=next((p for p in case['ports']if p['id']==case['route_spec']['to_port']),None)
    direction=1 if case['exit_port'][0]>=case['spawn'][0]else -1
    out=[copy.deepcopy(case)]
    out[0]['id']+='-policy-walk'
    # Original authored shores and intermediate platforms guide launch points.
    # We never integrate a replacement motion model or call this a viable path.
    a=case['spawn'][0];b=case['exit_port'][0]
    floors=[(i,r)for i,r in enumerate(case['platforms'])
            if min(a,b)-24<=r[0]+r[2]/2<=max(a,b)+24]
    if source and 'support_index'in source:
        si=source['support_index'];floors=[(si,case['platforms'][si])]+[(i,r)for i,r in floors if i!=si]
    floors.sort(key=lambda item:direction*item[1][0])
    transitions=[]
    for (i,r),(j,n)in zip(floors,floors[1:]):
        if direction*(n[0]+n[2]/2-a)<0:continue
        gap=n[0]-(r[0]+r[2])if direction>0 else r[0]-(n[0]+n[2])
        if gap>8 or n[1]<r[1]-8:
            edge=r[0]+r[2]-36 if direction>0 else r[0]+36
            transitions.append((edge,gap))
    for hold,recoil in ((8,False),(12,False),(12,True)):
        value=copy.deepcopy(case);value['id']+=f'-policy-jump{hold}-r{int(recoil)}'
        plan=[dict(op='axis',trigger=dict(after=0),value=direction)]
        for edge,gap in transitions:
            plan.append(dict(op='wait',trigger=dict(dynamic=dict(kind='actor_x',direction='gte'if direction>0 else'lte',value=edge),timeout=200)))
            plan.append(dict(op='jump',trigger=dict(after=0)))
            plan.append(dict(op='jump_release',trigger=dict(after=hold)))
            if recoil:plan.append(dict(op='shoot',trigger=dict(after=6),direction=[-direction*.85,.5267826876]))
            plan.append(dict(op='wait',trigger=dict(after=12,state='grounded',timeout=180)))
        if case.get('latches'):
            for latch in case['latches']:
                plan.insert(1,dict(op='shoot',trigger=dict(after=0),aim_cell=dict(kind='bell',id=latch['id'])))
        plan.append(dict(op='settle',trigger=dict(after=0),target_x=case['exit_port'][0],deadband=3))
        value['control_plan']=plan;value.pop('module_sha256',None)
        out.append(value)
    for value in out:
        value.pop('module_sha256',None);value['module_sha256']=module_hash(value)
    return out


def purpose(case, raw):
    """Original static content may intentionally require no recoil at all."""
    reasons=[]
    if not raw.get('ok'):reasons.append('original_route_not_stably_reached')
    if raw.get('hp')!=5 or raw.get('returns'):reasons.append('original_route_damage_or_reset')
    required={l['id']for l in case.get('latches',[])}
    opened={e['id']for e in raw.get('plains',{}).get('events',[])if e.get('type')=='bell_open'}
    if case.get('route_spec',{}).get('require_bell')and not required<=opened:
        reasons.append('original_external_mechanism_not_executed')
    for latch in case.get('latches',[]):
        if any(latch.get('sequence_offset',[])):
            steps=[b.get('sequence_step',0)for f in raw.get('frames',[])for b in f.get('plains',{}).get('bells',[])if b.get('id')==latch['id']]
            if not any(step==1 for step in steps):reasons.append('original_sequence_not_actually_bound_or_executed')
    if case.get('decoder_pending_behavior'):reasons.append('unbound_original_behavior')
    return dict(ok=not reasons,reasons=reasons,scope='source-defined original mechanics; no human approval')


def stage(out, adapt=False):
    out=Path(out).resolve()
    if out.exists():raise ValueError('game_staging_output_exists')
    out.mkdir(parents=True);rows=source_entries();resources={r['id']:r for r in rows if r['kind']=='resource'}
    report=dict(schema='pcg/original-game-migration-inputs/v1',sourceCommit=COMMIT,
        registeredReferences=len(rows),sourceKinds=dict(Counter(r['kind']for r in rows)),
        rows=[],foundationCertifiedModules=0,humanReview='UNKNOWN')
    exports=[];fingerprints={}
    for row in rows:
        folder=out/core.safe_id('game-'+re.sub(r'[^a-z0-9_-]+','-',row['id'].lower()).replace('__','-').replace('_','-'))
        folder.mkdir();core.write(folder/'source.json',row)
        receipt=dict(id=row['id'],kind=row['kind'],source=row['sourceDocument'],
            sourceSha256=row['sourceDocumentSha256'],out=core.relative(folder),status='decoded_unverified')
        try:
            case=resource_case(row)if row['kind']=='resource'else forest_case(row)if row['kind']=='forest'else foundry_case(row,resources)
            core.write(folder/'cases.json',dict(cases=[case]))
            receipt.update(caseSha256=core.sha(folder/'cases.json'),
                pendingBehavior=case.get('decoder_pending_behavior',[]),
                physicalPortCount=len(case.get('ports',[])))
            equivalence=digest(dict(kind=row['kind'],data=row['data']))
            if equivalence in fingerprints:receipt['exactOriginalAliasOf']=fingerprints[equivalence]
            else:fingerprints[equivalence]=row['id']
            exports.append(dict(row=row,case=case,folder=core.relative(folder)))
        except Exception as error:receipt.update(status='decoder_error',conflict=str(error))
        report['rows'].append(receipt)
    bundle=out/'document-inputs.json';core.write(bundle,dict(rows=exports))
    command=['node',str(core.REPO/'pcg/migration/game_document.mjs'),str(bundle)]
    result=subprocess.run(command,cwd=core.REPO,capture_output=True,text=True)
    if result.returncode:raise ValueError(result.stderr or result.stdout)
    output=json.loads(result.stdout)
    by_id={r['id']:r for r in report['rows']}
    for result_row in output:
        target=by_id[result_row['id']];target.update(result_row)
        if adapt and result_row.get('document'):
            try:
                from .adaptation import adapt as adapt_geometry
                folder=core.REPO/target['out'];doc=core.read(folder/'module.mapnote.json')
                doc,cases,changes=adapt_geometry(doc,core.read(folder/'cases.json')['cases'])
                core.write(folder/'module.mapnote.json',doc);core.write(folder/'cases.json',dict(cases=cases))
                core.write(folder/'adaptation.json',changes)
                target.update(status='adapted_unverified',adaptation=core.relative(folder/'adaptation.json'))
            except Exception as error:target.update(status='adaptation_error',conflict=str(error))
    report['counts']=dict(Counter(r['status']for r in report['rows']))
    core.write(out/'manifest.json',report)
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',required=True);parser.add_argument('--adapt',action='store_true')
    parser.add_argument('--prepare-source',help='prepare already decoded source stage')
    args=parser.parse_args();r=prepare_all(args.prepare_source,args.out)if args.prepare_source else stage(args.out,args.adapt)
    print(json.dumps({k:v for k,v in r.items()if k!='rows'},ensure_ascii=False,indent=2))



def prepare_all(source_stage, out, source_root=None):
    """Freeze exact source packages, adapt all registered inputs, validate v2.

    Source packages live in their explicit import staging namespace. Successful
    promotion can archive them; original shared game dependencies are immutable.
    """
    import shutil
    from .adaptation import adapt
    from .corners import annotate
    source_stage=Path(source_stage).resolve();out=Path(out).resolve()
    source_root=Path(source_root or core.REPO/'pcg/migration/game-sources').resolve()
    if out.exists():raise ValueError('prepared_original_output_exists')
    out.mkdir(parents=True);source_root.mkdir(parents=True,exist_ok=True)
    plan=core.read(source_stage/'manifest.json');rows=[];files=[]
    for entry in plan['rows']:
        row=copy.deepcopy(entry);folder=core.REPO/entry['out'];name=folder.name
        frozen=source_root/name;target=out/name
        try:
            if not (folder/'module.mapnote.json').exists():raise ValueError('decoded_document_missing:'+str(entry.get('conflict')))
            frozen.mkdir(exist_ok=True)
            for filename in ('module.mapnote.json','cases.json','source.json'):
                src=folder/filename;dest=frozen/filename
                if dest.exists()and core.sha(src)!=core.sha(dest):raise ValueError('frozen_original_source_changed:'+name+'/'+filename)
                if not dest.exists():shutil.copy2(src,dest)
            original=core.read(frozen/'module.mapnote.json');old=original['generationContract']['contentVersion']
            record=dict(schema='pcg/original-game-source-package/v1',sourceType='original_game',
                sourceCommit=entry.get('sourceCommit',COMMIT),contentVersion=old,
                document_sha256=core.sha(frozen/'module.mapnote.json'),cases_sha256=core.sha(frozen/'cases.json'),
                technical_status='source_import_unverified',evidence=[],
                specification=dict(id=name),originalSource=core.read(frozen/'source.json'))
            if (frozen/'record.json').exists()and core.read(frozen/'record.json')!=record:raise ValueError('frozen_source_record_changed:'+name)
            core.write(frozen/'record.json',record)
            cases=core.read(frozen/'cases.json')['cases']
            from .godot_package import bind_case_behavior
            original=bind_case_behavior(original,cases)
            doc,cases,changes=adapt(original,cases)
            target.mkdir();core.write(target/'cases.json',dict(cases=cases));core.write(target/'module.mapnote.json',doc)
            core.write(target/'adaptation.json',changes);files.append(str(target/'module.mapnote.json'))
            row.update(status='adapted_unverified',sourcePackage=core.relative(frozen),prepared=core.relative(target),
                originalVersion=old,internalGeometryChanged=changes['internalGeometryChanged'])
        except Exception as error:row.update(status='prepare_error',conflict=str(error))
        rows.append(row)
    index=out/'finalize-list.json';core.write(index,files)
    result=subprocess.run(['node',str(core.REPO/'pcg/migration/game_document.mjs'),'--finalize-list',str(index)],cwd=core.REPO,capture_output=True,text=True)
    if result.returncode:raise ValueError(result.stderr or result.stdout)
    for row in rows:
        if row['status']!='adapted_unverified':continue
        target=core.REPO/row['prepared'];frozen=core.REPO/row['sourcePackage']
        try:
            doc=core.read(target/'module.mapnote.json');annotate(doc)
            source=core.read(frozen/'source.json')
            doc['generationContract']['generation']['migration']=dict(sourcePath=core.relative(frozen),
                sourceVersion=row['originalVersion'],moduleId=target.name,policy='minimal_actual_shore_adaptation',
                sourceDocumentSha256=core.sha(frozen/'module.mapnote.json'))
            core.write(target/'module.mapnote.json',doc)
            core.write(target/'migration.json',dict(schema='pcg/module-migration/v1',moduleId=target.name,
                sourceType='original_game',sourcePath=core.relative(frozen),sourceVersion=row['originalVersion'],
                sourceFiles=core._tree_files(frozen),status='prepared_unverified',humanReview='UNKNOWN',
                productionAdmitted=False,internalGeometryChanged=row['internalGeometryChanged'],
                adaptation=core.read(target/'adaptation.json'),evidence=[],
                runtimeBaseline='12f6cb006d7119598e3235f4ca4f7323e4c9d092',
                originalGameSourceCommit=source['sourceCommit'],
                unresolved=['actual routes','external mechanisms','boundary crossing','closure profiles','mirror','unsearched pairs']))
            checked=core.contract(target/'module.mapnote.json',refresh=True)
            row.update(status='prepared_unverified',contentVersion=core.read(target/'module.mapnote.json')['generationContract']['contentVersion'],
                staticValidation=checked)
        except Exception as error:row.update(status='static_validation_failed',conflict=str(error))
    report=dict(schema='pcg/original-game-prepared-migration/v1',sourceCommit=COMMIT,
        sourceStage=core.relative(source_stage),registeredReferences=len(rows),
        counts=dict(Counter(r['status']for r in rows)),rows=rows,
        actualPhysicsAttempts=0,foundationCertifiedModules=0,humanReview='UNKNOWN')
    core.write(out/'manifest.json',report)
    core.write(core.STATE/'game-prepared-v1.json',report)
    return report


def discover(prepared, name, ids=None):
    """One declared clean discovery pass; no calibration/holdout admission."""
    from pcg.prototype.workshop.engine import WorkshopEngine
    prepared=Path(prepared).resolve();manifest=core.read(prepared/'manifest.json')
    plans=[];rows=[]
    for row in manifest['rows']:
        if row['status']!='prepared_unverified' or row['kind']!='resource':continue
        if ids and row['id']not in ids:continue
        folder=core.REPO/row['prepared'];case=core.read(folder/'cases.json')['cases'][0]
        for value in policy_candidates(case):plans.append((row['id'],value))
    run=core.REPO/'pcg/results'/core.safe_id(name)
    if run.exists():raise ValueError('original_discovery_name_exists')
    engine=WorkshopEngine(run,batch_size=12,extra_sources=SOURCE_DEPENDENCIES,runner_script=RUNNER_SCRIPT)
    core.write(run/'protocol.json',dict(schema='pcg/original-game-policy-discovery/v1',
        maximumAttempts=len(plans),programsPerResource=4,seeds='no random search',
        selection='first clean success; freeze before independent calibration/holdout',
        qualityThresholdsUnchanged=True,cleanDiscoveryIsCertification=False,
        originalGameSourceCommit=COMMIT,runtimeBaseline='12f6cb006d7119598e3235f4ca4f7323e4c9d092'))
    originals={value['id']:module_id for module_id,value in plans}
    for case,raw,evidence in engine.run([v for _,v in plans],'original-game-policy-discovery'):
        check=purpose(case,raw);rows.append(dict(moduleId=originals[case['id']],case=case,
            passed=check['ok'],check=check,evidence=evidence,actualResult=dict(ok=raw.get('ok'),reason=raw.get('reason'),
                hp=raw.get('hp'),shots=raw.get('shots'),jumps=raw.get('jumps'),frames=len(raw.get('frames',[])))))
    selected={}
    for row in rows:
        if row['passed']and row['moduleId']not in selected:selected[row['moduleId']]=row
    report=dict(schema='pcg/original-game-policy-discovery-results/v1',actualAttempts=engine.sim.cases,
        checkedResources=len({r['moduleId']for r in rows}),cleanSuccessResources=len(selected),
        certifiedModules=0,selected=selected,rows=rows)
    core.write(run/'discovery.json',report)
    return report


def freeze_selected(prepared, discovery_path, out):
    """Freeze first calibration-discovery successes, never choose from holdout."""
    import shutil
    prepared=Path(prepared).resolve();out=Path(out).resolve();discovery_path=Path(discovery_path).resolve()
    if out.exists():raise ValueError('selected_original_output_exists')
    out.mkdir(parents=True)
    manifest=core.read(prepared/'manifest.json');discovery=core.read(discovery_path)
    selected=discovery['selected'];rows=[]
    physical=('capabilities','platforms','one_way_platform_indices','wall_platform_indices',
        'hazards','thorns','saws','moving_platforms','hooks','latches','enemies','world_bounds',
        'ports','block_ports','migration_adaptation')
    for row in manifest['rows']:
        if row['id']not in selected:continue
        source=core.REPO/row['prepared'];old=core.read(source/'cases.json')['cases'][0]
        winner=selected[row['id']]['case']
        mismatches=[k for k in physical if old.get(k)!=winner.get(k)]
        if mismatches:raise ValueError('discovery_geometry_changed:'+row['id']+':'+','.join(mismatches))
        target=out/source.name;shutil.copytree(source,target)
        core.write(target/'cases.json',dict(cases=[winner]))
        doc=core.read(target/'module.mapnote.json');gc=doc['generationContract']
        gc['generation']['parameters']['controlPlan']=winner['control_plan']
        gc['generation']['parameters']['originalGameProgramSelection']=dict(
            source=core.relative(discovery_path),sha256=core.sha(discovery_path),
            rule='first clean success among four preregistered source-guided programs; no holdout used')
        gc['generation']['source']['moduleSha256']=winner['module_sha256']
        gc['generation']['source']['sourceCaseId']=winner['id']
        for route in gc['routes']:
            route['actionTags']=sorted({c['op']for c in winner['control_plan']if c['op']not in ('wait','axis')})
        core.write(target/'module.mapnote.json',doc);core.contract(target/'module.mapnote.json',refresh=True)
        meta=core.read(target/'migration.json');meta['programSelection']=dict(path=core.relative(discovery_path),sha256=core.sha(discovery_path))
        core.write(target/'migration.json',meta)
        rows.append(dict(id=row['id'],prepared=core.relative(target),status='program_frozen_pending_independent_quality',
            selectedProgramId=winner['id'],contentVersion=core.read(target/'module.mapnote.json')['generationContract']['contentVersion']))
    receipt=dict(schema='pcg/original-game-selected-programs/v1',
        sourceDiscovery=dict(path=core.relative(discovery_path),sha256=core.sha(discovery_path)),
        frozenModules=len(rows),rows=rows,calibrationAndHoldout='NOT_RUN',certifiedModules=0)
    core.write(out/'manifest.json',receipt)
    return receipt


if __name__=='__main__':main()
