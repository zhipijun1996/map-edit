"""Complete exporter-only failure using the already frozen independent holdout.
Never rerun or select a holdout phase, alter physics cases, or replace failed bytes.
"""
import json,shutil
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.factory.core.quality import digest
from pcg.module_library.library import CandidateLibrary
HERE=Path(__file__).parent
old=ROOT/'results/workshop-creative-resource-routes-v4/round-01'
new=ROOT/'results/workshop-creative-resource-routes-sequence-export-v3'
cs=json.loads((old/'review_cases.json').read_text())['cases'];evs=json.loads((old/'evaluations.json').read_text())
lib=CandidateLibrary(new/'CandidateLibrary');records=[]
for c in cs:
 e=next(e for e in evs if digest(e['case'])==c['factory_id'])
 assert e['quality_gate']['status']=='awaiting_human_review'
 doc=new/'modules'/('generated-'+c['factory_id']+'.mapnote.json')
 artifacts=[dict(path=str(p.relative_to(ROOT.parent)),sha256=file_sha(p))for p in [old/'evaluations.json',old/'protocol.json',old/'bound-counterexamples.json',old/'counter-decisions.json']]
 records.append(lib.enroll(c,doc,e['quality_gate'],artifacts))
(new/'export-source.json').write_text(json.dumps({'schema':'pcg/export-source/v1','source_files':{str(p.relative_to(ROOT.parent)):file_sha(p)for p in [Path(__file__),HERE/'export-v3.mjs']},'original_failed_exporter':str((HERE/'export-v2.mjs').relative_to(ROOT.parent)),'physics_source_binding':str((old/'source_binding.json').relative_to(ROOT.parent)),'reason':'pure schema completion of explicit first sequence gate and second bell; original holdout unchanged'},indent=2))
(new/'summary.json').write_text(json.dumps({'technical_candidates':len(records),'recipe':'sequence-spatial-lock','original_run':str(old.relative_to(ROOT.parent)),'holdout_repeated':False,'changed_gameplay':False,'production_admitted':False,'human_fun':'unreviewed','records':records},indent=2))
print(new)
