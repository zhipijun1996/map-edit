"""Real top-Port fixture preflight, before selecting a formal run."""
import sys
from pcg.migration import core,physics
from .new_ideas_v1 import rows,label
from .finalize_ideas_v1 import folder_for

def run(row):
 f=folder_for(row);eng,cs,_=physics._engine(f,'approved-ideas-'+label(row)+'-boundary-preflight-v1',physics.FULL_PROTOCOL);d=core.read(f/'module.mapnote.json');ports={p['id']for p in d['generationContract']['ports']if p['face']=='TOP'}
 probes=[c for c in physics.seam_cases(cs[0],d)if c['migration_probe']['portId']in ports and c['id'].endswith('-0')]
 probes +=[physics.continuous_entry(c,d)for c in cs if c['route_spec']['from_port']in ports];probes +=[physics.continuous_exit(c,d)for c in cs if c['route_spec']['to_port']in ports]
 checks=[]
 for c,r,e in eng.run(probes,'top-port-preflight'):
  q=physics.crossing(c,r);checks.append(dict(case=c,check=q,evidence=e));print(label(row),c['id'],q['passed'],r.get('reason'),flush=True)
 core.write(eng.out/'boundary-checks.json',dict(passed=all(v['check']['passed']for v in checks),rows=checks,fullBodyThresholdsUnchanged=True,independentHoldout=False))
if __name__=='__main__':
 for r in rows():
  if label(r)in sys.argv[1:]:run(r)
