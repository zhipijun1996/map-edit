import json
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT
from pcg.prototype.workshop.library import WorkshopLibrary
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.workshop.production_loop import run
from pcg.prototype.creative_batches.grapple import recipes_v1,recipes_v5,recipes_v7,recipes_v8
REPO=ROOT.parent
LIB=ROOT/'results/workshop-creative-grapple-library-final-v1'
SELECTED=[('anchor-gap',1,0,recipes_v1),('bounce-brake',5,1,recipes_v5),('jump-refill',7,0,recipes_v7),('hazard-window',7,2,recipes_v7),('hang-recast',8,0,recipes_v8)]
DISPATCH={recipe:module for recipe,_,_,module in SELECTED}
def compiler(req):return DISPATCH[req['recipe']].compiler(req)
def purpose(c,r):return DISPATCH[c['production_recipe']].purpose(c,r)
def alts(c):return DISPATCH[c['production_recipe']].alternatives(c)
def do_reuse(name,recipes):
 run(name,requests=[dict(recipe=r)for r in recipes],cycles=len(recipes),library_root=LIB,compiler=compiler,checker=purpose,counter_builder=alts,source_file=Path(__file__),extra_sources=[Path(m.__file__)for m in DISPATCH.values()]+[recipes_v8.RUNNER],runner_script=recipes_v8.RUNNER.resolve())
if __name__=='__main__':
 out=ROOT/'results/workshop-creative-grapple-delivery-v1';out.mkdir();rows=[]
 for recipe,version,index,module in SELECTED:
  origin=ROOT/f'results/workshop-creative-grapple-production-v{version}/round-{index:02d}'
  raw=json.loads((origin/'review_cases.json').read_text())['cases'][0];manifest=json.loads((origin/'modules/manifest.json').read_text())['modules'][0];doc=origin/'modules'/manifest['file'];record_path=ROOT/f'results/workshop-creative-grapple-library-v{version}/candidates'/manifest['contentVersion'].removeprefix('sha256:')/'record.json';record=json.loads(record_path.read_text());stats=json.loads((origin/'evaluations.json').read_text())[0]
  bundle=json.loads((origin/'source-bundle.json').read_text());actual=bundle['rows'][0]['result']['capability_snapshot']['declared'];assert sorted(actual)==sorted(raw['capabilities']),[recipe,actual,raw['capabilities']]
  stored=WorkshopLibrary(LIB).enroll(raw,doc,record['quality_gate'],record['evidence'])
  matches=WorkshopLibrary(LIB).find_single_exact(raw['map_specification']);assert len(matches)==1
  rows.append(dict(recipe=recipe,source_task='/root/grapple_creator',contentVersion=manifest['contentVersion'],json=str(doc.relative_to(REPO)),svg=str(doc.with_name(doc.name.replace('.mapnote.json','.svg')).relative_to(REPO)),json_sha256=file_sha(doc),source=str(Path(module.__file__).relative_to(REPO)),source_sha256=file_sha(module.__file__),source_binding=str((origin/'source_binding.json').relative_to(REPO)),calibration=json.loads((origin/'calibration-evaluations.json').read_text())[0]['stats'],holdout=stats['stats'],counterexamples=len(json.loads((origin/'counterexamples.json').read_text())),disk_retrieval_matches=len(matches),return_status='UNKNOWN',human_fun='unreviewed',human_playtest='unreviewed',production_admitted=False))
 report=dict(schema='pcg/creative-grapple-delivery/v1',technical_candidates=len(rows),human_confirmed_action_families=0,relation_hypotheses=['active anchored departure','forced automatic departure plus trajectory repair','spent extra-jump contact replenishment','autonomous periodic hazard synchronization','held target reselection and returning trajectory; novelty review pending'],modules=rows,withdrawn_or_superseded=[dict(version='sha256:15190bab6de1b6f180bd4cd8b376e5d096fee184da71c82951640e1cee9d7b61',reason='additional long-press single jump then hook bypasses spent-before-contact jump hypothesis',audit='pcg/results/workshop-creative-grapple-jump-audit-v1/summary.json'),dict(version='sha256:a9337f777bf0781b96193f079104e79f04f1863083faafe5b2933c6c4cf932c1',reason='mandatory observation from hang invalidated by legitimate ground synchronization; semantic replacement hazard-window accepts same-core entry synchronization',audit='pcg/results/workshop-creative-grapple-hang-audit-v1/summary.json')],additional_recast_counter_audit='pcg/results/workshop-creative-grapple-recast-audit-v1/summary.json',library=str(LIB.relative_to(REPO)),limitations=['finite actual Godot policies, not necessity proof','UNKNOWN placement, reverse traversal, and full action envelopes remain blocked','display source.path inherited from shared canonical exporter; exact author source is listed here and source_binding snapshot hashes are authoritative','no human fun/play/production approval'])
 (out/'summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 do_reuse('workshop-creative-grapple-reuse-v1',[r[0]for r in SELECTED[:4]])
 do_reuse('workshop-creative-grapple-reuse-v2',[SELECTED[4][0]])
 print(json.dumps(dict(out=str(out),technical_candidates=len(rows)),ensure_ascii=False))
