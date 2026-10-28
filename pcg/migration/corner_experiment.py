"""Materialize and validate an actual corner interface using existing physics.

The first bounded experiment uses an existing brake-branch Module. It does not
invent a new challenge: the recovery shore's corner interface is made one-way,
and the former side opening receives a real narrow rock closure. A sixteen-pixel
coplanar overlap preserves the original resource's full-body standing support.
"""
from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from . import core, corners

CONFIGURATION_ID = 'c-bottom-right-v1'


def _closed_cases(folder):
    """Predeclared finite attempts against the former side, not an absence proof."""
    from .physics import fresh
    source=core.read(Path(folder)/'cases.json')['cases'][0]
    original=core.read(Path(folder)/'migration.json')['cornerConfiguration']['originalPort']
    right,y=original['position'][0],original['stagingPosition'][1]
    cases=[]
    for kind in ('walk','jump','jump-recoil'):
        for offset in (-2,0,2):
            c=fresh(source,'old-side-'+kind+'-'+str(offset))
            c.update(spawn=[right-64,y-4+offset],goal=[right+40,y-5,16,10],max_frames=160,trace_all=True)
            plan=[dict(op='axis',trigger=dict(after=0),value=1)]
            if kind!='walk':plan.append(dict(op='jump',trigger=dict(after=3,state='grounded',timeout=60)))
            if kind=='jump-recoil':plan.append(dict(op='shoot',trigger=dict(after=6),direction=[-1,0]))
            c['control_plan']=plan
            c['corner_closed_probe']=dict(kind=kind,offset=offset,formerBoundary=original['position'],
                formerNormal=original['normal'],body=[24,36],claim='finite retired-opening approaches')
            cases.append(c)
    return cases


def _closed_check(case,raw):
    right=case['corner_closed_probe']['formerBoundary'][0]
    frames=raw.get('frames',[])
    return dict(passed=bool(frames and len(frames)==160 and raw.get('hp')==5 and not raw.get('returns')
                           and all(f['x']+12<=right+.05 for f in frames)),
                observedFrames=len(frames),maximumBodyRight=max((f['x']+12 for f in frames),default=None),
                formerBoundaryX=right,hp=raw.get('hp'),returns=raw.get('returns',[]),
                absenceOfOtherBypasses='UNKNOWN')


def run_closed(folder,name):
    from . import physics
    from pcg.prototype.workshop.engine import WorkshopEngine
    core.safe_id(name)
    folder=Path(folder).resolve();cases=_closed_cases(folder)
    author=physics.author_for(cases[0]);runner=physics.runner_for(cases[0],author)
    engine=WorkshopEngine(core.REPO/'pcg/results'/name,batch_size=24,
        extra_sources=[Path(__file__),Path(corners.__file__),Path(physics.__file__),Path(core.__file__),
                       physics.FULL_PROTOCOL,*physics.author_sources([author],runner)],runner_script=runner)
    physics.deduplicate_snapshot(engine.out)
    core.write(engine.out/'input-binding.json',dict(module=physics.artifact(folder/'module.mapnote.json'),
        cases=physics.artifact(folder/'cases.json'),protocol=physics.artifact(folder/'corner-protocol.json')))
    rows=[]
    for case,raw,evidence in engine.run(cases,'retired-side-approaches'):
        rows.append(dict(id=case['id'],check=_closed_check(case,raw),evidence=evidence))
    report=dict(schema='pcg/corner-retired-opening/v1',contentVersion=core.read(folder/'module.mapnote.json')['generationContract']['contentVersion'],
                passed=all(r['check']['passed']for r in rows),actualAttempts=engine.sim.cases,rows=rows,
                sourceBinding=physics.artifact(engine.out/'source_binding.json'),batches=physics.artifact(engine.out/'batches.json'),
                inputBinding=physics.artifact(engine.out/'input-binding.json'),absenceOfOtherBypasses='UNKNOWN')
    core.write(engine.out/'retired-opening.json',report)
    return report


