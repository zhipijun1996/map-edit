"""Aim at the original third diver's observed recovery displacement."""
from pcg.migration import core, godot_package
from .new_ideas_v1 import rows, label

def main():
    row = next(row for row in rows() if label(row) == 'enemies-3')
    folder = core.REPO / row['outputDirectory']
    cases = core.read(folder / 'cases.json')['cases']
    core.write(folder / 'history/pre-repair-v10-cases.json', dict(cases=cases))
    for case in cases:
        case['id'] = case['id'].replace('newideas-v12', 'newideas-v13')
        for command in case['control_plan']:
            if command.get('chain_window', {}).get('id') == 'enemy-3':
                command['aim_cell']['body_offset'] = [-8, -6]
    document = godot_package.bind_case_behavior(core.read(folder / 'module.mapnote.json'), cases)
    core.write(folder / 'module.mapnote.json', document)
    core.contract(folder / 'module.mapnote.json', refresh=True)
    core.write(folder / 'cases.json', dict(cases=cases))
if __name__ == '__main__':
    main()
