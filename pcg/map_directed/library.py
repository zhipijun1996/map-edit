"""Versioned candidate records. No automatic promotion into production."""
import copy
import gzip
import json
from pathlib import Path
import shutil
import subprocess
from .director import REPO
from .composition import rect_bounds
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.factory.core.quality import POLICY, digest,module_hash

def withdrawn_versions():
    versions=set()
    for path in sorted((REPO/'pcg/feedback/content-withdrawals').glob('*.json')):
        notice=json.loads(path.read_text())
        if notice.get('schema')!='pcg/content-technical-withdrawal/v1':raise ValueError('unknown_content_withdrawal_schema')
        versions.update(notice['contentVersions'])
    return versions


def fits(case,spec):
    bounds=rect_bounds(case)
    return (case['family']==spec['required_family'] and (len(case['ports']) if case.get('ports') else 2)==spec['ports']['count']
        and abs(case['entry_port'][1]-case['exit_port'][1]-spec.get('rise',case['entry_port'][1]-case['exit_port'][1]))<1e-6
        and bounds[2]<=spec['space']['max_width'] and bounds[3]<=spec['space']['max_height']
        and abs(case['exit_port'][0]-case['entry_port'][0])<=spec['space']['max_port_span_x']
        and case['entry_port'][1]==spec.get('entry_y',case['entry_port'][1])
        and set(case['capabilities'])<=set(spec['capabilities']['allOf']))


