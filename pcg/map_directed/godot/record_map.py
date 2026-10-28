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
import re
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
BODY_SCENE = ROOT / 'prototype/godot/scenes/player/player.tscn'
BODY_SIZE = tuple(float(v) for v in re.search(r'size = Vector2\(([^,]+),\s*([^\)]+)\)',
    BODY_SCENE.read_text()).groups())


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


def equivalent_support(actual, original, state, case, frames):
    """Only simultaneous coplanar static contacts at an explicit map seam.

    move_and_slide reports contacts during the step, so use the actual complete
    body sweep from the previous frame, not merely the final body center.
    """
    if not state or not state.get('grounded'):
        return None
    names = [re.fullmatch(r'Platform(\d+)', value) for value in (actual, original)]
    if not all(names):
        return None
    indices = [int(m.group(1)) for m in names]
    platforms = case['platforms']
    if any(i >= len(platforms) or i in case.get('one_way_platform_indices', []) for i in indices):
        return None
    first, second = [platforms[i] for i in indices]
    left, right = sorted((first, second), key=lambda r:r[0])
    if abs(left[1] - right[1]) > 1e-7 or abs(left[0] + left[2] - right[0]) > 1e-7:
        return None
    index = int(state['frame'])
    point = state.get('position', [state.get('x'), state.get('y')])
    previous = frames.get(index-1, state)
    prior = previous.get('position', [previous.get('x'), previous.get('y')])
    if None in point or None in prior or not previous.get('grounded'):
        return None
    half_x, half_y = BODY_SIZE[0]/2, BODY_SIZE[1]/2
    # Original safe-margin resting contact is about 0.075 world units above top.
    distances = [abs(p[1]+half_y-left[1]) for p in (point, prior)]
    if max(distances) > .1:
        return None
    seam_x = right[0]
    body_sweep = [min(point[0],prior[0])-half_x, max(point[0],prior[0])+half_x]
    if not body_sweep[0] < seam_x < body_sweep[1]:
        return None
    for seam in case['map_semantics']['seams']:
        x,y,w,h = seam['region']
        crossing_x = seam.get('crossing_x', x+w/2)
        if abs(crossing_x-seam_x) <= 1e-7 and x <= point[0] <= x+w and y <= point[1] <= y+h:
            return dict(frame=index, seam_id=seam['id'], original_support=original,
                native_support=actual, platform_indices=indices, platform_rectangles=[first,second],
                body_size=list(BODY_SIZE), previous_center=prior, current_center=point,
                actual_body_sweep_x=body_sweep, top_contact_distances=distances,
                criterion='explicit seam, coplanar contiguous static supports, actual adjacent-frame full-body sweep contacts both')
    return None


def assert_equivalent(actual, original, case, frames, normalizations, path='', state=None):
    if actual == original:
        return
    if path.endswith('/support_id'):
        accepted = equivalent_support(actual, original, state, case, frames)
        assert accepted is not None, (path, actual, original, 'not geometrically equivalent')
        accepted['field_path'] = path
        normalizations.append(accepted)
        return
    if isinstance(actual, dict) and isinstance(original, dict):
        assert actual.keys() == original.keys(), (path, 'dictionary keys')
        if 'frame' in actual and ('position' in actual or 'x' in actual):
            state = actual
        for key in actual:
            if actual[key] == original[key]:
                continue
            if key == 'support_id':
                accepted = equivalent_support(actual[key], original[key], state, case, frames)
                assert accepted is not None, (path, key, actual[key], original[key], 'not geometrically equivalent')
                accepted['field_path'] = path+'/'+key
                normalizations.append(accepted)
            else:
                assert_equivalent(actual[key], original[key], case, frames, normalizations, path+'/'+key, state)
    elif isinstance(actual, list) and isinstance(original, list):
        assert len(actual) == len(original), (path, 'list lengths')
        for index,(a,b) in enumerate(zip(actual,original)):
            assert_equivalent(a,b,case,frames,normalizations,path+'/'+str(index),state)
    else:
        assert actual == original, (path, actual, original)


