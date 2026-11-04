"""Jump before the diver's final recoil overshoots the declared top neighbor."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core, godot_package
from .new_ideas_v1 import rows, label

def main():
    row = next(row for row in rows() if label(row) == 'enemies-3')
    folder = core.REPO / row['outputDirectory']
    cases = core.read(folder / 'cases.json')['cases']
    core.write(folder / 'history/pre-repair-v11-cases.json', dict(cases=cases))
    for case in cases:
        case['id'] = case['id'].replace('newideas-v13', 'newideas-v14')
        case['generation_rule']['registration_source'] = 'pcg/manual_review/ideas_author_v9.py'
    document = godot_package.bind_case_behavior(core.read(folder / 'module.mapnote.json'), cases)
    core.write(folder / 'module.mapnote.json', document)
    core.contract(folder / 'module.mapnote.json', refresh=True)
    core.write(folder / 'cases.json', dict(cases=cases))
if __name__ == '__main__':
    main()