def verify_closed(folder,proof):
    from pcg.prototype.factory.core.quality import module_hash
    folder=Path(folder).resolve();core.verify_artifacts([proof]);path=core.resolve_artifact(proof['path']);report=core.read(path)
    if report.get('schema')!='pcg/corner-retired-opening/v1' or report['contentVersion']!=core.read(folder/'module.mapnote.json')['generationContract']['contentVersion']:
        raise ValueError('corner_retired_opening_report_identity_mismatch')
    core.verify_artifacts([report[k]for k in ('sourceBinding','batches','inputBinding')])
    binding=core.read(core.resolve_artifact(report['inputBinding']['path']))
    if binding['cases']['sha256']!=core.sha(folder/('physics-input-cases.json'if(folder/'physics-input-cases.json').exists()else'cases.json')):
        raise ValueError('corner_retired_opening_inputs_changed')
    source=core.read(core.resolve_artifact(report['sourceBinding']['path']))
    for rel,sha in source['source_files'].items():
        frozen=path.parent/'source_snapshot'/rel
        if not frozen.is_file()or core.sha(frozen)!=sha:raise ValueError('corner_retired_opening_frozen_source_changed:'+rel)
    expected={c['id']:c for c in _closed_cases(folder)};rows=[]
    for batch in core.read(core.resolve_artifact(report['batches']['path'])):
        compressed=path.parent/batch['gzip_path']
        if core.sha(compressed)!=batch['gzip_sha256']:raise ValueError('corner_retired_opening_raw_changed')
        with gzip.open(compressed,'rb')as stream:data=stream.read()
        if hashlib.sha256(data).hexdigest()!=batch['raw_output_sha256']:raise ValueError('corner_retired_opening_raw_identity_changed')
        execution=core.read(path.parent/batch['execution']);inputs=path.parent/'physics'/(batch['batch']+'.input.json')
        if execution['exit_code']or core.sha(inputs)!=execution['input_sha256']:raise ValueError('corner_retired_opening_execution_changed')
        cases=core.read(inputs)['cases'];results=json.loads(data)['results']
        if len(cases)!=len(results):raise ValueError('corner_retired_opening_case_count')
        for c,raw in zip(cases,results):
            wanted=expected.pop(c['id'],None)
            if wanted is None or raw['id']!=c['id']or module_hash(wanted)!=module_hash(c):raise ValueError('corner_retired_opening_case_identity')
            rows.append(_closed_check(c,raw))
    if expected or len(rows)!=9 or report['actualAttempts']!=9 or not all(r['passed']for r in rows):
        raise ValueError('corner_retired_opening_finite_checks_failed')
    return report


