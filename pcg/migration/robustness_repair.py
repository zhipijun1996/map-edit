"""Bounded control repairs selected only from failed calibration evidence.

No geometry, capability, resource, runtime or quality-policy changes. Every
revision is a new immutable prepared package and gets independent real tests.
"""
from __future__ import annotations
import argparse, copy, json, shutil
from pathlib import Path
from . import core, physics
from pcg.prototype.factory.core.quality import digest

PLANS = {
 '01c1569a6399': [
  dict(kind='shorter_variable_jump_hold',hold=4,reason='Moderate timing noise leaves the second burst rising into ceiling thorns. Earlier release keeps the real body in the lower readable channel.'),
  dict(kind='shorter_hold_level_recoil',hold=6,shotDown=0.04,reason='If the first bounded repair still hits either wall, use a medium hold and a nearly horizontal burst to center the body in the channel.')],
 '08aed42071a3': [
  dict(kind='aim_actual_bell',reason='A fixed world-space direction misses the bell when timing shifts the real muzzle. Aim at the existing receiver using the original muzzle compensation, retaining aim perturbation.'),
  dict(kind='aim_actual_bell_earlier_release',hold=10,reason='If receiver aiming is insufficient, shorten the authored hold by two frames to widen the shot approach while retaining the same native bell and recoil.')]
}


def prepare(source, prefix, revision, out):
    source,out=Path(source).resolve(),Path(out).resolve()
    if out.exists():raise ValueError('repair_destination_exists')
    plan=copy.deepcopy(PLANS[prefix][revision-1])
    doc=core.read(source/'module.mapnote.json');cases=core.read(source/'cases.json')['cases']
    before=copy.deepcopy(cases)
    for case in cases:
        for name in ('recorded_frames','factory_evidence','module_sha256','noise'):case.pop(name,None)
        for command in case['control_plan']:
            if command['op']=='jump_release'and 'hold'in plan:command['trigger']['after']=plan['hold']
            if command['op']=='shoot':
                if plan['kind'].startswith('aim_actual_bell'):
                    command['aim_cell']=dict(kind='bell',id=case['latches'][0]['id'])
                if 'shotDown'in plan:
                    import math
                    y=plan['shotDown'];command['direction']=[-math.sqrt(1-y*y),y]
    # Bind the new actual control plan to the semantic document; historical
    # source rules/checkers remain original and all failed artifacts survive.
    gc=doc['generationContract'];parent_version=gc['contentVersion']
    changed=[dict(routeId=c['route_spec']['id'],before=b['control_plan'],after=c['control_plan'],controlPlanSha256=digest(c['control_plan']))for b,c in zip(before,cases)]
    gc['generation']['parameters']['controlPlan']=copy.deepcopy(cases[0]['control_plan'])
    failed=core.REPO/'pcg/results'/('foundation-migration-full-quality-v1-'+prefix)/'calibration-0.json'
    receipt=dict(schema='pcg/calibration-control-repair/v1',prefix=prefix,revision=revision,
        parentContentVersion=parent_version,sourcePrepared=core.relative(source),sourceDocumentSha256=core.sha(source/'module.mapnote.json'),
        failedCalibration=dict(path=core.relative(failed),sha256=core.sha(failed)),plan=plan,changes=changed,
        maximumRevisions=2,selection='Calibration failures only; no holdout consulted.',
        unchanged=['actual_geometry','Cell_mechanisms','capabilities','resources','quality_thresholds','perturbation_distribution','causal_checker'],
        source=dict(path=core.relative(Path(__file__)),sha256=core.sha(__file__)))
    gc['generation']['migration']['robustnessRevision']=copy.deepcopy(receipt)
    for v in gc['validations']:v.update(result='UNKNOWN',artifacts=[],method='pending_robustness_revision_actual_validation',unverified=['new_control_version_not_run'])
    shutil.copytree(source,out)
    for name in ('replay-cases.json','physics-input-cases.json','godot-package.json'):(out/name).unlink(missing_ok=True)
    core.write(out/'module.mapnote.json',doc);core.write(out/'cases.json',dict(cases=cases));core.write(out/'repair-receipt.json',receipt)
    meta=core.read(out/'migration.json');meta.update(status='prepared_unverified',evidence=[],controlProgramChanged=True)
    for name in ('physicsReport','boundaryProbe','godotLoad'):meta.pop(name,None)
    core.write(out/'migration.json',meta)
    result=core.contract(out/'module.mapnote.json',refresh=True)
    from .godot_package import audit_cases
    audit_cases(core.read(out/'module.mapnote.json'),cases,require_replay=False)
    return dict(prepared=core.relative(out),contentVersion=result.get('contentVersion'),plan=plan)


