"""Preserve native rejection when an unqualified manual sample takes damage."""
from pcg.migration import core,physics,godot_package
from .refresh_review045_v1 import rows
from .finalize_review045_v1 import folder_for
from .finalize_review045_v2 import partial

def retain(row,error):
 f=folder_for(row);compiled=godot_package.verify_package(f/'playable',require_loaded=False)
 core.write(f/'package-result.json',{**compiled,'passed':False,'loadExecuted':True,'loaded':False,'error':str(error),'evidence':physics.artifact(f/'playable/load-evidence/index.json'),'scope':'Compiled manual candidate; actual native replay failed. No successful native route.'})
 core.write(f/'delivery-scope.json',dict(status='UNQUALIFIED',successfulDirections=0,requestedDirections=2,failedReplayOnly=True,nativeReplayPassed=False,manualPlaytest='UNKNOWN'))
 print(row['reviewId'],'NATIVE_FAILURE_RETAINED',str(error),flush=True)
if __name__=='__main__':
 for r in rows():
  if r['reviewId']=='51':retain(r,'original v2 load_execution_failed; actual native HP4; original traceback retained')
  if r['reviewId']=='52':
   try:partial(r)
   except godot_package.PackageError as e:retain(r,e)
