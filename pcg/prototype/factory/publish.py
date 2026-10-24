"""Package auditable factory data; stage a small immutable review portal.

Data is committed outside Pages first, then stage --data-commit pins it.
Neither command pushes or overwrites an existing published directory.
"""
import argparse,hashlib,json,os,re,shutil,subprocess,sys,zipfile
from pathlib import Path
import markdown
ROOT=Path(__file__).resolve().parents[2]
HOST=Path('/workspace/pcg-preview-host')
OUT=ROOT/'delivery/factory-v1'
WEB=OUT/'web-release'
TASK='PCG-FACTORY-05'
ASSET='pcg-factory-05-source-and-data.zip'
DATA=OUT/'data-v2'
BASE_URL='https://zhipijun1996.github.io/gunman-rush-previews/'

def sha(path):
 with Path(path).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def clean(root):
 if subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True).strip():raise ValueError('Commit existing changes before packaging/staging: '+str(root))
def source():
 clean(ROOT)
 return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
def package():
 commit=source();DATA.mkdir(exist_ok=True);archive=DATA/ASSET
 if archive.exists():raise ValueError('Refuse existing archive; keep prior evidence')
 files={ROOT/p for p in subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines()if not p.startswith('results/')}
 # One historical regression test explicitly checks this frozen failure.
 files.add(ROOT/'results/dynamic-evaluation-v1/summary.json')
 for d in (ROOT/'results').glob('factory-*'):files.update(p for p in d.rglob('*')if p.is_file())
 for d in OUT.iterdir():
  if d.is_dir()and(d.name.startswith('browser-')or d.name.startswith('web-')):
   files.update(p for p in d.rglob('*')if p.is_file())
 files.update(OUT.glob('*.log'))
 files.update((ROOT/'delivery').glob('factory-*.log'))
 files=sorted(files)
 if any(p.is_symlink()for p in files):raise ValueError('No symlinks in source archive')
 index={p.relative_to(ROOT).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p))for p in files}
 with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for p in files:z.write(p,p.relative_to(ROOT))
  z.writestr('FACTORY-SOURCE-COMMIT.txt',commit+'\n')
  z.writestr('FACTORY-ARCHIVE-FILES.json',json.dumps(index,indent=2))
 with zipfile.ZipFile(archive)as z:
  if z.testzip():raise ValueError('Archive CRC failure')
 if archive.stat().st_size>=100*1024**2:raise ValueError('Data exceeds Git file transport limit')
 prefix=f'artifacts/{TASK}/{commit}'
 parts=[]
 with archive.open('rb')as f:
  while chunk:=f.read(10*1024**2):
   p=DATA/(ASSET+f'.part{len(parts)+1:03}');p.write_bytes(chunk)
   parts.append(dict(repository_path=prefix+'/'+p.name,bytes=len(chunk),sha256=sha(p)))
 receipt=dict(source_commit=commit,bytes=archive.stat().st_size,sha256=sha(archive),files=len(files),local_path=str(archive),repository_path=prefix+'/'+ASSET,parts=parts,manifest_path=prefix+'/manifest.json',download_script_path=prefix+'/download.py')
 write(DATA/'manifest.json',{k:v for k,v in receipt.items()if k!='local_path'})
 shutil.copy2(ROOT/'prototype/factory/download_archive.py',DATA/'download.py')
 write(OUT/'archive-v2.json',receipt);print(json.dumps(receipt,indent=2))
 return receipt
def page(text):
 return '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><style>body{max-width:1050px;margin:28px auto;padding:0 18px;font:16px/1.8 system-ui;color:#183144}table{border-collapse:collapse;display:block;overflow:auto}td,th{padding:6px;border:1px solid #abc}pre{background:#eef3f6;padding:14px;overflow:auto}</style>'+markdown.markdown(text,extensions=['tables','fenced_code'])
