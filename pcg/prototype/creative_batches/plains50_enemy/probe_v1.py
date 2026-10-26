from pathlib import Path
import json
from .rules_v1 import compiler,purpose,sources,runner,RECIPES
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
if __name__=='__main__':
 for recipe in RECIPES:
  response=compiler(dict(recipe=recipe));e=WorkshopEngine(ROOT/'results'/('workshop-plains50-enemy-probe-v1-'+recipe),extra_sources=sources()+[Path(__file__)],runner_script=runner(recipe));rows=[]
  for c,r,ev in e.run(response['cases'],'probe'):
   p=purpose(c,r);row=dict(id=c['id'],ok=r.get('ok'),purpose=p,reason=r.get('reason'),hp=r.get('hp'),coins=r.get('workshop',{}).get('coins'),evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
  (e.out/'summary.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
