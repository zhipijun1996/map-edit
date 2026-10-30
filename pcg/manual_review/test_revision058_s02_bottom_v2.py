"""One explicit ingress-fixture correction; original route and holdout failures untouched."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy
from pcg.migration import core,physics
from .continue_revision058_v1 import rows,label,OUT
from .finalize_revision058_v1 import folder_for
from .complete_revision058_protocol_v1 import actual

def main():
 r=next(r for r in rows()if label(r)=='s02');f=folder_for(r);root=core.REPO/'pcg/results/approved-r058-s02-qualified-final-v1';old=next(v for v in core.read(root/'boundary-probes.json')if not v['check']['passed']);case,_=actual(root,old['evidence']);fixed=copy.deepcopy(case);fixed['control_plan']=[dict(op='axis',value=0,cancel_settle=True,trigger=dict(after=0)),dict(op='wait',observed_y=dict(direction='lte',value=620),trigger=dict(after=1,state='observed_height',timeout=180))]+case['control_plan'];# Jump before waiting for full-body clearance.
 fixed['control_plan']=[fixed['control_plan'][0],dict(op='jump',trigger=dict(after=1)),fixed['control_plan'][1],dict(op='settle',target_x=350,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),dict(op='jump_release',trigger=dict(after=24))]+[dict(op='wait',trigger=dict(after=24,state='grounded',migration_goal=[346,587,8,6],timeout=300))]
 fixed['id']+='-full-body-aligned';fixed['module_sha256']=physics.module_hash(fixed)
 eng,_,_=physics._engine(f,'approved-r058-s02-bottom-fixture-v2',physics.FULL_PROTOCOL);c,raw,e=next(eng.run([fixed],'one-bottom-ingress-fixture'));check=physics.crossing(c,raw)
 core.write(eng.out/'check.json',dict(passed=check['passed'],check=check,evidence=e,original=old,newPhysicsAttempts=1,newIndependentHoldout=False,scope='hold horizontal alignment through entire bottom64px aperture before moving to internal350 dock; no Module changes, no new nominal or holdout'))
 core.write(OUT/'verification/s02-bottom-fixture-v2.json',dict(passed=check['passed'],proof=physics.artifact(eng.out/'check.json'),newPhysicsAttempts=1,newHoldout=False,wholeModuleQualified=False));print('S02_BOTTOM_FULL_BODY_ALIGNED',check['passed'])
if __name__=='__main__':main()
