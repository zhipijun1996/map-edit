"""Exact approved geometry, bounded controls, formal proofs and native samples."""
import gzip,json,hashlib,subprocess
from pcg.migration import core,physics
from .refresh_review045_v1 import OUT,rows
from .finalize_review045_v1 import folder_for
QUALIFIED={'41','57','61','62','115','169','223','225','55'}
def main():
 checks=[];versions=[];proofs=[]
 for row in rows():
  n=row['reviewId'];f=folder_for(row);doc=core.read(f/'module.mapnote.json');design=core.read(core.REPO/row['designFile']);actual={o['id']:o for o in doc['objects']};glyphs=[]
  for o in design['visualObjects']:
   if o['type']=='route':continue
   a=actual[o['id']]
   if o['type']=='enemy':
    assert a['type']=='enemy'and a['x']+a['w']/2==o['x']+o['w']/2
    assert (a['y']+a['h']/2==o['y']+o['h']/2 if a['definition']=='plains_diver'else a['y']+a['h']==o['y']+o['h'])
    assert [a['w'],a['h']]==[28,32];glyphs.append(dict(objectId=o['id'],diagram=[o[k]for k in ['x','y','w','h']],native=[a[k]for k in ['x','y','w','h']],anchor='air center / ground foot center'))
   else:assert all(a[k]==o[k]for k in ['type','x','y','w','h']),(n,o['id'])
   for k in ['points','duration','dwell','initialPhase','wallClimbable']:
    if k in o:assert a[k]==o[k],(n,o['id'],k)
  assert doc['generationContract']['space']['bounds']==design['bounds']
  for a,p in zip(design['ports'],doc['generationContract']['ports']):
   assert all(a[k]==p[k]for k in ['id','position','normal','surface'])
   assert {'IN':'INPUT','OUT':'OUTPUT'}.get(a['permission'],a['permission'])==p['permission']
  core.verify_artifacts(list(core.read(f/'frozen.json').values()))
  if n in QUALIFIED:
   q=core.read(f/('qualification-repaired.json'if n=='62'else'qualification.json'));r=physics.verify_report(f,q['report'],deep=True);assert r['passed'];proofs.append(dict(reviewId=n,report=q['report'],passed=True,originalAttempts=r['actualAttempts']))
  elif n=='42':assert not core.read(f/'qualification.json')['passed']
  else:assert not(f/'qualification.json').exists(),'unqualified_must_not_have_selected_formal_run'
  package=f/'playable';result=f/'package-result.json';p=core.read(result);assert p['passed']==(n not in {'51','52'})
  examples=[];root=core.REPO/'pcg/results'/('approved-r045-'+n+('-delivery-final-v1'if n in QUALIFIED|{'42'}else'-partial-delivery-v1'))
  for entry in core.read(root/'canonical.json')['rows']:
   if not entry['check']['ok']:continue
   e=entry['evidence'];r=json.loads(gzip.decompress((root/e['output']).read_bytes()))['results'][e['index']];assert r['hp']==5 and not r['returns'];example=dict(route=entry['case']['route_spec']['id'],hp=r['hp'],ticks=r['ticks'],shots=r['shots'],coins=r['workshop']['coins'])
   if n=='206':
    release=r['review040_release'];assert release['released']and release['claim_frame']<=release['release_frame']and release['support_collision_layer']==0;assert r['workshop']['coins']==14 and r['air_exit_complete_frames']>=6;example.update(release=release,completeAIRFrames=r['air_exit_complete_frames'])
    before=[v['review040_release']for v in r['frames']if v['frame']<release['claim_frame']];assert before and all(not v['released']and v['support_collision_layer']==1 for v in before)
   if n=='115':
    carry=[v for frame in r['frames']for v in frame.get('refresh_consumers',[])if v.get('carried_frames',0)>0];assert carry;example['actualNativeCarry']=carry[-1]
   examples.append(example)
  checks.append(dict(reviewId=n,exactBoundsAndPorts=True,exactStaticGeometry=True,nativeGlyphDecoding=glyphs,qualified=n in QUALIFIED,nativeExamples=examples,package=physics.artifact(package/'godot-package.json'),nativePackageCases=p['canonical_cases']))
  draft=core.REPO/row['outputDirectory'];programs={}
  for path in [*draft.glob('history/*cases.json'),draft/'cases.json']:
   if path.name=='imported-review040-cases.json':continue
   cs=core.read(path)['cases'];h=hashlib.sha256(json.dumps([c['control_plan']for c in cs],sort_keys=True).encode()).hexdigest();programs.setdefault(h,[]).append(core.relative(path))
  assert len(programs)<=7,(n,len(programs));versions.append(dict(reviewId=n,distinctProgramVersions=len(programs),maximumInitialPlusRevisions=7,formalVersions=1 if n in QUALIFIED|{'42'} else 0,programs=programs))
 core.write(OUT/'verification/geometry-and-native-audit.json',dict(passed=True,rows=checks,formatAdaptation223='approved objects as one Module, obsolete Macro components/exports removed; source Macro retained; geometry and Ports unchanged'))
 core.write(OUT/'verification/deep-proofs.json',proofs);core.write(OUT/'verification/revision-budget.json',versions)
 prov=core.read('pcg/prototype/godot/source_provenance.json');assert all(core.sha(core.REPO/'pcg/prototype/godot'/p)==sha for p,sha in prov['files'].items());diff=subprocess.check_output(['git','diff','--name-only','origin/main','--','generation/manual-review'],text=True).splitlines();assert not diff
 core.write(OUT/'verification/source-audit.json',dict(passed=True,protectedFiles=len(prov['files']),protectedMismatches=[],designWebEdits=diff,engine=physics.artifact(core.REPO/'pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64'),gameSourceCommit='12f6cb006d7119598e3235f4ca4f7323e4c9d092'));print('GEOMETRY_NATIVE_PROOFS_SOURCE_PASS',flush=True)
if __name__=='__main__':main()
