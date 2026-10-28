"""Freeze, qualify and package the five approved candidates with existing tools."""
import argparse
import copy
import gzip
import json
import shutil
from pathlib import Path
from pcg.migration import core, physics, holdout_guard, godot_package
from pcg.prototype.factory.core.quality import digest
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
from .implement_approved_batch001 import verify_handoff


def rows(ids=None):
    return [r for r in verify_handoff()['rows'] if not ids or r['reviewId'] in ids]


def freeze(row):
    folder=core.REPO/row['outputDirectory']
    if (folder/'frozen.json').exists():raise ValueError('candidate_already_frozen')
    before=folder/'revisions/initial-v1';before.mkdir(parents=True)
    for name in ('module.mapnote.json','cases.json','thumbnail.svg','migration.json'):
        shutil.copy2(folder/name,before/name)
    cases=core.read(folder/'cases.json')['cases'];selections=[]
    run='approved-b001-'+row['reviewId']+'-'+('repair1' if row['reviewId']=='01' else 'repair3')
    selected=[]
    if row['reviewId'] in ('01','03','05'):
        selected=core.read(core.REPO/'pcg/results'/run/'repair-check.json')['rows']
    for i,c in enumerate(cases):
        match=next((v for v in selected if v['case']['route_spec']['id']==c['route_spec']['id'] and v['check']['ok']),None)
        if match:
            c=copy.deepcopy(match['case'])
            selections.append(dict(routeId=c['route_spec']['id'],run=run,evidence=match['evidence'],selection='first strict clean pass in predeclared enumeration'))
        for key in ('module_sha256','noise','recorded_frames','factory_evidence','factory_id'):c.pop(key,None)
        c['id']='approved-b001-'+row['reviewId']+'-'+c['route_spec']['id']+'-frozen-v2'
        cases[i]=c
    doc=core.read(folder/'module.mapnote.json');g=doc['generationContract']
    g['generation']['approvedImplementation']['controlProgramsSha256']=digest([c['control_plan'] for c in cases])
    g['generation']['approvedImplementation']['controlSelection']=selections
    for route,c in zip(g['routes'],cases):
        route['actionTags']=list(dict.fromkeys(x['op'] for x in c['control_plan'] if x['op'] not in ('wait','axis')))
        route['resourceProfile']=dict(status='declared_pending_qualification',capabilities=c['capabilities'],initialAirShots=1,
            initialHealth=5,initialStamina=100,scriptedRecovery=False,
            recovery='Original landing and actual projectile-hit consumers only; evidence records accepted recovery events.',
            rewardSites=c['reward_sites'],requiredRewards=c.get('required_rewards',[]))
        route['initialConditions']=dict(status='declared_pending_qualification',spawn=c['spawn'],entryPort=c['route_spec']['from_port'],
            latches=c['latches'],enemies=c['enemies'],warmupFrames=c.get('warmup_frames',4),worldRebuiltBeforeRoute=True,
            connectedPortSubset=[p['id'] for p in g['ports']],closureProfile='all-ports-open-test-only',orientation='original')
        route['resourcePressure']=dict(status='declared',requestedShots=sum(v['op']=='shoot' for v in c['control_plan']),requestedJumps=sum(v['op']=='jump' for v in c['control_plan']),note='Input requests are not accepted actions or minimum requirements; see raw for actual consumption.')
    core.write(folder/'cases.json',dict(cases=cases));core.write(folder/'module.mapnote.json',doc)
    core.contract(folder/'module.mapnote.json',refresh=True)
    core.write(folder/'parameters.json',dict(schema='pcg/approved-design-parameters/v1',designVersion=row['designVersion'],
        implementationVersion=core.read(folder/'module.mapnote.json')['generationContract']['contentVersion'],
        blockSize=128,rectangle=g['space']['bounds'],actorBody=[24,36],
        content=godot_package.content_from_objects(doc),ports=g['ports'],
        controls=[dict(route=c['route_spec'],spawn=c['spawn'],goal=c['goal'],control_plan=c['control_plan'],max_frames=c['max_frames']) for c in cases],
        originalTuning=physics.artifact(core.REPO/'pcg/prototype/godot/config/player_tuning.json'),
        enemyDefinitions=[physics.artifact(core.REPO/'pcg/prototype/godot/resources/enemies'/name) for name in ('plains_sentry.tres','plains_diver.tres','patrol_health.tres')],
        difficulty='UNKNOWN: finite bot perturbations are not human difficulty',productionApproval=False))
    core.write(folder/'frozen.json',dict(module=physics.artifact(folder/'module.mapnote.json'),cases=physics.artifact(folder/'cases.json'),
        parameters=physics.artifact(folder/'parameters.json'),designVersion=row['designVersion'],
        implementationVersion=core.read(folder/'module.mapnote.json')['generationContract']['contentVersion'],
        selection=selections,geometryRevisions=0,controlProbeBudget=80,holdoutObserved=False))
    print(row['reviewId'],'frozen',flush=True)