def stage(data_commit):
 commit=source();clean(HOST)
 if not re.fullmatch('[0-9a-f]{40}',data_commit):raise ValueError('Pin a full data commit')
 receipt=json.loads((OUT/'archive-v2.json').read_text())
 if receipt['source_commit']!=commit or sha(receipt['local_path'])!=receipt['sha256']:raise ValueError('Archive/source binding changed')
 for part in receipt['parts']:
  tracked=subprocess.check_output(['git','show',data_commit+':'+part['repository_path']],cwd=HOST)
  if len(tracked)!=part['bytes']or hashlib.sha256(tracked).hexdigest()!=part['sha256']:raise ValueError('Pinned Git data bytes differ')
 external={k:v for k,v in receipt.items()if k!='local_path'}
 external['data_commit']=data_commit
 prefix=f'https://raw.githubusercontent.com/zhipijun1996/gunman-rush-previews/{data_commit}/'
 external['url']=prefix+receipt['manifest_path']
 external['download_script_url']=prefix+receipt['download_script_path']
 for part in external['parts']:part['url']=prefix+part['repository_path']
 browser=json.loads((OUT/'browser-release/browser.json').read_text())
 if browser['records'][-1].get('action')!='all_checks_passed'or browser['errors']or browser['real_human_reviews']!=0:raise ValueError('Missing clean final browser evidence')
 manifest=json.loads((WEB/'overlay-manifest.json').read_text());overlay=manifest['overlay'];build=overlay['sha256'][:12]
 if sha(WEB/overlay['pack'])!=overlay['sha256']:raise ValueError('Changed pack')
 from .core.feedback import check_catalog
 catalog=json.loads((WEB/'catalog.json').read_text());check_catalog(catalog)
 if catalog['presentation_binding']['pack_sha256']!=overlay['sha256']:raise ValueError('Presentation differs')
 for rel,h in catalog['presentation_binding']['source_files'].items():
  if sha(ROOT/rel)!=h:raise ValueError('UI source changed after browser validation: '+rel)
 dependencies={}
 for url in (manifest['base']['url'],manifest['engine']['prefix']+'.js',manifest['engine']['prefix']+'.wasm'):
  path=HOST/'site'/url.removeprefix('/gunman-rush-previews/')
  dependencies[url]=dict(bytes=path.stat().st_size,sha256=sha(path))
 if dependencies[manifest['base']['url']]['sha256']!=manifest['base']['sha256']:raise ValueError('Frozen base differs')
 files={p.relative_to(WEB).as_posix():p.read_bytes()for p in WEB.rglob('*')if p.is_file()}
 files['data.json']=json.dumps(dict(schema='pcg/factory-download/v1',full_source_and_data=external,catalog_sha256=catalog['catalog_sha256'],restoration='See README.md and source snapshots. Original assets/official Godot are pinned dependencies, not included.'),indent=2).encode()
 manifest['runtime_verified']=True;manifest['browser_evidence']='browser.json';manifest['limits']=['Four candidate witnesses plus manual-input/export UI checked in Chromium; zero human fun ratings or approvals.','Requires the hash-pinned existing base and official engine URLs.']
 files['overlay-manifest.json']=json.dumps(manifest,indent=2).encode()
 footer='\n\n[进入盲评试玩](index.html) · [网页质量档案](catalog.json) · [独立审查](factory-audit.html) · [完整源码与原始数据清单]('+external['url']+')\n\n数据按GitHub连接器大小限制分片保存，未删失败。下载[标准库合并脚本]('+external['download_script_url']+')后执行：\n\n```sh\npython3 download.py --revision '+data_commit+' --manifest-path '+receipt['manifest_path']+'\n```\n\n合并ZIP SHA256：`'+external['sha256']+'`；脚本逐片和整体核对，内含源与轨迹账本。真人反馈0，批准0。'
 report=(ROOT/'FACTORY-REPORT.md').read_text()+footer
 files['report.md']=report.encode();files['report.html']=page(report).encode()
 files['factory-audit.html']=page((ROOT/'research/factory-audit.md').read_text()).encode()
 files['browser.json']=(OUT/'browser-release/browser.json').read_bytes()
 for folder in ('factory-production-v1','factory-production-v2','factory-parent-comparison-v1','factory-feedback-loop-test-v2'):
  files[folder+'.json']=(ROOT/'results'/folder/'summary.json').read_bytes()
 info=dict(schema='pcg/factory-delivery/v1',source_commit=commit,game_source_commit='12f6cb006d7119598e3235f4ca4f7323e4c9d092',build_id=build,pack=overlay['pack'],pack_bytes=overlay['bytes'],scene='res://main_factory.tscn',candidates=4,human_feedback=0,approved_offline=0,catalog_sha256=catalog['catalog_sha256'],dependencies=dependencies,external_artifacts={'full_source_and_data':external})
 files['build-info.json']=json.dumps(info,indent=2).encode()
 files['index.cache-sw.js']=('// Integrity metadata only; no registered service worker.\nconst RESOURCE_MAP = '+json.dumps({overlay['pack']:dict(sha256=overlay['sha256'],bytes=overlay['bytes'],chunks=[])})+';\n').encode()
 rel=Path('previews')/TASK/commit/build;dest=HOST/'site'/rel
 if dest.exists():raise ValueError('Immutable destination exists')
 # Preserve a before-image of every existing site file; only add one index link.
 before={p.relative_to(HOST/'site').as_posix():sha(p)for p in(HOST/'site').rglob('*')if p.is_file()}
 amount=sum(p.stat().st_size for p in(HOST/'site').rglob('*')if p.is_file())+sum(map(len,files.values()))+32000
 if amount>900*1024**2:raise ValueError('Unchanged 900 MiB guard exceeded')
 dest.mkdir(parents=True)
 for name,data in files.items():
  p=dest/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 url=BASE_URL+rel.as_posix()+'/'
 pack_check=dict(source_commit=commit,build_id=build,pack=overlay['pack'],pack_bytes=overlay['bytes'],pack_sha256=overlay['sha256'],reconstructed=False,failed=0)
 meta=dict(schema_version=1,task=TASK,source_commit=commit,build_id=build,entry='standalone-factory-review',scene=info['scene'],url=url,pack_verification=pack_check,dependencies=dependencies,external_artifacts=info['external_artifacts'],files={name:hashlib.sha256(data).hexdigest()for name,data in files.items()})
 write(dest/'preview.json',meta)
 index=HOST/'site/index.html';index.write_text(index.read_text()+'<p><a href="'+rel.as_posix()+'/">PCG-FACTORY-05 · 离线Module生产与盲评试玩</a> · <a href="'+rel.as_posix()+'/report.html">质量、实验与数据</a></p>')
 changed=[name for name,h in before.items()if name!='index.html'and sha(HOST/'site'/name)!=h]
 if changed:raise ValueError('Existing site bytes changed: '+str(changed))
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
 check=subprocess.run([sys.executable,str(HOST/'_tools/cloud_delivery.py'),'verify-host','--host-root',str(HOST)],cwd=HOST,env=env,check=True,capture_output=True,text=True)
 (OUT/'host-verify.json').write_text(check.stdout)
 result=dict(path=str(dest),url=url,source_commit=commit,build_id=build,catalog_sha256=catalog['catalog_sha256'],site_bytes=sum(p.stat().st_size for p in(HOST/'site').rglob('*')if p.is_file()),existing_files_unchanged=len(before)-1,archive=external)
 write(OUT/'staged-preview.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('command',choices=('package','stage'));p.add_argument('--data-commit');a=p.parse_args()
 if a.command=='package':package()
 elif not a.data_commit:p.error('stage requires --data-commit')
 else:stage(a.data_commit)
