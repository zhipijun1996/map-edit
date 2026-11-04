"""Freeze a clean native demonstration without selecting a formal qualification."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import inspect
from pcg.migration import core, physics
from . import finalize_first40_v1 as shared
from .new_ideas_v1 import AUTH, rows, label
from .finalize_ideas_v1 import folder_for, ROOT
from .ideas_content_v1 import decode

def main():
    row = next(r for r in rows() if label(r) == 'enemies-3')
    draft = core.REPO / row['outputDirectory']
    screen = core.REPO / 'pcg/results/approved-ideas-enemies-3-control-screen-v15/screen.json'
    assert not core.read(screen)['passed']
    assert core.read(draft / 'native-preflight-v15.json')['passed']
    source = inspect.getsource(shared.freeze).replace('approved-first40-final-v1-', 'approved-newideas-final-v1-').replace('pcg/manual_review/first30_content_v2.py','pcg/manual_review/ideas_content_v1.py')
    namespace = {**shared.__dict__, 'AUTH': AUTH, 'ROOT': ROOT, 'folder_for': folder_for, 'decode': decode}
    exec(compile(source, __file__, 'exec'), namespace)
    namespace['freeze'](row)
    core.write(folder_for(row) / 'qualification-not-run.json', dict(passed=False, status='UNQUALIFIED', reason='Bounded controls did not pass the preregistered screen. Native clean demonstration is not qualification.', screen=physics.artifact(screen), independentHoldoutUsed=False, designImpossible=False, geometryChanged=False, prohibited='No extra versions, new seeds or relaxed thresholds after budget.'))
if __name__ == '__main__':
    main()
