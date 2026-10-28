"""Interpret one audited observer conflict without changing physics or raw data.

Original Controller lands, renews the one jump and consumes a buffered request
after motor.step. The old observer classifies using pre-step state. Only this
specific, physically supported landing signature is recognized here.
"""
import copy


def classify(case, result):
    corrected = copy.deepcopy(result)
    snapshot = result.get('capability_snapshot', {})
    recognized = []
    if snapshot.get('maximum_jumps') == 1 and snapshot.get('double_enabled') is False:
        for before, after in zip(result.get('frames', []), result.get('frames', [])[1:]):
            if not any(e.get('type') == 'air_jump' for e in after.get('accepted', [])):
                continue
            support = str(after.get('support_id', ''))
            if not support.startswith('Platform') or not support[8:].isdigit():
                continue
            index = int(support[8:])
            if index >= len(case.get('platforms', [])):
                continue
            x, top, width, height = case['platforms'][index]
            actual_landing = (not before.get('grounded') and before.get('jumps_used', 0) >= 1
                              and after.get('grounded') is True and after.get('jump_maximum') == 1
                              and after.get('jumps_used') == 1 and after.get('can_air_jump') is False
                              and abs(after['y'] + 18 - top) < .5
                              and x <= after['x'] - 12 and after['x'] + 12 <= x + width
                              and abs(after['vy']) < .1 and after['real_velocity'][1] > 0
                              and after['normal_velocity'][1] < 0)
            if actual_landing:
                recognized.append(after['frame'])
    raw = result.get('air_jumps', 0)
    if len(recognized) > raw:
        raise ValueError('landing event count exceeds raw observer count')
    corrected['air_jumps'] = raw - len(recognized)
    return corrected, dict(raw_air_jump_events=raw, recognized_ground_buffer_frames=recognized,
                           remaining_unclassified_air_jump_events=corrected['air_jumps'],
                           raw_result_changed=False, physics_changed=False)
