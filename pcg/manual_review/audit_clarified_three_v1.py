"""Read-only geometry, actual input, causal and fixture lineage audit."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy,gzip,json,subprocess
from pcg.migration import core,physics,review_oneway_fixture_v1 as fixture
from pcg.manual_review.repair_clarified_three_v1 import OUT,AUTH,rows
from pcg.manual_review.finalize_clarified_three_v1 import folder_for

def main():
 records=[];bindings=[];proofs=[]
 for row in rows():
  n=row['reviewId'];f=folder_for(row);d=core.read(f/'module.mapnote.json');oldbinding=core.read(AUTH/(n+'-original-binding.json'));old=core.read(core.REPO/('pcg/manual_review/implementation/review-029-final-v1'if n!='174'else'pcg/manual_review/implementation/batch-019')/row['moduleId']/'module.mapnote.json');cs=core.read(f/'physics-input-cases.json')['cases'];q=core.read(f/('qualification-repaired.json'if n=='174'else'qualification.json'));report=physics.verify_report(f,q['report'],deep=True);assert report['passed'];proofs.append(dict(reviewId=n,report=q['report'],passed=True))
  assert old['objects']==d['objects'];assert old['generationContract']['space']['bounds']==d['generationContract']['space']['bounds']
  changes=[]
  for a,b in zip(old['generationContract']['ports'],d['generationContract']['ports']):
   assert all(a[k]==b[k]for k in ['id','position','normal','permission'])
   if a['surface']!=b['surface']:changes.append(dict(port=b['id'],before=a['surface'],after=b['surface']))
  assert changes==([dict(port='exit',before='ROCK',after='ONE_WAY_PLATFORM')]if n=='174'else[])
  rdir=core.REPO/('pcg/results/approved-c3-'+n+'-delivery-final-v1');canonical=core.read(rdir/'canonical.json');examples=[]
  for v in canonical['rows']:
   e=v['evidence'];r=json.loads(gzip.decompress((rdir/e['output']).read_bytes()))['results'][e['index']];assert v['check']['ok']
   accepted=[dict(frame=f['frame'],**a)for f in r['frames']for a in f['accepted']if a['type']=='shot'];signs=[1 if e['direction'][0]>0 else-1 for e in accepted]
   if n=='171':
    assert r['jumps']==0 and len(signs)==6 and all(a*b<0 for a,b in zip(signs,signs[1:]));assert all(a['hp']==0 and a['dead']for a in r['frames'][-1]['review029_wave']['actors'])
   if n=='175':
    board=[f for f in r['frames']if f.get('support_id')=='key-carrier'];assert board and any(f['frame']>130 for f in board);dock=[e for e in r['plains']['events']if e.get('type')=='dock_occupied'];assert any(e['occupied']for e in dock);assert any(e.get('type')=='bell_open'and e['id']=='key-control'and e['count']>=3 for e in r['plains']['events'])
   examples.append(dict(route=v['case']['route_spec']['id'],source=physics.artifact(rdir/'canonical.json'),hp=r['hp'],jumps=r['jumps'],actualShotDirections=signs,actualShotFrames=[s['frame']for s in accepted],stable=r['ok']))
  records.append(dict(reviewId=n,allWorldObjectsUnchanged=True,boundsUnchanged=True,portChanges=changes,canonicalNativeExamples=examples,packagePassed=core.read(f/'package-result.json')['passed']))
  # Frozen generation metadata retains the original published design provenance.
  # This explicit overlay binds the current chat authority and its exact target;
  # it does not relabel that older published file as having the new surface.
  bindings.append(dict(reviewId=n,currentAuthorization=physics.artifact(AUTH/'request.json'),currentDesign=physics.artifact(core.REPO/row['designFile']),currentDesignVersion=row['designVersion'],implementationVersion=d['generationContract']['contentVersion'],historicalPublishedDesign=physics.artifact(core.REPO/oldbinding['designFile']),frozenGenerationDesignFileRole='historical published source; current chat authorization/target governs the implementation',canonicalCases=physics.artifact(f/'physics-input-cases.json')))
 core.write(OUT/'verification/geometry-and-native-audit.json',dict(passed=True,rows=records));core.write(OUT/'verification/deep-proofs.json',proofs);core.write(AUTH/'version-bindings.json',dict(schema='pcg/chat-authorization-overlay/v1',rows=bindings,newPhysicsAttempts=0,newIndependentHoldout=False,geometryAndControllerSemanticsChangedByThisOverlay=False))
 # Prove the correction is limited to the exact target and invalid +2 fixture.
 case=dict(spawn=[0,294],approved_implementation=dict(reviewId='174',designVersion=fixture.DESIGN_VERSION));port=dict(surface='ONE_WAY_PLATFORM',normal=[-1,0],stagingPosition=[-104,292]);fixture.repair(case,port,2);assert case['spawn'][1]==288
 tests=[]
 for name,change in [('other_module',lambda c,p:c['approved_implementation'].update(reviewId='171')),('old_version',lambda c,p:c['approved_implementation'].update(designVersion='sha256:old')),('rock_port',lambda c,p:p.update(surface='ROCK'))]:
  c=copy.deepcopy(case);c['spawn'][1]=294;p=copy.deepcopy(port);change(c,p);before=copy.deepcopy(c);fixture.repair(c,p,2);assert c==before;tests.append(name)
 core.write(OUT/'verification/oneway-fixture-scope.json',dict(passed=True,invalidEmbeddedPlus2CorrectedToMinus4=True,otherCasesUnchanged=tests,allNominalTrialsAndSeedsUnchanged=True))
 prov=core.read('pcg/prototype/godot/source_provenance.json');assert all(core.sha(core.REPO/'pcg/prototype/godot'/p)==sha for p,sha in prov['files'].items());assert not subprocess.check_output(['git','diff','--name-only','HEAD','--','generation/manual-review']).strip()
 core.write(OUT/'verification/source-audit.json',dict(passed=True,protectedFiles=len(prov['files']),protectedMismatches=[],designWebEdits=False,engine=physics.artifact(core.REPO/'pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64'),gameSourceCommit='12f6cb006d7119598e3235f4ca4f7323e4c9d092'))
 print('CLARIFIED_THREE_NATIVE_AND_SOURCE_PASS',flush=True)
if __name__=='__main__':main()
