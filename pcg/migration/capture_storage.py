"""Losslessly archive ignored AVI intermediates, preserving exact recovery bytes."""
import argparse,hashlib,json,lzma,os,shutil,subprocess
from pathlib import Path
from . import core

ROOT=core.REPO/'pcg/results/foundation-migration-capture-storage-v1'


def decoded_sha(path):
    digest=hashlib.sha256();size=0
    with lzma.open(path,'rb')as stream:
        while data:=stream.read(1024*1024):digest.update(data);size+=len(data)
    return digest.hexdigest(),size


def save_index(path,value):
    temporary=path.with_suffix('.json.partial')
    with temporary.open('w')as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2);stream.flush();os.fsync(stream.fileno())
    os.replace(temporary,path)


def compact():
    ROOT.mkdir(parents=True,exist_ok=True);index_file=ROOT/'index.json'
    index=core.read(index_file)if index_file.exists()else dict(schema='pcg/lossless-avi-storage/v1',files={},policy='Exact original capture bytes, no video re-encoding; source traces, MP4s, current modules and failures untouched.')
    files=sorted((p for root in ('generation','pcg')for p in(core.REPO/root).rglob('*.avi')),key=lambda p:-p.stat().st_size)
    for source in files:
        relative=core.relative(source)
        if subprocess.run(['git','check-ignore','-q','--',relative],cwd=core.REPO).returncode:continue
        before=source.stat();checksum=core.sha(source);target=ROOT/'objects'/(checksum+'.avi.xz')
        target.parent.mkdir(exist_ok=True)
        if not target.exists():
            temporary=target.with_suffix('.xz.partial')
            with source.open('rb')as incoming,temporary.open('xb')as outgoing:
                with lzma.LZMAFile(outgoing,'w',preset=6)as compressed:shutil.copyfileobj(incoming,compressed,1024*1024)
            if decoded_sha(temporary)!=(checksum,before.st_size):raise ValueError('lossless_capture_verification_failed')
            temporary.rename(target)
        if decoded_sha(target)!=(checksum,before.st_size)or core.sha(source)!=checksum:raise ValueError('capture_changed_or_corrupt')
        index['files'][relative]=dict(sha256=checksum,bytes=before.st_size,compressed=dict(path=core.relative(target),sha256=core.sha(target),bytes=target.stat().st_size),originalPathRecoverable=True)
        save_index(index_file,index)
        source.unlink()
        print(json.dumps(dict(path=relative,originalBytes=before.st_size,retainedBytes=target.stat().st_size,verifiedLossless=True)),flush=True)
    return dict(files=len(index['files']),originalBytes=sum(v['bytes']for v in index['files'].values()),retainedBytes=sum(v['compressed']['bytes']for v in index['files'].values()))


def restore(relative):
    target=(core.REPO/relative).resolve()
    if not target.is_relative_to(core.REPO)or target.suffix!='.avi':raise ValueError('restore_only_original_repo_avi')
    entry=core.read(ROOT/'index.json')['files'][relative]
    if target.exists():
        if core.sha(target)!=entry['sha256']:raise ValueError('existing_capture_differs_preserved')
        return dict(status='already_present',path=relative)
    source=core.REPO/entry['compressed']['path'];core.verify_artifacts([entry['compressed']])
    if decoded_sha(source)!=(entry['sha256'],entry['bytes']):raise ValueError('lossless_capture_corrupt')
    target.parent.mkdir(parents=True,exist_ok=True);temporary=target.with_suffix('.avi.partial')
    with lzma.open(source,'rb')as incoming,temporary.open('xb')as outgoing:shutil.copyfileobj(incoming,outgoing,1024*1024)
    if core.sha(temporary)!=entry['sha256']:raise ValueError('restored_capture_corrupt')
    temporary.rename(target);return dict(status='restored_exact_bytes',path=relative,sha256=entry['sha256'])


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--restore');args=parser.parse_args()
    print(json.dumps(restore(args.restore)if args.restore else compact()))
