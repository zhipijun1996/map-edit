"""A recoil-only view of original CandidateLibrary, never a parallel store.

The index stores references/roles only. The original documents, cases, evidence
and scoped physics remain authoritative. Query never turns UNKNOWN into pass.
"""
import argparse,json
from pathlib import Path
from pcg.map_directed.library import CandidateLibrary,withdrawn_versions
from pcg.prototype.workshop.library import WorkshopLibrary
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.creative_batches.catalog_v1 import REPO,path,read,write_new

HERE=Path(__file__).parent

def capability_conflicts(spec,profile):
    if not isinstance(spec,dict):return [dict(field='challenge_specification',reason='JSON object required')]
    caps=spec.get('capabilities',{})
    if not isinstance(caps,dict):return [dict(field='capabilities',reason='invalid capability configuration')]
    if caps.get('status')!='defined':return [dict(field='capabilities',reason='explicit tested capability configuration required')]
    allowed=set(profile['allowed_tested_capabilities']);wanted=set(caps.get('allOf',[]))
    for group in caps.get('anyOfGroups',[]):wanted.update(group)
    if wanted-allowed:return [dict(field='capabilities',reason='outside plains special-ability boundary',unsupported=sorted(wanted-allowed),allowed=sorted(allowed))]
    return []

def disposition(version,cases,doc,profile,selected):
    tested=set().union(*(set(c.get('capabilities',[]))for c in cases))
    required=set(doc.get('capabilityRequirements',{}).get('allOf',[]))
    for group in doc.get('capabilityRequirements',{}).get('anyOfGroups',[]):required.update(group)
    unsupported=(tested|required)-set(profile['allowed_tested_capabilities'])
    if version in withdrawn_versions():return False,'technical_withdrawal','withdrawn',sorted(unsupported)
    if unsupported:return False,'reserved_for_later_abilities','later_region',sorted(unsupported)
    if not tested or any(not c.get('capabilities')for c in cases):return False,'tested_capabilities_missing','UNKNOWN',[]
    item=selected.get(version)
    if item:
        role=profile['supporting_roles'][item['id']]
        return True,'capability_compatible_candidate',role,[]
    family=cases[0]['family']
    if family=='carrier-rendezvous':return False,'pacing_held','pacing_held',[]
    if family in profile['original_recoil_rules']:return True,'original_recoil_rule_candidate','core_recoil_practice',[]
    if doc['generationContract']['kind']=='macro' and version in {r['contentVersion']for r in read(path(profile['macro_manifest']))['modules']if r.get('kind')=='macro'}:
        return True,'local_macro_candidate','continuous_return_macro',[]
    return False,'curation_required','unclassified_legacy',[]

def snapshot(profile):
    pub=read(path(profile['selected20']));selected={r['contentVersion']:r for r in pub['clips']};rows=[]
    lib=path(profile['library']);withdrawn=withdrawn_versions()
    for p in sorted((lib/'candidates').glob('*/record.json')):
        record=read(p);docpath=p.parent/'module.mapnote.json';doc=read(docpath)
        if file_sha(docpath)!=record['document_sha256']:raise ValueError('library_document_drift')
        csfile=p.parent/('case.json'if (p.parent/'case.json').exists()else'cases.json');payload=read(csfile);cases=[payload]if csfile.name=='case.json'else payload['cases']
        key='case_sha256'if csfile.name=='case.json'else'cases_sha256'
        if file_sha(csfile)!=record[key]:raise ValueError('library_case_drift')
        version=record['contentVersion'];yes,reason,role,extra=disposition(version,cases,doc,profile,selected)
        if record.get('production_admitted')or record['technical_status']not in ['passed_scoped','passed_scoped_multi_route']:yes=False;reason='outside_scoped_candidate_store'
        rows.append(dict(contentVersion=version,id=record['id'],kind=doc['generationContract']['kind'],family=cases[0]['family'],case_ids=[c['id']for c in cases],sample=selected.get(version,{}).get('id'),tested_capabilities=sorted(set().union(*(set(c['capabilities'])for c in cases))),requirements_status=doc.get('capabilityRequirements',{}).get('status','UNKNOWN'),selected_for_plains_candidates=yes,selection_reason=reason,content_role=role,additional_capabilities=extra,record=str(p.relative_to(REPO)),document=str(docpath.relative_to(REPO)),document_sha256=record['document_sha256'],technical_status=record['technical_status'],technical_scope=record['technical_scope'],assembly='UNKNOWN; blocked without new placement/state verification',video_observation='positive_overall_batch'if version in selected else 'separate historical feedback, if any',individual_human_approval='UNKNOWN',human_playtest='unreviewed',production_admitted=False))
    return dict(schema='pcg/plains-candidate-view/v1',profile=profile['id'],library=profile['library'],library_versions=len(rows),selected_candidate_versions=sum(r['selected_for_plains_candidates']for r in rows),reserved_advanced_versions=sum(r['selection_reason']=='reserved_for_later_abilities'for r in rows),production_versions=0,old_six_action_relationships=6,new20_compatible_relationships=sum(set(r['capabilities'])<=set(profile['allowed_tested_capabilities'])for r in pub['clips']),new20_reserved_for_later=9,warning='Version count is not action-family count. Compatibility alone is not recoil teaching or assembly approval.',rows=rows)

def query(spec,profile):
    conflicts=capability_conflicts(spec,profile);view=snapshot(profile);allowed={r['contentVersion']for r in view['rows']if r['selected_for_plains_candidates']}
    if not isinstance(spec,dict):spec={}
    required=['required_family','ports','space','relations','region','objective','resource_state','return_conditions']
    missing=[k for k in required if k not in spec]
    if missing:conflicts.append(dict(field='challenge_specification',reason='missing fields',fields=missing))
    if not isinstance(spec.get('ports'),dict)or not isinstance(spec.get('space'),dict):conflicts.append(dict(field='ports/space',reason='explicit port and space objects required'))
    if not conflicts:
        if type(spec['ports'].get('count'))is not int:conflicts.append(dict(field='ports.count',reason='integer required'))
    if not conflicts:
        lib=WorkshopLibrary(path(profile['library']))
        matches=lib.find_multi(spec)if spec.get('ports',{}).get('count',2)>2 else lib.find_single_exact(spec)
        matches=[m for m in matches if m['record']['contentVersion']in allowed]
        if matches:return dict(status='supported_candidate',profile=profile['id'],versions=[m['record']['contentVersion']for m in matches],records=[m['path']for m in matches],generator_called=False,new_physics_cases=0,assembly='UNKNOWN; placement/continuous verification required',production_admitted=False)
        conflicts=[dict(field='full_challenge_specification',reason='no exact currently selected candidate; geometry, resources and return cannot be inferred')]
    return dict(status='unsatisfied',profile=profile['id'],conflicts=conflicts,searched=dict(library=profile['library'],candidate_versions=len(allowed),capabilities=profile['allowed_tested_capabilities']),negotiable=['explicit supported demand','new bounded rule adaptation with original physics','new direction or return only after continuous evidence'],generator_called=False,new_physics_cases=0,production_admitted=False)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--profile',type=Path,default=HERE/'profile-v1.json');g=p.add_mutually_exclusive_group();g.add_argument('--query',type=Path);g.add_argument('--out',type=Path);a=p.parse_args();profile=read(a.profile)
    result=query(read(a.query),profile)if a.query else snapshot(profile)
    if a.out:write_new(a.out,result)
    else:print(json.dumps(result,ensure_ascii=False,indent=2))
    return 2 if result.get('status')=='unsatisfied'else 0
if __name__=='__main__':raise SystemExit(main())
