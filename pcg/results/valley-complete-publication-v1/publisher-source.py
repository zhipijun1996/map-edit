import base64,concurrent.futures,hashlib,json,subprocess,tempfile,shutil
from pathlib import Path
REPO='zhipijun1996/gunman-rush-previews'
ROOT=Path('/workspace/map-edit');SCRATCH=Path('/workspace/scratch');SOURCE='359e3f5963b6e925809d907bb059d28068580785';TASK='MAPGEN-VALLEY-02'
manifest=json.loads((SCRATCH/'valley-complete-web-v3/overlay-manifest.json').read_text());BUILD=manifest['overlay']['sha256'][:12]

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

stage=SCRATCH/'valley-complete-public-assets-v1';stage.mkdir()
media=ROOT/'generation/maps/valley-complete-v1'
for p in media.iterdir():
 if p.is_file()and p.suffix in ['.png','.mp4','.svg','.json']:shutil.copy2(p,stage/p.name)
packname='index.'+BUILD+'.pck';shutil.copy2(SCRATCH/'valley-complete-web-v3'/manifest['overlay']['pack'],stage/packname)
shutil.copy2(SCRATCH/'valley-complete-web-v3/overlay-manifest.json',stage/'overlay-manifest.json')
(stage/'build-info.json').write_text(json.dumps(dict(schema='pcg/direct-module-public-build/v1',task=TASK,source_commit=SOURCE,build_id=BUILD,scope='8 source-owned landforms, 3 treasure chests, aerial carrier parking, enemy refund relay and original shop, fixed small region'),indent=2)+'\n')
assets=publish(stage,'artifacts/'+TASK+'/'+SOURCE+'/'+BUILD,'Add open valley recoil map and exact native route videos [skip ci]',SCRATCH/'valley-complete-asset-publication-v1.json')
assetbase='https://raw.githubusercontent.com/'+REPO+'/'+assets['host_commit']+'/artifacts/'+TASK+'/'+SOURCE+'/'+BUILD
from pcg.map_directed.thin_preview import build
thin=SCRATCH/'valley-complete-public-thin-v1';build(SCRATCH/'valley-complete-web-v3',assetbase,thin)
report=(media/'report.html').read_text()
for p in stage.iterdir():
 report=report.replace('"'+p.name+'"','"'+assetbase+'/'+p.name+'"')
(thin/'report.html').write_text(report)
url='https://zhipijun1996.github.io/gunman-rush-previews/launchers/'+TASK+'/'+SOURCE+'/'+BUILD+'/'
remote=dict(schema='pcg/immutable-external-preview/v1',task=TASK,source_repository='zhipijun1996/map-edit',source_commit=SOURCE,build_id=BUILD,url=url,asset_commit=assets['host_commit'],asset_base=assetbase,
 pack=dict(pack=packname,pack_bytes=manifest['overlay']['bytes'],pack_sha256=manifest['overlay']['sha256'],reconstructed=False,failed=0),external_files=assets['files'],human_fun='unverified',production_admitted=False)
(thin/'remote-preview.json').write_text(json.dumps(remote,ensure_ascii=False,indent=2)+'\n')
added=sum(p.stat().st_size for p in thin.iterdir()if p.is_file())
if added>50000:raise ValueError('thin_launcher_budget_exceeded')
result=publish(thin,'site/launchers/'+TASK+'/'+SOURCE+'/'+BUILD,'Publish open valley recoil map and short native videos',SCRATCH/'valley-complete-thin-publication-v1.json')
result.update(url=url,asset_commit=assets['host_commit'],asset_base=assetbase,site_added_bytes=added,site_cap=900*1024*1024,site_cap_authority='existing unchanged deployment CI includes reconstructed files')
(SCRATCH/'valley-complete-publication-v1.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:result[k]for k in ['host_commit','asset_commit','url','asset_base','site_added_bytes']},ensure_ascii=False),flush=True)
