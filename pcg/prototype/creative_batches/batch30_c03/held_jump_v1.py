import argparse,json
from pathlib import Path
from . import rules_v2 as rules
from pcg.prototype.workshop.rules import cmd,wait_x,settle
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();engine=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),HERE/'held-jump-protocol-v1.json',Path(rules.__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);cs=[];rows=[]
 for shot in [6,12,18,24]:
  for held in [8,20,36]:
   c=rules.candidate(0,3);c['id']+=f'-counter-held-jump-{shot}-{held}';c['control_plan']=[cmd('axis',value=1),wait_x(205),cmd('jump'),cmd('shoot',shot,direction=[0,1]),cmd('jump_release',held),settle(450,6)];cs.append(c)
 for c,r,e in engine.run(cs,'held-jump-counter'):
  same=bool(r.get('ok'))and r.get('workshop',{}).get('coins',0)>=12 and r.get('hp')==5;rows.append(dict(case=c,result=r,evidence=e,same_external_outcome=same));print(json.dumps(dict(id=c['id'],same=same,min_y=min((f['y']for f in r.get('frames',[])),default=None),last={k:r.get('frames',[{}])[-1].get(k)for k in ['x','y','support_id']})),flush=True)
 write(engine.out/'counter-results.json',rows)
if __name__=='__main__':main()
