import base64,concurrent.futures,hashlib,json,subprocess,tempfile,shutil
from pathlib import Path
REPO='zhipijun1996/gunman-rush-previews'
ROOT=Path('/workspace/map-edit');SCRATCH=Path('/workspace/scratch');SOURCE='d3e29ca31ba1dcaa304a9ccf745b3455d563cb73';TASK='MAPGEN-R2-FULL-01'
manifest=json.loads((SCRATCH/'r2-web-v3/overlay-manifest.json').read_text());BUILD=manifest['overlay']['sha256'][:12]

def api(endpoint,payload=None):
 args=['gh','api','repos/'+REPO+'/'+endpoint]
 if payload is not None:
  with tempfile.NamedTemporaryFile(mode='w',suffix='.json',delete=False)as f:json.dump(payload,f);name=f.name
  try:result=subprocess.check_output(args+['--method','PATCH'if endpoint.startswith('git/refs/')else'POST','--input',name])
  finally:Path(name).unlink()
 else:result=subprocess.check_output(args)
 return json.loads(result)

def publish(folder,prefix,message,receipt):
 head=api('git/ref/heads/main')['object']['sha'];base=api('git/commits/'+head)['tree']['sha']
 old=api('git/trees/'+base+'?recursive=1');known={item['path']for item in old['tree']}
 files=[p for p in sorted(folder.iterdir())if p.is_file()]
 if any(prefix+'/'+p.name in known for p in files):raise ValueError('immutable_published_path_already_exists')
 def upload(p):
  data=p.read_bytes();expected=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
  response=api('git/blobs',dict(content=base64.b64encode(data).decode(),encoding='base64'))
  if response['sha']!=expected:raise ValueError('uploaded_git_blob_identity_mismatch')
  return dict(path=prefix+'/'+p.name,mode='100644',type='blob',sha=response['sha'])
 with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:entries=list(pool.map(upload,files))
 tree=api('git/trees',dict(base_tree=base,tree=entries))['sha']
 commit=api('git/commits',dict(message=message,tree=tree,parents=[head]))['sha']
 api('git/refs/heads/main',dict(sha=commit,force=False))
 result=dict(previous_host_commit=head,host_commit=commit,tree=tree,source_commit=SOURCE,build_id=BUILD,
             prefix=prefix,added_files=entries,added_bytes=sum(p.stat().st_size for p in files),old_files_modified=0,
             files={p.name:dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())for p in files})
 receipt.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');return result

stage=SCRATCH/'r2-public-assets-v1';stage.mkdir()
media=ROOT/'generation/maps/r2-full-v2'
for p in media.iterdir():
 if p.is_file()and p.suffix in ['.png','.mp4','.svg','.json']:shutil.copy2(p,stage/p.name)
packname='index.'+BUILD+'.pck';shutil.copy2(SCRATCH/'r2-web-v3'/manifest['overlay']['pack'],stage/packname)
shutil.copy2(SCRATCH/'r2-web-v3/overlay-manifest.json',stage/'overlay-manifest.json')
info={'schema':'pcg/r2-full-public-build/v1','task':TASK,'source_repository':'zhipijun1996/map-edit','source_commit':SOURCE,'build_id':BUILD,'pack':packname,'pack_sha256':manifest['overlay']['sha256'],'pack_bytes':manifest['overlay']['bytes'],'scope':'Full original R2 map, real manual Godot consumer, technical candidate, no production or human fun approval'}
(stage/'build-info.json').write_text(json.dumps(info,indent=2)+'\n')
assets=publish(stage,'artifacts/'+TASK+'/'+SOURCE+'/'+BUILD,'Add complete R2 map binary and native loop media [skip ci]',SCRATCH/'r2-asset-publication-v1.json')
assetbase='https://raw.githubusercontent.com/'+REPO+'/'+assets['host_commit']+'/artifacts/'+TASK+'/'+SOURCE+'/'+BUILD
from pcg.map_directed.thin_preview import build
thin=SCRATCH/'r2-public-thin-v1';build(SCRATCH/'r2-web-v3',assetbase,thin)
for name in ['whole-map.png','original-r2-layout.svg','manifest.json','validation-summary.json','library-reuse-geometry.json']:
 shutil.copy2(media/name,thin/name)
report=(media/'report.html').read_text()
for name in ['lower-loop.mp4','upper-loop.mp4','bell-expedition-excerpt.mp4','bell-expedition-full.mp4']:
 report=report.replace('"'+name+'"','"'+assetbase+'/'+name+'"')
(thin/'report.html').write_text(report)
url='https://zhipijun1996.github.io/gunman-rush-previews/launchers/'+TASK+'/'+SOURCE+'/'+BUILD+'/'
remote=dict(schema='pcg/immutable-external-preview/v1',task=TASK,source_repository='zhipijun1996/map-edit',source_commit=SOURCE,build_id=BUILD,url=url,asset_commit=assets['host_commit'],asset_base=assetbase,
 pack=dict(pack=packname,pack_bytes=manifest['overlay']['bytes'],pack_sha256=manifest['overlay']['sha256'],reconstructed=False,failed=0),
 external_files=assets['files'],transport='Official Engine init/preloadFile/start; full external PCK bytes and SHA256 checked before startup',human_fun='unverified',production_admitted=False)
(thin/'remote-preview.json').write_text(json.dumps(remote,ensure_ascii=False,indent=2)+'\n')
head=api('git/ref/heads/main')['object']['sha'];tree=api('git/trees/'+api('git/commits/'+head)['tree']['sha']+'?recursive=1')
site_bytes=sum(item.get('size',0)for item in tree['tree']if item['type']=='blob'and item['path'].startswith('site/'))
added=sum(p.stat().st_size for p in thin.iterdir()if p.is_file())
if site_bytes+added>900*1024*1024:raise ValueError('existing_site_cap_would_be_exceeded')
result=publish(thin,'site/launchers/'+TASK+'/'+SOURCE+'/'+BUILD,'Publish complete R2 map with immutable native loop videos',SCRATCH/'r2-thin-publication-v1.json')
result.update(url=url,asset_commit=assets['host_commit'],asset_base=assetbase,site_before=site_bytes,site_after=site_bytes+added,site_cap=900*1024*1024)
(SCRATCH/'r2-publication-v1.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:result[k]for k in ['host_commit','asset_commit','url','asset_base','site_after','site_cap']},ensure_ascii=False),flush=True)
