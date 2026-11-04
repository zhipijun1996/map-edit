"""Open an isolated compiled sample; no generation or qualification on launch."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import argparse
import subprocess
from pcg.migration import core, godot_package


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('review_id',choices=['01','02','03','04','05'])
    p.add_argument('--route',help='Route ID (default: first declared route)')
    p.add_argument('--replay',action='store_true')
    a=p.parse_args()
    row=next(r for r in core.read(core.REPO/'feedback/manual-review/implementation-results/batch-001/authorization/handoff-v1.json')['rows'] if r['reviewId']==a.review_id)
    package=core.REPO/row['outputDirectory']/'playable'
    godot_package.verify_package(package,require_loaded=False)
    cases=core.read(package/'cases.json')['cases']
    index=next((i for i,c in enumerate(cases) if c['route_spec']['id']==a.route),0 if a.route is None else None)
    if index is None:p.error('Unknown route; choose '+', '.join(c['route_spec']['id'] for c in cases))
    engine=core.REPO/'pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64'
    command=[str(engine),'--path',str(godot_package.PROJECT),str(package/'demo.tscn'),'--','--case',str(index)]
    if a.replay:command.append('--replay')
    return subprocess.call(command,cwd=core.REPO)


if __name__=='__main__':raise SystemExit(main())
