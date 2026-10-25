"""Read-only artifact audit, original CandidateLibrary disk queries and delivery index."""
import gzip,hashlib,json,shutil
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT
from pcg.prototype.workshop.library import WorkshopLibrary
from pcg.prototype.factory.core.engine import file_sha
HERE=Path(__file__).parent;REPO=ROOT.parent
out=ROOT/'results/workshop-creative-resource-routes-delivery-v1'
if out.exists():raise ValueError('immutable delivery exists')
out.mkdir();(out/'modules').mkdir()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
selected=[('sightline-backtrack','workshop-creative-resource-routes-v6','round-00'),('trapdoor-commit','workshop-creative-resource-routes-v5','round-02'),('ordered-target-transaction','workshop-creative-resource-routes-ordered-target-v2','round-00'),('moving-ray-window','workshop-creative-resource-routes-moving-ray-v1','round-00')]
rows=[]
for family,run,round_id in selected:
 batch=ROOT/'results'/run;rd=batch/round_id
 manifest=json.loads((rd/'modules/manifest.json').read_text());assert len(manifest['modules'])==1
 e=manifest['modules'][0];doc=rd/'modules'/e['file'];svg=doc.with_name(e['id']+'.svg')
 spec=json.loads((rd/'challenge-specifications.json').read_text())[0]
 hits=WorkshopLibrary(batch/'CandidateLibrary').find_single_exact(spec)
 assert len(hits)==1 and hits[0]['record']['contentVersion']==e['contentVersion']
 for p in [doc,svg]:shutil.copy2(p,out/'modules'/p.name)
 counter=json.loads((rd/'counterexamples.json').read_text());cal=json.loads((rd/'calibration-evaluations.json').read_text())[0];held=json.loads((rd/'evaluations.json').read_text())[0]
 assert len(counter)>=18 and not any(x['invalidates_design']for x in counter)
 assert cal['quality_gate']['status']==held['quality_gate']['status']=='awaiting_human_review'
 rows.append(dict(family=family,id=e['id'],contentVersion=e['contentVersion'],document=str(doc.relative_to(REPO)),svg=str(svg.relative_to(REPO)),document_sha256=file_sha(doc),svg_sha256=file_sha(svg),run=str(rd.relative_to(REPO)),review_cases=str((rd/'review_cases.json').relative_to(REPO)),source_binding=str((rd/'source_binding.json').relative_to(REPO)),candidate_library=str((batch/'CandidateLibrary').relative_to(REPO)),disk_query_matches=len(hits),counterexamples=len(counter),same_core_safe_alternatives=sum(x['safe_stable']for x in counter),bypasses=0,calibration=cal['stats'],holdout=held['stats'],independent_holdout_runs=1,human_fun='unreviewed',production_admitted=False))
# Verify every own preserved batch, including failures, from original-byte hashes.
raw_cases=0;raw_batches=0;snapshot_files=0;run_dirs=[]
for p in sorted((ROOT/'results').glob('workshop-creative-resource-routes*')):
 if p==out:continue
 for b in sorted(p.rglob('batches.json')):
  if 'source_snapshot' in b.parts:continue
  root=b.parent;bs=json.loads(b.read_text());run_dirs.append(str(root.relative_to(REPO)))
  for receipt in bs:
   z=root/receipt['gzip_path'];assert file_sha(z)==receipt['gzip_sha256']
   raw=gzip.decompress(z.read_bytes());assert hashlib.sha256(raw).hexdigest()==receipt['raw_output_sha256'];assert len(raw)==receipt['raw_output_bytes']
   raw_cases+=receipt['cases'];raw_batches+=1
  binding=json.loads((root/'source_binding.json').read_text())
  for rel,h in binding['source_files'].items():
   assert file_sha(root/'source_snapshot'/rel)==h;snapshot_files+=1
# A paired physical shot-blocked witness, with actual dynamic position.
rd=ROOT/'results/workshop-creative-resource-routes-moving-ray-v1/round-00'
c=next(c for c in json.loads((rd/'counterexamples.json').read_text())if c['kind']=='other-ray-phase-0.14')
e=c['evidence'];r=json.loads(gzip.decompress((rd/e['output']).read_bytes()))['results'][e['index']]
impact=next(x for x in r['plains']['events']if x['type']=='projectile_impact');f=next(f for f in r['frames']if f['frame']==impact['frame']);moving=next(x for x in f['moving_platforms']if x['id']=='ray-shutter')
assert not r['ok'] and not any(x['type']=='bell_open'for x in r['plains']['events'])
x,y=moving['position'];px,py=impact['point'];assert x<=px<=x+20 and y<=py<=y+110
write(out/'moving-ray-blocked-witness.json',dict(counter=c,result_shots=r['shots'],impact=impact,actual_shutter=moving,contains_projectile_impact=True,real_bell_open=False))
# Exact same two target requests have different persistent final world state.
rd=ROOT/'results/workshop-creative-resource-routes-ordered-target-v2/round-00'
c=next(c for c in json.loads((rd/'counterexamples.json').read_text())if c['kind']=='swapped-resource-order-0')
e=c['evidence'];r=json.loads(gzip.decompress((rd/e['output']).read_bytes()))['results'][e['index']]
assert r['shots']==2 and not any(b['open']for b in r['plains']['bells'])
write(out/'ordered-swapped-witness.json',dict(counter=c,accepted_shots=r['shots'],impacts=[x for x in r['plains']['events']if x['type']=='projectile_impact'],final_bells=r['plains']['bells'],correct_order_final_open=True,wrong_order_final_open=False,legal_recovery_alternatives='same-core safe alternatives remain admitted'))
write(out/'manifest.json',dict(schema='pcg/creative-resource-routes-delivery/v1',author_task='/root/resource_routes_creator',source_type='llm_subagent_proposal',technical_candidates=4,distinct_relationship_hypotheses=4,human_fun_approved=0,production_admitted=False,modules=rows,additional_adaptations_not_counted=['sequence-spatial-lock','drop-key-late-recoil-v7'],withdrawn_versions=['sha256:56e4381d569c19e9df374984f60198a8c8a83642b55c49d1678c92738b703a25']))
write(out/'audit.json',dict(raw_cases=raw_cases,raw_batches=raw_batches,source_snapshot_files=snapshot_files,preserved_runs=run_dirs,original_raw_sha256_verified=True,frozen_source_bytes_verified=True,disk_queries=4,disk_matches=4,source_file=str(Path(__file__).relative_to(REPO)),source_sha256=file_sha(__file__)))
print(json.dumps(dict(out=str(out.relative_to(REPO)),modules=4,raw_cases=raw_cases,raw_batches=raw_batches,source_snapshot_files=snapshot_files)))
