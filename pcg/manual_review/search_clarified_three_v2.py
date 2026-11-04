"""Correct pending-input scheduling before physics; retain the invalid v1 run."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import inspect,copy
from pcg.migration import core,physics,godot_package
from pcg.prototype.workshop.rules import cmd
from pcg.manual_review.repair_clarified_three_v1 import OUT,AUTH,WORK,rows
from pcg.manual_review import search_clarified_three_v1 as old
from pcg.manual_review.prepare_review029_v1 import at,end
from pcg.manual_review.repair_review029_v2 import axis

def programs(n,base):
 if n=='171':yield from old.programs(n,base)
 else:
  for start,lead in [(1048,36),(1052,36),(1048,48)]:
   c=base[0];p=copy.deepcopy(c['control_plan']);i=next(i for i,v in enumerate(p)if v['op']=='settle'and v['target_x']==1030);j=next(i for i,v in enumerate(p)if v.get('carrier_value')==1430)
   replacement=at(start,420)
   for _ in range(3):
    attempt=[dict(op='wait',trigger=dict(state='grounded_shot_ready',migration_goal=[start-5,416,10,8],timeout=150)),cmd('shoot',aim_cell=dict(kind='bell',id='key-control')),cmd('wait',18)]+at(start,420)
    for op in attempt:op['skip_if_carrier_running']='key-carrier'
    replacement+=attempt
   replacement+=at(1080,420)+[axis(0),dict(op='wait',trigger=dict(state='boarding_window',timeout=180),carrier_id='key-carrier',lead_distance=lead),cmd('jump'),cmd('jump_release',8),dict(op='wait',trigger=dict(dynamic=dict(kind='on_platform',id='key-carrier'),timeout=180)),axis(0),dict(op='wait',trigger=dict(state='carrier_x_gte',timeout=900),carrier_id='key-carrier',carrier_value=1430)]
   p[i:j+1]=replacement;yield dict(groundRestartX=start,boardLeadDistance=lead),[p]

def run(row):
 n=row['reviewId'];folder=core.REPO/row['outputDirectory'];cs=core.read(folder/'cases.json')['cases'];core.write(folder/'history/pre-driver-v2-cases.json',dict(cases=cs))
 for c in cs:c['generation_rule']['registration_source']='pcg/manual_review/clarified_three_author_v2.py'
 core.write(folder/'cases.json',dict(cases=cs));doc=godot_package.bind_case_behavior(core.read(folder/'module.mapnote.json'),cs);core.write(folder/'module.mapnote.json',doc);core.contract(folder/'module.mapnote.json',refresh=True)
 source=inspect.getsource(old.run).replace("n+'-domain.json'","n+'-corrected-domain-v2.json'").replace("'approved-c3-'+n+'-screen-'","'approved-c3-'+n+'-corrected-screen-'").replace("folder/('search/candidate-'","folder/('search-corrected/candidate-'")
 scope={**old.__dict__,'programs':programs};exec(compile(source,__file__,'exec'),scope);scope['run'](row)
if __name__=='__main__':
 import sys
 for r in rows():
  if r['reviewId']in sys.argv[1:]:run(r)
