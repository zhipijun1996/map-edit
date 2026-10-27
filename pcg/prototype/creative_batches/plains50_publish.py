"""Publish an immutable view/copies of ORIGINAL candidates, not a second pool."""
import argparse,collections,json,shutil,subprocess
from pathlib import Path
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.factory.core.quality import module_hash
from pcg.module_library.library import withdrawn_versions,verified_document

REPO=Path(__file__).resolve().parents[3]
BASELINE=REPO/'pcg/creative-production/curation/plains50-baseline-v1.json'
SOURCES=[
 'generation/workshop/plains50-terrain-v1/manifest-v2.json',
 'generation/workshop/plains50-enemy-v1/manifest.json',
 'generation/workshop/plains50/resources/manifest.json',
 'generation/workshop/plains50-new-relations/catalog-entries-v1.json',
 'generation/workshop/plains50-new-relations/manifest.json',
 'generation/workshop/plains50-machinery-v2/manifest.json',
]
ROOT_NAMES={'investment-fork':'单枪投资高奖或低路','thorn-branch':'尖刺窄道与低路分叉','brake-branch':'刹入侧袋与下层分流','timed-branch':'短门取宝与下层分流','refund-retreat-fork':'命中回充登高或西侧撤离'}
def read(p):return json.loads(Path(p).read_text())
def rel(p):return str(Path(p).resolve().relative_to(REPO))
def binding(p):return dict(path=rel(p),sha256=file_sha(p))
def walk(v):
    if isinstance(v,dict):
        yield v
        for child in v.values():yield from walk(child)
    elif isinstance(v,list):
        for child in v:yield from walk(child)

def video_index():
    found={};seen=set()
    for directory in sorted((REPO/'generation/workshop').glob('plains50*')):
        for p in sorted(directory.rglob('*.json')):
            if 'manifest'not in p.name and 'recording-index'not in p.name:continue
            for clip in walk(read(p)):
                case_sha=clip.get('case_sha256');name=clip.get('file',clip.get('path',''))
                if not case_sha or not isinstance(name,str)or not name.endswith('.mp4')or not clip.get('sha256'):continue
                options=[p.parent/name,REPO/name];movie=next((q for q in options if q.is_file()),None)
                if movie is None:continue
                if file_sha(movie)!=clip['sha256']:raise ValueError('movie_drift/'+str(movie))
                key=(case_sha,str(movie.resolve()))
                if key in seen:continue
                seen.add(key);strict=clip.get('strict_comparison')
                if not strict:strict='passed'if clip.get('frames_exact',0)>0 and clip.get('cell_events_exact')else'UNKNOWN'
                found.setdefault(case_sha,[]).append(dict(path=rel(movie),sha256=clip['sha256'],manifest=binding(p),case_sha256=case_sha,strict_comparison=strict,review_only=bool(clip.get('review_only')or strict=='failed'),frames_exact=clip.get('frames_exact',0),duration=clip.get('duration',clip.get('duration_seconds'))))
    return found

