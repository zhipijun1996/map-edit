"""Ask the original Godot parser before paying for actual case execution."""
import subprocess
from pathlib import Path
from pcg.prototype.factory.core.engine import ENGINE,PROJECT,file_sha

def check(paths):
    rows=[]
    for path in dict.fromkeys(Path(p).resolve()for p in paths):
        command=[str(ENGINE),'--headless','--path',str(PROJECT),'--check-only','--script',str(path)]
        result=subprocess.run(command,capture_output=True,text=True,timeout=30)
        log=result.stdout+result.stderr
        rows.append(dict(script=str(path),source_sha256=file_sha(path),command=command,
            returncode=result.returncode,log=log,
            ok=result.returncode==0 and not any(v in log for v in ['SCRIPT ERROR','ERROR:'])))
    return dict(status='syntax_checked'if rows and all(r['ok']for r in rows)else'needs_design',
        actual_physics_cases=0,engine_sha256=file_sha(ENGINE),rows=rows,
        scope='Original Godot --check-only. No actual Module, mechanism or physics success inferred.')
