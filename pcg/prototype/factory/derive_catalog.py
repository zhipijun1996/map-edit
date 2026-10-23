"""Reclassify unchanged frozen evidence under an explicit stricter tier.
Never changes physics, reselects finalists, reruns lucky seeds or overwrites a run.
"""
import argparse,copy,json,shutil
from pathlib import Path
from .core.quality import POLICY,digest,gate,module_hash
from .core.engine import ROOT,file_sha

def derive(source,out,tier='regular'):
 source=Path(source);out=Path(out)
 if out.exists():raise ValueError('Refuse existing derived catalog')
 old=json.loads((source/'catalog.json').read_text());catalog=copy.deepcopy(old);policy=copy.deepcopy(POLICY);policy['requested_tier']=tier
 catalog['quality_policy']=policy;catalog['quality_policy_sha256']=digest(policy);catalog['run_id']=out.name
 catalog['derivation']=dict(source_run=str(source.relative_to(ROOT)),source_catalog_sha256=old['catalog_sha256'],operation='strict_explicit_tier_reclassification_only',new_physics_cases=0,admission_source_sha256=file_sha(Path(__file__).parent/'core/quality.py'))
 for row in catalog['candidates']:
  row['previous_admission']=row['admission'];dynamic=row['family']in ('hook_saw','carrier_double','carrier_recoil')
  row['admission']=gate(row['validation'],row['shortcut_witnesses'],dynamic,policy,requested_tier=tier)
 allowed={c['uid']for c in catalog['candidates']if c['admission']['status']=='awaiting_human_review'}
 original=json.loads((source/'review_cases.json').read_text())['cases'];cases=[]
 for c in original:
  if c['factory_id']not in allowed:continue
  if module_hash(c)!=c['module_sha256']:raise ValueError('source witness integrity')
  cases.append(c)
 for i,c in enumerate(cases):c['title']=c['review_alias']=f'样例 {i+1:02d}'
 catalog['review_modules']=[dict(uid=c['factory_id'],module_sha256=c['module_sha256'],alias=c['review_alias'])for c in cases]
 catalog.pop('catalog_sha256');catalog['catalog_sha256']=digest(catalog)
 out.mkdir(parents=True)
 for n,v in [('catalog',catalog),('review_cases',{'cases':cases}),('summary',dict(schema='pcg/factory-derivation/v1',source_run=source.name,requested_tier=tier,finalists=len(catalog['candidates']),awaiting_human_review=len(cases),rework=len(catalog['candidates'])-len(cases),approved_offline=0,human_feedback=0,new_physics_cases=0,source_catalog_sha256=old['catalog_sha256'],gameplay_fields_unchanged=True))]:
  (out/(n+'.json')).write_text(json.dumps(v,ensure_ascii=False,indent=2))
 for p in [Path(__file__),Path(__file__).parent/'core/quality.py']:
  q=out/'source_snapshot'/p.name;q.parent.mkdir(exist_ok=True);shutil.copy2(p,q)
 return catalog
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--name',required=True);p.add_argument('--tier',choices=['regular','precision_review'],default='regular');a=p.parse_args();c=derive(ROOT/'results'/a.source,ROOT/'results'/a.name,a.tier);print(json.dumps(dict(review_modules=len(c['review_modules']),catalog_sha256=c['catalog_sha256'])))