def run(source, out, scratch, display, reuse=False):
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
        recording_exists = any(p.exists() for p in (avi, log, trace))
        if recording_exists and not (reuse and all(p.exists() for p in (avi,log,trace))):
            raise ValueError('Preserve existing attempt; choose new output/scratch: ' + str(log))
        command = [str(ENGINE), '--path', str(ROOT / 'prototype/godot'),
            '--resolution', '1600x900', '--audio-driver', 'Dummy',
            '--write-movie', str(avi), '--fixed-fps', '60', '--script',
            str(ROOT / 'map_directed/godot/map_boot.gd'), '--',
            '--cases-json', str(cases_path), '--case', str(index), '--movie',
            '--trace-json', str(trace)]
        returncode = 0
        if not recording_exists:
            (out / f'command-{index+1:02}.json').write_text(json.dumps(command, indent=2))
            with log.open('w') as stream:
                process = subprocess.run(command, env=dict(os.environ, DISPLAY=display,
                    LIBGL_ALWAYS_SOFTWARE='1'), stdout=stream, stderr=subprocess.STDOUT,
                    timeout=180)
                returncode = process.returncode
        text = log.read_text()
        failure = None
        try:
            assert returncode == 0, ('native exit', returncode, text[-3000:])
            assert all(s not in text for s in ('SCRIPT ERROR', 'ERROR:', 'were leaked')), text[-3000:]
            final = json.loads(next(line.split(' ', 1)[1] for line in text.splitlines()
                if line.startswith('MAP_NATIVE_RESULT ')))
            assert final['case_id'] == case['id'] and final['module_sha256'] == case['module_sha256']
            assert final['safe'] and final['hp'] == 5 and final['stable_frames'] >= 6
            normalizations = []
            original_frames = {f['frame']:f for f in expected['frames']}
            assert_equivalent(final['map_validation'], expected['map_validation'], case, original_frames,
                normalizations, 'final/map_validation')
            assert final['returns'] == len(expected['returns'])
            assert final['frame'] == len(expected['frames'])
            assert final['position'] == [expected['frames'][-1]['x'], expected['frames'][-1]['y']]
            native = json.loads(trace.read_text())
            assert native['case_id'] == case['id'] and native['module_sha256'] == case['module_sha256']
            assert len(native['frames']) == len(expected['frames'])
            for actual, original in zip(native['frames'], expected['frames']):
                for key in FRAME_KEYS:
                    assert_equivalent(actual[key], original[key], case, original_frames, normalizations,
                        f'frames/{actual["frame"]}/{key}', actual)
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
                error=failure, native_exit=returncode, preserved_movie=str(avi),
                log=log.name, trace=trace.name, source_binding_sha256=sha(physics/'source_binding.json')), indent=2))
            raise
        if not mp4.exists():
            with (out / f'encode-{index+1:02}.log').open('w') as stream:
                subprocess.run(['ffmpeg', '-nostdin', '-i', str(avi), '-an', '-c:v', 'libx264',
                    '-preset', 'medium', '-crf', '24', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
                    str(mp4)], stdout=stream, stderr=subprocess.STDOUT, check=True)
        probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_format',
            '-show_streams', '-of', 'json', str(mp4)]))
        assert probe['streams'][0]['avg_frame_rate'] == '60/1'
        unique_equivalences = {}
        for item in normalizations:
            key = (item['frame'], item['original_support'], item['native_support'], item['seam_id'])
            if key not in unique_equivalences:
                unique_equivalences[key] = {k:v for k,v in item.items() if k != 'field_path'}
                unique_equivalences[key]['field_paths'] = []
            unique_equivalences[key]['field_paths'].append(item['field_path'])
        clips.append(dict(id=case['id'], route=case['map_semantics']['route_id'], file=mp4.name,
            bytes=mp4.stat().st_size, sha256=sha(mp4), duration=float(probe['format']['duration']),
            width=probe['streams'][0]['width'], height=probe['streams'][0]['height'], fps='60/1',
            module_sha256=case['module_sha256'], map_geometry_sha256=case['map_semantics']['geometry_sha256'],
            actual_result=final, native_trace=dict(file=trace.name, bytes=trace.stat().st_size,
                sha256=sha(trace), frames=len(native['frames']), compared_fields=list(FRAME_KEYS),
                exact_fields=[k for k in FRAME_KEYS if k not in ('support_id','map')],
                maximum_position_error=0, all_cell_events_and_states_match=True,
                support_order_equivalences=list(unique_equivalences.values()),
                unique_support_equivalence_states=len(unique_equivalences),
                compared_support_field_occurrences=len(normalizations),
                comparison_scope='motion/resources/clocks/mechanisms/events exact; support_id only accepts explicit coplanar seam contact-order equivalence'),
            physics_evidence=raw_bindings[case['id']], source_binding_sha256=sha(physics/'source_binding.json')))
        (out / 'partial-receipt.json').write_text(json.dumps(dict(clips=clips, status='in_progress'), indent=2))
        print(json.dumps(dict(case_id=case['id'], frames=len(native['frames']),
            motion_resource_clock_exact=True, support_equivalence_observations=len(normalizations), file=str(mp4))), flush=True)
    concat = scratch / 'concat.txt'
    concat.write_text(''.join("file '" + str(out/c['file']) + "'\n" for c in clips))
    combined = out / 'all-routes.mp4'
    if not combined.exists():
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
        body_geometry_source=dict(file=str(BODY_SCENE.relative_to(ROOT)),sha256=sha(BODY_SCENE),size=list(BODY_SIZE)),
        first_strict_comparison_failure_preserved=dict(file='failure-01.json', comparator='comparator-first-pass.py',
            failure_sha256=sha(out/'failure-01.json'), comparator_sha256=sha(out/'comparator-first-pass.py'),
            reason='PhysicsServer ordering of simultaneous coplanar seam contacts differs; original IDs and evidence retained'),
        human_playtests=0, human_fun_approval='unverified', end_hold_seconds=1,
        scope='Actual GUI Godot / llvmpipe native 60Hz playback. Each complete route followed by one second frozen completion; combined file concatenates these complete clips. Motion/resources/clocks/mechanisms/events compare exactly at every frame; only static coplanar contact support ordering at explicit seams uses separately documented full-body sweep geometry equivalence. Not formal game, universal transfer, real-time performance or human fun admission.')
    (out/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    print(json.dumps(dict(status='passed', clips=len(clips), frames=sum(c['native_trace']['frames'] for c in clips), combined=str(combined))), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', default='pcg/results/map-directed-loop-v2')
    parser.add_argument('--out', default='generation/maps/map-directed-loop-v1')
    parser.add_argument('--scratch', default='/workspace/scratch/maploop-movies')
    parser.add_argument('--display', default=':103')
    parser.add_argument('--reuse-existing-recordings', action='store_true')
    args = parser.parse_args()
    run(REPO/args.source, REPO/args.out, Path(args.scratch), args.display, args.reuse_existing_recordings)
