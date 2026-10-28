"""Register explicitly published new batches on the original recoil-only view.

No capability-compatible document is auto-approved. Exact immutable library
records and case/doc hashes must match the published candidate metadata.
"""
import argparse,copy,json
from pathlib import Path
from .catalog_v1 import snapshot as original_snapshot,HERE
from pcg.prototype.creative_batches.catalog_v1 import REPO,path,read,write_new
from pcg.prototype.factory.core.engine import file_sha
from .catalog_v1 import capability_conflicts
from pcg.prototype.workshop.library import WorkshopLibrary

def snapshot(manifest_path,additional_manifests=None):
    profile=read(HERE/'profile-v1.json');view=original_snapshot(profile)
    manifest=read(manifest_path);batches=[(Path(manifest_path),manifest)]+[(Path(p),read(p))for p in (additional_manifests or [])]
    published=[r for _,batch in batches for r in batch['modules']];registered={r['contentVersion']:r for r in published}
    if len(registered)!=len(published):raise ValueError('duplicate_published_version')
    allowed=set(profile['allowed_tested_capabilities']);seen=set()
    for row in view['rows']:
        item=registered.get(row['contentVersion'])
        if not item:continue
        seen.add(row['contentVersion']);record_path=path(row['record']);doc_path=path(row['document'])
        if file_sha(record_path)!=item['record_sha256']or file_sha(doc_path)!=item['document_sha256']:raise ValueError('published_candidate_binding_drift')
        if row['selection_reason'] in ['technical_withdrawal','outside_scoped_candidate_store','tested_capabilities_missing']or row['additional_capabilities']or not set(row['tested_capabilities'])<=allowed:raise ValueError('published_candidate_not_plains_qualified')
        if not row['tested_capabilities']:raise ValueError('missing_actual_tested_configuration')
        batch_id=next(batch['id']for _,batch in batches if item in batch['modules'])
        row.update(selected_for_plains_candidates=True,selection_reason='version_bound_published_candidate_batch',content_role=item['content_role'],video_observation='unreviewed_new_version',publication_batch=batch_id,title=item['name'])
    if seen!=set(registered):raise ValueError('published_version_not_in_original_candidate_store')
    # A technical publication must not erase subsequent human design feedback.
    holds={h['contentVersion']:h for h in profile.get('model_design_holds',[])+profile.get('design_holds',[])}
    for row in view['rows']:
        hold=holds.get(row['contentVersion'])
        if hold:
            source=hold['feedback']
            if file_sha(path(source['path']))!=source['sha256']:raise ValueError('design_hold_feedback_drift')
            model_review=hold.get('source_type')=='model_design_refutation'
            row.update(selected_for_plains_candidates=False,selection_reason='pacing_held',content_role='design_rejected_technical_specimen',video_observation='ai_design_refutation'if model_review else'human_negative_boring',design_hold_reason=hold['reason'],design_feedback=source,design_feedback_type='model_design_refutation'if model_review else'human_video_observation')
    view.update(profile='plains-recoil-v2',published_batch=str(Path(manifest_path).resolve().relative_to(REPO)),published_batch_sha256=file_sha(manifest_path),selected_candidate_versions=sum(r['selected_for_plains_candidates']for r in view['rows']))
    if additional_manifests:view['published_batches']=[dict(path=str(p.resolve().relative_to(REPO)),sha256=file_sha(p))for p,_ in batches]
    return view

def query(spec,manifest_path,additional_manifests=None):
    profile=read(HERE/'profile-v1.json');view=snapshot(manifest_path,additional_manifests)
    conflicts=capability_conflicts(spec,profile)
    required=['required_family','ports','space','relations','region','objective','resource_state','return_conditions']
    if not isinstance(spec,dict):spec={}
    missing=[key for key in required if key not in spec]
    if missing:conflicts.append(dict(field='challenge_specification',reason='missing explicit constraints',fields=missing))
    if not isinstance(spec.get('ports'),dict)or not isinstance(spec.get('space'),dict):conflicts.append(dict(field='ports/space',reason='explicit port and space objects required'))
    def signature(value):
        v=copy.deepcopy(value)
        for key in ['id','budget','map_seed']:v.pop(key,None)
        return v
    matches=[];held_matches=[];allowed={r['contentVersion']for r in view['rows']if r['selected_for_plains_candidates']};holds={r['contentVersion']:r for r in view['rows']if r.get('design_feedback')}
    if not conflicts:
        if type(spec['ports'].get('count'))is not int:conflicts.append(dict(field='ports.count',reason='integer required'))
        else:
            lib=WorkshopLibrary(path(profile['library']));multi=spec['ports']['count']>2
            rows=[(hit,True)for hit in lib.find_multi(spec)]
            if not multi:rows += [(hit,False)for hit in lib.find_single_exact(spec)]
            for hit,is_grouped in rows:
                stored=hit['record']['specification']if is_grouped else hit['case']['map_specification']
                # Original coarse lookup is only a prefilter. Every complete
                # mechanical constraint is compared, including extra requests.
                if hit['record']['contentVersion']in allowed and signature(spec)==signature(stored):matches.append(hit['record']['contentVersion'])
                elif hit['record']['contentVersion']in holds and signature(spec)==signature(stored):held_matches.append(holds[hit['record']['contentVersion']])
    if matches:return dict(status='supported_candidate',versions=matches,generator_called=False,new_physics_cases=0,assembly='UNKNOWN pending actual placement and entry/seam proof',production_admitted=False)
    if not conflicts:conflicts=([dict(field='model_design_feedback'if r.get('design_feedback_type')=='model_design_refutation'else'human_design_feedback',reason='technical match held after explicit design review; redesign required',contentVersion=r['contentVersion'],feedback=r['design_feedback'])for r in held_matches]if held_matches else[dict(field='full_challenge_specification',reason='no exact published candidate; unknown or additional mechanics cannot be inferred')])
    return dict(status='unsatisfied',conflicts=conflicts,searched=dict(candidate_versions=len(allowed),library_versions=view['library_versions'],capabilities=profile['allowed_tested_capabilities']),negotiable=['explicit published interface','new bounded rule adaptation and original physical gate'],generator_called=False,new_physics_cases=0,production_admitted=False)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--manifest',type=Path,default=REPO/'generation/workshop/plains50-v1/manifest.json');p.add_argument('--additional-manifest',type=Path,action='append',default=[]);p.add_argument('--out',type=Path);p.add_argument('--query',type=Path);a=p.parse_args();value=query(read(a.query),a.manifest,a.additional_manifest)if a.query else snapshot(a.manifest,a.additional_manifest)
    if a.out:write_new(a.out,value)
    else:print(json.dumps(value,ensure_ascii=False,indent=2))
    if value.get('status')=='unsatisfied':raise SystemExit(2)
