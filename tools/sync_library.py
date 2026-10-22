"""Generate a new library only after immutable download, Godot extraction and checks."""
import argparse
import pathlib
import subprocess
import sys
import tempfile
from snapshot_source import snapshot

ROOT=pathlib.Path(__file__).resolve().parents[1]

def run(args,cwd=ROOT,marker=None):
    result=subprocess.run(args,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=240)
    print(result.stdout,flush=True)
    if result.returncode or 'SCRIPT ERROR:' in result.stdout or 'Parse Error:' in result.stdout or (marker and marker not in result.stdout):
        raise RuntimeError('Library sync stopped: '+str(args[0]))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--ref',default='main');parser.add_argument('--godot',required=True)
    args=parser.parse_args();engine=str(pathlib.Path(args.godot).resolve())
    commit=snapshot(args.ref)
    with tempfile.TemporaryDirectory(prefix='map-notes-extract-') as tmp:
        run([sys.executable,'tools/prepare_extraction.py',tmp])
        run([engine,'--headless','--editor','--path',tmp,'--import'])
        run([engine,'--headless','--path',tmp,'--script','extract_modules.gd'],marker='EXTRACTION_OK')
        run([sys.executable,'tools/build_library.py',str(pathlib.Path(tmp)/'extracted.json')])
    run(['npm','run','check'])
    print('LIBRARY_SYNC_OK '+commit)
