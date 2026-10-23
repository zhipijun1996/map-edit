"""Immutable second research preview; reuse byte-identical existing engine URLs.
No prior bundle changes, no hosting guard changes, no production deployment.
"""
from pathlib import Path
import json,hashlib,subprocess,shutil,re,zipfile
import markdown
from simulator import ROOT
HOST=Path('/workspace/pcg-preview-host');TASK='PCG-RESEARCH-02'
OLD=Path('previews/PCG-RESEARCH-01/7c7b42e46e33c895d51741c1ca5d26a516568a27/8f8ded8ce59a')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def page(md):
 text=re.sub(r'\]\(([^\s():]+)\.md\)',r'](\1.html)',md)
 return '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{max-width:1080px;margin:30px auto;padding:0 20px;font:16px/1.8 system-ui;color:#183144}img,video{max-width:100%}table{border-collapse:collapse;display:block;overflow:auto}td,th{border:1px solid #b6c8d0;padding:6px}pre{background:#eef2f5;padding:14px;overflow:auto}a{color:#12649d}</style>'+markdown.markdown(text,extensions=['tables','fenced_code'])+'</html>'

def stage():
 if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip():raise RuntimeError('Commit research source and results before staging')
 source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();web=ROOT/'delivery/composable-v2/web';build=sha(web/'index.pck')[:12]
 base=Path('previews')/TASK/source/build;dest=HOST/'site'/base
 if dest.exists():raise RuntimeError('Refuse immutable destination overwrite')
 # The old public engine is an immutable dependency. Sharing these exact bytes
 # avoids duplicating 38 MiB of WASM under the unchanged 900 MiB site limit.
 for n in ('index.js','index.wasm'):
  if sha(web/n)!=sha(HOST/'site'/OLD/n):raise RuntimeError('Shared engine differs:'+n)
 dest.mkdir(parents=True)
 for p in web.iterdir():
  if p.is_file() and p.name not in ('index.js','index.wasm'):shutil.copy2(p,dest/p.name)
 pack=f'index.{build}.pck';(dest/'index.pck').rename(dest/pack)
 prefix='/gunman-rush-previews/'+OLD.as_posix()+'/index'
 html=(dest/'index.html').read_text().replace('src="index.js"','src="'+prefix+'.js"')
 html=html.replace('"executable":"index",','"executable":'+json.dumps(prefix)+',"mainPack":'+json.dumps(pack)+',')
 html=html.replace('"index.pck":',json.dumps(pack)+':').replace('"index.wasm":',json.dumps(prefix+'.wasm')+':')
 html=html.replace('</body>','<div style="position:fixed;bottom:3px;left:4px;z-index:50;background:#183144;color:white;padding:4px;font:12px sans-serif"><a style="color:white" href="COMPOSABLE-REPORT.html">能力组合研究报告</a> · <a style="color:white" href="delivery/composable-v2/modules.mp4">真实录像</a> · 预生成候选，趣味待试玩</div></body>')
 (dest/'index.html').write_text(html)
 info=dict(schema='disordered-clock/research-export/v2',source_commit=source,game_source_commit='12f6cb006d7119598e3235f4ca4f7323e4c9d092',build_id=build,pack=pack,pack_bytes=(dest/pack).stat().st_size,scope='independent research; offline generation and real-input replays; human fun/device/production integration unverified',physics_hz=60,shared_engine={n:dict(url='/gunman-rush-previews/'+(OLD/n).as_posix(),sha256=sha(web/n),bytes=(web/n).stat().st_size) for n in ('index.js','index.wasm')})
 (dest/'build-info.json').write_text(json.dumps(info,indent=2));(dest/'index.cache-sw.js').write_text('// Integrity metadata only; no registered service worker.\nconst RESOURCE_MAP = '+json.dumps({pack:dict(sha256=sha(dest/pack),bytes=info['pack_bytes'],chunks=[])})+';\n')
 paths=[ROOT/n for n in ('COMPOSABLE-REPORT.md','REPORT.md','README.md')]
 paths += [p for p in (ROOT/'research').rglob('*') if p.is_file()]
 paths += [p for p in (ROOT/'evidence/composable-audit').rglob('*') if p.is_file()]
 paths += [ROOT/'prototype/godot'/n for n in ('ADAPTATION.md','WORKER_V2.md','source_provenance.json','asset_licenses_provenance.json')]
 result_names=['composable-search-v5','composable-search-seed2','composable-search-final','composable-evaluation-final','composable-contract-matrix-v2','composable-delivery-v2','composable-custom-wall-no-jump','composable-custom-no-move','composable-custom-no-move-v2']
 paths += [ROOT/'results'/n/'summary.json' for n in result_names]
 paths += [p for p in (ROOT/'delivery/composable-v2').rglob('*') if p.is_file() and p.suffix in ('.json','.png','.mp4','.log') and 'web'not in p.parts]
 for p in paths:
  if not p.is_file():continue
  q=dest/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
  if q.suffix=='.md':q.with_suffix('.html').write_text(page(p.read_text()))
 for rel,expected in json.loads((ROOT/'prototype/godot/asset_licenses_provenance.json').read_text())['files'].items():
  p=ROOT/'prototype/godot'/rel
  if sha(p)!=expected:raise RuntimeError('License drift:'+rel)
  q=dest/'licenses'/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
 # Code + exact formal inputs/full outputs. Earlier diagnostics remain in local git;
 # include their summaries so failures are visible without duplicating every trace.
 files=[ROOT/p for p in subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines()]
 zip_path=dest/'source-and-data.zip'
 with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in files:
   rel=p.relative_to(ROOT)
   if rel.parts[0]=='results' and len(rel.parts)>1 and rel.parts[1]not in result_names and p.name not in ('environment.json','summary.json'):continue
   z.write(p,rel)
  for p in (ROOT/'delivery/composable-v2/mapnotes').glob('*.json'):z.write(p,p.relative_to(ROOT))
  z.writestr('RESEARCH_SOURCE_COMMIT.txt',source+'\n')
 (dest/'COMPOSABLE-REPORT.html').write_text((dest/'COMPOSABLE-REPORT.html').read_text().replace('</html>','<p><a href="source-and-data.zip">下载源码、完整正式实验数据与Map Notes草图</a> · <a href="delivery/composable-v2/modules.mp4">原生Godot录像</a> · <a href="index.html">试玩</a></p></html>'))
 verification=dict(source_commit=source,build_id=build,pack=pack,pack_bytes=info['pack_bytes'],pack_sha256=sha(dest/pack),reconstructed=False,failed=0)
 files={p.relative_to(dest).as_posix():sha(p) for p in sorted(dest.rglob('*')) if p.is_file()}
 url='https://zhipijun1996.github.io/gunman-rush-previews/'+base.as_posix()+'/'
 (dest/'preview.json').write_text(json.dumps(dict(schema_version=1,task=TASK,source_commit=source,game_source_commit=info['game_source_commit'],build_id=build,seed='920100/920101/920102; holdout331051',entry='standalone-research-scene',scene='res://main_v2.tscn',url=url,pack_verification=verification,validation='real physics, paired perturbation, bounded counterexamples and recorded inputs; human fun/device approval unverified',files=files),indent=2))
 total=sum(p.stat().st_size for p in (HOST/'site').rglob('*') if p.is_file())
 if total>900*1024**2:raise RuntimeError('Unchanged hosting limit exceeded: '+str(total))
 index=HOST/'site/index.html';old=index.read_text();link='<p><a href="'+base.as_posix()+'/">PCG-RESEARCH-02 · 能力组合生成试玩</a> · <a href="'+base.as_posix()+'/COMPOSABLE-REPORT.html">报告、录像与数据</a></p>'
 index.write_text(old.replace('</body>',link+'</body>') if '</body>'in old else old+link)
 (ROOT/'delivery/composable-v2/staged-preview.json').write_text(json.dumps(dict(path=str(dest),url=url,source_commit=source,build_id=build,site_bytes=total,source_zip_bytes=zip_path.stat().st_size),indent=2));print(url)
if __name__=='__main__':stage()
