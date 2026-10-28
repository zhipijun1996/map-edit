"""Record concrete assembled-map witnesses and compare every frame to physics.

Reuses the actual native movie/trace method from pcg/tools/record_plains.py.
AVI files remain outside Git; no actor positions or resources are injected.
"""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
REPO = ROOT.parent
sys.path.insert(0, str(ROOT))
from prototype.factory.core.quality import module_hash
from prototype.factory.core.engine import ENGINE

FRAME_KEYS = ('frame', 'x', 'y', 'vx', 'vy', 'grounded', 'axis', 'requested',
    'shot_charges', 'shot_cooldown', 'jumps_used', 'jump_maximum', 'energy', 'hp',
    'traversal_state', 'real_velocity', 'normal_velocity', 'module_clock',
    'moving_platforms', 'saws', 'support_id', 'goal_stable_frames', 'hazard_contacts',
    'static_contacts', 'platform_velocity', 'actor_epoch', 'lifetime_active',
    'dead', 'damage_commits', 'damage_submissions', 'returns', 'map')


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def event_key(value):
    event = dict(value)
    # Original projectile damage sources contain process-local Godot ObjectIDs.
    # This is the same narrow normalization as the existing record_plains tool.
    if event.get('type') == 'damage' and str(event.get('source', '')).startswith('player_projectile:'):
        event['source'] = 'player_projectile:<process-object-id>'
    return event


