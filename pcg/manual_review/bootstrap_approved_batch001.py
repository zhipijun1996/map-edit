"""Install hash-verified existing resources and the pinned official engine.

Run from a complete checkout. No game files, tuning or import caches are committed.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from pcg.migration import core
from pcg.tools.restore_archive import restore

ENGINE_NAME='Godot_v4.7.2-stable_linux.x86_64'
ENGINE_SHA='8d106cbe6144c2dc7e881d61d2429c1a8a76e6b22ef48bd5e48dcf934953f71e'
ZIP_SHA='cadd3204e728a35d3f13adb7fd0d7902636b79f6b95c40c265eb73b6c35329e4'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--authoring',action='store_true',help='Also restore feedback-001 inputs and the historical Harness path alias')
    args=p.parse_args()
    restore('godot-runtime-v1',extract=True,prefix='prototype/godot/')
    additions=core.read(core.REPO/'pcg/research/plains-runtime-additions.json')
    for name,binding in additions['files'].items():
        target=core.REPO/'pcg/prototype/godot'/name
        if target.exists():
            if core.sha(target)!=binding['sha256']:raise ValueError('existing_additional_resource_changed:'+name)
            continue
        target.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory() as temp:
            downloaded=Path(temp)/'resource'
            subprocess.run(['curl','-fsSL','https://raw.githubusercontent.com/zhipijun1996/gunman-rush/'+additions['source_commit']+'/'+name,'-o',str(downloaded)],check=True)
            if core.sha(downloaded)!=binding['sha256']:raise ValueError('downloaded_resource_checksum_mismatch:'+name)
            shutil.copyfile(downloaded,target)
    engine=core.REPO/'pcg/toolchain'/ENGINE_NAME
    if engine.exists():
        if core.sha(engine)!=ENGINE_SHA:raise ValueError('existing_engine_checksum_mismatch')
    else:
        engine.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory() as temp:
            archive=Path(temp)/'godot.zip'
            subprocess.run(['curl','-fsSL','https://github.com/godotengine/godot/releases/download/4.7.2-stable/'+ENGINE_NAME+'.zip','-o',str(archive)],check=True)
            if core.sha(archive)!=ZIP_SHA:raise ValueError('official_engine_zip_checksum_mismatch')
            with zipfile.ZipFile(archive) as z:engine.write_bytes(z.read(ENGINE_NAME))
        engine.chmod(0o755)
        if core.sha(engine)!=ENGINE_SHA:raise ValueError('engine_checksum_mismatch')
    if args.authoring:
        restore('manual-review-batch001-feedback001-v1',extract=True)
        from pcg.migration import physics
        for row in core.read(core.REPO/'feedback/manual-review/implementation-results/batch-001/authorization/handoff-v1.json')['rows']:
            cases=core.read(core.REPO/row['outputDirectory']/'cases.json')['cases']
            for source in physics.author_sources([physics.author_for(c) for c in cases]):
                if source.exists():continue
                relative=source.relative_to(core.REPO/'pcg')
                matches=list((core.REPO/'pcg/results').glob('manual-review-*/source_snapshot/'+relative.as_posix()))
                if not matches or len({core.sha(m) for m in matches})!=1:raise ValueError('missing_or_ambiguous_frozen_author_dependency:'+str(source))
                source.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(matches[0],source)
        alias=Path('/workspace/map-edit-task-a')
        if alias.exists() or alias.is_symlink():
            if alias.resolve()!=core.REPO:raise ValueError('historical_Harness_path_already_used:'+str(alias))
        else:alias.symlink_to(core.REPO,target_is_directory=True)
    subprocess.run([str(engine),'--headless','--editor','--path',str(core.REPO/'pcg/prototype/godot'),'--import'],check=True)
    print('Pinned Godot 4.7.2 and original resources verified. Samples are ready.')


if __name__=='__main__':main()