def prepare(source, out):
    source, out = Path(source).resolve(), Path(out).resolve()
    if out.is_relative_to(core.ACTIVE) or out.is_relative_to(core.RECYCLE):
        raise ValueError('prepare_corner_outside_authoritative_archives_first')
    if out.exists():
        raise ValueError('corner_experiment_destination_exists')
    doc = core.read(source / 'module.mapnote.json')
    source_cases=source/'physics-input-cases.json'
    if not source_cases.exists():source_cases=source/'cases.json'
    cases = core.read(source_cases)['cases']
    c = doc['generationContract']
    base_case_sha=core.sha(source_cases)
    c['generation']['cornerConfiguration']=dict(id=CONFIGURATION_ID,
        baseContentVersion=c['contentVersion'],basePhysicsInputSha256=base_case_sha,
        meaning='One frozen local interface configuration; base route programs preserved')
    port = next(p for p in c['ports'] if p['id'] == 'C')
    option = corners.options(doc, port)['BOTTOM_RIGHT']
    if not option['applicable'] or port['face'] != 'RIGHT':
        raise ValueError('corner_experiment_requires_existing_bottom_right_side_port_C')
    b = c['space']['bounds']
    support = next(o for o in doc['objects'] if o['id'] == port['support']['objectId'])
    if support['type'] != 'terrain' or support.get('trackId'):
        raise ValueError('corner_experiment_requires_native_static_endpoint_rock')
    index = support['sourceIndex']
    right, bottom = b['x'] + b['w'], b['y'] + b['h']
    cut = right - 128
    before = [support[k] for k in ('x', 'y', 'w', 'h')]
    if abs(support['x'] + support['w'] - right) > 1e-5:
        raise ValueError('corner_experiment_requires_endpoint_shore_reaching_right_edge')
    surface = copy.deepcopy(support)
    # Sixteen-pixel overlap gives the original body-width goal x=900 a full
    # single supporting shape; the original resource validator cannot accept
    # a standing point straddling two otherwise coplanar platform shapes.
    surface.update(id=doc['id'] + '/corner-C-one-way', type='platform', x=cut-16,
                   w=144, sourceIndex=len(cases[0]['platforms']))
    new_surface = support['x'] < cut
    if not new_surface:
        surface['sourceIndex'] = support['sourceIndex']
        surface['id'] = support['id']
    wall = copy.deepcopy(support)
    wall.update(id=doc['id'] + '/corner-C-old-side-closure', x=right - 8,
                y=bottom - 256, w=8, h=256,
                sourceIndex=len(cases[0]['platforms']) + int(new_surface))
    for obj in doc['objects']:
        if obj['type']=='terrain' and obj is not support and obj['y']==surface['y'] and obj['x']<cut<obj['x']+obj['w']:
            obj['w']=cut-obj['x']
    if new_surface:support['w']=cut-support['x']
    else:doc['objects'][doc['objects'].index(support)] = surface
    additions=([surface] if new_surface else [])+[wall]
    doc['objects'] += additions
    c['space']['occupancy']['objectIds'] += [o['id'] for o in additions]
    for obj in additions:
        c['composition']['cells'].append(dict(id=obj['id'], objectIds=[obj['id']], contentVersion='sha256:'+'0'*64))
    original_port = copy.deepcopy(port)
    port.update(position=option['targetPosition'], normal=[0, 1], face='BOTTOM',
                surface='ONE_WAY_PLATFORM', stagingPosition=[right - 64, surface['y'] - 18],
                support=dict(objectId=surface['id'], face='top', status='source_derived'))
    marker = next(o for o in doc['objects'] if o['id'] == port['objectId'])
    marker.update(x=port['position'][0] - marker['w']/2, y=port['position'][1] - marker['h']/2)
    for route in c['routes']:
        a = next(p for p in c['ports'] if p['id'] == route['from'])
        z = next(p for p in c['ports'] if p['id'] == route['to'])
        route['localDisplacementBlocks'] = [(v-u)/128 for u, v in zip(a['position'], z['position'])]
    for validation in c['validations']:
        validation.update(result='UNKNOWN',artifacts=[],failures=[],
            method='pending_actual_corner_configuration_revalidation',coverage={},
            unverified=['corner configuration physics not yet run'])
    corners.annotate(doc)
    for case in cases:
        for obj in doc['objects']:
            if obj['type'] in ('terrain','platform') and not obj.get('trackId'):
                rect=[obj[k]for k in ('x','y','w','h')]
                i=obj['sourceIndex']
                if i<len(case['platforms']):case['platforms'][i]=rect
                else:case['platforms'].append(rect)
        case.setdefault('one_way_platform_indices', []).append(surface['sourceIndex'])
        cp = next(p for p in case['ports'] if p['id'] == 'C')
        cp.update(position=port['stagingPosition'], normal=[0, 1], support_index=surface['sourceIndex'])
        case['block_ports']['C'].update(position=port['position'], normal=[0, 1],
                                      stagingPosition=port['stagingPosition'],
                                      aperture=[cut, bottom - 32, 128, 64],
                                      crossing_offset=[0, port['stagingPosition'][1] - bottom])
        case.pop('recorded_frames', None)
    out.mkdir(parents=True)
    core.write(out / 'module.mapnote.json', doc)
    core.write(out / 'cases.json', dict(cases=cases))
    meta = core.read(source / 'migration.json')
    meta.update(status='prepared_unverified', evidence=[], internalGeometryChanged=True,
                cornerConfiguration=dict(id=CONFIGURATION_ID, portId='C', corner='BOTTOM_RIGHT',
                    baseContentVersion=c['contentVersion'], baseDocumentSha256=core.sha(source/'module.mapnote.json'),
                    basePhysicsInputSha256=base_case_sha,
                    source=core.relative(source), originalPort=original_port))
    core.write(out / 'migration.json', meta)
    core.write(out / 'corner-adaptation.json', dict(configurationId=CONFIGURATION_ID,
        source=core.relative(source), sourceDocumentSha256=core.sha(source/'module.mapnote.json'),
        scope='Corner shore interface and narrow retired-side closure; no core terrain scaling or new challenge',
        originalSupport=before, retainedRocks=[[o[k]for k in ('x','y','w','h')]for o in doc['objects']if o['type']=='terrain'and o['y']==surface['y']],
        oneWay=[surface[k] for k in ('x','y','w','h')], oldOpeningClosure=[wall[k] for k in ('x','y','w','h')],
        targetPort=port, abilityAndResourceRequirementsChanged=False,
        canonicalProgramsChanged=False, geometryCertification='NOT_RUN'))
    # Exact JS Cell hashing, including its canonical numeric representation.
    script = """import fs from 'node:fs';import {canonical,sha256} from './module-contract.js';
const p=process.argv[1],d=JSON.parse(fs.readFileSync(p));for(const c of d.generationContract.composition.cells){const os=c.objectIds.map(id=>d.objects.find(o=>o.id===id));c.contentVersion='sha256:'+sha256(canonical(os.length===1?os[0]:os));}fs.writeFileSync(p,JSON.stringify(d,null,2)+'\\n');"""
    subprocess.run(['node','--input-type=module','-e',script,str(out/'module.mapnote.json')],cwd=core.REPO,check=True)
    core.contract(out / 'module.mapnote.json', refresh=True)
    physics_protocol=core.read(core.STATE/'protocol-full-v2.json')
    protocol = dict(schema='pcg/corner-interface-experiment-protocol/v1',
        configurationId=CONFIGURATION_ID, baseModuleSource=core.relative(source),
        frozenTargetDocumentSha256=core.sha(out/'module.mapnote.json'),
        fixedGeometry=True, maximumAttempts=350,
        calibrationSeed=physics_protocol['calibrationSeed'], holdoutSeed=physics_protocol['holdoutSeed'], trialsPerNoiseLevel=12,
        thresholds=dict(clean=.9,mild=.85,moderate=.65),
        selection='One predeclared local interface; no holdout reselection',
        required=['all original directed route programs','all original permissions',
                  'complete-body vertical ingress and egress', 'former side opening blocked',
                  'continuous route exit without reset', 'actual compiled playable package'],
        unknown=['arbitrary external state','unsearched route pairs','full Map','human review'])
    core.write(out / 'corner-protocol.json', protocol)
    return dict(status='prepared_unverified',folder=str(out),configurationId=CONFIGURATION_ID)


