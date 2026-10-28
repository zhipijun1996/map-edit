import argparse
import json
from pathlib import Path
from . import core


def main():
    parser = argparse.ArgumentParser(description='Migrate existing Modules; never generate new gameplay.')
    commands = parser.add_subparsers(dest='command', required=True)
    audit = commands.add_parser('audit'); audit.add_argument('--out', type=Path)
    inspect = commands.add_parser('inspect'); inspect.add_argument('source', type=Path)
    prepare = commands.add_parser('prepare'); prepare.add_argument('source', type=Path); prepare.add_argument('--out', required=True, type=Path); prepare.add_argument('--id')
    validate = commands.add_parser('validate'); validate.add_argument('folder', type=Path); validate.add_argument('--certified', action='store_true')
    promote = commands.add_parser('promote'); promote.add_argument('folder', type=Path)
    replay = commands.add_parser('replay'); replay.add_argument('folder', type=Path); replay.add_argument('--name', required=True); replay.add_argument('--protocol',type=Path)
    certify = commands.add_parser('certify'); certify.add_argument('folder', type=Path); certify.add_argument('--report', type=Path, required=True)
    package = commands.add_parser('package'); package.add_argument('folder', type=Path); package.add_argument('--out', type=Path, required=True)
    refresh = commands.add_parser('refresh-package'); refresh.add_argument('folder',type=Path)
    equivalence = commands.add_parser('equivalence');equivalence.add_argument('source',type=Path);equivalence.add_argument('--primary',required=True);equivalence.add_argument('--out',type=Path,required=True)
    archive = commands.add_parser('archive'); archive.add_argument('source', type=Path); archive.add_argument('--reason', required=True, choices=['explicitly_discarded','exact_duplicate']); archive.add_argument('--reason-record', required=True)
    commands.add_parser('build')
    campaign = commands.add_parser('campaign'); campaign.add_argument('--name', default='foundation-migration-pilot');campaign.add_argument('--group',choices=['pilot','remaining'],default='pilot')
    full = commands.add_parser('full'); full.add_argument('--name', default='foundation-full-v4'); full.add_argument('--stage', choices=['prepare','clean','complete'], default='complete')
    args = parser.parse_args()
    if args.command == 'audit':
        result = core.audit()
        if args.out: core.write(args.out, result)
        result = {key: value for key, value in result.items() if key != 'rows'}
    elif args.command == 'inspect': result = core.assess(args.source)
    elif args.command == 'prepare': result = core.prepare(args.source, args.out, args.id)
    elif args.command == 'validate': result = core.validate(args.folder, args.certified)
    elif args.command == 'promote': result = core.promote(args.folder)
    elif args.command == 'replay':
        from .physics import run
        from . import pool_protocols,holdout_guard
        protocol_path=pool_protocols.runtime_protocol(args.folder,args.protocol,new_run=True)
        holdout_guard.check(args.folder,protocol_path=protocol_path)
        result = run(args.folder, args.name,protocol_path=protocol_path)
        holdout_guard.observe_report(args.folder,core.REPO/'pcg/results'/args.name/'migration-physics.json')
    elif args.command == 'certify': result = core.certify(args.folder, args.report)
    elif args.command == 'package': result = core.package(args.folder, args.out)
    elif args.command == 'refresh-package': result = core.refresh_package(args.folder)
    elif args.command == 'equivalence':
        from .equivalence import decision
        result = decision(args.source,args.primary,args.out)
    elif args.command == 'archive': result = core.archive(args.source, args.reason, args.reason_record)
    elif args.command == 'full':
        from .full_campaign import run
        result = run(args.name,args.stage)
    elif args.command == 'campaign':
        from .campaign import run
        result = run(args.name,args.group)
    else: result = core.build_catalog()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result.get('status') in ('needs_repair','unsatisfied'):
        raise SystemExit(2)


if __name__ == '__main__':
    try:
        main()
    except (ValueError,RuntimeError,OSError,KeyError) as error:
        print(json.dumps(dict(status='needs_repair',
            conflicts=[dict(code=getattr(error,'code',str(error).split(':')[0]),reason=str(error))],
            searched={'scope':'implemented migration path only'},
            negotiable=['repair the reported source, evidence, or unsupported adapter',
                        'inspect ledger and transaction state before retrying'],
            automaticDisposal=False),ensure_ascii=False,indent=2))
        raise SystemExit(2)
