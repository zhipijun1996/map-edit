"""Freeze the one repaired candidate before allocating its independent pool."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import sys
from pcg.migration import core,physics
from .continue_revision065_lift_v1 import rows,label,OUT as ORIGINAL_OUT,ID
from .continue_revision066_lift_repair_v1 import AUTH,OUT
from .run_revision065_lift_v1 import inherited,frozen_row
FINAL=core.REPO/'pcg/manual_review/implementation/revision-066-final-v1'
def folder_for(r):return FINAL/r['moduleId']
def main():
 from . import finalize_revision063_v1 as m
 row=rows()[0];action=sys.argv[1]
 if action=='freeze':
  repair=core.REPO/'pcg/results/approved-r065-lift-known-calibration-repair-v4/repair-check.json';assert core.read(repair)['passed']
  inherited(m,'freeze',[('approved-r063','approved-r065'),('revision063_content_v1','revision065_content_v1')],ROOT=FINAL,AUTH=AUTH,OUT=OUT,folder_for=folder_for)(row,'v4')
  f=folder_for(row);core.write(AUTH/'frozen-candidate.json',dict(module=physics.artifact(f/'module.mapnote.json'),cases=physics.artifact(f/'physics-input-cases.json'),parameters=physics.artifact(f/'parameters.json'),selection=physics.artifact(f/'selection.json'),calibrationRepair=physics.artifact(repair),taskAuthorization=physics.artifact(AUTH/'request.json'),frozenBeforePoolAllocation=True,newHumanApproval=False))
 elif action in ['qualify','deliver']:
  core.verify_artifacts([core.read(AUTH/'frozen-candidate.json')[k]for k in ['module','cases','parameters','selection','calibrationRepair']])
  inherited(m,action,[('approved-r063','approved-r066')],ROOT=FINAL,AUTH=AUTH,OUT=OUT,folder_for=folder_for)(row)
 else:raise ValueError(action)
if __name__=='__main__':main()
