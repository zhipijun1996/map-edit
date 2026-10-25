"""Publish immutable large assets and a thin report through the existing host.

Uses gh's configured identity for local binary blobs (connector has no local-file
stream input). No old paths are changed; all byte hashes and commits are saved.
"""
import argparse,base64,concurrent.futures,hashlib,json,shutil,subprocess,tempfile
from pathlib import Path
from pcg.map_directed.director import REPO
from pcg.map_directed.run import write
from pcg.map_directed.thin_preview import build as thin_build
from pcg.prototype.factory.core.engine import file_sha

HOST='zhipijun1996/gunman-rush-previews'
TASK='MAPGEN-WOVEN-REGION-01'


def api(endpoint,payload=None):
    args=['gh','api','repos/'+HOST+'/'+endpoint]
    if payload is None:return json.loads(subprocess.check_output(args))
    with tempfile.NamedTemporaryFile(mode='w',suffix='.json',delete=False)as f:json.dump(payload,f);name=f.name
    try:return json.loads(subprocess.check_output(args+['--method','PATCH'if endpoint.startswith('git/refs/')else'POST','--input',name]))
    finally:Path(name).unlink()


def publish(folder,prefix,message,receipt):
    folder=Path(folder);receipt=Path(receipt)
    head=api('git/ref/heads/main')['object']['sha'];base=api('git/commits/'+head)['tree']['sha'];tree=api('git/trees/'+base+'?recursive=1')
    if tree.get('truncated'):raise ValueError('cannot_check_immutable_prefix_on_truncated_tree')
    known={v['path']for v in tree['tree']};files=[p for p in sorted(folder.iterdir())if p.is_file()]
    if any(prefix+'/'+p.name in known for p in files):raise ValueError('immutable_published_path_exists')
    upload_receipt=receipt.with_suffix('.uploads.json')
    entries=json.loads(upload_receipt.read_text())if upload_receipt.exists()else[]
    done={v['path']:v for v in entries}
    def upload(p):
        data=p.read_bytes();expected=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();path=prefix+'/'+p.name
        if path in done:
            if done[path]['sha']!=expected:raise ValueError('resumed_blob_bytes_changed')
            return done[path]
        response=api('git/blobs',dict(content=base64.b64encode(data).decode(),encoding='base64'))
        if response['sha']!=expected:raise ValueError('uploaded_git_blob_identity_mismatch')
        return dict(path=path,mode='100644',type='blob',sha=response['sha'])
    entries=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:
        jobs={pool.submit(upload,p):p for p in files}
        for job in concurrent.futures.as_completed(jobs):
            entry=job.result();entries.append(entry);write(upload_receipt,entries)
            print('BLOB_VERIFIED',jobs[job].name,flush=True)
    newtree=api('git/trees',dict(base_tree=base,tree=entries))['sha']
    commit=api('git/commits',dict(message=message,tree=newtree,parents=[head]))['sha']
    write(receipt.with_suffix('.pending.json'),dict(expected_head=head,commit=commit,tree=newtree))
    api('git/refs/heads/main',dict(sha=commit,force=False))
    result=dict(previous_host_commit=head,host_commit=commit,tree=newtree,prefix=prefix,old_files_modified=0,
        added_bytes=sum(p.stat().st_size for p in files),files={p.name:dict(bytes=p.stat().st_size,sha256=file_sha(p))for p in files})
    write(receipt,result);return result


def run(play,media,out):
    play=Path(play).resolve();media=Path(media).resolve();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    if(out/'publication.json').exists():raise ValueError('immutable_publication_exists')
    source=json.loads((media/'results.json').read_text())['source_commit'];manifest=json.loads((play/'overlay-manifest.json').read_text());build=manifest['overlay']['sha256'][:12]
    stage=out/'assets';stage.mkdir(exist_ok=True)
    for p in media.iterdir():
        if p.is_file()and p.suffix in ['.png','.mp4','.svg','.json']:shutil.copy2(p,stage/p.name)
    packname='index.'+build+'.pck';shutil.copy2(play/manifest['overlay']['pack'],stage/packname)
    shutil.copy2(play/'overlay-manifest.json',stage/'overlay-manifest.json')
    write(stage/'build-info.json',dict(task=TASK,source_commit=source,build_id=build,case_sha256=file_sha(REPO/'pcg/results/woven-release-v1/cases.json'),
        compiled_sha256=file_sha(REPO/'pcg/results/woven-release-v1/compiled.json'),scope='One R2-driven 19-Macro whole map; 25 frozen + 13 warm + 4 paired real routes; 4 failed bypass counterfactuals; no Boss/campaign/human fun/production admission'))
    if(out/'assets-publication.json').exists():assets=json.loads((out/'assets-publication.json').read_text())
    else:assets=publish(stage,'artifacts/'+TASK+'/'+source+'/'+build,'Archive woven-region map and exact native replay evidence [skip ci]',out/'assets-publication.json')
    assetbase='https://raw.githubusercontent.com/'+HOST+'/'+assets['host_commit']+'/artifacts/'+TASK+'/'+source+'/'+build
    thin=out/'thin';thin_build(play,assetbase,thin)
    report=(media/'report.html').read_text()
    for p in stage.iterdir():report=report.replace('"'+p.name+'"','"'+assetbase+'/'+p.name+'"')
    (thin/'report.html').write_text(report)
    url='https://zhipijun1996.github.io/gunman-rush-previews/launchers/'+TASK+'/'+source+'/'+build+'/'
    write(thin/'remote-preview.json',dict(schema='pcg/immutable-external-preview/v1',task=TASK,source_repository='zhipijun1996/map-edit',source_commit=source,build_id=build,
        url=url,asset_commit=assets['host_commit'],asset_base=assetbase,pack=dict(file=packname,sha256=manifest['overlay']['sha256'],bytes=manifest['overlay']['bytes']),
        external_files=assets['files'],production_admitted=False,human_fun='unreviewed'))
    size=sum(p.stat().st_size for p in thin.iterdir()if p.is_file())
    if size>50000:raise ValueError('thin_launcher_budget_exceeded')
    launcher=publish(thin,'site/launchers/'+TASK+'/'+source+'/'+build,'Publish R2-driven whole-map report and manual playable preview',out/'thin-publication.json')
    result=dict(**launcher,source_commit=source,build_id=build,url=url,asset_base=assetbase,asset_commit=assets['host_commit'],site_added_bytes=size)
    write(out/'publication.json',result);print(json.dumps(result,ensure_ascii=False),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--play',required=True);p.add_argument('--media',required=True);p.add_argument('--out',required=True);a=p.parse_args();run(a.play,a.media,a.out)