def install(base_folder, prepared, report_path, preflight_path, closed_path):
    """Install a verified external configuration without changing base bytes."""
    from . import physics
    from .godot_package import compile_package, run_package_validation
    base_folder, prepared = Path(base_folder).resolve(), Path(prepared).resolve()
    if base_folder.parent!=core.ACTIVE.resolve():
        raise ValueError('corner_configuration_requires_current_formal_base')
    core.validate(base_folder,require_certified=True)
    base = core.read(base_folder/'module.mapnote.json')
    meta = core.read(prepared/'migration.json')
    if base['generationContract']['contentVersion'] != meta['cornerConfiguration']['baseContentVersion']:
        raise ValueError('corner_base_semantics_changed')
    base_inputs=base_folder/'physics-input-cases.json'
    if not base_inputs.exists():base_inputs=base_folder/'cases.json'
    if core.sha(base_inputs)!=meta['cornerConfiguration']['basePhysicsInputSha256']:
        raise ValueError('corner_base_programs_changed')
    report_path, preflight_path = Path(report_path).resolve(), Path(preflight_path).resolve()
    proof = dict(path=core.relative(report_path),sha256=core.sha(report_path))
    physics.verify_report(prepared,proof)
    closed_path=Path(closed_path).resolve()
    closed_proof=dict(path=core.relative(closed_path),sha256=core.sha(closed_path))
    verify_closed(prepared,closed_proof)
    preflight = core.read(preflight_path)
    if not preflight['passed'] or preflight['contentVersion'] != core.read(prepared/'module.mapnote.json')['generationContract']['contentVersion']:
        raise ValueError('corner_clean_package_inputs_not_verified')
    core.certify(prepared,report_path)
    output = base_folder/'port-configurations'/CONFIGURATION_ID
    if output.exists():raise ValueError('corner_configuration_already_installed')
    target = prepared/'module.mapnote.json'
    recorded = preflight_path.parent/'replay-cases.json'
    compile_package(target,recorded,output,stable_id=meta['moduleId'])
    shutil.copy2(prepared/'cases.json',output/'physics-input-cases.json')
    shutil.copy2(prepared/'migration.json',output/'migration.json')
    shutil.copy2(prepared/'corner-adaptation.json',output/'corner-adaptation.json')
    shutil.copy2(prepared/'corner-protocol.json',output/'corner-protocol.json')
    load=run_package_validation(output)
    physics.verify_report(output,proof)
    target_doc=core.read(output/'module.mapnote.json')
    p=next(p for p in target_doc['generationContract']['ports']if p['id']=='C')
    receipt=dict(schema='pcg/corner-port-configuration/v1',moduleId=meta['moduleId'],
        configurationId=CONFIGURATION_ID,baseContentVersion=base['generationContract']['contentVersion'],
        baseDocumentSha256=core.sha(base_folder/'module.mapnote.json'),
        basePhysicsInputSha256=core.sha(base_inputs),
        relocations=[dict(portId='C',corner='BOTTOM_RIGHT',targetFace=p['face'],targetPosition=p['position'],surface=p['surface'],permission=p['permission'])],
        configuration=dict(path=core.relative(output/'module.mapnote.json'),sha256=core.sha(output/'module.mapnote.json'),contentVersion=target_doc['generationContract']['contentVersion']),
        physicsReport=proof,retiredOpeningReport=closed_proof,
        package=dict(path=core.relative(output/'godot-package.json'),sha256=core.sha(output/'godot-package.json')),
        allowed=True,technicalStatus='verified',humanReview='UNKNOWN',
        actualAttempts=core.read(report_path)['actualAttempts'],nativeReplayFrames=sum(r['actual_frames']for r in load['observed']),
        scope='One exact corner configuration; no automatic combination, mirror or full Map certification')
    core.write(output/'receipt.json',receipt)
    return receipt


