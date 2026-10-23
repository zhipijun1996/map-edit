"""Build the actual Godot review portal, reusing the frozen public engine/base."""
import argparse,importlib.util,json,shutil,subprocess,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def build(run,out):
 run=Path(run);out=Path(out)
 if out.exists():raise ValueError('Refuse existing review build')
 catalog=json.loads((run/'catalog.json').read_text());cases=json.loads((run/'review_cases.json').read_text())
 if not cases['cases']:raise ValueError('No technically qualified modules; no playable review pool')
 from .core.quality import module_hash,digest
 for c in cases['cases']:
  if module_hash(c)!=c['module_sha256']:raise ValueError('Module witness changed after binding')
 out.mkdir(parents=True);extra=out/'resources';extra.mkdir()
 for name in ('main_v3.gd','main_v3.tscn','dynamic_context.gd','lab_draw_v3.gd','main_factory.gd','main_factory.tscn'):shutil.copy2(ROOT/'prototype/godot'/name,extra/name)
 (extra/'modules_v3.json').write_text(json.dumps(cases,ensure_ascii=False))
 spec=importlib.util.spec_from_file_location('factory_overlay',ROOT/'prototype/packaging_v3/overlay_pack.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 manifest=module.build(ROOT/'delivery/composable-v2/web/index.pck',out/'play',main_scene='res://main_factory.tscn',extra_dir=extra)
 old=manifest['overlay']['pack'];new='index.'+manifest['overlay']['sha256'][:12]+'.pck'
 (out/'play'/old).rename(out/new)
 (out/'play/index.html').write_text((out/'play/index.html').read_text().replace(old,'../'+new).replace('PCG overlay packaging proof','失序之钟 · Module 盲评试玩').replace('Packaging proof only · frozen base + independent overlay','离线生成候选 · 待真人评审 · 真实输入回放'))
 manifest['overlay']['pack']=new;(out/'overlay-manifest.json').write_text(json.dumps(manifest,indent=2));(out/'play/overlay-manifest.json').unlink()
 for p in (ROOT/'prototype/factory/web').iterdir():shutil.copy2(p,out/p.name)
 # Human evidence binds presentation as well as physics/module content. Keep
 # the original technical catalog intact; callers import with this web catalog.
 technical_sha=catalog.pop('catalog_sha256')
 ui_files=[ROOT/'prototype/godot'/n for n in ('main_v3.gd','lab_draw_v3.gd','main_factory.gd','main_factory.tscn')]+list((ROOT/'prototype/factory/web').glob('*'))
 catalog['source_technical_catalog_sha256']=technical_sha
 catalog['presentation_binding']=dict(pack_sha256=manifest['overlay']['sha256'],source_files={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(ui_files)})
 catalog['catalog_sha256']=digest(catalog)
 (out/'catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2))
 (out/'data.json').write_text(json.dumps(dict(status='local_candidate',scope='Public immutable source/data URLs are bound at publication.'),indent=2))
 for p in extra.iterdir():p.unlink()
 extra.rmdir()
 return manifest
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--run',required=True);p.add_argument('--out',required=True);a=p.parse_args();m=build(ROOT/'results'/a.run,ROOT/a.out);print(json.dumps(m['overlay']))