def publish(out,expected):
    if (out/'manifest.json').exists():raise ValueError('immutable published batch exists')
    baseline={r['contentVersion']for r in read(BASELINE)['rows']};withdrawn=withdrawn_versions();meta={};inputs=[]
    for name in SOURCES:
        p=REPO/name
        if not p.is_file():raise ValueError('missing completed owner manifest/'+name)
        data=read(p);inputs.append(binding(p))
        key=next(k for k in ['modules','rows','candidates','items']if k in data)
        for row in data[key]:
            version=row.get('contentVersion')
            if version:meta.setdefault(version,[]).append((row,p))
    candidates=[]
    for p in sorted((REPO/'pcg/module_library/store/candidates').glob('*/record.json')):
        record=read(p);version=record['contentVersion']
        if version in baseline or version in withdrawn:continue
        if record['technical_status']not in ['passed_scoped','passed_scoped_multi_route']or record.get('production_admitted'):raise ValueError('not_scoped_candidate')
        doc_path=p.parent/'module.mapnote.json';doc=verified_document(doc_path)
        if file_sha(doc_path)!=record['document_sha256']:raise ValueError('document_byte_drift')
        cp=p.parent/('cases.json'if(p.parent/'cases.json').exists()else'case.json');payload=read(cp);cases=payload['cases']if cp.name=='cases.json'else[payload]
        if file_sha(cp)!=record['cases_sha256'if cp.name=='cases.json'else'case_sha256']:raise ValueError('case_byte_drift')
        if any(set(c['capabilities'])-{'move','jump','shot_recoil'}for c in cases):raise ValueError('advanced_capability_in_plains')
        for c in cases:
            if module_hash(c)!=c['module_sha256']:raise ValueError('case_semantic_hash_drift')
        for a in record['evidence']:
            if file_sha(REPO/a['path'])!=a['sha256']:raise ValueError('candidate_artifact_drift')
        candidates.append((p,record,doc_path,doc,cp,cases))
    if len(candidates)!=expected:raise ValueError(f'expected {expected} qualified NEW versions, got {len(candidates)}')
    videos=video_index();modules=[];out.mkdir(parents=True,exist_ok=True);(out/'modules').mkdir(exist_ok=True)
    for p,record,doc_path,doc,cp,cases in candidates:
        gc=doc['generationContract'];version=record['contentVersion'];items=meta.get(version,[]);primary=items[0][0]if items else{}
        scene_value=next((row[k]for row,_ in items for k in ['scene','main_scene','play_scene']if row.get(k)),None)
        if isinstance(scene_value,dict):scene_path=REPO/scene_value['path']
        elif isinstance(scene_value,str):scene_path=REPO/scene_value
        elif cases[0].get('production_recipe')in ['investment-fork','thorn-branch','brake-branch','timed-branch','refund-fork']:scene_path=REPO/'pcg/prototype/workshop/main.tscn'
        else:raise ValueError('missing exact native scene/'+version)
        if not scene_path.is_file():raise ValueError('native scene missing')
        title=primary.get('name',primary.get('title',doc['title']))
        spec=record.get('specification',cases[0]['map_specification']);objective=spec.get('objective',{});recipe=objective.get('recipe',cases[0].get('production_recipe',cases[0]['family']))
        if not items:title=f'{ROOT_NAMES.get(recipe,recipe)} · {len(gc["ports"])}口 · 接口{cases[0]["interface"]+1}'
        if cases[0]['family']=='brake-gate-catch':title='开门与过檐刹入侧袋（可分步组合） · 接口'+str(cases[0].get('interface',objective.get('interface',0))+1)
        route_sources={x['routeId']:x['sourceCaseId']for x in gc['generation']['source'].get('routeCases',[])}
        routes=[dict(id=r['id'],case_id=route_sources.get(r['id'],gc['generation']['source'].get('sourceCaseId')),**{'from':r['from'],'to':r['to']},role=r['role'],via_ports=next((c.get('route_spec',{}).get('via_ports',[])for c in cases if c['id']==route_sources.get(r['id'])),[]))for r in gc['routes']]
        if any(r['case_id']not in {c['id']for c in cases}for r in routes):raise ValueError('route_case_binding_missing')
        qs=record.get('quality_gates',[record.get('quality_gate',{})])
        if any(q.get('status')!='awaiting_human_review'for q in qs):raise ValueError('original_quality_gate_not_passed')
        clips=[v for c in cases for v in videos.get(c['module_sha256'],[])]
        role='multiport_branch'if len(gc['ports'])>=3 else'threat_timing'if cases[0]['family']=='enemy-attack-relay'else'gravity_commitment'if cases[0]['family']=='trapdoor-commit'else'ordered_world_transaction'if cases[0]['family']=='sequence-order'else'plains_recoil_or_world_combination'
        row=dict(id='',name=title,contentVersion=version,family=cases[0]['family'],recipe=recipe,content_role=role,port_count=len(gc['ports']),ports=[dict(id=q['id'],position=q['position'],normal=q['normal'])for q in gc['ports']],directed_relations=gc['relations'],routes=routes,case_ids=[c['id']for c in cases],record=binding(p),record_sha256=file_sha(p),document=binding(doc_path),document_sha256=file_sha(doc_path),case_file=binding(cp),scene=binding(scene_path),specification=spec,source_manifests=[binding(m)for _,m in items],videos=clips,human_video_observation='unreviewed_new_version',human_playtest='UNKNOWN',assembly='UNKNOWN pending actual placement/entry-state/seam verification',production_admitted=False)
        modules.append(row)
    modules.sort(key=lambda m:(m['port_count']>=3,m['family'],m['specification']['id']))
    for index,row in enumerate(modules,1):
        row['id']=f'P{index:02d}';doc=read(REPO/row['document']['path']);target=out/'modules'/(doc['id']+'.mapnote.json');shutil.copy2(REPO/row['document']['path'],target)
        row['published_document']=binding(target);row['diagram']=rel(out/'modules'/(doc['id']+'.svg'))
    render="import fs from 'node:fs';import {renderContractSvg} from './module-contract-render.js';const x=JSON.parse(fs.readFileSync(process.argv[1]));for(const p of x){const d=JSON.parse(fs.readFileSync(p));fs.writeFileSync(p.replace(/\\.mapnote\\.json$/,'.svg'),renderContractSvg(d));}"
    job=out/'render-input.json';job.write_text(json.dumps([str(REPO/r['published_document']['path'])for r in modules]));subprocess.run(['node','--input-type=module','-e',render,str(job)],cwd=REPO,check=True);job.unlink()
    counts=collections.Counter(m['port_count']for m in modules)
    value=dict(schema='pcg/plains50-delivery/v1',id='plains50-v1',source_type='actual_current_codex_session_and_authorized_subagents',target_new_modules=expected,new_modules=len(modules),baseline=binding(BASELINE),human_source=binding(REPO/'pcg/feedback/workshop/idea-sources/human-plains50-branch-modules/v1.json'),publisher_source=binding(Path(__file__)),baseline_versions=len(baseline),existing_versions_counted_as_new=0,port_counts={str(k):v for k,v in sorted(counts.items())},only_special_player_ability='shot_recoil',owner_manifests=inputs,modules=modules,video_count=sum(len(m['videos'])for m in modules),exact_version_video_coverage=sum(bool(m['videos'])for m in modules),warning='Version/layout count is not distinct action family count. Candidate technical evidence does not grant arbitrary port interchange, seam or Map assembly.',human_fun='awaiting_batch_review',production_admitted=False)
    (out/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in value.items()if k not in ['modules','owner_manifests','baseline']}));return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=REPO/'generation/workshop/plains50-v1');p.add_argument('--expected',type=int,default=50);a=p.parse_args();publish(a.out,a.expected)