def main():
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('prepare');p.add_argument('--source',required=True);p.add_argument('--out',required=True)
    p=sub.add_parser('closed');p.add_argument('--prepared',required=True);p.add_argument('--name',required=True)
    p=sub.add_parser('preflight');p.add_argument('--prepared',required=True);p.add_argument('--name',required=True)
    p=sub.add_parser('validate');p.add_argument('--prepared',required=True);p.add_argument('--name');p.add_argument('--report')
    p=sub.add_parser('install');p.add_argument('--base',required=True);p.add_argument('--prepared',required=True);p.add_argument('--report',required=True);p.add_argument('--preflight',required=True);p.add_argument('--closed',required=True)
    args=parser.parse_args()
    if args.command=='prepare':result=prepare(args.source,args.out)
    elif args.command=='closed':result=run_closed(args.prepared,args.name)
    elif args.command=='preflight':
        from . import physics
        result=physics.run_clean(args.prepared,args.name)
    elif args.command=='validate':
        from . import physics,holdout_guard
        if args.report:
            report=Path(args.report).resolve()
            holdout_guard.check(args.prepared,existing_report=report)
            verified=physics.verify_report(args.prepared,dict(path=core.relative(report),sha256=core.sha(report)))
            result=dict(status='read_only_evidence_reverified',passed=verified['passed'],newGodotAttempts=0,
                        originalReportAttempts=verified['actualAttempts'])
        else:
            if not args.name:raise ValueError('fresh_corner_validation_requires_name')
            holdout_guard.check(args.prepared)
            result=physics.run(args.prepared,args.name)
            holdout_guard.observe_report(args.prepared,core.REPO/'pcg/results'/args.name/'migration-physics.json')
    else:result=install(args.base,args.prepared,args.report,args.preflight,args.closed)
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':main()
