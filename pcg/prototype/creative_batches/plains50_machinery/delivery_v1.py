"""Read actual artifacts and reuse existing persistent library; never generates."""
import argparse,json,subprocess
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT
from pcg.prototype.workshop.library import WorkshopLibrary
from pcg.prototype.factory.core.engine import file_sha
REPO=ROOT.parent
HERE=Path(__file__).parent
RUNS=['workshop-plains50-machinery-production-v1','workshop-plains50-machinery-production-v2']

def actual_candidates():
    rows=[]
    for run in RUNS:
        folder=ROOT/'results'/run
        if not folder.exists():continue
        for manifest in sorted(folder.glob('round-*/modules/manifest.json')):
            for item in json.loads(manifest.read_text())['modules']:
                directory=ROOT/'map_directed/library/candidates'/item['contentVersion'].removeprefix('sha256:')
                if not(directory/'record.json').is_file():continue
                c=json.loads((directory/'case.json').read_text());rec=json.loads((directory/'record.json').read_text());doc=directory/'module.mapnote.json'
                assert rec['document_sha256']==file_sha(doc) and rec['case_sha256']==file_sha(directory/'case.json')
                rows.append(dict(contentVersion=rec['contentVersion'],id=rec['id'],family=c['family'],title=json.loads(doc.read_text())['title'],
                    case_id=c['id'],document=str(doc.relative_to(REPO)),record=str((directory/'record.json').relative_to(REPO)),
                    case_file=str((directory/'case.json').relative_to(REPO)),specification=c['map_specification'],
                    run=str(manifest.parent.parent.relative_to(ROOT/'results')),portCount=2,
                    scene='pcg/prototype/creative_batches/machinery/dock_main_v17.tscn' if c['family']=='carrier-dual-service' else 'pcg/prototype/workshop/main.tscn',
                    play_cases_json=str((manifest.parent.parent/'review_cases.json').relative_to(REPO)),
                    implementation_source=c.get('rule_source_path','UNKNOWN'),generation_rule=c.get('generation_rule',{}),
                    technical_status=rec['technical_status'],new_action_family=False,production_admitted=False))
    return rows

def query():
    found=[];library=WorkshopLibrary(ROOT/'map_directed/library')
    for row in actual_candidates():
        hits=library.find_single_exact(row['specification']);versions=[m['record']['contentVersion']for m in hits]
        assert row['contentVersion']in versions
        found.append(dict(specification=row['specification']['id'],requested_version=row['contentVersion'],versions=versions,generator_calls=0,physics_cases=0))
    return dict(schema='pcg/plains50-machinery-disk-retrieval/v1',new_process=True,rows=found,generator_calls=0,physics_cases=0,production_admitted=False)

def deliver():
    rows=actual_candidates();out=REPO/'generation/workshop/plains50-machinery-v1';out.mkdir(parents=True,exist_ok=True)
    if (out/'manifest.json').exists():raise ValueError('immutable delivery exists')
    result=subprocess.run(['python3','-m','pcg.prototype.creative_batches.plains50_machinery.delivery_v1','--query-only'],cwd=REPO,capture_output=True,text=True,check=True)
    reuse=json.loads(result.stdout);(out/'disk-retrieval.json').write_text(json.dumps(reuse,ensure_ascii=False,indent=2)+'\n')
    ledgers=[]
    for run in RUNS:
        p=ROOT/'results'/run/'ledger.json'
        if p.exists():ledgers.extend(json.loads(p.read_text()))
    probes=[]
    for name in ['workshop-plains50-machinery-probe-v1','workshop-plains50-machinery-probe-v2','workshop-plains50-machinery-rising-probe-v1','workshop-plains50-machinery-rising-probe-v2']:
        p=ROOT/'results'/name/'batches.json'
        if p.exists():probes.append(dict(run=name,physics_cases=sum(v['cases']for v in json.loads(p.read_text()))))
    videos=[]
    for p in sorted((out/'videos').glob('*/manifest.json')):
        d=json.loads(p.read_text())
        for c in d['clips']:
            media=p.parent/c['file'];assert file_sha(media)==c['sha256']
            videos.append(dict(family=c['family'],video=str(media.relative_to(REPO)),sha256=c['sha256'],duration=c['duration'],frames_exact=c['frames_exact'],manifest=str(p.relative_to(REPO)),human_fun='unreviewed'))
    manifest=dict(schema='pcg/plains50-machinery-delivery/v1',candidate_versions=len(rows),preexisting_relationships_adapted=4,new_action_families=0,
        capabilities=['move','jump','shot_recoil'],candidates=rows,ledger=ledgers,probes=probes,actual_physics_cases=sum(r['physics_cases']for r in ledgers)+sum(p['physics_cases']for p in probes),
        videos=videos,disk_retrieval=dict(path=str((out/'disk-retrieval.json').relative_to(REPO)),sha256=file_sha(out/'disk-retrieval.json'),matched=len(reuse['rows']),generator_calls=0),
        failed_requirement='evacuate-rejoin v1 wide-low island y250 moderate7/12, no holdout; negotiated wide island y245 is a separate explicit demand',
        stopped_proposals=['Rising-side exit: two source revisions/16 probes, no full calibration or holdout, no candidate.','Evacuate wide negotiated refuge: second revision mild10/12 below85%; no held test, no third revision.'],
        sources=[dict(path=str(p.relative_to(REPO)),sha256=file_sha(p))for p in sorted(HERE.glob('*'))if p.is_file()],
        return_and_seams='UNKNOWN unless separately evidenced; no Map guarantee',human_playtest='unreviewed',production_admitted=False)
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(candidates=len(rows),videos=len(videos),physics_cases=manifest['actual_physics_cases'],manifest=str((out/'manifest.json').relative_to(REPO))),ensure_ascii=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--query-only',action='store_true');a=p.parse_args()
    if a.query_only:print(json.dumps(query(),ensure_ascii=False))
    else:deliver()
