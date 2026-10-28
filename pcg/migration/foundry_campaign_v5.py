"""Bounded original Foundry source-policy migration; uses existing admission API."""
from __future__ import annotations
import argparse,copy,json,shutil,traceback
from pathlib import Path
from . import core,physics,holdout_guard,game_adapter,foundry_feedback_v5 as feedback
from pcg.prototype.workshop.engine import WorkshopEngine


def stage(prepared,out,name):
    prepared=Path(prepared).resolve();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    source={r['id']:r for r in game_adapter.source_entries()}
    calibration=core.REPO/'pcg/results/foundation-migration-original-foundry-feedback-v5/calibration-results.json'
    reviewed=core.read(calibration)['rows'];selection={}
    for template in feedback.REPRESENTATIVES:
        passing=[r for r in reviewed if r['template']==template and r['clean']['ok'] and r.get('calibration',{}).get('status')=='awaiting_human_review']
        if not passing:raise ValueError('no_calibration_policy:'+template)
        selection[template]=min(passing,key=lambda r:r['variant'])['variant']
    # Selected before seeing these conditions. Other variants never inherit proof.
    core.write(out/'protocol.json',dict(schema='pcg/original-foundry-feedback-campaign/v5',selection=selection,
        calibration=dict(path=core.relative(calibration),sha256=core.sha(calibration)),maximumSources=54,
        maximumCleanAttempts=54,maximumFormalAttemptsPerSource=1000,maximumPolicyRevisions=0,
        selectionRule='First passing original-driver feedback variant; source-profile and geometry frozen before canonical clean and independent holdout',
        originalSourceCommit=game_adapter.COMMIT,humanReview='UNKNOWN',sourcePosesAppliedToMotor=False))
    rows=[];cases=[];labels={}
    for entry in core.read(prepared/'manifest.json')['rows']:
        row=source[entry['id']]
        if row['kind']!='foundry':continue
        template=next((t for t in feedback.REPRESENTATIVES if row['id'].startswith('foundry__'+t+'-')),'original-driver-composite')
        variant=selection.get(template,0)
        folder=out/Path(entry['prepared']).name
        if not folder.exists():feedback.prepare_one(core.REPO/entry['prepared'],row,variant,folder)
        case=core.read(folder/'cases.json')['cases'][0];cases.append(case)
        metadata=dict(id=row['id'],moduleId=folder.name,prepared=core.relative(folder),template=template,variant=variant,status='prepared_unverified')
        rows.append(metadata);labels[case['id']]=metadata
        core.write(out/'manifest.json',dict(rows=rows,totalSources=54))
    engine=WorkshopEngine(core.REPO/'pcg/results'/name,batch_size=18,extra_sources=feedback.SOURCE_DEPENDENCIES,runner_script=feedback.RUNNER_SCRIPT)
    physics.deduplicate_snapshot(engine.out)
    for case,raw,evidence in engine.run(cases,'all-source-canonical-clean'):
        row=labels[case['id']];check=feedback.purpose(case,raw);row.update(clean=check,evidence=evidence,actualGoal=raw.get('ok'),reason=raw.get('reason'))
        row['status']='clean_only'if check['ok']else'needs_repair'
        if check['ok']:
            folder=core.REPO/row['prepared'];core.write(folder/'replay-cases.json',dict(cases=[physics._recording(case,raw)]))
        core.write(out/'manifest.json',dict(rows=rows,totalSources=54,actualCleanAttempts=engine.sim.cases))
        print(json.dumps({k:v for k,v in row.items()if k!='evidence'}),flush=True)
    return out


def qualify(manifest,limit=None):
    manifest=Path(manifest);entries=core.read(manifest)['rows'];rows=[]
    # Real base templates first, then registered phase/profile/composite samples.
    entries.sort(key=lambda r:('-base-v0-p0'not in r['id'],r['id']))
    if limit is not None:entries=entries[:limit]
    for entry in entries:
        row=copy.deepcopy(entry);folder=core.REPO/row['prepared'];module_id=row['moduleId']
        try:
            if not row.get('clean',{}).get('ok'):rows.append(row);continue
            clean_name='foundation-migration-original-'+module_id+'-feedback-preflight-v5'
            preflight=physics.run_clean(folder,clean_name);row.update(preflight=preflight['passed'],cleanAttempts=preflight['actualAttempts'])
            if preflight['passed']:
                shutil.copy2(core.REPO/'pcg/results'/clean_name/'replay-cases.json',folder/'replay-cases.json')
                gate=holdout_guard.check(folder);row['holdoutGuard']=gate['status']
                quality_name='foundation-migration-original-'+module_id+'-feedback-quality-v5'
                quality=physics.run(folder,quality_name);report=core.REPO/'pcg/results'/quality_name/'migration-physics.json'
                holdout_guard.observe_report(folder,report);row.update(quality=quality['passed'],qualityAttempts=quality['actualAttempts'])
                if quality['passed']:
                    core.certify(folder,report);package=core.REPO/'.cache/migration'/('queued-'+module_id+'-feedback-v5')
                    core.package(folder,package);row.update(status='package_queued',package=core.relative(package))
                else:row['status']='needs_repair'
            else:row['status']='needs_repair'
        except Exception as error:
            row['status']='needs_repair';row['conflict']=str(error);traceback.print_exc()
        rows.append(row);core.write(core.STATE/'game-foundry-feedback-quality-v5.json',dict(rows=rows,totalSources=len(entries),actualAttempts=sum(r.get('cleanAttempts',0)+r.get('qualityAttempts',0)for r in rows)))
        print(json.dumps(row),flush=True)
    return rows


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='action',required=True)
    p=sub.add_parser('stage');p.add_argument('--prepared',required=True);p.add_argument('--out',required=True);p.add_argument('--name',required=True)
    p=sub.add_parser('qualify');p.add_argument('--manifest',required=True);p.add_argument('--limit',type=int)
    args=parser.parse_args()
    if args.action=='stage':stage(args.prepared,args.out,args.name)
    else:qualify(args.manifest,args.limit)
