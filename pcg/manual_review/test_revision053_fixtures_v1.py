"""Exact-scope fixture guards and append-only lineage regression checks."""
import copy
from pcg.migration import core,physics,review_oneway_fixture_v3 as fixture,review_boundary_repair_v8 as lineage
from .continue_revision053_v1 import rows,OUT
from .finalize_revision053_v2 import folder_for

def main():
 r=next(r for r in rows()if r['reviewId']=='50');f=folder_for(r);doc=core.read(f/'module.mapnote.json');port=next(p for p in doc['generationContract']['ports']if p['id']=='C');case=core.read(f/'cases.json')['cases'][0];checks=[]
 c=copy.deepcopy(case);c['spawn']=port['stagingPosition'].copy();fixture.repair(c,port,2);assert c['spawn'][1]==port['stagingPosition'][1]-4;checks.append('exact50_positive')
 for kind in ['wrong_id','wrong_version','wrong_offset','wrong_port','wrong_surface','wrong_normal']:
  c=copy.deepcopy(case);p=copy.deepcopy(port);offset=2
  if kind=='wrong_id':c['approved_implementation']['reviewId']='61'
  elif kind=='wrong_version':c['approved_implementation']['designVersion']='sha256:invalid'
  elif kind=='wrong_offset':offset=-2
  elif kind=='wrong_port':p['id']='entry'
  elif kind=='wrong_surface':p['surface']='ROCK'
  else:p['normal']=[-1,0]
  before=copy.deepcopy(c);fixture.repair(c,p,offset);assert c==before;checks.append(kind)
 proof=core.read(f/'qualification-repaired.json')['report'];path=core.resolve_artifact(proof['path']);report=core.read(path);lineage.validate_lineage(report,path);checks.append('actual_lineage_positive')
 for kind in ['nominal_tamper','attempt_count','new_holdout']:
  bad=copy.deepcopy(report)
  if kind=='nominal_tamper':bad['routes'][0]['passed']=False
  elif kind=='attempt_count':bad['boundaryRepair']['newPhysicsAttempts']=3
  else:bad['boundaryRepair']['newIndependentHoldout']=True
  try:lineage.validate_lineage(bad,path)
  except (ValueError,AssertionError):checks.append(kind+'_rejected')
  else:raise AssertionError(kind)
 core.write(OUT/'verification/oneway50-lineage-tests.json',dict(passed=True,tests=checks,source=physics.artifact(__file__),nominalAndHoldoutRawUnchanged=True));print('EXACT_SCOPE_AND_LINEAGE_TESTS_PASS',len(checks))
if __name__=='__main__':main()
