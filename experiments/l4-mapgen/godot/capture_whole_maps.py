#!/usr/bin/env python3
"""Render actual whole maps in an external game checkout, storing everything here."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
CASES = [(region, seed) for region in ['plains', 'forest', 'forest-v18'] for seed in ['00', '03', '04']]
ERRORS = re.compile(r'(?m)^ERROR:|SCRIPT ERROR:|Parse Error:|SHADER ERROR:|ObjectDB.*leaked|resources? still in use at exit')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--game', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    game = a.game.resolve()
    commit = subprocess.check_output(['git', '-C', str(game), 'rev-parse', 'HEAD'], text=True).strip()
    if subprocess.check_output(['git', '-C', str(game), 'status', '--porcelain', '--untracked-files=no'], text=True).strip():
        raise ValueError('Game input must have clean tracked files')
    a.output.mkdir(parents=True, exist_ok=True)
    report = {'schema': 'map-notes/whole-map-gallery/v1', 'source_game_commit': commit,
              'map_index': 2, 'seeds': ['l4-baseline-00', 'l4-baseline-03', 'l4-baseline-04'],
              'selection': 'Same three seeds for all profiles; cover the three existing Plains skeleton families; not a statistical sample',
              'capture_script_sha256': hashlib.sha256((ROOT / 'godot/whole_map_capture.gd').read_bytes()).hexdigest(),
              'scope': 'Actual game scene stills; only inspection camera/HUD/callbacks changed; no playability or new-algorithm integration claim',
              'cases': []}
    for label, suffix in CASES:
        folder = a.output / (label + '-' + suffix)
        if folder.exists():
            raise ValueError('Do not overwrite an existing capture: ' + str(folder))
        folder.mkdir()
        command = ['bash', str(game / 'tools/godot.sh'), '--path', str(game), '--audio-driver', 'Dummy',
                   '--resolution', '4096x2304', '--script', str(ROOT / 'godot/whole_map_capture.gd'), '--',
                   '--output-dir=' + str(folder.resolve()), '--region=' + ('plains' if label == 'plains' else 'thorn_forest'),
                   '--map=2', '--seed=l4-baseline-' + suffix]
        if label == 'forest-v18':
            command += ['--layout=forest-exploration-places-v18']
        env = {**os.environ, 'DISPLAY': os.environ.get('DISPLAY', ':99'),
               'LIBGL_ALWAYS_SOFTWARE': '1', 'OMP_NUM_THREADS': '1', 'MAP_CAPTURE_GAME_COMMIT': commit}
        started = time.monotonic()
        process = subprocess.run(command, cwd=game, env=env, capture_output=True, text=True, timeout=90)
        text = process.stdout + process.stderr
        (folder / 'native.txt').write_text(text)
        receipt = json.loads((folder / 'receipt.json').read_text()) if (folder / 'receipt.json').is_file() else {}
        valid = (process.returncode == 0 and 'WHOLE MAP CAPTURE: PASS' in text and not ERRORS.search(text)
                 and receipt.get('save_error') == 0 and receipt.get('image_size') == [4096, 2304]
                 and receipt.get('player_was_moved') is False and receipt.get('source_game_commit') == commit)
        report['cases'].append({'id': folder.name, 'path': str(folder.relative_to(a.output)), 'exit_code': process.returncode,
                                'seconds': time.monotonic() - started, 'passed': bool(valid), 'command': command,
                                'receipt': receipt})
        (a.output / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        print(folder.name, 'PASS' if valid else 'FAIL', round(time.monotonic() - started, 2), flush=True)
        if not valid:
            raise RuntimeError('Capture failed; native log and report preserved: ' + folder.name)
    report['game_tracked_clean_after'] = not subprocess.check_output(['git', '-C', str(game), 'status', '--porcelain', '--untracked-files=no'], text=True).strip()
    report['all_passed'] = all(r['passed'] for r in report['cases']) and report['game_tracked_clean_after']
    (a.output / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
