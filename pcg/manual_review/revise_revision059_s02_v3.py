from pcg.migration import core
from .continue_revision059_v1 import rows,label
from .revise_revision059_v2 import save
from .prepare_revision058_v2 import jump
from .prepare_review045_v1 import at,end

def main():
 r=next(r for r in rows()if label(r)=='s02');cs=core.read(core.REPO/r['outputDirectory']/'cases.json')['cases']
 for c in cs:
  c['generation_rule']['registration_source']='pcg/manual_review/revision059_repair_author_v3.py'
  if c['route_spec']['from_port']!='B':continue
  c['control_plan']=[dict(op='wait',trigger=dict(after=1,state='repair_ledge_start',timeout=1800))]+jump(64,24,[.7,.7141428429])+at(64,382)+[dict(op='wait',trigger=dict(after=1,state='repair_ledge_board',timeout=1800))]+jump(130,24)+[dict(op='wait',carrier='P',trigger=dict(after=1,state='carrier_supported',timeout=300)),dict(op='settle',target_x=100,revision_follow='P',deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),dict(op='wait',carrier='P',exit_y=170,trigger=dict(after=1,state='carrier_exit',timeout=1800))]+jump(64,24)+end(*c['exit_port'])
 save(r,cs,'v3')
if __name__=='__main__':main()
