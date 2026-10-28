import argparse,json
from pathlib import Path
from . import rules_v2 as rules
from pcg.prototype.workshop.rules import cmd,wait_x,settle
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();engine=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),HERE/'window-protocol-v1.json',Path(rules.__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);cs=[];rows=[]
 for x in [80,110]:
  c=rules.candidate(0,3);c['id']+=f'-closed-window-at-{x}';c['goal']=[55,416,50,8];c['control_plan']=([cmd('axis',value=1),wait_x(x),cmd('axis',value=0),cmd('wait',8)]if x>80 else[])+[cmd('shoot',aim_cell=dict(kind='enemy',id='window-sentry')),cmd('wait',45),settle(80,6)];cs.append(c)
 for c,r,e in engine.run(cs,'closed-window-projectile'):
  row=dict(case=c,result=r,evidence=e);rows.append(row);print(json.dumps(dict(id=c['id'],ok=r.get('ok'),enemies=r.get('plains',{}).get('enemies'),events=[x for x in r.get('plains',{}).get('events',[])if x.get('type')=='enemy_hit'])),flush=True)
 write(engine.out/'probe-results.json',rows)
if __name__=='__main__':main()
