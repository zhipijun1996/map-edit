"""Actual raw positives and fail-closed negatives for scoped measurement/completion changes."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy,gzip,json
from pcg.migration import core,physics,revision058_top_observer_v2 as top,revision058_protocol_completion_v2 as lineage,review_counter_scope_v12 as counter,revision058_boundary_v1 as boundary
from .continue_revision058_v1 import OUT,rows,label
from .finalize_revision058_v1 import folder_for
from .complete_revision058_protocol_v1 import actual

def main():
 checks=[];bindings=[]
 for lab in ['lt-1x2','s07']:
  root=core.REPO/f'pcg/results/approved-r058-{lab}-qualified-final-v1';row=next(v for v in core.read(root/'boundary-probes.json')if not v['check']['passed']);case,raw=actual(root,row['evidence']);positive=top.observe(case,raw);assert positive and physics.crossing(case,raw)['passed'];bindings.append(physics.artifact(root/row['evidence']['output']));checks.append(lab+'_actual_top_positive')
  for name in ['version','id','direction','neighbor','damage','goal','last-frame','waiting']:
   c,r=copy.deepcopy(case),copy.deepcopy(raw)
   if name=='version':c['approved_implementation']['designVersion']='wrong'
   elif name=='id':c['approved_implementation']['reviewId']='42'
   elif name=='direction':c['migration_probe']['direction']='ingress'
   elif name=='neighbor':c['migration_probe']['neighbor']['floor'][1]-=1
   elif name=='damage':r['hp']=4
   elif name=='goal':c['goal'][1]+=1
   elif name=='last-frame':r['frames'][-1]['grounded']=False
   else:r['plan_error']='trigger_timeout/0/grounded'
   assert top.observe(c,r)is None,(lab,name);checks.append(lab+'_'+name+'_rejected')
 for r in rows():
  f=folder_for(r);p=f/'qualification-supplemented.json'
  if not p.exists():continue
  q=core.read(p);path=core.resolve_artifact(q['report']['path']);report=core.read(path);lineage.validate_lineage(report,path);physics.verify_report(f,q['report'],deep=True);checks.append(label(r)+'_lineage_and_actual_full_coverage')
  for name in ['route','attempts','new-holdout','full-v2-claim']:
   bad=copy.deepcopy(report)
   if name=='route':bad['routes'][0]['passed']=False
   elif name=='attempts':bad['actualAttempts']+=1
   elif name=='new-holdout':bad['protocolCompletion']['newIndependentHoldout']=True
   else:bad['protocolCompletion']['fullV2Qualification']=True
   try:lineage.validate_lineage(bad,path)
   except (ValueError,AssertionError):checks.append(label(r)+'_'+name+'_rejected')
   else:raise AssertionError(name)
 # Positive and exact-version refusal for distinct valid side one-way starts.
 r=next(r for r in rows()if label(r)=='lb-1x2');f=folder_for(r);c=core.read(f/'physics-input-cases.json')['cases'][0];port=core.read(f/'module.mapnote.json')['generationContract']['ports'][0]
 a=copy.deepcopy(c);a['spawn']=port['stagingPosition'].copy();boundary.side_start(a,port,2);assert a['spawn'][1]==port['stagingPosition'][1]-4;checks.append('side_oneway_distinct_valid_start')
 for name in ['version','surface','offset']:
  a,p=copy.deepcopy(c),copy.deepcopy(port);offset=2
  if name=='version':a['approved_implementation']['designVersion']='wrong'
  elif name=='surface':p['surface']='ROCK'
  else:offset=0
  before=copy.deepcopy(a);boundary.side_start(a,p,offset);assert a==before;checks.append('side_'+name+'_rejected')
 core.write(OUT/'verification/measurement-regressions.json',dict(passed=True,checks=checks,originalRaw=bindings,protectedPhysicsChanged=False,newGodotAttempts=0,newHoldout=False,observer=physics.artifact(top.__file__),lineage=physics.artifact(lineage.__file__)));print('SCOPED_MEASUREMENT_REGRESSION_PASS',len(checks))
if __name__=='__main__':main()
