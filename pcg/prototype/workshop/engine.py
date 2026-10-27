"""Extend PlainsEngine source freezing, not its simulation or acceptance rules."""
import json, shutil
from pathlib import Path
from pathlib import Path
from ..plains.engine import PlainsEngine, ROOT
from ..factory.core.engine import file_sha
from ..factory.core.quality import digest

HERE = Path(__file__).parent

class WorkshopEngine(PlainsEngine):
    def __init__(self, out, batch_size=12, extra_sources=None, runner_script=None):
        super().__init__(out, batch_size)
        files=list(HERE.rglob('*'))+list((ROOT/'module_library').glob('*.py'))+list((ROOT/'module_library').glob('*.json'))+[ROOT/'module_library/validate_document.mjs',ROOT/'contract/export.py']+[Path(p)for p in (extra_sources or [])]
        for p in sorted(files):
            if p.suffix not in ('.py', '.gd', '.json', '.mjs', '.tscn'): continue
            rel = p.relative_to(ROOT).as_posix()
            self.hashes[rel] = file_sha(p)
            dest = self.out/'source_snapshot'/rel
            dest.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(p, dest)
        self.sim.runner_script = str(runner_script or HERE/'runner.gd')
        self.binding.update(runner=self.sim.runner_script, source_files=self.hashes,
                            source_manifest_sha256=digest(self.hashes))
        (self.out/'source_binding.json').write_text(json.dumps(self.binding, indent=2))