def run(source, out, scratch, display):
    source, out, scratch = source.resolve(), out.resolve(), scratch.resolve()
    out.mkdir(parents=True, exist_ok=True)
    scratch.mkdir(parents=True, exist_ok=True)
    cases_path = source / 'replay_cases.json'
    cases = json.loads(cases_path.read_text())['cases']
    physics = source / 'whole-map-physics'
    binding = json.loads((physics / 'source_binding.json').read_text())
    for relative, expected in binding['source_files'].items():
        if relative.startswith('map_directed/godot/'):
            assert sha(ROOT / relative) == expected, ('frozen map adapter drift', relative)
    assert sha(ENGINE) == binding['engine_sha256']
    raw, raw_bindings = {}, {}
    for batch in json.loads((physics / 'batches.json').read_text()):
        blob = gzip.decompress((physics / batch['gzip_path']).read_bytes())
        assert hashlib.sha256(blob).hexdigest() == batch['raw_output_sha256']
        for result in json.loads(blob)['results']:
            raw[result['id']] = result
            raw_bindings[result['id']] = dict(file=batch['gzip_path'], raw_sha256=batch['raw_output_sha256'])
    clips = []
    for index, case in enumerate(cases):
        assert module_hash(case) == case['module_sha256']
        expected = raw[case['id']]
        assert expected['ok'] and expected['map_validation']['ok']
        avi = scratch / f'sample-{index+1:02}.avi'
        log = out / f'record-{index+1:02}.log'
        trace = out / f'native-trace-{index+1:02}.json'
        mp4 = out / f'sample-{index+1:02}.mp4'
        if any(p.exists() for p in (avi, log, trace, mp4)):
            raise ValueError('Preserve existing attempt; choose new output/scratch: ' + str(log))
        command = [str(ENGINE), '--path', str(ROOT / 'prototype/godot'),
            '--resolution', '1600x900', '--audio-driver', 'Dummy',
            '--write-movie', str(avi), '--fixed-fps', '60', '--script',
            str(ROOT / 'map_directed/godot/map_boot.gd'), '--',
            '--cases-json', str(cases_path), '--case', str(index), '--movie',
            '--trace-json', str(trace)]
        (out / f'command-{index+1:02}.json').write_text(json.dumps(command, indent=2))
        with log.open('w') as stream:
            process = subprocess.run(command, env=dict(os.environ, DISPLAY=display,
                LIBGL_ALWAYS_SOFTWARE='1'), stdout=stream, stderr=subprocess.STDOUT,
                timeout=180)
        text = log.read_text()
        failure = None
        try:
            assert process.returncode == 0, ('native exit', process.returncode, text[-3000:])
            assert all(s not in text for s in ('SCRIPT ERROR', 'ERROR:', 'were leaked')), text[-3000:]
            final = json.loads(next(line.split(' ', 1)[1] for line in text.splitlines()
                if line.startswith('MAP_NATIVE_RESULT ')))
            assert final['case_id'] == case['id'] and final['module_sha256'] == case['module_sha256']
            assert final['safe'] and final['hp'] == 5 and final['stable_frames'] >= 6
            assert final['map_validation'] == expected['map_validation']
            assert final['returns'] == len(expected['returns'])
            assert final['frame'] == len(expected['frames'])
            assert final['position'] == [expected['frames'][-1]['x'], expected['frames'][-1]['y']]
            native = json.loads(trace.read_text())
            assert native['case_id'] == case['id'] and native['module_sha256'] == case['module_sha256']
            assert len(native['frames']) == len(expected['frames'])
            for actual, original in zip(native['frames'], expected['frames']):
                for key in FRAME_KEYS:
                    assert actual[key] == original[key], (index, actual['frame'], key, actual[key], original[key])
                assert [event_key(e) for e in actual['plains']['events']] == [event_key(e) for e in original['plains']['events']]
                for key in ('bells', 'enemies', 'player_damage'):
                    assert actual['plains'][key] == original['plains'][key], (index, actual['frame'], key)
            expected_events = dict(jump=expected['jumps'], air_jump=expected['air_jumps'],
                anchor_jump=expected['anchor_jumps'], wall_jump=expected['wall_jumps'],
                shot=expected['shots'], hook_cast=expected['grapples'], hook_contact=expected['hook_contacts'])
            assert final['events'] == expected_events
            assert [event_key(e) for e in final['plains']['events']] == [event_key(e) for e in expected['plains']['events']]
        except (AssertionError, StopIteration, KeyError) as error:
            failure = repr(error)
            (out / f'failure-{index+1:02}.json').write_text(json.dumps(dict(case_id=case['id'],
                error=failure, native_exit=process.returncode, preserved_movie=str(avi),
                log=log.name, trace=trace.name, source_binding_sha256=sha(physics/'source_binding.json')), indent=2))
            raise
        with (out / f'encode-{index+1:02}.log').open('w') as stream:
            subprocess.run(['ffmpeg', '-nostdin', '-i', str(avi), '-an', '-c:v', 'libx264',
                '-preset', 'medium', '-crf', '24', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
                str(mp4)], stdout=stream, stderr=subprocess.STDOUT, check=True)
        probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_format',
            '-show_streams', '-of', 'json', str(mp4)]))
        assert probe['streams'][0]['avg_frame_rate'] == '60/1'
        clips.append(dict(id=case['id'], route=case['map_semantics']['route_id'], file=mp4.name,
            bytes=mp4.stat().st_size, sha256=sha(mp4), duration=float(probe['format']['duration']),
            module_sha256=case['module_sha256'], map_geometry_sha256=case['map_semantics']['geometry_sha256'],
            actual_result=final, native_trace=dict(file=trace.name, bytes=trace.stat().st_size,
                sha256=sha(trace), frames=len(native['frames']), exact_fields=list(FRAME_KEYS),
                maximum_position_error=0, all_cell_events_and_states_match=True),
            physics_evidence=raw_bindings[case['id']], source_binding_sha256=sha(physics/'source_binding.json')))
        (out / 'partial-receipt.json').write_text(json.dumps(dict(clips=clips, status='in_progress'), indent=2))
        print(json.dumps(dict(case_id=case['id'], frames=len(native['frames']),
            exact_match=True, file=str(mp4))), flush=True)
    concat = scratch / 'concat.txt'
    concat.write_text(''.join("file '" + str(out/c['file']) + "'\n" for c in clips))
    combined = out / 'all-routes.mp4'
    with (out / 'concat.log').open('w') as stream:
        subprocess.run(['ffmpeg', '-nostdin', '-f', 'concat', '-safe', '0', '-i', str(concat),
            '-c', 'copy', '-movflags', '+faststart', str(combined)], stdout=stream,
            stderr=subprocess.STDOUT, check=True)
    files = [Path(__file__)] + list((ROOT/'map_directed/godot').glob('*.gd'))
    files += [ROOT/'prototype/godot'/name for name in ('main_plains.gd', 'plains_cells.gd',
        'dynamic_context.gd', 'lab_draw_v3.gd', 'plains_lifecycle.gd')]
    manifest = dict(schema='pcg/map-native-media/v1', status='passed', physics_hz=60,
        playback_speed=1, source_game_commit=binding['game_source_commit'], engine_sha256=sha(ENGINE),
        cases_sha256=sha(cases_path), physics_source_binding_sha256=sha(physics/'source_binding.json'),
        source_files={str(p.relative_to(ROOT)):sha(p) for p in files}, clips=clips,
        combined=dict(file=combined.name, bytes=combined.stat().st_size, sha256=sha(combined)),
        whole_map=dict(file='whole-map.png', sha256=sha(out/'whole-map.png')),
        human_playtests=0, human_fun_approval='unverified', end_hold_seconds=1,
        scope='Actual GUI Godot / llvmpipe native 60Hz playback. Each complete route followed by one second frozen completion; combined file concatenates these complete clips. Exact per-frame comparison to the same concrete map physics; not formal game, universal transfer, real-time performance or human fun admission.')
    (out/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    print(json.dumps(dict(status='passed', clips=len(clips), frames=sum(c['native_trace']['frames'] for c in clips), combined=str(combined))), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', default='pcg/results/map-directed-loop-v2')
    parser.add_argument('--out', default='generation/maps/map-directed-loop-v1')
    parser.add_argument('--scratch', default='/workspace/scratch/maploop-movies')
    parser.add_argument('--display', default=':103')
    args = parser.parse_args()
    run(REPO/args.source, REPO/args.out, Path(args.scratch), args.display)
