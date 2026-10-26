"""Read/play immutable plains candidates; never generate or validate physics.

Manifest modules bind id/name/contentVersion/port_count, original record and
scene {path,sha256}, plus routes [{id,case_id,from,to}] and optional case_ids.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PCG = REPO / 'pcg'
DEFAULT_MANIFEST = REPO / 'generation/workshop/plains50-v1/manifest.json'
ENGINE = PCG / 'toolchain/Godot_v4.7.2-stable_linux.x86_64'


def sha(path):
    with path.open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def read(path):
    return json.loads(path.read_text())


def repository_file(value):
    if not isinstance(value, str):
        raise ValueError('repository file path required')
    path = (REPO / value).resolve()
    if not path.is_relative_to(REPO) or not path.is_file():
        raise ValueError('missing or outside-repository file: ' + value)
    return path


def bound_file(binding, label):
    if not isinstance(binding, dict) or not isinstance(binding.get('sha256'), str):
        raise ValueError(label + ' requires {path,sha256}')
    path = repository_file(binding.get('path'))
    if sha(path) != binding['sha256']:
        raise ValueError(label + ' bytes differ: ' + str(path.relative_to(REPO)))
    return path


def load_catalog(path):
    manifest = read(path)
    modules = manifest.get('modules')
    if not isinstance(modules, list) or not modules or not all(isinstance(entry, dict) for entry in modules):
        raise ValueError('manifest.modules must be a nonempty list')
    for field in ['id', 'contentVersion']:
        values = [entry.get(field) for entry in modules]
        if any(not isinstance(value, str) or not value for value in values) or len(set(values)) != len(values):
            raise ValueError('nonempty unique module ' + field + ' required')
    return manifest, modules


def inspect_entry(entry):
    """Checksum and identity checks only; no Harness or new admission decision."""
    record_path = bound_file(entry.get('record'), 'record')
    record = read(record_path)
    if entry.get('record_sha256', sha(record_path)) != sha(record_path):
        raise ValueError('record_sha256 differs from record binding')
    folder = record_path.parent
    document_path = repository_file(str((folder / 'module.mapnote.json').relative_to(REPO)))
    if not document_path.is_file() or sha(document_path) != record.get('document_sha256'):
        raise ValueError('stored document bytes differ')
    if 'document' in entry and sha(bound_file(entry['document'], 'document')) != sha(document_path):
        raise ValueError('manifest document differs from original stored document')
    if entry.get('document_sha256', sha(document_path)) != sha(document_path):
        raise ValueError('document_sha256 differs from stored document')
    document = read(document_path)
    contract = document.get('generationContract', {})
    version = entry['contentVersion']
    if record.get('contentVersion') != version or contract.get('contentVersion') != version or record.get('id') != document.get('id'):
        raise ValueError('record/document/manifest identity differs')
    status = record.get('technical_status')
    if status == 'passed_scoped':
        cases_path = repository_file(str((folder / 'case.json').relative_to(REPO)))
        expected = record.get('case_sha256')
        cases = [read(cases_path)] if cases_path.is_file() else []
    elif status == 'passed_scoped_multi_route':
        cases_path = repository_file(str((folder / 'cases.json').relative_to(REPO)))
        expected = record.get('cases_sha256')
        cases = read(cases_path).get('cases', []) if cases_path.is_file() else []
    else:
        raise ValueError('unsupported original candidate status: ' + str(status))
    if not cases_path.is_file() or sha(cases_path) != expected or not cases:
        raise ValueError('stored case bytes differ or missing cases')
    by_id = {case['id']: case for case in cases}
    if len(by_id) != len(cases):
        raise ValueError('duplicate original case identity')
    if 'case_ids' in entry and set(entry['case_ids']) != set(by_id):
        raise ValueError('manifest case_ids differ from original stored cases')
    port_count = entry.get('port_count')
    if type(port_count) is not int or port_count < 2 or port_count != len(contract.get('ports', [])):
        raise ValueError('manifest port_count differs from original contract')
    routes = entry.get('routes')
    if not isinstance(routes, list) or not routes or not all(isinstance(route, dict) for route in routes):
        raise ValueError('explicit routes [{id,case_id,from,to}] required')
    route_ids = [route.get('id') for route in routes]
    if any(not isinstance(value, str) or not value for value in route_ids) or len(set(route_ids)) != len(route_ids):
        raise ValueError('nonempty unique route id required')
    original_routes = {route['id']: route for route in contract.get('routes', [])}
    route_sources = {row['routeId']: row['sourceCaseId'] for row in contract.get('generation', {}).get('source', {}).get('routeCases', [])}
    single_source = contract.get('generation', {}).get('source', {}).get('sourceCaseId')
    for route in routes:
        key = route['id']
        if key not in original_routes or route.get('case_id') not in by_id:
            raise ValueError('route or route case is not in the original candidate: ' + key)
        if route_sources.get(key, single_source) != route['case_id']:
            raise ValueError('route case binding differs from original source: ' + key)
        for direction in ['from', 'to']:
            if direction in route and route[direction] != original_routes[key].get(direction):
                raise ValueError('route direction differs from original contract: ' + key)
    scene = bound_file(entry.get('scene'), 'scene')
    if scene.suffix != '.tscn':
        raise ValueError('native .tscn scene required')
    return dict(record_path=record_path, document_path=document_path, cases_path=cases_path,
                record=record, document=document, cases=by_id, scene=scene, routes=routes)


def select_entry(modules, selector):
    direct = [entry for entry in modules if selector in [entry['id'], entry['contentVersion']]]
    if direct:
        return direct[0]
    if selector.isdecimal() and 1 <= int(selector) <= len(modules):
        return modules[int(selector) - 1]
    raise ValueError('unknown module number/id/contentVersion: ' + selector)


def play(entry, inspected, route_id, replay=False, quit_after=None):
    routes = inspected['routes']
    if route_id is None:
        if entry['port_count'] >= 3 or len(routes) != 1:
            raise ValueError('--route required; available: ' + ', '.join(route['id'] for route in routes))
        route = routes[0]
    else:
        matches = [route for route in routes if route['id'] == route_id]
        if not matches:
            raise ValueError('unknown route; available: ' + ', '.join(route['id'] for route in routes))
        route = matches[0]
    if not ENGINE.is_file():
        raise ValueError('Godot runtime missing; restore original runtime first')
    results = PCG / 'results'
    results.mkdir(exist_ok=True)
    out = Path(tempfile.mkdtemp(prefix='workshop-plains50-play-', dir=results))
    cases_path = out / 'review_cases.json'
    # Only the envelope is new. The original case dictionary is unchanged.
    case = inspected['cases'][route['case_id']]
    cases_path.write_text(json.dumps(dict(cases=[case]), ensure_ascii=False) + '\n')
    command = [str(ENGINE)] + (['--audio-driver', 'Dummy'] if quit_after is not None else [])
    command += ['--path', str(PCG / 'prototype/godot'), str(inspected['scene']),
               '--', '--cases-json', str(cases_path), '--case', '0']
    if replay:
        command += ['--trace-json', str(out / 'replay.trace.json')]
    launch = dict(schema='pcg/plains-candidate-launch/v1', id=entry['id'], contentVersion=entry['contentVersion'],
                  route=route['id'], case_id=case['id'], original_record=str(inspected['record_path'].relative_to(REPO)),
                  original_cases_sha256=sha(inspected['cases_path']), source_scene=entry['scene'],
                  mode='program_replay' if replay else 'manual', quit_after_wall_seconds=quit_after,
                  copied_case_unchanged=(read(cases_path)['cases'][0] == case), command=command,
                  new_physics_validation=False, human_playtest_claimed=False)
    (out / 'launch.json').write_text(json.dumps(launch, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(launch=str((out / 'launch.json').relative_to(REPO)), mode=launch['mode'],
                          route=route['id'], case_id=case['id']), ensure_ascii=False), flush=True)
    with (out / 'native.log').open('w') as log:
        process = subprocess.Popen(command, cwd=REPO, stdout=log, stderr=subprocess.STDOUT)
        timed_out = False
        try:
            code = process.wait(timeout=quit_after)
        except subprocess.TimeoutExpired:
            timed_out = True
            process.terminate()
            try:
                code = process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                code = process.wait()
    errors = [line for line in (out / 'native.log').read_text().splitlines() if any(token in line for token in ['ERROR:', 'SCRIPT ERROR', 'Parse Error'])]
    (out / 'exit.json').write_text(json.dumps(dict(returncode=code, intentional_smoke_timeout=timed_out, native_errors=errors,
                                                 new_physics_validation=False, human_playtest_claimed=False), indent=2) + '\n')
    if errors:
        raise ValueError('native consumer logged errors; see ' + str(out / 'native.log'))
    if not timed_out and code:
        raise ValueError('native consumer exited with ' + str(code) + '; see ' + str(out / 'native.log'))
    return out


def main():
    parser = argparse.ArgumentParser(description='列出/手玩已有平原候选；只校验原件字节，不生成Module或运行物理验收。')
    parser.add_argument('--manifest', type=Path, default=DEFAULT_MANIFEST)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--list', action='store_true', help='列出编号、名称、端口、关系与路线')
    action.add_argument('--play', metavar='ID_OR_VERSION', help='编号、稳定ID或完整contentVersion')
    parser.add_argument('--route', help='精确routeId；三/四端口必须明确指定')
    parser.add_argument('--replay', action='store_true', help='回放原案例输入；默认手玩，也可在原生窗口点击Replay')
    parser.add_argument('--quit-after', type=float, metavar='SECONDS', help='按墙钟秒自动退出，烟测使用Dummy音频')
    args = parser.parse_args()
    if args.quit_after is not None and args.quit_after <= 0:
        parser.error('--quit-after must be positive wall-clock seconds')
    if args.list and (args.route or args.replay or args.quit_after is not None):
        parser.error('--route/--replay/--quit-after require --play')
    try:
        manifest, modules = load_catalog(args.manifest.resolve())
        if args.list:
            for index, entry in enumerate(modules, 1):
                inspected = inspect_entry(entry)
                group = entry.get('decision_group') or entry.get('family', 'UNKNOWN')
                print(f"{index:02} {entry['id']} | {entry.get('name', entry['id'])} | {entry['port_count']}port | {group} | routes=" + ','.join(route['id'] for route in inspected['routes']))
        else:
            entry = select_entry(modules, args.play)
            play(entry, inspect_entry(entry), args.route, args.replay, args.quit_after)
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as error:
        parser.error(str(error))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
