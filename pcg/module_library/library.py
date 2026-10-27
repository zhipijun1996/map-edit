"""Versioned candidate records. No automatic promotion into production."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
from .paths import REPO, DEFAULT_LIBRARY, evidence_path
from .matching import fits
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.factory.core.quality import POLICY, digest,module_hash

def withdrawn_versions():
    versions=set()
    for path in sorted((REPO/'pcg/feedback/content-withdrawals').glob('*.json')):
        notice=json.loads(path.read_text())
        if notice.get('schema')!='pcg/content-technical-withdrawal/v1':raise ValueError('unknown_content_withdrawal_schema')
        versions.update(notice['contentVersions'])
    return versions


def verified_document(path):
    result=subprocess.run(['node',str(REPO/'pcg/module_library/validate_document.mjs'),'--validate',str(path)],
        capture_output=True,text=True,check=True,cwd=REPO)
    if not json.loads(result.stdout)['versionMatches']:raise ValueError('stale_candidate_document')
    doc=json.loads(Path(path).read_text());proofs=[v for v in doc['generationContract']['validations']if v['kind']=='physics'and v['result']=='pass']
    if not proofs:raise ValueError('candidate_has_no_physics_witness')
    for proof in proofs:
        for artifact in proof['artifacts']:
            p=evidence_path(artifact['path'],artifact['sha256'])
            if not p.is_relative_to(REPO)or file_sha(p)!=artifact['sha256']:raise ValueError('candidate_physics_evidence_drift')
    return doc


def verify_case_binding(case,doc):
    source=doc['generationContract']['generation']['source']
    if module_hash(case)!=case.get('module_sha256') or module_hash(case)!=source.get('moduleSha256'):
        raise ValueError('candidate_case_does_not_match_canonical_physics_source')
    if source.get('sourceCaseId')!=case.get('id') or doc['id']!='generated-'+case.get('factory_id',''):
        raise ValueError('candidate_case_identity_does_not_match_document')


class CandidateLibrary:
    def __init__(self,root=None):
        self.root=Path(root or DEFAULT_LIBRARY).resolve()
        if not self.root.is_relative_to(REPO):raise ValueError('candidate_library_must_stay_in_workspace_repository')
        if 'map_directed' in self.root.relative_to(REPO).parts or self.root.is_relative_to(REPO/'archive'):
            raise ValueError('retired_map_store_is_not_a_module_library')
        # Technical counterexamples can revoke reuse without rewriting immutable
        # old records or pretending that a new human review took place.
        self.withdrawn=withdrawn_versions()

    def find(self,spec):
        found=[]
        for p in sorted((self.root/'candidates').glob('*/record.json')):
            record=json.loads(p.read_text())
            if record.get('contentVersion')in self.withdrawn:continue
            if record['technical_status']!='passed_scoped' or record['production_admitted']:continue
            case_path=p.parent/'case.json';doc_path=p.parent/'module.mapnote.json'
            if file_sha(case_path)!=record['case_sha256'] or file_sha(doc_path)!=record['document_sha256']:
                raise ValueError('candidate_library_content_drift:'+str(p))
            document=verified_document(doc_path)
            if record['id']!=document['id']or record['contentVersion']!=document['generationContract']['contentVersion']:
                raise ValueError('candidate_record_version_drift')
            for artifact in record['evidence']:
                proof=evidence_path(artifact['path'],artifact['sha256'])
                if not proof.is_relative_to(REPO)or file_sha(proof)!=artifact['sha256']:raise ValueError('candidate_enrollment_evidence_drift')
            case=json.loads(case_path.read_text())
            verify_case_binding(case,document)
            if fits(case,spec):
                # This first adapter only exports the canonical two-port ascent.
                doc=json.loads(doc_path.read_text());gc=doc['generationContract'];ports=gc['ports']
                if [p['normal']for p in ports]!=spec['ports']['required_normals']:continue
                if any(not any(r['from']==q['from']and r['to']==q['to']for r in gc['routes'])for q in spec['relations']):continue
                found.append(dict(record=record,case=case,path=str(p.relative_to(REPO))))
        return found

    def enroll(self,case,doc,quality,artifacts):
        if quality.get('status')!='awaiting_human_review':raise ValueError('technical_quality_gate_not_passed')
        document=verified_document(doc);version=document['generationContract']['contentVersion']
        if version in self.withdrawn:raise ValueError('candidate_version_technically_withdrawn')
        verify_case_binding(case,document)
        for artifact in artifacts:
            p=evidence_path(artifact['path'],artifact['sha256'])
            if not p.is_relative_to(REPO)or file_sha(p)!=artifact['sha256']:raise ValueError('invalid_candidate_enrollment_evidence')
        destination=self.root/'candidates'/version.removeprefix('sha256:')
        if destination.exists():raise ValueError('immutable_candidate_version_exists')
        destination.mkdir(parents=True)
        (destination/'case.json').write_text(json.dumps(case,ensure_ascii=False,separators=(',',':')))
        shutil.copy2(doc,destination/'module.mapnote.json')
        record=dict(schema='map-notes/module-library-entry/v1',id=document['id'],contentVersion=version,
            document_sha256=file_sha(destination/'module.mapnote.json'),case_sha256=file_sha(destination/'case.json'),
            technical_status='passed_scoped',technical_scope='finite single-module policies and perturbations; general assembly stays blocked',
            quality_gate=quality,human_quality='awaiting_review',human_reviews=[],production_admitted=False,
            map_reuse_policy='isolated instance validation required on every new placement; canonical assemblyInterface is not bypassed for production',
            evidence=artifacts)
        (destination/'record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
        return record

    @staticmethod
    def promotion_reasons(record,interface_eligible=False):
        # Existing factory policy remains authoritative; no AI-authored approval
        # can substitute for actual external human review evidence.
        reasons=[]
        if record.get('contentVersion')in withdrawn_versions():reasons.append('technical_counterexample_withdrawal')
        if record.get('technical_status')!='passed_scoped':reasons.append('technical_validation_missing')
        reviewers={r.get('reviewer') for r in record.get('human_reviews',[]) if r.get('type')=='human_quality_review' and r.get('approved') and r.get('artifact_sha256')}
        if len(reviewers)<POLICY['minimum_human_reviewers']:reasons.append('human_quality_review_missing')
        if not interface_eligible:reasons.append('canonical_assembly_interface_not_admitted')
        return reasons
