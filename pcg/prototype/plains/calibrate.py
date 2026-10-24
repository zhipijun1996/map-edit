"""A bounded calibration milestone before preregistered final holdout."""
import argparse,json,collections
from .engine import ROOT,PlainsEngine
from .evaluation import evaluate
def run(name,pilot):
 out=ROOT/'results'/name;engine=PlainsEngine(out,12);qualified=json.loads((ROOT/'results'/pilot/'qualified.json').read_text());cases=[e['case']for e in qualified]
 entries=evaluate(engine,cases,240810,4,'decision-calibration',levels=('clean','mild','moderate'))
 summary=dict(scope='Calibration only; not final held-out success rates',physics_cases=engine.sim.cases,candidates=len(entries),rows=[dict(uid=e['uid'],family=e['case']['family'],stats=e['stats'],sequence=e['behavior']['sequence']if e['behavior']else None)for e in entries])
 (out/'entries.json').write_text(json.dumps(entries,ensure_ascii=False));(out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--pilot',default='plains-pilot-v3');a=p.parse_args();run(a.name,a.pilot)
