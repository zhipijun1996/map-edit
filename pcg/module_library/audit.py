"""Audit relocated records without generating content or changing certification."""
import argparse
import json
import subprocess
from .paths import REPO, DEFAULT_LIBRARY, evidence_path
from .library import verified_document, verify_case_binding, withdrawn_versions
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.factory.core.quality import module_hash


def audit(records_only=False):
    rows=[];withdrawn=withdrawn_versions()
    from pcg.prototype.workshop.library import WorkshopLibrary
    for record_file in sorted((DEFAULT_LIBRARY/'candidates').glob('*/record.json')):
        folder=record_file.parent;record=json.loads(record_file.read_text());doc_file=folder/'module.mapnote.json'
        if file_sha(doc_file)!=record['document_sha256']:raise ValueError('candidate_document_drift')
        if records_only:
            checked=subprocess.run(['node',str(REPO/'pcg/module_library/validate_document.mjs'),'--validate',str(doc_file)],check=False,capture_output=True,text=True)
            if checked.returncode:raise ValueError('invalid_candidate_document')
            if not json.loads(checked.stdout)['versionMatches']:raise ValueError('stale_candidate_document')
            doc=json.loads(doc_file.read_text())
        else:doc=verified_document(doc_file)
        gc=doc['generationContract']
        if gc['contentVersion']!=record['contentVersion']or doc['id']!=record['id']or folder.name!=record['contentVersion'][7:]:raise ValueError('candidate_identity_drift')
        if record['technical_status']=='passed_scoped':
            case_file=folder/'case.json'
            if file_sha(case_file)!=record['case_sha256']:raise ValueError('candidate_case_drift')
            cases=[json.loads(case_file.read_text())];verify_case_binding(cases[0],doc)
        elif record['technical_status']=='passed_scoped_multi_route':
            case_file=folder/'cases.json'
            if file_sha(case_file)!=record['cases_sha256']:raise ValueError('candidate_cases_drift')
            cases=json.loads(case_file.read_text())['cases']
            if {c['id']:module_hash(c)for c in cases}!={r['sourceCaseId']:r['moduleSha256']for r in gc['generation']['source']['routeCases']}:raise ValueError('multi_route_case_drift')
            if not records_only:WorkshopLibrary().verify_components(doc_file,doc)
        else:raise ValueError('Map-context or unsupported record in Module candidate store')
        if not records_only:
            for artifact in record['evidence']:evidence_path(artifact['path'],artifact['sha256'])
        rows.append(dict(version=record['contentVersion'],kind=gc['kind'],withdrawn=record['contentVersion']in withdrawn,production_admitted=record['production_admitted']))
    return dict(ok=True,records=len(rows),scope='stored_bytes_and_document_contracts'if records_only else'stored_bytes_original_scoped_evidence_and_versions',
                fresh_physics_cases=0,new_certifications=0,rows=rows)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--records-only',action='store_true');a=p.parse_args()
    print(json.dumps(audit(a.records_only),ensure_ascii=False,indent=2))
