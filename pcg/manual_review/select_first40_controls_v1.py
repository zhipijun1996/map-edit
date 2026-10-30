"""Install one predeclared all-pass calibration selection; preserve initial input."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import argparse,copy,shutil
from pcg.migration import core,physics,godot_package
from pcg.prototype.factory.core.quality import digest

def main(n,version):
    row=next(r for r in core.read('feedback/manual-review/implementation-results/first-40-v1/authorization/handoff.json')['rows']if r['reviewId']==n);folder=core.REPO/row['outputDirectory'];path=core.REPO/'pcg/results'/('approved-b040-'+n+'-control-screen-'+version)/'screen.json';selection=core.read(path)['selected'];assert selection
    before=folder/'revisions'/('before-selection-'+version);before.mkdir(parents=True,exist_ok=False)
    for name in ('cases.json','module.mapnote.json','parameters.json','thumbnail.svg'):shutil.copy2(folder/name,before/name)
    for key in ('noise','module_sha256','factory_evidence','recorded_frames'):selection.pop(key,None)
    cases=[selection];doc=core.read(folder/'module.mapnote.json');doc['generationContract']['generation']['approvedImplementation'].update(controlProgramsSha256=digest([c['control_plan']for c in cases]),repairSelection=physics.artifact(path));doc=godot_package.bind_case_behavior(doc,cases)
    core.write(folder/'cases.json',dict(cases=cases));core.write(folder/'module.mapnote.json',doc);core.contract(folder/'module.mapnote.json',refresh=True)
    p=core.read(folder/'parameters.json');p.update(controls=[dict(route=c['route_spec'],control_plan=c['control_plan'])for c in cases],repairSelection=physics.artifact(path));core.write(folder/'parameters.json',p)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('id');p.add_argument('version');a=p.parse_args();main(a.id,a.version)
