"""Real Godot isolation smoke: fresh recipe, recoil, carrier and multi-Port.

No Map code, geometry adaptation, new quality certification or library promotion.
"""
import argparse
import copy
import importlib.abc
import json
from pathlib import Path
import subprocess
import sys
from pcg.module_library.paths import REPO, DEFAULT_LIBRARY, write
from pcg.module_library.library import CandidateLibrary, verified_document
from pcg.prototype.workshop.engine import WorkshopEngine, ROOT, HERE
from pcg.prototype.workshop.rules import generate
from pcg.prototype.workshop.evaluate import purpose
from pcg.prototype.workshop.library import WorkshopLibrary
from pcg.prototype.factory.core.quality import digest, module_hash
from pcg.prototype.factory.core.engine import file_sha
from pcg.contract.export import collect


class NoRetiredMap(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if 'map_directed' in fullname or fullname == 'region_network':
            raise RuntimeError('retired Map import attempted: '+fullname)


def selected(prefix):
    matches=list((DEFAULT_LIBRARY/'candidates').glob(prefix+'*'))
    if len(matches)!=1:raise ValueError('ambiguous fixed smoke version '+prefix)
    folder=matches[0];record=json.loads((folder/'record.json').read_text())
    filename='case.json' if record['technical_status']=='passed_scoped' else 'cases.json'
    value=json.loads((folder/filename).read_text())
    return folder,record,value['cases'] if filename=='cases.json' else [value]


def run(name):
    sys.meta_path.insert(0,NoRetiredMap())
    if (ROOT/'map_directed').exists():raise ValueError('retired Map directory still exists')
    source,record,original=selected('c5825cd7')
    spec=copy.deepcopy(original[0]['map_specification']);response=generate(spec)
    if response['status']!='requires_physics':raise ValueError('independent recipe no longer works')
    fresh=copy.deepcopy(response['cases'][0]);fresh['map_specification']=spec
    fresh['factory_id']=digest(fresh);fresh['review_alias']=fresh['id']
    carrier=selected('26544bbf')[2]
    multi=selected('e90dfa35')[2]
    cases=[fresh]+original+carrier+multi
    out=ROOT/'results'/name
    engine=WorkshopEngine(out,batch_size=1,extra_sources=[Path(__file__)])
    write(out/'cases.json',dict(cases=cases));write(out/'protocol.json',dict(scope='bounded isolation smoke; not regular quality admission',
        cases=len(cases),source_versions=[record['contentVersion'],selected('26544bbf')[1]['contentVersion'],selected('e90dfa35')[1]['contentVersion']],
        fresh_generator_called=True,retired_map_absent=True,production_admitted=False))
    rows=[];fresh_witness=None
    for case,result,evidence in engine.run(cases,'independent-module'):
        check=purpose(case,result)
        rows.append(dict(id=case['id'],family=case['family'],ok=check['ok'],physics_ok=result['ok'],reason=result['reason'],
                         causal=check,shots=result.get('shots'),ticks=result.get('ticks'),evidence=evidence))
        write(out/'rows.json',rows);print(json.dumps(rows[-1],ensure_ascii=False),flush=True)
        if case['id']==fresh['id']:fresh_witness=(case,result,evidence)
    if not all(r['ok'] for r in rows):
        write(out/'summary.json',dict(ok=False,rows=rows,production_admitted=False));return out
    c,r,e=fresh_witness;review=copy.deepcopy(c);review['factory_evidence']=e
    review['module_sha256']=module_hash(review)
    write(out/'review_cases.json',dict(cases=[review]))
    exported=collect(out/'review_cases.json',out)
    exported[0]['workshopPurpose']=purpose(c,r)
    write(out/'source-bundle.json',dict(rows=exported,sourceCommit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()))
    subprocess.run(['node',str(HERE/'export.mjs'),str(out/'source-bundle.json'),str(out/'modules')],check=True,cwd=REPO)
    manifest=json.loads((out/'modules/manifest.json').read_text());new_doc=verified_document(out/'modules'/manifest['modules'][0]['file'])
    # A temporary copy of an ALREADY certified historical candidate tests
    # enrollment/retrieval; one fresh clean run is not called regular quality.
    temporary=CandidateLibrary(out/'test-library')
    enrolled=temporary.enroll(original[0],source/'module.mapnote.json',record['quality_gate'],record['evidence'])
    hits=WorkshopLibrary(out/'test-library').find_single_exact(original[0]['map_specification'])
    if [h['record']['contentVersion'] for h in hits]!=[record['contentVersion']]:raise ValueError('temporary enrollment/retrieval failed')
    summary=dict(ok=True,passed=sum(r['ok']for r in rows),total=len(rows),fresh_generated_cases=1,exported_documents=1,
                 exported_version=new_doc['generationContract']['contentVersion'],temporary_enrollment=enrolled['contentVersion'],
                 default_library_modified=False,new_quality_certifications=0,production_admitted=False,
                 scope='finite independent Module regression, not Map or human-fun acceptance',
                 retired_imports=[k for k in sys.modules if 'map_directed'in k or k=='region_network'])
    if summary['retired_imports']:raise ValueError('retired import leakage')
    write(out/'summary.json',summary);return out


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--name',required=True);a=p.parse_args();print(run(a.name))
