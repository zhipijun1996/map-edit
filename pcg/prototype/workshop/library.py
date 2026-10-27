"""Multi-route extension inside the existing CandidateLibrary candidate store.

Single-route callers retain their strict original behavior. They skip the new
scoped status, rather than treating a group as one interchangeable route.
"""
import copy,json,shutil,subprocess
from pcg.module_library.library import CandidateLibrary,verified_document
from pcg.module_library.matching import demand_key
from ..factory.core.engine import file_sha
from ..factory.core.quality import module_hash
from .experiments import REPO,write

class WorkshopLibrary(CandidateLibrary):
    def find_single_exact(self,spec):
        """Keep original store/verification, then honor full mechanical demand."""
        def signature(value):
            v=copy.deepcopy(value)
            for k in ['id','budget','map_seed']:v.pop(k,None)
            for rel in v.get('relations',[]):
                rel.pop('from',None);rel.pop('to',None)
            return v
        query=copy.deepcopy(spec)
        query['relations']=[dict(**r,**{'from':r['from_port'],'to':r['to_port']})for r in spec['relations']]
        return [m for m in self.find(query)if signature(m['case'].get('map_specification',{}))==signature(spec)]
    def verify_components(self,document,doc):
        gc=doc['generationContract']
        if gc['kind']!='macro':return
        dependencies=gc['generation']['source'].get('componentDocuments',[])
        if len(dependencies)!=len(gc['composition']['components']):raise ValueError('macro_component_documents_missing')
        paths=[]
        for dependency in dependencies:
            p=(REPO/dependency['path']).resolve()
            if not p.is_relative_to(REPO)or file_sha(p)!=dependency['sha256']:raise ValueError('macro_component_evidence_drift')
            paths.append(str(p))
        result=subprocess.run(['node',str(REPO/'pcg/prototype/workshop/macro_export.mjs'),'--verify',str(document),*paths],capture_output=True,text=True,cwd=REPO,check=True)
        if not json.loads(result.stdout)['versionMatches']:raise ValueError('macro_resolved_content_drift')

    def enroll_multi(self,cases,document,spec,qualities,artifacts):
        if not cases or any(q['status']!='awaiting_human_review'for q in qualities):raise ValueError('multi_route_quality_gate_not_passed')
        doc=verified_document(document);gc=doc['generationContract'];version=gc['contentVersion']
        if version in self.withdrawn or any(p['contentVersion']in self.withdrawn for p in gc['composition']['components']):raise ValueError('candidate_or_component_technically_withdrawn')
        self.verify_components(document,doc)
        declared={s['sourceCaseId']:s['moduleSha256']for s in gc['generation']['source']['routeCases']}
        if declared!={c['id']:module_hash(c)for c in cases}:raise ValueError('multi_route_case_binding_mismatch')
        for a in artifacts:
            p=(REPO/a['path']).resolve()
            if not p.is_relative_to(REPO)or file_sha(p)!=a['sha256']:raise ValueError('multi_route_evidence_drift')
        dest=self.root/'candidates'/version.removeprefix('sha256:')
        if dest.exists():raise ValueError('immutable_candidate_version_exists')
        dest.mkdir(parents=True);write(dest/'cases.json',dict(cases=cases));shutil.copy2(document,dest/'module.mapnote.json')
        record=dict(schema='map-notes/module-library-entry/v1',id=doc['id'],contentVersion=version,
            technical_status='passed_scoped_multi_route',content_kind=gc['kind'],technical_scope='whole local Macro route witnesses plus continuous excursion; no arbitrary-state or Map guarantee'if gc['kind']=='macro'else'independent single-module route witnesses; no arbitrary-state or Map guarantee',
            cases_sha256=file_sha(dest/'cases.json'),document_sha256=file_sha(dest/'module.mapnote.json'),
            demand_key=demand_key(spec),specification=spec,quality_gates=qualities,evidence=artifacts,
            human_quality='awaiting_review',human_reviews=[],production_admitted=False)
        write(dest/'record.json',record);return record

    def find_multi(self,spec):
        found=[]
        for p in sorted((self.root/'candidates').glob('*/record.json')):
            rec=json.loads(p.read_text())
            if rec.get('contentVersion')in self.withdrawn:continue
            if rec.get('technical_status')!='passed_scoped_multi_route'or rec.get('production_admitted')or rec['demand_key']!=demand_key(spec):continue
            # ecosystem's coarse key drops prose `objective`. Here objective
            # contains mechanical coordinates: verify them after coarse lookup.
            if rec['specification'].get('objective')!=spec.get('objective'):continue
            doc_path=p.parent/'module.mapnote.json';cases_path=p.parent/'cases.json'
            if file_sha(doc_path)!=rec['document_sha256']or file_sha(cases_path)!=rec['cases_sha256']:raise ValueError('multi_route_candidate_content_drift')
            doc=verified_document(doc_path);cases=json.loads(cases_path.read_text())['cases']
            if any(p['contentVersion']in self.withdrawn for p in doc['generationContract']['composition']['components']):continue
            self.verify_components(doc_path,doc)
            if doc['generationContract']['contentVersion']!=rec['contentVersion']:raise ValueError('multi_route_version_drift')
            if {r['sourceCaseId']:r['moduleSha256']for r in doc['generationContract']['generation']['source']['routeCases']}!={c['id']:module_hash(c)for c in cases}:raise ValueError('multi_route_case_binding_mismatch')
            for a in rec['evidence']:
                q=(REPO/a['path']).resolve()
                if not q.is_relative_to(REPO)or file_sha(q)!=a['sha256']:raise ValueError('multi_route_evidence_drift')
            found.append(dict(record=rec,cases=cases,path=str(p.relative_to(REPO))))
        return found

