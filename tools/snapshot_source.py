"""Refresh the authoring snapshot from ONE immutable public game commit.

Download into a staging directory; never mix old and new source files. No secrets
are written to the snapshot. GITHUB_TOKEN, when present, is used for API reads only.
"""
import argparse
import concurrent.futures
import hashlib
import json
import os
import pathlib
import re
import shutil
import tempfile
import time
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = 'zhipijun1996/gunman-rush'
EXTRA_PATHS = [
    'project.godot','scenes/demo/demo.tscn','scripts/player/player_tuning.gd',
    'scripts/player/traversal_definition.gd','scripts/enemies/enemy_definition.gd',
    'scripts/enemies/forest_enemy_definition.gd','scripts/resources/definitions/health_definition.gd',
    'resources/enemies/forest_swing_pod.tres','resources/enemies/patrol_health.tres',
    'resources/player/traversal.tres','resources/foundry/batch.json',
    'config/platforming_foundry.json','config/foundry_capabilities.json','config/plains_shot_latches.json',
    'scripts/demo/demo_app.gd','scripts/ui/demo_menu.gd','scripts/demo/foundry_lab.gd',
    'scripts/demo/module_lab.gd','scripts/demo/forest_exploration_place_lab.gd',
    'scripts/demo/forest_varied_module_golden.gd',
]

def get(url):
    headers={'User-Agent':'Map-Notes-library-sync','Accept':'application/vnd.github+json'}
    token=os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if token and url.startswith('https://api.github.com/'):
        headers['Authorization']='Bearer '+token
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=45) as response:
                return response.read()
        except Exception:
            if attempt==2: raise
            time.sleep(1+attempt)

def api(path):
    return json.loads(get('https://api.github.com/repos/'+REPO+'/'+path))

def snapshot(ref):
    commit=api('commits/'+urllib.parse.quote(ref,safe=''))['sha']
    modules=api('contents/resources/generation/modules?ref='+commit)
    generation=api('contents/scripts/generation?ref='+commit)
    rows=[r for r in modules if r['name'].endswith('.tres')]
    rows += [r for r in generation if r['name'].endswith('.gd')]
    expected={r['path']:r['sha'] for r in rows}
    paths=set(expected)|set(EXTRA_PATHS)
    with tempfile.TemporaryDirectory(prefix='map-notes-source-') as tmp:
        stage=pathlib.Path(tmp)/'source';stage.mkdir()
        def download(path):
            if pathlib.PurePosixPath(path).is_absolute() or '..' in pathlib.PurePosixPath(path).parts:
                raise ValueError('Invalid repository path')
            data=get('https://raw.githubusercontent.com/'+REPO+'/'+commit+'/'+path)
            if path in expected:
                git_hash=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
                if git_hash!=expected[path]:raise ValueError('Source blob mismatch: '+path)
            out=stage/path;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            list(pool.map(download,sorted(paths)))
        scene_refs=set()
        for path in ['project.godot','scripts/demo/module_lab.gd']:
            scene_refs.update(re.findall(r'res://(scenes/[^"\s]+\.tscn)',(stage/path).read_text()))
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            list(pool.map(download,sorted(scene_refs-paths)))
        (stage/'module-index.json').write_text(json.dumps([r for r in modules if r['name'].endswith('.tres')],ensure_ascii=False,indent=2))
        (stage/'generation-index.json').write_text(json.dumps(generation,ensure_ascii=False,indent=2))
        destination=ROOT/'library/source'
        if destination.exists():shutil.rmtree(destination)
        shutil.copytree(stage,destination)
    (ROOT/'library/source-commit.txt').write_text(commit+'\n')
    print(f'SOURCE_SNAPSHOT_OK {commit} ({len(paths)} files)')
    return commit

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--ref',default='main')
    snapshot(parser.parse_args().ref)
