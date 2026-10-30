"""Keep all relay versions, rejected/interrupted screens and both formal runs."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core,physics
from pcg.tools.build_archive import build
from pcg.tools.restore_archive import restore
from .continue_revision065_lift_v1 import OUT
def main():
 paths=sorted(p.relative_to(core.REPO/'pcg').as_posix()for prefix in ['approved-r065-*','approved-r066-*']for p in(core.REPO/'pcg/results').glob(prefix)if p.is_dir());name='approved-revision065-066-lift-relay-v1';manifest=core.REPO/'pcg/archives'/name/'manifest.json'
 m=core.read(manifest)if manifest.exists()else build(name,paths,deduplicate=True,stream_parts=True);v=restore(name,verify_parts_only=True)
 core.write(OUT/'verification/raw-archive.json',dict(passed=True,runDirectories=len(paths),paths=paths,manifest=physics.artifact(manifest),verification=v,files=m['files'],scope='All actual successful/failed/interrupted diagnostics, both formal runs, completed-source snapshots, same-input screen continuation and native extra demonstrations. No prior results overwritten.'))
 print('R065_RAW_ARCHIVE_PASS',m['files'],flush=True)
if __name__=='__main__':main()
