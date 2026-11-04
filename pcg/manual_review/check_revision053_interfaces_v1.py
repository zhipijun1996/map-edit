"""Real closed-gate negative fixtures and unchanged full-body upward crossing."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy,sys
from pcg.migration import core,physics,revision053_runtime_v1 as backend
from pcg.prototype.factory.core.quality import module_hash
from .continue_revision053_v1 import rows,label,OUT

def main():
 for row in rows():
  n=label(row)
  if n not in sys.argv[1:]:continue
  f=core.REPO/row['outputDirectory'];doc=core.read(f/'module.mapnote.json');cs=core.read(f/'cases.json')['cases'];arrival=next(c for c in cs if c['route_spec']['to_port']=='B');top=next(p for p in doc['generationContract']['ports']if p['id']=='B');x=top['position'][0]
  eng,_,_=physics._engine(f,'approved-r053-'+n+'-top-interface-v1',physics.FULL_PROTOCOL);tests=[]
  c=copy.deepcopy(arrival);c.update(id=c['id']+'-forbidden-top-ingress',spawn=[x,-50],goal=[x-8,24,16,8],max_frames=240,control_plan=[dict(op='drop_through',trigger=dict(after=1)),dict(op='wait',trigger=dict(after=150))]);c['module_sha256']=module_hash(c);tests.append(c)
  c=copy.deepcopy(arrival);c.update(id=c['id']+'-closed-interior-up-jump',spawn=[x,46],goal=[x-8,-54,16,8],max_frames=240,control_plan=[dict(op='jump',trigger=dict(after=1)),dict(op='jump_release',trigger=dict(after=24)),dict(op='wait',trigger=dict(after=150))]);c['module_sha256']=module_hash(c);tests.append(c)
  checks=[]
  for c,r,e in eng.run(tests,'initial-closed-gate-negatives'):
   above=c['spawn'][1]<0;crossed=any(t['y']-18>=0 if above else t['y']+18<=0 for t in r['frames']);bell=any(v.get('type')=='bell_open'for v in r['plains']['events']);passed=not crossed and not bell and r['hp']==5 and not r['returns'];checks.append(dict(id=c['id'],passed=passed,initialTopPermission=top['permission'],fullBodyCrossed=crossed,bellOpened=bell,evidence=e))
  _,positive=backend.audit_cases(doc,cs,require_replay=False);negative=[]
  for kind in ['foreign-floor','foreign-index','owned-copy','wrong-permission']:
   ds=copy.deepcopy(doc);vs=copy.deepcopy(cs);v=next(v for v in vs if v.get('explicit_exit_neighbor'))
   if kind=='foreign-floor':v['explicit_exit_neighbor']['floor'][1]-=1
   elif kind=='foreign-index':v['explicit_exit_neighbor']['index']-=1
   elif kind=='owned-copy':v['explicit_exit_neighbor']['copiedIntoModule']=True
   else:next(p for p in ds['generationContract']['ports']if p['id']=='B')['permission']='INOUT'
   try:backend.audit_cases(ds,vs,require_replay=False)
   except (AssertionError,ValueError)as error:negative.append(dict(kind=kind,rejected=True,reason=str(error)))
   else:raise AssertionError('invalid neighbor accepted:'+kind)
  core.write(eng.out/'interface-checks.json',dict(passed=all(c['passed']for c in checks),checks=checks,nativeOwnershipPositive=positive,nativeOwnershipNegative=negative,source=physics.artifact(__file__),scope='Initial OUTPUT gating only; positive upward exit is the separate complete canonical program. Neighbor fixture never owned by this Module.'))
  assert all(c['passed']for c in checks);print(n,'TOP_INITIAL_OUTPUT_AND_OWNERSHIP_PASS',flush=True)
if __name__=='__main__':main()
