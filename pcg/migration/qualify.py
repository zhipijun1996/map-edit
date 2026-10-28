"""Finish actual fixed-quality experiments and native packages after diagnostics."""
from __future__ import annotations
import argparse
import collections
import shutil
import time
from pathlib import Path
from . import core, physics, holdout_guard, pool_protocols


def run(prepared_root, clean_campaign, name, follow=False):
    root = Path(prepared_root).resolve()
    campaign = Path(clean_campaign).resolve()
    core.safe_id(name)
    target = core.STATE/'campaigns'/(name+'.json')
    state = core.read(target) if target.exists() else dict(
        schema='pcg/full-migration-qualification/v1', preparedRoot=core.relative(root),
        cleanCampaign=core.relative(campaign), rows=[], humanApproval='UNKNOWN')
    if state['preparedRoot'] != core.relative(root) or state['cleanCampaign'] != core.relative(campaign):
        raise ValueError('qualification_campaign_identity_changed')
    with core.batch_enrollment():
        while True:
            diagnostics = core.read(campaign)
            completed = {row['source'] for row in state['rows']}
            pending = [row for row in diagnostics['rows'] if row['status']=='passed' and row['source'] not in completed]
            for diagnostic in pending:
                source = diagnostic['source']; folder = root/source
                plan = next(row for row in diagnostics['plan'] if row['source']==source)
                row = dict(source=source, status='repair_required', actualAttempts=0)
                experiment = name+'-'+source[:12]
                report_path = core.REPO/'pcg/results'/experiment/'migration-physics.json'
                ready = root.parent/(name+'-packages')/source
                try:
                    core.verify_artifacts([diagnostic['report'], diagnostic['replayCases']])
                    if core.sha(folder/'module.mapnote.json') != plan['documentSha256'] or core.sha(folder/'cases.json') != plan['casesSha256']:
                        # A successful prior qualification attached certificate
                        # fields; its report must still bind the same semantics.
                        if not report_path.exists():raise ValueError('frozen_diagnostic_inputs_changed')
                    shutil.copy2(core.REPO/diagnostic['replayCases']['path'], folder/'replay-cases.json')
                    if report_path.exists():
                        report=core.read(report_path)
                    else:
                        protocol_path=pool_protocols.runtime_protocol(folder,new_run=True)
                        holdout_guard.check(folder,protocol_path=protocol_path)
                        report=physics.run(folder,experiment,protocol_path=protocol_path)
                    holdout_guard.observe_report(folder,report_path)
                    row.update(actualAttempts=report['actualAttempts'],physicsReport=core.relative(report_path))
                    if not report['passed']:
                        row['status']='quality_or_boundary_failed'
                    else:
                        core.certify(folder,report_path)
                        if not ready.exists():core.package(folder,ready)
                        result=core.promote(ready)
                        row.update(status='active',moduleId=result['moduleId'])
                except holdout_guard.HoldoutConflict as error:
                    row.update(status='holdout_pool_locked',phase='holdout_guard',conflict=error.details)
                except Exception as error:
                    row['conflict']=str(error)
                state['rows'].append(row)
                state['counts']=dict(collections.Counter(r['status']for r in state['rows']))
                state['actualAttempts']=sum(r['actualAttempts']for r in state['rows'])
                core.write(target,state)
                print(__import__('json').dumps(row,ensure_ascii=False),flush=True)
            state['diagnosticCounts']=diagnostics.get('counts',{})
            state['diagnosticComplete']=diagnostics.get('complete',False)
            core.write(target,state)
            if not follow or diagnostics.get('complete'):
                break
            time.sleep(2)
    return state


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepared-root',required=True)
    parser.add_argument('--clean-campaign',required=True)
    parser.add_argument('--name',required=True)
    parser.add_argument('--follow',action='store_true')
    args=parser.parse_args()
    result=run(args.prepared_root,args.clean_campaign,args.name,args.follow)
    print(__import__('json').dumps(result.get('counts',{}),ensure_ascii=False))