def verified_document(path):
    result=subprocess.run(['node',str(REPO/'pcg/map_directed/library_bridge.mjs'),'--validate',str(path)],
        capture_output=True,text=True,check=True,cwd=REPO)
    if not json.loads(result.stdout)['versionMatches']:raise ValueError('stale_candidate_document')
    doc=json.loads(Path(path).read_text());proofs=[v for v in doc['generationContract']['validations']if v['kind']=='physics'and v['result']=='pass']
    if not proofs:raise ValueError('candidate_has_no_physics_witness')
    for proof in proofs:
        for artifact in proof['artifacts']:
            p=(REPO/artifact['path']).resolve()
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
        self.root=Path(root or REPO/'pcg/map_directed/library').resolve()
        if not self.root.is_relative_to(REPO):raise ValueError('candidate_library_must_stay_in_workspace_repository')
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
                proof=(REPO/artifact['path']).resolve()
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
            p=(REPO/artifact['path']).resolve()
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

    def enroll_direct_instance(self,run):
        """Index a quarantined whole-map candidate, never a generic Module pass.

        This extends the existing candidate library. Canonical UNKNOWN routes
        stay UNKNOWN; reusing the exact demand still requires a fresh Map test.
        """
        run=Path(run).resolve()
        summary=json.loads((run/'summary.json').read_text())
        if not summary['rows'] or not summary['all_passed']:
            raise ValueError('complete_direct_instance_validation_required')
        from .direct_join.audit import audit
        from .direct_join.canonical import reload_catalog
        compiled=json.loads((run/'compiled.json').read_text());receipt=audit(compiled)
        catalog=run/'module-library';loaded=reload_catalog(catalog)
        if [m['content_version']for m in loaded]!=[m['content_version']for m in compiled['modules']]:
            raise ValueError('validated_instance_does_not_match_module_catalog')
        cases={v['id']:v for v in json.loads((run/'cases.json').read_text())['cases']}
        observed=set();seen=set()
        artifacts=[run/'summary.json',run/'cases.json',run/'compiled.json',run/'map-recipe.json',run/'physics/source_binding.json',run/'physics/batches.json',catalog/'source.json',catalog/'documents/manifest.json']
        for batch in json.loads((run/'physics/batches.json').read_text()):
            trace=run/'physics'/batch['gzip_path']
            if file_sha(trace)!=batch['gzip_sha256']:raise ValueError('whole_map_trace_drift')
            for result in json.loads(gzip.decompress(trace.read_bytes()))['results']:
                if not result['ok'] or result['id']not in cases:raise ValueError('actual_map_trace_not_passed')
                seen.add(result['id']);legs={v['id']:v for v in cases[result['id']]['pilot_program']}
                for witness in result['pilot']['legs']:
                    leg=legs[witness['id']]
                    if witness.get('ok')and leg.get('edge_terminal'):observed.add((leg['edge_id'],leg['edge_from'],leg['edge_to']))
            artifacts.append(trace)
        graph=compiled['exploration_graph']
        expected={(e['id'],e['from'],e['to'])for e in graph['edges']}|{(e['id'],e['to'],e['from'])for e in graph['edges']if e['bidirectional']}
        if seen!=set(cases)or not expected<=observed:raise ValueError('actual_map_directed_edge_coverage_incomplete')
        identity=digest({'modules':[m['content_version']for m in loaded],'geometry':receipt['geometry_sha256']})
        target=self.root/'map-instances'/identity/'record.json'
        if target.exists():raise ValueError('immutable_direct_instance_record_exists')
        record=dict(schema='map-notes/isolated-map-candidate/v1',technical_status='whole_map_instance_passed',
            catalog=str(catalog.relative_to(REPO)),map_geometry_sha256=receipt['geometry_sha256'],
            modules=[m['canonical_document']for m in loaded],
            evidence=[dict(path=str(p.relative_to(REPO)),sha256=file_sha(p))for p in artifacts],
            reuse_scope='exact demands only; independent general Module relations remain UNKNOWN; every assembled map is tested anew',
            human_quality='awaiting_review',human_reviews=[],production_admitted=False)
        target.parent.mkdir(parents=True);target.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
        return record

    def find_direct_instance(self,specs):
        from .direct_join.canonical import reload_catalog
        for path in sorted((self.root/'map-instances').glob('*/record.json')):
            record=json.loads(path.read_text())
            if record['technical_status']!='whole_map_instance_passed' or record['production_admitted']:continue
            if any(m.get('contentVersion')in self.withdrawn for m in record.get('modules',[])):continue
            catalog=(REPO/record['catalog']).resolve()
            if not catalog.is_relative_to(REPO):raise ValueError('catalog_outside_repository')
            manifest=json.loads((catalog/'documents/manifest.json').read_text())
            if {m['nodeId']for m in manifest['modules']}!={s['node_id']for s in specs}:continue
            for artifact in record['evidence']:
                proof=(REPO/artifact['path']).resolve()
                if not proof.is_relative_to(REPO)or file_sha(proof)!=artifact['sha256']:raise ValueError('direct_instance_evidence_drift')
            catalog=(REPO/record['catalog']).resolve()
            if not catalog.is_relative_to(REPO):raise ValueError('catalog_outside_repository')
            modules=reload_catalog(catalog)
            by={m['id']:m for m in modules}
            if set(by)=={s['node_id']for s in specs}and all(by[s['node_id']]['spec']==s for s in specs):
                return dict(modules=modules,record=str(path.relative_to(REPO)),scope=record['reuse_scope'])
        return None

    def find_payload(self,spec,*,isolated_experiment=False):
        """Per-Module retrieval from scoped Map witnesses, never UNKNOWN admission.

        Current geometry/port/state constraints match exactly; prose/seed IDs
        need not. Translation/adaptation is a new version requiring new physics.
        A production caller cannot opt into these experimental payloads.
        """
        if not isolated_experiment:return []
        from .ecosystem.ideas import demand_key
        from .direct_join.canonical import reload_catalog
        from pcg.prototype.factory.core.engine import ENGINE,PROJECT
        found=[];key=demand_key(spec)
        for path in sorted((self.root/'payloads'/key).glob('*/record.json')):
            record=json.loads(path.read_text())
            if record.get('contentVersion')in self.withdrawn:continue
            if record.get('status')!='validated_in_concrete_map' or record.get('production_admitted'):continue
            for artifact in record['evidence']:
                p=(REPO/artifact['path']).resolve()
                if not p.is_relative_to(REPO)or file_sha(p)!=artifact['sha256']:raise ValueError('payload_evidence_drift')
            binding=json.loads((REPO/record['physics_binding']).read_text())
            if binding['engine_sha256']!=file_sha(ENGINE)or binding['source_index_sha256']!=file_sha(PROJECT/'source_provenance.json'):
                raise ValueError('payload_physics_baseline_changed')
            # Validate every frozen source, including the actual producer. A
            # matching document alone cannot keep a stale experiment alive.
            if any(file_sha(REPO/'pcg'/rel)!=sha for rel,sha in binding['source_files'].items()):
                raise ValueError('payload_runtime_or_producer_changed')
            modules=reload_catalog(REPO/record['catalog'])
            module=next(m for m in modules if m['id']==record['node_id'])
            if demand_key(module['spec'])!=key or module['content_version']!=record['contentVersion']:
                raise ValueError('payload_demand_or_version_drift')
            module['spec']=copy.deepcopy(spec)
            found.append(dict(module=module,record=str(path.relative_to(REPO)),
                scope='isolated concrete-instance reuse only; fresh whole-map physics mandatory'))
        return found

    def enroll_payloads(self,run):
        """Extend this library with individually searchable whole-Map payloads.

        Existing enrollment verifies gzip bytes, every route and all directed
        graph edges. This index never upgrades the canonical UNKNOWN relations.
        """
        from .ecosystem.ideas import demand_key
        run=Path(run).resolve()
        parent=self.enroll_direct_instance(run)
        compiled=json.loads((run/'compiled.json').read_text());records=[]
        for module in compiled['modules']:
            key=demand_key(module['spec']);version=module['content_version']
            destination=self.root/'payloads'/key/version.removeprefix('sha256:')/'record.json'
            record=dict(schema='map-notes/scoped-module-payload/v1',node_id=module['id'],
                demand_key=key,contentVersion=version,status='validated_in_concrete_map',
                design_contract=module['spec']['design_contract'],catalog=parent['catalog'],
                physics_binding=str((run/'physics/source_binding.json').relative_to(REPO)),
                evidence=parent['evidence'],human_quality='awaiting_review',human_reviews=[],
                production_admitted=False,general_relations='UNKNOWN',
                scope='Same hard demand in isolated experiment; every new assembly requires full physical validation')
            if not destination.exists():
                destination.parent.mkdir(parents=True)
                destination.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
            elif json.loads(destination.read_text())['demand_key']!=key:raise ValueError('immutable_payload_collision')
            records.append(str(destination.relative_to(REPO)))
        return records
