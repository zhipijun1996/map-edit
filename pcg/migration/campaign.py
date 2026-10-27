"""Bounded sequential migration of existing templates, with durable outcomes."""
from pathlib import Path
from . import core

PILOTS = [('n16','87731645f7be'), ('n17','21fc69bcbdcc'),
          ('n08','1685840df001'), ('n06','9450553d8135'),
          ('n11','87b8ed50f5b8'), ('n07','88c75d0f8e7a')]
REMAINING = [('n06-four','af12390291ec'), ('n10','24f33e573c24'),
             ('n04-three','f5b43214c3b5'), ('n19','8f066baa2327')]


def locate(prefix):
    sources = list(core.LEGACY.glob(prefix+'*'))
    sources += [core.resolve_artifact(source+'/record.json').parent
                for source, entry in core.ledger()['entries'].items()
                if entry.get('sourceVersion', entry.get('contentVersion','')).removeprefix('sha256:').startswith(prefix)
                and entry.get('migrationStatus') == 'active']
    if len(sources) != 1:
        raise ValueError('ambiguous_or_missing_existing_version:'+prefix)
    return sources[0]


def expected_attempts(folder, doc):
    cases = core.legacy_cases(folder)
    return sum(72 if c.get('moving_platforms') or c.get('saws') or c.get('enemies') else 50
               for c in cases)+6*len(doc['generationContract']['ports'])+len(cases)


def run(name='foundation-migration-pilot', group='pilot'):
    from . import physics
    core.safe_id(name)
    target = core.STATE/'campaigns'/(name+'.json')
    items = PILOTS if group=='pilot' else REMAINING if group=='remaining' else None
    if items is None:raise ValueError('unknown_predeclared_campaign_group')
    plan = [dict(name=label, sourcePrefix=prefix) for label,prefix in items]
    protocol = core.read(physics.PROTOCOL)
    if target.exists():
        ledger = core.read(target)
        if ledger['plan'] != plan or ledger['protocolSha256'] != core.sha(physics.PROTOCOL):
            raise ValueError('campaign_definition_changed')
    else:
        estimate = sum(expected_attempts(locate(prefix), core.read(locate(prefix)/'module.mapnote.json')) for _,prefix in items)
        if estimate > protocol['maximumAttemptsThisBatch']:
            raise ValueError('campaign_exceeds_predeclared_budget')
        ledger = dict(schema='pcg/foundation-migration-campaign/v1', plan=plan,
            protocolSha256=core.sha(physics.PROTOCOL), maximumAttempts=protocol['maximumAttemptsThisBatch'],
            reservedAttempts=estimate, rows=[], newGameplayFamilies=0)
        core.write(target, ledger)
    for label, prefix in items:
        previous = next((row for row in ledger['rows'] if row['name'] == label), None)
        if previous and previous['status'] in ('active','needs_repair'):
            continue
        folder = locate(prefix)
        original = next((source for source, entry in core.ledger()['entries'].items()
                         if entry.get('migrationStatus') == 'active' and entry.get('archive') == core.relative(folder)), None)
        if original:
            entry = core.ledger()['entries'][original]
            core.validate(core.REPO/entry['destination'], require_certified=True)
            row=dict(name=label,status='active',moduleId=entry['moduleId'],source=original,
                     attempts=expected_attempts(folder,core.read(folder/'module.mapnote.json')),reused=True)
        else:
            prepared = core.REPO/'.cache/migration'/('pilot-'+label+'-v1')
            ready = core.REPO/'.cache/migration'/('ready-'+label+'-v1')
            run_name = 'foundation-migration-'+label+'-v1'
            report_path = core.REPO/'pcg/results'/run_name/'migration-physics.json'
            row=dict(name=label, source=core.relative(folder), status='needs_repair', attempts=0)
            try:
                if not prepared.exists():
                    response=core.prepare(folder,prepared)
                    if response['status']!='prepared_unverified':raise ValueError(str(response))
                core.validate(prepared)
                if not report_path.exists():
                    physics.run(prepared,run_name)
                report=core.read(report_path);row['attempts']=report['actualAttempts']
                core.certify(prepared,report_path)
                if not ready.exists():core.package(prepared,ready)
                else:core.validate(ready,require_certified=True)
                result=core.promote(ready)
                row.update(status='active',moduleId=result['moduleId'])
            except Exception as error:
                row['conflict']=str(error)
                journal=core.ledger()
                entry=journal['entries'].setdefault(row['source'],{})
                entry.update(migrationStatus='needs_repair',lastFailure=str(error),
                    physicsReport=core.relative(report_path) if report_path.exists() else 'NOT_COMPLETED',
                    destination='original')
                core.write(core.JOURNAL,journal)
        ledger['rows']=[r for r in ledger['rows'] if r['name']!=label]+[row]
        ledger['actualAttempts']=sum(r['attempts']for r in ledger['rows'])
        if ledger['actualAttempts'] > ledger['maximumAttempts']:
            raise ValueError('campaign_actual_budget_exceeded')
        core.write(target,ledger)
        print(__import__('json').dumps(row,ensure_ascii=False),flush=True)
    ledger['activeModules']=sum(row['status']=='active'for row in ledger['rows'])
    ledger['pendingModules']=sum(row['status']=='needs_repair'for row in ledger['rows'])
    core.write(target,ledger)
    return ledger
