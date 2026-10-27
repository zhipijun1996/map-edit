"""Package standard documents, evidence summaries and review-only native media."""
import argparse,copy,json,shutil,subprocess
from pathlib import Path
from .engine import ROOT,HERE
from .experiments import REPO,write
from .library import WorkshopLibrary
from .intake import propose
from ..factory.core.engine import file_sha
from pcg.module_library.library import verified_document

def deliver(out_name):
    run=ROOT/'results/workshop-macro-holdout-v2';retry=ROOT/'results/workshop-macro-retry-held-v2';out=REPO/out_name
    if (out/'audit.json').exists():raise ValueError('immutable_macro_delivery')
    out.mkdir(parents=True,exist_ok=True);shutil.copytree(run/'modules',out/'modules')
    manifest=json.loads((run/'modules/manifest.json').read_text());specs=json.loads((run/'challenge-specifications.json').read_text());summary=json.loads((run/'summary.json').read_text())
    assert summary['passed_regular']and json.loads((retry/'summary.json').read_text())['all_passed']
    modules=[];seams=[]
    for item in manifest['modules']:
        doc=verified_document(run/'modules'/item['file']);gc=doc['generationContract'];assert not item['productionAdmitted']
        modules.append(dict(**{k:v for k,v in item.items()if k!='assembly'},document_sha256=file_sha(out/'modules'/item['file']),svg_sha256=file_sha(out/'modules'/(item['id']+'.svg'))))
        if item['kind']=='macro':
            assert len(gc['ports'])==3 and len(gc['relations'])==6
            assert sum(r['status']=='path'for r in gc['relations'])==4
            seams.append(dict(contentVersion=item['contentVersion'],variant=item['variant'],connections=gc['composition']['connections'],generic_assembly='UNKNOWN'))
    # Actual disk reads through the existing library, in addition to publication's
    # initial new-object read and the separate --query-only process receipt.
    retrieval=[]
    for spec in specs:
        matches=WorkshopLibrary(run/'library').find_multi(spec);assert len(matches)==1
        retrieval.append(dict(specification=spec['id'],contentVersion=matches[0]['record']['contentVersion'],generator_calls=0,from_persisted_candidates=True))
    reviews=json.loads((run/'review_cases.json').read_text())['cases'];retry_reviews=json.loads((retry/'review_cases.json').read_text())['cases']
    order=sorted(reviews,key=lambda c:(c['route_spec']['id']!='loop',c['family']!='gate-brake-return',c['rule_parameters']['variant'],c['id']))
    write(out/'review_cases.json',dict(cases=order+retry_reviews))
    write(out/'manifest.json',dict(schema='pcg/workshop-macro-delivery/v1',modules=modules,action_families_added=0,parent_action_families=6,production_admitted=False))
    write(out/'specifications.json',specs);write(out/'internal-seams.json',seams);write(out/'retrieval.json',retrieval)
    for filename in ['summary.json','evaluations.json','bound-counterexamples.json','demand-responses.json']:
        shutil.copy2(run/filename,out/filename)
    shutil.copy2(retry/'rows.json',out/'miss-retry-results.json')
    source_files=[REPO/p for p in ['module-contract.js','module-contract-render.js','model.js','capabilities.js','difficulty.js','tools/export-module-contracts.mjs','pcg/contract/export.py','pcg/prototype/workshop/export.mjs','pcg/prototype/workshop/macro_export.mjs','pcg/prototype/workshop/macro_publish.py','pcg/prototype/workshop/macro_delivery.py']]
    hashes={}
    for p in source_files:
        q=run/'export_source'/p.relative_to(REPO);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);hashes[str(p.relative_to(REPO))]=file_sha(p)
    write(run/'export-source.json',dict(source_files=hashes,workingTreeBaseCommit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),scope='actual adapter bytes; not a claim that uncommitted implementation equals base commit'))
    shutil.copy2(run/'export-source.json',out/'export-source.json')
    failure=dict(id='macro-composition-rejection-v1',type='technical_experiment',family='gate-brake-return',flag='controls_issue',
        failures=['lower chest reachable by ordinary jump in rejected geometry: 4/6 policies','four geometry revisions did not solve return','initial controller calibration interrupted by source-freeze guard after 324 cases; incomplete, never passed','controller revision 4 passed regular but failed lower supported seam: airborne crossing instead of E landing'],
        source_runs=['workshop-macro-cheap-v2','workshop-macro-probe-v1','workshop-macro-probe-v2','workshop-macro-probe-v3','workshop-macro-probe-v4','workshop-macro-calibration-v2','workshop-macro-export-probe-v1','workshop-macro-holdout-v1'],
        next_revision='same fourth geometry; require actual E landing before supported lower seam, independent new protocol and seed',
        resolved_by=dict(protocol='pcg/prototype/workshop/protocol-macro-port-v3.json',holdout='workshop-macro-holdout-v2',retry='workshop-macro-retry-held-v2',contentVersions=[m['contentVersion']for m in modules if m['kind']=='macro']),production_admitted=False)
    write(ROOT/'feedback/workshop/macro-composition-resolution-v1.json',failure)
    unresolved=copy.deepcopy(failure);unresolved.pop('resolved_by')
    write(out/'proposal-feedback.json',dict(source_proposal='pcg/prototype/workshop/macro-proposal-v1.json',parent_video_feedback='pcg/feedback/workshop/v2-positive-video-v1.json',before=propose(dict(content_kind='macro',family='gate-brake-return'),[unresolved]),after=propose(dict(content_kind='macro',family='gate-brake-return'),[failure])))
    videos=json.loads((out/'videos/manifest.json').read_text());differences=[d for c in videos['clips']for d in c['differences']]
    audit=dict(schema='pcg/workshop-macro-audit/v1',macro_documents=2,component_documents=4,ports_per_macro=3,directed_relations_per_macro=6,declared_paths_per_macro=4,
        prescribed_quality_cases=450,purpose_valid_cases=sum(v['purpose_valid']for e in summary['entries']for v in e['stats'].values()),all_routes_pass_original_regular_policy=summary['passed_regular'],
        counter_policies=88,same_entry_counter_policies=64,different_entry_counter_policies=24,found_safe_counter_arrivals=0,necessity_proof=False,
        continuous_loop_cases=50,continuous_loop_purpose_valid=sum(v['purpose_valid']for e in summary['entries']if 'continuous-loop'in e['id']for v in e['stats'].values()),miss_retry_cases=26,miss_retry_passed=26,
        zero_connector_terrain=True,persisted_macro_retrievals=2,generator_calls_on_retrieval=0,
        native_review_clips=3,native_physics_frames=1672,all_field_exact_video_count=videos['exact_video_count'],native_differences=len(differences),native_difference_fields=sorted({d['field']for d in differences}),
        native_video_scope='actual Godot completion; strict comparator failed and remains unchanged. Review-only videos, not all-field exact proof.',
        parent_v2_user_video_observation='positive_overall',new_macro_human_video_observation='unreviewed',human_playtest=False,production_admitted=False,whole_map='UNKNOWN')
    write(out/'audit.json',audit);print(json.dumps(audit,ensure_ascii=False));return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',default='generation/workshop/macro-v1');a=p.parse_args();deliver(a.out)
