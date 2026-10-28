"""A version-bound delivery view over the original candidate store."""
import argparse
import collections
import json
import shutil
import subprocess
from pathlib import Path

from pcg.map_directed.library import verified_document
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.workshop.experiments import write

REPO = Path(__file__).resolve().parents[4]
OUT = REPO / 'generation/workshop/plains30-v1'


def binding(p):
    return dict(path=str(p.relative_to(REPO)), sha256=file_sha(p))


def scene_for(case):
    explicit = case.get('native_scene')
    if explicit:
        return REPO / 'pcg' / explicit.removeprefix('res://')
    named = {'finite-enemy-routes': 'd03_overview_v1.tscn',
             'park-for-return': 'd04_overview_v1.tscn',
             'bell-carrier-catch': 'd05_overview_v1.tscn'}
    if case['family'] in named:
        return Path(__file__).with_name(named[case['family']])
    if any(l.get('paired_gate') for l in case.get('latches', [])):
        return Path(__file__).parent.parent / 'batch30_cell/main_v3.tscn'
    raise ValueError('explicit native consumer required for new recipe')


def publish(runs, target):
    if target.exists():
        raise ValueError('immutable delivery manifest already exists')
    baseline_path = REPO / 'pcg/creative-production/batch30/baseline-v1.json'
    baseline = json.loads(baseline_path.read_text())
    old = {r['contentVersion'] for r in baseline['records']}
    for row in baseline['records']:
        for source in row['files']:
            if file_sha(REPO / source['path']) != source['sha256']:
                raise ValueError('original candidate bytes changed')
    modules, run_bindings = [], []
    for run in runs:
        summary_path = REPO / 'pcg/results' / run / 'summary.json'
        summary = json.loads(summary_path.read_text())
        run_bindings.append(binding(summary_path))
        for entry in summary['ledger']:
            for version in entry['versions']:
                if version in old:
                    raise ValueError('old candidate cannot count as new')
                folder = REPO / 'pcg/map_directed/library/candidates' / version.removeprefix('sha256:')
                record = json.loads((folder / 'record.json').read_text())
                document = verified_document(folder / 'module.mapnote.json')
                cases = json.loads((folder / 'cases.json').read_text())['cases']
                gc = document['generationContract']
                assert gc['contentVersion'] == record['contentVersion'] == version
                assert file_sha(folder / 'cases.json') == record['cases_sha256']
                assert all(q['status'] == 'awaiting_human_review' for q in record['quality_gates'])
                first = cases[0]
                idea = first['idea_ids'][0].removeprefix('PR-').removeprefix('B30-')
                if idea == 'human-d05-bell-carrier-catch': idea = 'D05'
                label = idea + '-' + str(first['interface'] + 1)
                route_cases = {r['routeId']:r['sourceCaseId'] for r in gc['generation']['source']['routeCases']}
                routes = [dict(id=r['id'], case_id=route_cases[r['id']],
                               **{'from':r['from'], 'to':r['to']}, role=r['role'],
                               via_ports=next(c['route_spec'].get('via_ports', []) for c in cases if c['id'] == route_cases[r['id']]))
                          for r in gc['routes']]
                clips = []
                for manifest in sorted((OUT / 'videos').glob('*/manifest.json')):
                    for clip in json.loads(manifest.read_text())['clips']:
                        if clip['case_sha256'] not in {c['module_sha256'] for c in cases}:continue
                        movie = manifest.parent / clip['file']
                        assert file_sha(movie) == clip['sha256']
                        clips.append(dict(**binding(movie), manifest=binding(manifest),
                                          case_sha256=clip['case_sha256'], frames_exact=clip['frames_exact'],
                                          duration=clip['duration'], strict_comparison='passed'))
                scene = scene_for(first)
                modules.append(dict(id=label, name=document['title'], contentVersion=version,
                    family=first['family'], content_role='action_challenge',
                    port_count=len(gc['ports']), ports=gc['ports'], directed_relations=gc['relations'],
                    routes=routes, case_ids=[c['id'] for c in cases],
                    record=binding(folder / 'record.json'), record_sha256=file_sha(folder / 'record.json'),
                    document=binding(folder / 'module.mapnote.json'), document_sha256=file_sha(folder / 'module.mapnote.json'),
                    case_file=binding(folder / 'cases.json'), scene=binding(scene),
                    presentation_source=binding(scene.with_suffix('.gd')),
                    specification=record['specification'], videos=clips,
                    source_run='pcg/results/' + run + '/' + entry['recipe'],
                    human_video_observation='unreviewed_new_version', human_playtest='UNKNOWN',
                    assembly='UNKNOWN pending exact placement/ingress/seam proof', production_admitted=False))
    assert modules and len({m['contentVersion'] for m in modules}) == len(modules)
    modules.sort(key=lambda m:m['id'])
    for item in modules:
        destination = OUT / 'modules' / (item['id'] + '.mapnote.json')
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():assert file_sha(destination) == item['document_sha256']
        else:shutil.copyfile(REPO / item['document']['path'], destination)
        item['published_document'] = binding(destination)
        svg = destination.with_name(item['id'] + '.svg')
        code = "import fs from 'node:fs';import {renderContractSvg} from './module-contract-render.js';fs.writeFileSync(process.argv[2],renderContractSvg(JSON.parse(fs.readFileSync(process.argv[1]))));"
        subprocess.run(['node', '--input-type=module', '-e', code, str(destination), str(svg)], cwd=REPO, check=True)
        item['diagram'] = str(svg.relative_to(REPO));item['diagram_binding'] = binding(svg)
    value = dict(schema='pcg/plains30-delivery/v1', id='plains30-v1', baseline=binding(baseline_path),
                 baseline_versions=len(old), target_new_modules=30, new_modules=len(modules),
                 registered_rule_relationships=len({m['family'] for m in modules}),
                 family_notice='Rule relationships and adapters await independent experience grouping; not30 distinct families.',
                 port_counts=dict(collections.Counter(str(m['port_count']) for m in modules)),
                 publisher_source=binding(Path(__file__)), source_runs=run_bindings,
                 human_source=binding(REPO / 'pcg/feedback/workshop/idea-sources/human-plains30-paired-bell/v1.json'),
                 modules=modules, video_count=sum(len(m['videos']) for m in modules),
                 human_fun='awaiting_review', production_admitted=False, whole_map='UNKNOWN')
    write(target, value)
    print(json.dumps(dict(manifest=str(target.relative_to(REPO)), modules=len(modules), videos=value['video_count'])))


if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--runs',nargs='+',required=True)
    p.add_argument('--manifest',type=Path,default=OUT/'manifest.json')
    a=p.parse_args();publish(a.runs,a.manifest)
