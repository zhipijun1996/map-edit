"""Keep every successful, failed and rejected execution from this user task."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core,physics
from pcg.tools.build_archive import build
from pcg.tools.restore_archive import restore
from .continue_revision063_v1 import OUT
def main():
 paths=sorted(p.relative_to(core.REPO/'pcg').as_posix()for prefix in ['approved-r063-*','approved-r064-*']for p in(core.REPO/'pcg/results').glob(prefix)if p.is_dir())
 name='approved-revision063-064-implementation-v1'
 manifest=core.REPO/'pcg/archives'/name/'manifest.json'
 m=core.read(manifest)if manifest.exists()else build(name,paths,deduplicate=True,stream_parts=True)
 v=restore(name,verify_parts_only=True)
 core.write(OUT/'verification/raw-archive.json',dict(passed=True,runDirectories=len(paths),paths=paths,manifest=physics.artifact(core.REPO/'pcg/archives'/name/'manifest.json'),verification=v,files=m['files'],scope='All successful/failed diagnostics, bounded screens, formal runs, setup rejections, native deliveries and frozen source snapshots from063 and064. AVI files are kept separately with the video artifacts.'))
if __name__=='__main__':main()
