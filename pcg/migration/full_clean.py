"""Resume real clean diagnostics for an entire frozen migration preparation.

This is orchestration of the existing Harness, never a second certification
system. Only full calibration/holdout + proof verification can admit a Module.
"""
from __future__ import annotations
import argparse
import hashlib
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
import json
from . import core,physics
from .godot_package import audit_cases


def run_name_for(name,folder):
    identity=Path(folder).name
    return name+'-'+identity[:28]+'-'+hashlib.sha256(identity.encode()).hexdigest()[:16]


def run(prepared_root,name,workers=2):
    root=Path(prepared_root).resolve();core.safe_id(name)
    if workers not in (1,2):raise ValueError('diagnostic_workers_must_be_one_or_two')
    folders=sorted(f.parent for f in root.glob('*/module.mapnote.json'))
    if not folders:raise ValueError('empty_migration_preparation')
    plan=[dict(source=f.name,documentSha256=core.sha(f/'module.mapnote.json'),
        casesSha256=core.sha(f/'cases.json'))for f in folders]
    target=core.STATE/'campaigns'/(name+'.json')
    if target.exists():
        manifest=core.read(target)
        if manifest['plan']!=plan:raise ValueError('frozen_full_clean_plan_changed')
    else:
        manifest=dict(schema='pcg/full-migration-clean-diagnostics/v1',name=name,preparedRoot=core.relative(root),
            plan=plan,protocol=dict(path=core.relative(physics.FULL_PROTOCOL),sha256=core.sha(physics.FULL_PROTOCOL)),
            maximumAttempts=core.read(physics.FULL_PROTOCOL)['maximumAttemptsThisBatch'],
            rows=[],technicalAdmission=False)
        core.write(target,manifest)
    completed={r['source']for r in manifest['rows']}
    def execute(folder):
        row=dict(source=folder.name,status='error',actualAttempts=0)
        run_name=run_name_for(name,folder)
        existed_before=(core.REPO/'pcg/results'/run_name).exists()
        try:
            doc=core.read(folder/'module.mapnote.json');cases=core.read(folder/'cases.json')['cases']
            audit_cases(doc,cases,require_replay=False)
            result=physics.run_clean(folder,run_name)
            row.update(status='passed'if result['passed']else'needs_repair',actualAttempts=result['actualAttempts'],
                contentVersion=result['contentVersion'],title=doc['title'],
                report=dict(path=f'pcg/results/{run_name}/clean-preflight.json',
                            sha256=core.sha(core.REPO/'pcg/results'/run_name/'clean-preflight.json')),
                routeFailures=[dict(routeId=r['routeId'],reasons=r['check']['reasons'])for r in result['routes']if not r['check']['ok']],
                probeFailures=[dict(id=p['id'],check=p['check'])for p in result['probes']if not p['check']['passed']],
                invalidatingCounters=[dict(id=c['id'],reasons=c['causalCheck']['reasons'],judgment=c['adjudication'])for c in result['counters']if c['adjudication']['invalidates_design']],
                preparationError=result['preparationError'])
            replay=core.REPO/'pcg/results'/run_name/'replay-cases.json'
            if replay.exists():row['replayCases']=dict(path=core.relative(replay),sha256=core.sha(replay))
        except Exception as error:
            row['error']=str(error)
            batches=core.REPO/'pcg/results'/run_name/'batches.json'
            if not existed_before and batches.exists():row['actualAttempts']=sum(b['cases']for b in core.read(batches))
        return row
    with ThreadPoolExecutor(max_workers=workers)as pool:
        jobs={pool.submit(execute,folder):folder for folder in folders if folder.name not in completed}
        for job in as_completed(jobs):
            row=job.result();manifest['rows'].append(row)
            manifest['rows'].sort(key=lambda r:r['source'])
            manifest['actualAttempts']=sum(r['actualAttempts']for r in manifest['rows'])
            manifest['counts']={status:sum(r['status']==status for r in manifest['rows'])for status in ('passed','needs_repair','error')}
            if manifest['actualAttempts']>manifest['maximumAttempts']:raise ValueError('full_clean_budget_exceeded')
            core.write(target,manifest)
            print(json.dumps({k:v for k,v in row.items()if k not in ('probeFailures','invalidatingCounters')},ensure_ascii=False),flush=True)
    manifest['complete']=len(manifest['rows'])==len(plan);core.write(target,manifest)
    return manifest


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--prepared-root',required=True);p.add_argument('--name',required=True);p.add_argument('--workers',type=int,default=2)
    args=p.parse_args();result=run(args.prepared_root,args.name,args.workers)
    print(json.dumps({k:v for k,v in result.items()if k not in ('rows','plan')},ensure_ascii=False))
