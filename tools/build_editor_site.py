"""Build only the static fetch closure of the authoritative current library."""
import argparse,hashlib,json,re,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
IMPORT=re.compile(r"(?:import|export)\s+(?:[^;\n]*?\s+from\s*)?['\"]([^'\"]+)['\"]")
def build(destination,include_history=False):
 destination=Path(destination).resolve()
 if destination.exists()or destination==ROOT or ROOT.is_relative_to(destination):raise ValueError('web_output_must_be_new_and_separate')
 destination.mkdir(parents=True);copied={};fetches=[]
 def asset(name,expected=None):
  name=str(name).removeprefix('./');p=Path(name)
  if p.is_absolute()or'..'in p.parts or'\\'in name:raise ValueError('unsafe_web_asset:'+name)
  source=ROOT/p
  if not source.is_file():raise ValueError('missing_web_asset:'+name)
  digest=hashlib.sha256(source.read_bytes()).hexdigest()
  if expected and digest!=expected:raise ValueError('web_asset_hash_mismatch:'+name)
  target=destination/p;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target);copied[name]=digest
  return source
 for name in ['index.html','style.css','generation/index.html']:asset(name)
 pending=['app.js']
 while pending:
  name=pending.pop()
  if name in copied:continue
  source=asset(name)
  for ref in IMPORT.findall(source.read_text()):
   if ref.startswith('.'):pending.append((source.parent/ref.split('?')[0]).resolve().relative_to(ROOT).as_posix())
 catalog=json.loads(asset('modules/catalog.json').read_text())
 for entry in catalog['modules']+catalog['designs']:
  asset(entry['file'],entry['contentSha256']);asset(entry['thumbnail']);fetches.extend([entry['file'],entry['thumbnail']])
 for entry in catalog['modules']+catalog['designs']+catalog['withdrawn']:asset(entry['record'],entry['recordSha256'])
 for name in ['index.html','model.js','workshop.js','workshop.css','data.json']:asset('generation/module-workshop/'+name)
 view=json.loads((ROOT/'generation/module-workshop/data.json').read_text())
 if {v['id']for v in view['modules']}!={v['id']for v in catalog['modules']}:raise ValueError('stale_workshop_current_view')
 for path in (ROOT/'evidence/module-production').glob('*.json'):asset(path.relative_to(ROOT))
 for name in ['MAP_FOUNDATION.md','MAP_GENERATION_GUIDE.md','docs/module-production.md','docs/module-package-consumers.md']:asset(name)
 (destination/'.nojekyll').touch()
 if any(p.suffix in ['.gd','.tscn','.tres']for p in destination.rglob('*')if p.is_file()):raise ValueError('native_source_in_web_output')
 manifest=dict(schema='map-notes/current-editor-static-build/v2',catalogSha256=copied['modules/catalog.json'],currentModules=len(catalog['modules']),developmentDesigns=len(catalog['designs']),assets=len(copied),historicalWebAssets=0,editorFetchTargets=fetches,fetchClosureComplete=True,legacyCatalogsIncluded=False,files=copied)
 (destination/'site-build-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');return manifest
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True,type=Path);p.add_argument('--no-history',action='store_true',help='Compatibility flag; current builds always exclude historical source trees.');a=p.parse_args();r=build(a.out);print(json.dumps({k:v for k,v in r.items()if k not in ['files','editorFetchTargets']}))