def index_multi(run):
    root=REPO/'pcg/results'/run;lib=WorkshopLibrary(root/'library')
    cases=json.loads((root/'review_cases.json').read_text())['cases'];entries=json.loads((root/'evaluations.json').read_text());manifest=json.loads((root/'modules/manifest.json').read_text());queries=[]
    for item in manifest['modules']:
        if item['portCount']<3:continue
        doc=json.loads((root/'modules'/item['file']).read_text());ids={r['sourceCaseId']for r in doc['generationContract']['generation']['source']['routeCases']}
        cs=[c for c in cases if c['id']in ids];spec=cs[0]['map_specification']
        qualities=[e['quality_gate']for e in entries if any(c['factory_id']==__import__('pcg.prototype.factory.core.quality',fromlist=['digest']).digest(e['case'])for c in cs)]
        artifacts=[dict(path=str(p.relative_to(REPO)),sha256=file_sha(p))for p in [root/'evaluations.json',root/'protocol.json',root/'bound-counterexamples.json']]
        lib.enroll_multi(cs,root/'modules'/item['file'],spec,qualities,artifacts)
        matches=WorkshopLibrary(root/'library').find_multi(spec)
        queries.append(dict(specification=spec['id'],versions=[m['record']['contentVersion']for m in matches],generator_called=False,persistent_candidates_store=True,production_admitted=False))
    write(root/'multi-route-retrieval.json',queries)
    return queries

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--run',required=True);p.add_argument('--query-only',action='store_true');a=p.parse_args()
    if a.query_only:
        root=REPO/'pcg/results'/a.run;specs=json.loads((root/'challenge-specifications.json').read_text());rows=[]
        for spec in specs:
            if spec['ports']['count']<3:continue
            rows.append(dict(specification=spec['id'],versions=[m['record']['contentVersion']for m in WorkshopLibrary(root/'library').find_multi(spec)],generator_called=False))
        write(root/'multi-route-retrieval-v2.json',rows);print(json.dumps(rows))
    else:print(json.dumps(index_multi(a.run)))
