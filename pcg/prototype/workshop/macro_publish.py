"""Strict candidate export and disk reuse on the existing CandidateLibrary."""
import argparse,copy,json,subprocess
from pathlib import Path
from .engine import ROOT,HERE
from .macro import purpose
from .macro_interface import specifications,generate
from .experiments import write,REPO
from .evidence import counter_records,geometry_key
from .library import WorkshopLibrary
from ..factory.core.engine import file_sha
from pcg.contract.export import collect

def publish(run_name,calibration,counters):
    out=ROOT/'results'/run_name
    if (out/'modules').exists():raise ValueError('immutable_macro_publication')
    summary=json.loads((out/'summary.json').read_text());cal=ROOT/'results'/calibration
    if summary['stage']!='holdout'or not summary['passed_regular']:raise ValueError('macro_holdout_regular_gate_not_passed')
    if not json.loads((cal/'summary.json').read_text())['passed_regular']:raise ValueError('macro_calibration_regular_gate_not_passed')
    cs=json.loads((out/'review_cases.json').read_text())['cases'];all_rows=collect(out/'review_cases.json',out)
    entries=json.loads((out/'evaluations.json').read_text());stats={e['id']:e for e in entries}
    counter_rows=counter_records(counters);counter_inputs=json.loads((ROOT/'results'/counters/'cases.json').read_text())['cases'];counter_scopes={c['id']:c['counterexample_scope']for c in counter_inputs}
    for r in counter_rows:r['scope']=counter_scopes[r['id']]
    if any(r['safe_stable']and r['scope']=='same_entry_cheaper'for r in counter_rows):raise ValueError('macro_counterexample_requires_rework')
    bindings=[]
    for c in cs:
        if c['family']!='gate-brake-return'or c['route_spec']['id']not in ('cache','descent'):continue
        bound=[r for r in counter_rows if r['base_id']==c['review_alias']and r['geometry_sha256']==geometry_key(c)]
        expected=25 if c['route_spec']['id']=='cache'else 7
        if len(bound)!=expected:raise ValueError('macro_exact_counter_geometry_coverage_missing')
        bindings.append(dict(caseId=c['id'],moduleSha256=c['module_sha256'],counterexamples=bound))
    write(out/'bound-counterexamples.json',dict(schema='pcg/workshop-macro-counter-bindings/v1',routes=bindings,all_counter_policies=counter_rows,necessity_proof=False))
    artifacts=[dict(path=str(p.relative_to(REPO)),sha256=file_sha(p))for p in [out/'evaluations.json',out/'rows.json',out/'protocol.json',out/'bound-counterexamples.json',cal/'summary.json']]
    for row in all_rows:
        p=purpose(row['case'],row['result'])
        if not p['ok']:raise ValueError('canonical_macro_witness_failed_purpose')
        row['macroPurpose']=row['workshopPurpose']=row['routePurpose']=p
        row['statistics']=stats[row['case']['review_alias']]['stats']
        row['trialRows']=[r for r in json.loads((out/'rows.json').read_text())if r['base_id']==row['case']['review_alias']]
        row['artifacts']+=artifacts
    rows=[r for r in all_rows if r['case']['route_spec']['id']!='loop'];continuous=[r for r in all_rows if r['case']['route_spec']['id']=='loop']
    specs=specifications();write(out/'challenge-specifications.json',specs)
    # Exercise the public demand entry. The selected programs must be identical
    # to those actually run, not substituted with unvalidated lookalike layouts.
    responses=[]
    for s in specs:
        response=generate(s);assert response['status']=='requires_physics'
        for base in response['cases']:
            witness=next(r['case']for r in rows if r['case']['review_alias']==base['id'])
            for key in ('platforms','latches','reward_sites','ports','control_plan','goal','spawn'):
                if base[key]!=witness[key]:raise ValueError('demand_program_does_not_match_executed_witness')
        responses.append(dict(specification=s['id'],status=response['status'],geometry_candidates=1,programs=len(response['cases']),independent_macro_validation=True,source_type=s['source_type'],b_director_approval='UNKNOWN'))
    write(out/'demand-responses.json',responses)
    bundle=dict(rows=rows,continuousRows=continuous,specifications=specs,sourceCommit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip())
    write(out/'source-bundle.json',bundle)
    subprocess.run(['node',str(HERE/'export.mjs'),str(out/'source-bundle.json'),str(out/'raw-modules')],cwd=REPO,check=True)
    subprocess.run(['node',str(HERE/'macro_export.mjs'),str((out/'source-bundle.json').relative_to(REPO)),str((out/'raw-modules').relative_to(REPO)),str((out/'modules').relative_to(REPO))],cwd=REPO,check=True)
    manifest=json.loads((out/'modules/manifest.json').read_text());library=WorkshopLibrary(out/'library');receipts=[]
    for s in specs:
        item=next(m for m in manifest['modules']if m['kind']=='macro'and m['variant']==s['objective']['interface'])
        doc_path=out/'modules'/item['file'];doc=json.loads(doc_path.read_text())
        ids={r['sourceCaseId']for r in doc['generationContract']['generation']['source']['routeCases']}
        cases=[c for c in cs if c['id']in ids];qualities=[stats[c['review_alias']]['quality_gate']for c in cases]
        deps=doc['generationContract']['generation']['source']['componentDocuments']
        proofs=artifacts+[dict(path=a['path'],sha256=a['sha256'])for a in deps]
        record=library.enroll_multi(cases,doc_path,s,qualities,proofs)
        matches=WorkshopLibrary(out/'library').find_multi(s)
        assert len(matches)==1 and matches[0]['record']['contentVersion']==record['contentVersion']
        receipts.append(dict(specification=s['id'],contentVersion=record['contentVersion'],storage='existing CandidateLibrary/candidates on disk',new_library_object=True,generator_calls_on_retrieval=0,production_admitted=False))
    write(out/'retrieval.json',receipts)
    print(json.dumps(dict(macros=2,components=4,persisted_retrievals=len(receipts),out=str(out))))
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run',required=True);p.add_argument('--calibration',required=True);p.add_argument('--counters',required=True);a=p.parse_args();publish(a.run,a.calibration,a.counters)