def qualify(row):
    folder=core.REPO/row['outputDirectory'];frozen=core.read(folder/'frozen.json')
    core.verify_artifacts([frozen[k] for k in ('module','cases','parameters')])
    guard=holdout_guard.check(folder)
    core.write(folder/'holdout-precheck.json',guard)
    report=physics.run(folder,'approved-b001-'+row['reviewId']+'-qualified-v2')
    print(row['reviewId'],'qualification',report['passed'],report['actualAttempts'],flush=True)


def package(row):
    folder=core.REPO/row['outputDirectory'];run=core.REPO/'pcg/results'/('approved-b001-'+row['reviewId']+'-canonical-v2')
    cases=core.read(folder/'cases.json')['cases'];recorded=[]
    for index,c in enumerate(cases):
        witness=core.read(run/'canonical.json')['rows'][index]
        if not witness['check']['ok']:raise ValueError('missing_clean_witness:'+c['id'])
        # Replay data is separate from the immutable qualifier input. Never
        # overwrite its cases or consume another holdout for packaging.
        evidence=witness['evidence'];raw=json.loads(gzip.decompress((run/evidence['output']).read_bytes()))['results'][evidence['index']]
        v=physics._recording(c,raw);v['id']=raw['id'];recorded.append(v)
    core.write(folder/'playback-cases.json',dict(cases=recorded))
    out=folder/'playable';godot_package.compile_package(folder/'module.mapnote.json',folder/'playback-cases.json',out,stable_id=row['moduleId'])
    try:
        result=godot_package.run_package_validation(out)
    except Exception as error:
        core.write(folder/'package-result.json',dict(passed=False,error=str(error)))
        raise
    core.write(folder/'package-result.json',result);print(row['reviewId'],'native package',result['passed'],flush=True)


def canonical(row):
    folder=core.REPO/row['outputDirectory'];eng,cases,authors=physics._engine(folder,'approved-b001-'+row['reviewId']+'-canonical-v2',physics.FULL_PROTOCOL)
    core.write(eng.out/'input-binding.json',dict(module=physics.artifact(folder/'module.mapnote.json'),cases=physics.artifact(folder/'cases.json')))
    checks=[]
    for index,(c,r,e) in enumerate(eng.run([physics.fresh(c,'canonical') for c in cases],'frozen-canonical')):
        check=checked_purpose(authors[index],c,r)
        checks.append(dict(routeId=c['route_spec']['id'],check=check,evidence=e,entrySnapshot=r.get('entry_snapshot'),
                           observedExit={k:r['frames'][-1].get(k) for k in ('x','y','vx','vy','grounded','shot_charges','energy','hp','jumps_used','shot_cooldown','support_id')},
                           seconds=r['ticks']/60,shots=r['shots'],jumps=r['jumps']))
    core.write(eng.out/'canonical.json',dict(rows=checks,passed=all(v['check']['ok'] for v in checks),source=physics.artifact(__file__)))
    print(row['reviewId'],'frozen canonical',all(v['check']['ok'] for v in checks),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['freeze','qualify','canonical','package']);p.add_argument('--ids',nargs='+');a=p.parse_args()
    for row in rows(a.ids):globals()[a.action](row)
