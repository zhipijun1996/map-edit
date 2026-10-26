"""Immutable eight-candidate revision, adding the real three-port branch."""
import argparse,json,subprocess
from pathlib import Path
from pcg.prototype.creative_batches.plains50_machinery import delivery_v1 as original
from pcg.prototype.workshop.library import WorkshopLibrary
from pcg.prototype.workshop.engine import ROOT
from pcg.prototype.factory.core.engine import file_sha
REPO=ROOT.parent;HERE=Path(__file__).parent
BRANCH_RUN='workshop-plains50-machinery-branch-production-v1'

def candidates():
    rows=original.actual_candidates();folder=ROOT/'results'/BRANCH_RUN/'carrier-safe-branch';manifest=json.loads((folder/'modules/manifest.json').read_text())
    for item in manifest['modules']:
        directory=ROOT/'map_directed/library/candidates'/item['contentVersion'].removeprefix('sha256:')
        if not(directory/'record.json').is_file():continue
        rec=json.loads((directory/'record.json').read_text());cs=json.loads((directory/'cases.json').read_text())['cases'];doc=directory/'module.mapnote.json'
        assert rec['document_sha256']==file_sha(doc) and rec['cases_sha256']==file_sha(directory/'cases.json')
        rows.append(dict(contentVersion=rec['contentVersion'],id=rec['id'],family=cs[0]['family'],title=json.loads(doc.read_text())['title'],
            case_ids=[c['id']for c in cs],document=str(doc.relative_to(REPO)),record=str((directory/'record.json').relative_to(REPO)),
            case_file=str((directory/'cases.json').relative_to(REPO)),specification=cs[0]['map_specification'],run=str(folder.relative_to(ROOT/'results')),portCount=3,
            scene='pcg/prototype/workshop/main.tscn',play_cases_json=str((folder/'review_cases.json').relative_to(REPO)),implementation_source='pcg/prototype/creative_batches/plains50_machinery/branch_v1.py',
            technical_status=rec['technical_status'],new_action_family=False,production_admitted=False))
    return rows

def query():
    rows=[];lib=WorkshopLibrary(ROOT/'map_directed/library')
    for c in candidates():
        hits=lib.find_multi(c['specification'])if c['portCount']>2 else lib.find_single_exact(c['specification']);versions=[m['record']['contentVersion']for m in hits]
        assert c['contentVersion']in versions
        rows.append(dict(specification=c['specification']['id'],requested_version=c['contentVersion'],matched_versions=versions,generator_calls=0,physics_cases=0))
    return dict(schema='pcg/plains50-machinery-disk-retrieval/v2',independent_new_process=True,rows=rows,generator_calls=0,physics_cases=0,production_admitted=False)

def deliver():
    rows=candidates();assert len(rows)==8
    out=REPO/'generation/workshop/plains50-machinery-v2';out.mkdir(parents=True,exist_ok=False)
    result=subprocess.run(['python3','-m','pcg.prototype.creative_batches.plains50_machinery.delivery_v2','--query-only'],cwd=REPO,capture_output=True,text=True,check=True)
    reuse=json.loads(result.stdout);(out/'disk-retrieval.json').write_text(json.dumps(reuse,ensure_ascii=False,indent=2)+'\n')
    previous=json.loads((REPO/'generation/workshop/plains50-machinery-v1/manifest.json').read_text());ledger=json.loads((ROOT/'results'/BRANCH_RUN/'ledger.json').read_text())
    probes=json.loads((ROOT/'results/workshop-plains50-machinery-branch-probe-v1/batches.json').read_text())
    videos=previous['videos'].copy()
    for name in ['branch-reward','branch-safe']:
        p=REPO/'generation/workshop/plains50-machinery-v1/videos'/name/'manifest.json';m=json.loads(p.read_text())
        for clip in m['clips']:
            video=p.parent/clip['file'];assert file_sha(video)==clip['sha256']
            videos.append(dict(family=clip['family'],route=name,video=str(video.relative_to(REPO)),sha256=clip['sha256'],duration=clip['duration'],frames_exact=clip['frames_exact'],manifest=str(p.relative_to(REPO)),human_fun='unreviewed'))
    manifest=dict(schema='pcg/plains50-machinery-delivery/v2',candidate_versions=8,two_port_modules=7,three_port_modules=1,four_port_modules=0,
        preexisting_relationships_adapted=4,new_action_families=0,capabilities=['move','jump','shot_recoil'],candidates=rows,
        previous_delivery=dict(path='generation/workshop/plains50-machinery-v1/manifest.json',sha256=file_sha(REPO/'generation/workshop/plains50-machinery-v1/manifest.json')),
        branch=dict(ledger=ledger,probe_physics_cases=sum(x['cases']for x in probes),declared_valid_directions=['A→B','A→C'],remaining_directions='UNKNOWN',all_ordered_relations=6,
            specification_source='parent explicit 3port carrier-safe-branch work order',reward_shared_and_initial_state_identical=True),
        actual_physics_cases=previous['actual_physics_cases']+sum(r['actual_physics_cases']for r in ledger)+sum(x['cases']for x in probes),
        videos=videos,total_strict_native_frames=sum(c['frames_exact']for c in videos),
        disk_retrieval=dict(path=str((out/'disk-retrieval.json').relative_to(REPO)),sha256=file_sha(out/'disk-retrieval.json'),matches=len(reuse['rows']),generator_calls=0,physics_cases=0),
        failures=['Wide-low refuge v1 moderate7/12 and negotiated-wide v2 mild10/12 rejected, no third revision.','Rising side exit two-source16-probe experiment failed; no candidate and no full calibration/holdout.'],
        source_files=[dict(path=str(p.relative_to(REPO)),sha256=file_sha(p))for p in sorted(HERE.rglob('*'))if p.is_file()and '__pycache__'not in p.parts],
        source_binding_note='Exact implementing files are in each immutable source_binding/source_snapshot; old exporter source.path labels retain helper ancestry and are not the sole source identity.',
        return_and_seams='UNKNOWN unless explicitly evidenced; branching does not authorize arbitrary-state assembly or all-to-all travel',human_playtest='unreviewed',production_admitted=False)
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(candidates=8,videos=len(videos),physics_cases=manifest['actual_physics_cases'],strict_frames=manifest['total_strict_native_frames'],manifest=str((out/'manifest.json').relative_to(REPO))),ensure_ascii=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--query-only',action='store_true');a=p.parse_args()
    if a.query_only:print(json.dumps(query(),ensure_ascii=False))
    else:deliver()
