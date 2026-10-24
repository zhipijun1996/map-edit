"""Read immutable production evidence, then export existing Map Notes documents.

Can also export incomplete cases without physics; missing evidence stays UNKNOWN.
python3 -m pcg.contract.export --cases ... --run ... --out ...
"""
import argparse,gzip,hashlib,json,subprocess,sys,re,shutil
from pathlib import Path
REPO=Path(__file__).resolve().parents[2];ROOT=REPO/'pcg'
sys.path.insert(0,str(ROOT))
from prototype.factory.core.quality import module_hash

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text())
def collect(cases_path,run=None):
 cases=read(cases_path)['cases'];protocol=read(run/'protocol.json')if run and(run/'protocol.json').exists()else None
 catalog=read(run/'catalog.json')if run and(run/'catalog.json').exists()else None
 params=read(run/'generation_parameters.json')if run and(run/'generation_parameters.json').exists()else 'UNKNOWN'
 binding=read(run/'source_binding.json')if run and(run/'source_binding.json').exists()else None
 batches=read(run/'batches.json')if run and(run/'batches.json').exists()else[]
 entries=read(run/'heldout_entries.json')if run and(run/'heldout_entries.json').exists()else[]
 project=ROOT/'prototype/godot';protected=read(project/'source_provenance.json')['files']
 def dimensions(path,pattern):
  p=project/path
  if path not in protected or sha(p)!=protected[path]:raise ValueError('Unbound geometry source: '+path)
  m=re.search(pattern,p.read_text())
  if not m:raise ValueError('Cannot extract original dimensions: '+path)
  return dict(size=[float(m[1]),float(m[2])],source=dict(path='pcg/prototype/godot/'+path,sha256=sha(p)))
 body=dimensions('scenes/player/player.tscn',r'size = Vector2\(([^,]+), ([^)]+)\)')
 bell=dimensions('scripts/world/shot_latch.gd',r'bell_rectangle.size = Vector2\(([^,]+), ([^)]+)\)')
 rows=[]
 for case in cases:
  if case.get('module_sha256')and module_hash(case)!=case['module_sha256']:raise ValueError('Mutated source module '+case['id'])
  ev=case.get('factory_evidence');result=None;artifacts=[];input_case=None
  if run and ev:
   b=next((b for b in batches if b['batch']==ev['batch']),None)
   if not b or b['raw_output_sha256']!=ev['raw_output_sha256']:raise ValueError('Unknown/stale batch evidence')
   packed=run/b['gzip_path'];raw=gzip.decompress(packed.read_bytes())
   if hashlib.sha256(raw).hexdigest()!=b['raw_output_sha256']or sha(packed)!=b['gzip_sha256']:raise ValueError('Physics output drift')
   output= json.loads(raw);result=output['results'][ev['index']]
   if result['id']!=case['id']:raise ValueError('Case/result identity mismatch')
   inp=run/'physics'/(b['batch']+'.input.json');execution=read(run/b['execution'])
   if sha(inp)!=execution['input_sha256']:raise ValueError('Physics input drift')
   input_case=read(inp)['cases'][ev['index']]
   # Compare the geometry, mechanics and action program independently of labels.
   for k,v in input_case.items():
    if k not in('title','review_alias','noise')and case.get(k)!=v:raise ValueError('Export no longer matches simulated case: '+k)
   for p in [packed,inp,run/'source_binding.json',run/'batches.json',run/b['execution']]:artifacts.append(dict(path=str(p.relative_to(REPO)),sha256=sha(p)))
   if protocol:artifacts.append(dict(path=str((run/'protocol.json').relative_to(REPO)),sha256=sha(run/'protocol.json')))
   if result.get('module_definition_valid')is not True:raise ValueError('Physics case not a valid module')
  # Each raw calibration/holdout trial retains independent direction and failures.
  item=next((e for e in entries if e['uid']==case.get('factory_id')),None)
  enemy_defs={e['definition']:dimensions('resources/enemies/'+e['definition']+'.tres',r'collision_size = Vector2\(([^,]+), ([^)]+)\)')for e in case.get('enemies',[])}
  rows.append(dict(case=case,generationMetadata=dict(seed=dict(status='known',value=catalog['seed'])if isinstance(catalog,dict)and catalog.get('schema')=='pcg/factory-catalog/v1'else None,parameters=params,producer='pcg/prototype/factory/core/producer.py'if isinstance(catalog,dict)and catalog.get('schema')=='pcg/factory-catalog/v1'else 'pcg/prototype/plains/produce.py'),geometryDefinitions=dict(player=body,bell=bell,enemies=enemy_defs),sourceRun=str(run.relative_to(REPO))if run else 'UNKNOWN',sourceCases=dict(path=str(cases_path.relative_to(REPO)),sha256=sha(cases_path)),protocol=protocol or 'UNKNOWN',binding=binding or 'UNKNOWN',result=result or 'UNKNOWN',inputCase=input_case or 'UNKNOWN',artifacts=artifacts,statistics=item['stats']if item else 'UNKNOWN',trialRows=item['rows']if item else []))
 return rows

def export(cases_path,out,run=None):
 out=Path(out).resolve()
 if out.exists():raise ValueError('Keep versioned exports; choose a new output directory')
 out.mkdir(parents=True)
 bundle=dict(rows=collect(Path(cases_path).resolve(),Path(run).resolve()if run else None),sourceCommit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip())
 bundle_path=out/'source-bundle.json';bundle_path.write_text(json.dumps(bundle,ensure_ascii=False,allow_nan=False))
 # Node shares the editor's capability/difficulty validators and exact schema.
 subprocess.run(['node',str(REPO/'tools/export-module-contracts.mjs'),str(bundle_path),str(out)],cwd=REPO,check=True)
 files=[REPO/n for n in ('module-contract.js','module-contract-render.js','model.js','capabilities.js','difficulty.js','tools/export-module-contracts.mjs','tools/compose-module-contract.mjs')]+[Path(__file__)]
 for p in files:
  target=out/'export_source'/p.relative_to(REPO);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
 (out/'export-source.json').write_text(json.dumps(dict(source_files={str(p.relative_to(REPO)):sha(p)for p in files},workingTreeBaseCommit=bundle['sourceCommit'],note='File hashes describe the adapter actually executed; base commit alone is not its implementation identity',changes='Output adapter only; generation/search/physics unchanged'),indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--cases',required=True);p.add_argument('--run');p.add_argument('--out',required=True);a=p.parse_args();export(a.cases,a.out,a.run)
