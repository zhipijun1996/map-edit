"""Stage a new small immutable preview over frozen existing public dependencies."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,zipfile,importlib.util
import markdown
ROOT=Path(__file__).resolve().parents[2];HOST=Path('/workspace/pcg-preview-host');TASK='PCG-DYNAMIC-04'
ASSET='pcg-dynamic-04-source-and-data.zip'
# Caller stores this archive with git add --sparse outside site/ before pushing.
# Pin the final download to that data commit in the publication receipt.
DOWNLOAD='https://raw.githubusercontent.com/zhipijun1996/gunman-rush-previews/main/artifacts/PCG-DYNAMIC-04/{source}/'+ASSET
def sha(p):
 with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def page(text):
 return '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{max-width:1050px;margin:28px auto;padding:0 18px;font:16px/1.8 system-ui;color:#183144}table{border-collapse:collapse;display:block;overflow:auto}td,th{padding:6px;border:1px solid #abc}pre{background:#eef3f6;padding:14px;overflow:auto}video,img{max-width:100%}</style>'+markdown.markdown(text,extensions=['tables','fenced_code'])
def package(source):
 out=ROOT/'delivery/dynamic-v3';archive=out/ASSET
 files=[ROOT/p for p in subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines() if not p.startswith('results/')]
 files+=[p for pattern in ('dynamic-*','region-*') for directory in (ROOT/'results').glob(pattern) for p in directory.rglob('*') if p.is_file()]
 files+=[p for p in out.rglob('*') if p.is_file() and p.suffix in ('.json','.log','.png','.mp4') and 'release-resources'not in p.parts and not any(x.startswith('web-') for x in p.parts) and p.name!='staged-preview.json']
 files=sorted(set(files));index={str(p.relative_to(ROOT)):dict(bytes=p.stat().st_size,sha256=sha(p))for p in files}
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for p in files:z.write(p,p.relative_to(ROOT))
  z.writestr('RESEARCH_SOURCE_COMMIT.txt',source+'\n')
  z.writestr('ARCHIVE-FILES.json',json.dumps(index,indent=2))
 return dict(url=DOWNLOAD.format(source=source),bytes=archive.stat().st_size,sha256=sha(archive),local_path=str(archive),files=len(files))
def stage():
 if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip():raise RuntimeError('Commit source before staging')
 if subprocess.check_output(['git','status','--porcelain'],cwd=HOST,text=True).strip():raise RuntimeError('Hosting checkout is dirty')
 source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 web=ROOT/'delivery/dynamic-v3/web-release-final';manifest=json.loads((web/'overlay-manifest.json').read_text());build=manifest['overlay']['sha256'][:12]
 browser=json.loads((ROOT/'delivery/dynamic-v3/browser-release-final/browser.json').read_text())
 if browser['records'][-1]['action']!='all_checks_passed':raise RuntimeError('Missing final actual browser checks')
 # Independently verify every local immutable dependency before sharing its URL.
 dependencies={}
 for url in (manifest['base']['url'],manifest['engine']['prefix']+'.js',manifest['engine']['prefix']+'.wasm'):
  path=HOST/'site'/url.removeprefix('/gunman-rush-previews/')
  dependencies[url]=dict(bytes=path.stat().st_size,sha256=sha(path))
 if dependencies[manifest['base']['url']]['sha256']!=manifest['base']['sha256']:raise RuntimeError('Frozen base differs')
 external=package(source)
 rel=Path('previews')/TASK/source/build;dest=HOST/'site'/rel
 if dest.exists():raise RuntimeError('Refuse immutable destination overwrite')
 files={}
 for p in web.iterdir():
  if p.is_file():files[p.name]=p.read_bytes()
 original_pack=manifest['overlay']['pack'];pack='index.'+build+'.pck'
 files[pack]=files.pop(original_pack);manifest['overlay']['pack']=pack
 manifest['runtime_verified']=True;manifest['browser_evidence']='browser.json'
 manifest['limits']=['Actual Chromium input witness checks passed for these 17 candidates; human fun/device approval unverified.','Frozen base/engine dependencies must also be available at their immutable URLs.']
 files['overlay-manifest.json']=json.dumps(manifest,indent=2).encode()
 text=files['index.html'].decode().replace(original_pack,pack).replace('PCG overlay packaging proof','失序之钟·动态机关与浮岛生成研究').replace('Packaging proof only · frozen base + independent overlay','PCG-DYNAMIC-04 · 17个预生成候选 · 趣味待试玩')
 text=text.replace('</html>','<div style="position:fixed;bottom:4px;right:6px;background:#183144;padding:4px;font:12px sans-serif"><a style="color:white" href="report.html">报告</a> · <a style="color:white" href="modules.mp4">真实录像</a></div></html>')
 # Generated template has no closing html tag; append the navigation in that case.
 if 'href="report.html"'not in text:text+='<div style="position:fixed;bottom:4px;right:6px;background:#183144;padding:4px;font:12px sans-serif"><a style="color:white" href="report.html">报告</a> · <a style="color:white" href="modules.mp4">真实录像</a></div>'
 files['index.html']=text.encode()
 report=(ROOT/'DYNAMIC-REPORT.md').read_text()
 footer='\n\n[试玩](index.html) · [原生录像](modules.mp4) · [完整源码与原始实验数据]('+external['url']+')\n\n完整数据 SHA256：`'+external['sha256']+'`。包含失败批次、正式输入输出、轨迹、执行源哈希和逐文件账本。资产从固定游戏源恢复，遵循原许可证。'
 files['report.md']=(report+footer).encode();files['report.html']=page(report+footer).encode()
 for name,path in {'modules.mp4':'delivery/dynamic-v3/modules-with-sky.mp4','browser.json':'delivery/dynamic-v3/browser-release-final/browser.json','ui-summary.json':'delivery/dynamic-v3/summary-with-sky.json','metadata-correction.json':'results/dynamic-delivery-metadata/summary.json','region-input.md':'research/region-input.md','dynamic-audit.md':'research/dynamic-audit.md','sky-islands.json':'regions/sky_islands.research.json','mushroom-caverns-proposed.json':'regions/mushroom_caverns.proposed.json'}.items():files[name]=(ROOT/path).read_bytes()
 for directory in ('dynamic-search-v3','dynamic-evaluation-v1','region-sky-v1','dynamic-source-verification','region-contract-negatives'):files[directory+'.json']=(ROOT/'results'/directory/'summary.json').read_bytes()
 for folder in ('prototype/dynamic','regions'):
  for p in (ROOT/folder).glob('*'):
   if p.is_file():files[p.relative_to(ROOT).as_posix()]=p.read_bytes()
 # Render report-relative research references locally without requiring the zip.
 for name in ('dynamic-audit','region-input'):
  path='research/'+name+'.html';files[path]=page((ROOT/'research'/(name+'.md')).read_text()).encode()
 html=files['report.html'].decode().replace('research/dynamic-audit.md','research/dynamic-audit.html').replace('research/region-input.md','research/region-input.html')
 old='/gunman-rush-previews/previews/PCG-RESEARCH-02/c8b7a735ce3befc8ada013a21a6e69577443f4dc/f7ae17e42bf4/'
 for name in ('COMPOSABLE-REPORT','REPORT'):html=html.replace(name+'.md',old+name+'.html')
 html=html.replace('research/algorithms.md',old+'research/algorithms.html');files['report.html']=html.encode()
 info=dict(schema='pcg/dynamic-delivery/v3',source_commit=source,game_source_commit='12f6cb006d7119598e3235f4ca4f7323e4c9d092',build_id=build,pack=pack,pack_bytes=manifest['overlay']['bytes'],scene='res://main_v3.tscn',candidates=17,dependencies=dependencies,external_artifacts={'full_source_and_data':external},validation='real-input browser replays; no human fun/device/production approval')
 files['build-info.json']=json.dumps(info,indent=2).encode()
 files['index.cache-sw.js']=('// Integrity metadata only; no registered service worker.\nconst RESOURCE_MAP = '+json.dumps({pack:dict(sha256=manifest['overlay']['sha256'],bytes=info['pack_bytes'],chunks=[])})+';\n').encode()
 total=sum(p.stat().st_size for p in (HOST/'site').rglob('*')if p.is_file())+sum(map(len,files.values()))+32000
 if total>900*1024**2:raise RuntimeError('Unchanged 900 MiB guard exceeded')
 dest.mkdir(parents=True)
 for name,data in files.items():
  p=dest/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 url='https://zhipijun1996.github.io/gunman-rush-previews/'+rel.as_posix()+'/'
 verification=dict(source_commit=source,build_id=build,pack=pack,pack_bytes=info['pack_bytes'],pack_sha256=manifest['overlay']['sha256'],reconstructed=False,failed=0)
 receipt=dict(schema_version=1,task=TASK,source_commit=source,game_source_commit=info['game_source_commit'],build_id=build,entry='standalone-research-overlay',scene=info['scene'],url=url,pack_verification=verification,dependencies=dependencies,files={name:hashlib.sha256(data).hexdigest()for name,data in files.items()},external_artifacts=info['external_artifacts'])
 (dest/'preview.json').write_text(json.dumps(receipt,indent=2))
 index=HOST/'site/index.html';index.write_text(index.read_text()+'<p><a href="'+rel.as_posix()+'/">PCG-DYNAMIC-04 · 动态机关与区域输入生成试玩</a> · <a href="'+rel.as_posix()+'/report.html">报告、录像、数据</a></p>')
 subprocess.run([sys.executable,str(HOST/'_tools/cloud_delivery.py'),'verify-host','--host-root',str(HOST)],cwd=HOST,check=True,stdout=subprocess.DEVNULL)
 (ROOT/'delivery/dynamic-v3/staged-preview.json').write_text(json.dumps(dict(path=str(dest),url=url,source_commit=source,build_id=build,site_bytes=sum(p.stat().st_size for p in (HOST/'site').rglob('*')if p.is_file()),archive=external),indent=2));print(url)
if __name__=='__main__':stage()