def run(prefix, source_root=None, name='foundation-robustness-v1', maximum=2):
    if prefix not in PLANS:raise ValueError('unknown_preregistered_repair')
    source_root=Path(source_root or core.REPO/'.cache/migration/full-v6').resolve()
    source=next(source_root.glob(prefix+'*'))
    state_path=core.STATE/'campaigns'/(name+'-'+prefix+'.json')
    state=core.read(state_path)if state_path.exists()else dict(schema='pcg/bounded-control-repair-campaign/v1',source=core.relative(source),prefix=prefix,plans=PLANS[prefix],maximumRevisions=min(2,maximum),rows=[])
    if state['plans']!=PLANS[prefix]:raise ValueError('frozen_repair_plan_changed')
    for revision in range(1,min(2,maximum)+1):
        previous=next((r for r in state['rows']if r['revision']==revision),None)
        if previous:
            if previous['status']=='package_ready':return state
            continue
        out=core.REPO/'.cache/migration'/name/(source.name+'-r'+str(revision))
        experiment=name+'-'+prefix+'-r'+str(revision)
        row=dict(revision=revision,status='repair_failed',experiment=experiment)
        try:
            row.update(prepare(source,prefix,revision,out))
            clean=physics.run_clean(out,experiment+'-clean')
            row.update(cleanReport=core.relative(core.REPO/'pcg/results'/(experiment+'-clean')/'clean-preflight.json'),cleanPassed=clean['passed'],actualAttempts=clean['actualAttempts'])
            if clean['passed']:
                shutil.copy2(core.REPO/'pcg/results'/(experiment+'-clean')/'replay-cases.json',out/'replay-cases.json')
                report=physics.run(out,experiment+'-physics')
                row.update(physicsReport=core.relative(core.REPO/'pcg/results'/(experiment+'-physics')/'migration-physics.json'),physicsPassed=report['passed'],actualAttempts=row['actualAttempts']+report['actualAttempts'])
                if report['passed']:
                    core.certify(out,core.REPO/row['physicsReport'])
                    ready=out.with_name(out.name+'-ready');loaded=core.package(out,ready)
                    row.update(status='package_ready',ready=core.relative(ready),packageResult=loaded)
                else:
                    cal=core.read(core.REPO/'pcg/results'/(experiment+'-physics')/'calibration-0.json')
                    # A held-out failure is not a new tuning signal. Keep it and
                    # stop rather than use revision 2 to fit the holdout.
                    if cal['quality_gate']['status']=='awaiting_human_review':row['stopReason']='independent_holdout_or_boundary_failed_no_revision_from_holdout'
        except Exception as error:row['conflict']=str(error)
        state['rows'].append(row);core.write(state_path,state);print(json.dumps(row,ensure_ascii=False),flush=True)
        if row['status']=='package_ready'or row.get('stopReason'):break
    return state

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--prefix',choices=PLANS,required=True);parser.add_argument('--source-root');parser.add_argument('--name',default='foundation-robustness-v1');parser.add_argument('--maximum',type=int,default=2)
    args=parser.parse_args();print(json.dumps(run(args.prefix,args.source_root,args.name,args.maximum),ensure_ascii=False))
