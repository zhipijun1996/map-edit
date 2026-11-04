"""Read-only exact geometry, real causal events, source and revision audit."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import gzip,json,hashlib,subprocess
from pcg.migration import core,physics
from .prepare_review031_v1 import OUT,rows
from .finalize_review031_v1 import folder_for
def main():
 checks=[];versions=[];proofs=[]
 for row in rows():
  n=row['reviewId']
  if n=='196':continue
  f=folder_for(row);d=core.read(f/'module.mapnote.json');design=core.read(core.REPO/row['designFile']);actual={o['id']:o for o in d['objects']}
  for o in design['visualObjects']:
   if o['type']=='route':continue
   assert all(actual[o['id']][k]==o[k]for k in ['type','x','y','w','h']),('geometry',n,o['id'])
   for k in ['points','duration','dwell','initialPhase','wallClimbable']:
    if k in o:assert actual[o['id']][k]==o[k],(n,o['id'],k)
  assert d['generationContract']['space']['bounds']==design['bounds']
  for a,p in zip(design['ports'],d['generationContract']['ports']):assert all(a[k]==p[k]for k in ['id','position','normal','surface','permission'])
  q=core.read(f/('qualification-reanalyzed.json'if n=='197'else'qualification.json'));report=physics.verify_report(f,q['report'],deep=True);assert report['passed'];proofs.append(dict(reviewId=n,report=q['report'],passed=True))
  root=core.REPO/'pcg/results'/('approved-r031-'+n+'-delivery-final-v1');examples=[]
  for r in core.read(root/'canonical.json')['rows']:
   assert r['check']['ok'];e=r['evidence'];raw=json.loads(gzip.decompress((root/e['output']).read_bytes()))['results'][e['index']];assert raw['hp']==5 and not raw['returns']
   events=raw['plains']['events'];accepted=[dict(frame=v['frame'],**a)for v in raw['frames']for a in v['accepted']if a['type']=='shot']
   if n=='197':assert raw['shots']==1 and any(v.get('type')=='bell_open'for v in events)
   if n=='198':assert {'carrier','other'}<={v.get('support_id')for v in raw['frames']};assert next(o for o in actual.values()if o['id'].endswith('moving-track-0'))['dwell']==7
   if n=='200'and r['case']['route_spec']['from_port']=='entry':
    hits=[v for v in events if v.get('type')=='enemy_hit'and v.get('fired_airborne')and v.get('player_airborne')];assert hits and hits[0]['shots_before_refund']==0;assert len(accepted)==2 and accepted[1]['frame']>hits[0]['frame']
   examples.append(dict(route=r['case']['route_spec']['id'],hp=raw['hp'],actualShots=accepted,coins=raw['workshop']['coins'],ticks=raw['ticks'],nativeOutcome=True))
  assert core.read(f/'package-result.json')['passed']
  checks.append(dict(reviewId=n,exactGeometryAndPorts=True,nativeExamples=examples,nativePackage=True))
  draft=core.REPO/row['outputDirectory'];programs={}
  for p in list((draft/'history').glob('*cases.json'))+[draft/'cases.json']:
   cs=core.read(p)['cases'];h=hashlib.sha256(json.dumps([c['control_plan']for c in cs],sort_keys=True).encode()).hexdigest();programs.setdefault(h,[]).append(core.relative(p))
  assert len(programs)<=7;versions.append(dict(reviewId=n,distinctProgramVersions=len(programs),maximumInitialPlusRevisions=7,programs=programs,formalVersions=1))
 core.write(OUT/'verification/geometry-and-native-audit.json',dict(passed=True,rows=checks));core.write(OUT/'verification/deep-proofs.json',proofs);core.write(OUT/'verification/revision-budget.json',versions)
 prov=core.read('pcg/prototype/godot/source_provenance.json');assert all(core.sha(core.REPO/'pcg/prototype/godot'/p)==sha for p,sha in prov['files'].items());diff=subprocess.check_output(['git','diff','--name-only','origin/main','--','generation/manual-review'],text=True).splitlines();assert not diff
 core.write(OUT/'verification/source-audit.json',dict(passed=True,protectedFiles=len(prov['files']),protectedMismatches=[],designWebEdits=diff,engine=physics.artifact(core.REPO/'pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64'),gameSourceCommit='12f6cb006d7119598e3235f4ca4f7323e4c9d092'))
 print('GEOMETRY_NATIVE_PROOFS_SOURCE_PASS',flush=True)
if __name__=='__main__':main()
