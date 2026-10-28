"""Version-bound delivery views of the original candidate store; no simulation."""
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
DEFAULT_RUNS = ['workshop-junction-windgap-production-v1', 'workshop-junction-bridges-production-v1']
OUT = REPO / 'generation/workshop/junctions-v1'


def binding(path):
    return dict(path=str(path.relative_to(REPO)), sha256=file_sha(path))


def publish(runs, target):
    if target.exists():
        raise ValueError('immutable delivery view exists')
    baseline_path = REPO / 'pcg/creative-production/curation/junction-baseline-v1.json'
    baseline = json.loads(baseline_path.read_text())
    old_versions = {r['contentVersion'] for r in baseline['records']}
    for row in baseline['records']:
        for source in row['files']:
            if file_sha(REPO / source['path']) != source['sha256']:
                raise ValueError('original candidate bytes changed')
    modules = []
    run_bindings = []
    for run in runs:
        summary_path = REPO / 'pcg/results' / run / 'summary.json'
        summary = json.loads(summary_path.read_text())
        run_bindings.append(binding(summary_path))
        for ledger in summary['ledger']:
            for version in ledger['versions']:
                if version in old_versions:
                    raise ValueError('old version cannot count as new')
                folder = REPO / 'pcg/map_directed/library/candidates' / version.removeprefix('sha256:')
                record = json.loads((folder / 'record.json').read_text())
                document = verified_document(folder / 'module.mapnote.json')
                cases = json.loads((folder / 'cases.json').read_text())['cases']
                gc = document['generationContract']
                if record['contentVersion'] != version or gc['contentVersion'] != version:
                    raise ValueError('candidate identity mismatch')
                if file_sha(folder / 'cases.json') != record['cases_sha256']:
                    raise ValueError('case bytes changed')
                if any(q['status'] != 'awaiting_human_review' for q in record['quality_gates']):
                    raise ValueError('original regular gate did not pass')
                idea = cases[0]['idea_ids'][0]
                label = idea + '-' + str(cases[0]['interface'] + 1)
                sources = {r['routeId']: r['sourceCaseId'] for r in gc['generation']['source']['routeCases']}
                routes = [dict(id=r['id'], case_id=sources[r['id']],
                               **{'from':r['from'], 'to':r['to']}, role=r['role'],
                               via_ports=next(c['route_spec'].get('via_ports', []) for c in cases if c['id'] == sources[r['id']]))
                          for r in gc['routes']]
                clips = []
                for p in sorted((OUT / 'videos').glob('*/manifest.json')):
                    for clip in json.loads(p.read_text())['clips']:
                        if clip['case_sha256'] not in {c['module_sha256'] for c in cases}:
                            continue
                        movie = p.parent / clip['file']
                        if file_sha(movie) != clip['sha256']:
                            raise ValueError('native clip bytes changed')
                        clips.append(dict(**binding(movie), manifest=binding(p),
                                          case_sha256=clip['case_sha256'], frames_exact=clip['frames_exact'],
                                          duration=clip['duration'], strict_comparison='passed'))
                item = dict(id=label, name=document['title'], contentVersion=version,
                            family=cases[0]['family'], content_role='spatial_junction',
                            port_count=len(gc['ports']), ports=gc['ports'], directed_relations=gc['relations'],
                            routes=routes, case_ids=[c['id'] for c in cases], record=binding(folder / 'record.json'),
                            record_sha256=file_sha(folder / 'record.json'), document=binding(folder / 'module.mapnote.json'),
                            document_sha256=file_sha(folder / 'module.mapnote.json'), case_file=binding(folder / 'cases.json'),
                            scene=binding(Path(__file__).with_name('main_v1.tscn')),
                            presentation_source=binding(Path(__file__).with_name('main_v1.gd')),
                            specification=record['specification'], videos=clips,
                            source_run='pcg/results/' + run + '/' + ledger['recipe'],
                            human_video_observation='unreviewed_new_version', human_playtest='UNKNOWN',
                            assembly='UNKNOWN pending exact placement/ingress/seam proof', production_admitted=False)
                modules.append(item)
    modules.sort(key=lambda m:m['id'])
    if not modules or len({m['contentVersion'] for m in modules}) != len(modules):
        raise ValueError('empty or duplicate delivery')
    for item in modules:
        destination = OUT / 'modules' / (item['id'] + '.mapnote.json')
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() and file_sha(destination) != item['document_sha256']:
            raise ValueError('existing published document changed')
        shutil.copyfile(REPO / item['document']['path'], destination)
        item['published_document'] = binding(destination)
        item['diagram'] = str(destination.with_suffix('').with_suffix('.svg').relative_to(REPO))
    job = OUT / ('render-' + target.stem + '.json')
    write(job, [str(REPO / m['published_document']['path']) for m in modules])
    render = "import fs from 'node:fs';import {renderContractSvg} from './module-contract-render.js';for(const p of JSON.parse(fs.readFileSync(process.argv[1]))){fs.writeFileSync(p.replace(/\\.mapnote\\.json$/,'.svg'),renderContractSvg(JSON.parse(fs.readFileSync(p))));}"
    subprocess.run(['node', '--input-type=module', '-e', render, str(job)], cwd=REPO, check=True)
    job.unlink()
    for item in modules:
        item['diagram_binding'] = binding(REPO / item['diagram'])
    value = dict(schema='pcg/spatial-junction-delivery/v1', id='junctions-v1',
                 baseline=binding(baseline_path), baseline_versions=len(old_versions), new_modules=len(modules),
                 spatial_hypotheses=len({m['family'] for m in modules}),
                 port_counts=dict(collections.Counter(str(m['port_count']) for m in modules)),
                 publisher_source=binding(Path(__file__)), source_runs=run_bindings,
                 human_source=binding(REPO / 'pcg/feedback/workshop/idea-sources/human-multiport-implementation/v1.json'),
                 modules=modules, video_count=sum(len(m['videos']) for m in modules),
                 human_fun='awaiting_review', production_admitted=False, whole_map='UNKNOWN')
    write(target, value)
    print(json.dumps(dict(manifest=str(target.relative_to(REPO)), modules=len(modules), videos=value['video_count'])))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--runs', nargs='+', default=DEFAULT_RUNS)
    parser.add_argument('--manifest', type=Path, default=OUT / 'manifest.json')
    args = parser.parse_args()
    publish(args.runs, args.manifest.resolve())
