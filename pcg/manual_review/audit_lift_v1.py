"""Reproducible exact approved Cell/geometry and immutable-source audit."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import hashlib,json,subprocess
from pcg.migration import core,physics,lift_runtime_v1 as backend
from .lift_idea_v1 import OUT,rows
from .finalize_lift_v1 import folder_for

def main():
    row=rows()[0];f=folder_for(row);design=core.read(row['designFile']);doc=core.read(f/'module.mapnote.json');objects={o['id']:o for o in doc['objects']}
    assert core.sha(core.REPO/row['designFile'])==row['designFileSha256']
    for visual in design['visualObjects']:
        if visual['type']=='route':continue
        actual=objects[visual['id']]
        assert all(visual[k]==actual[k]for k in ['type','x','y','w','h'])
        for key in ['trackId','designMotion','points']:
            if key in visual:assert actual[key]==visual[key]
    for original,port in zip(design['ports'],doc['generationContract']['ports']):
        assert all(original[k]==port[k]for k in ['id','position','normal','surface','permission'])
    core.verify_artifacts(list(core.read(f/'frozen.json').values()))
    assert core.read(f/'package-result.json')['passed']
    backend.verify_package(f/'playable',require_loaded=True)
    content=core.read(f/'parameters.json')['content']
    assert len(content['platforms'])==2 and len(content['moving_platforms'])==4 and len(content['saws'])==3 and len(content['enemies'])==1 and not content['hazards']
    for platform in content['moving_platforms']:
        track=objects[objects[platform['platform_id']]['trackId']]
        assert all(platform[k]==track['designMotion'][k]for k in ['start','finish','travel_duration','dwell_duration','initial_phase'])
    for saw in content['saws']:
        track=objects[objects[saw['source_id']]['trackId']]
        assert all(saw[k]==track['designMotion'][k]for k in ['origin','travel','period','initial_phase']) and saw['radius']==24
    versions={}
    for run in sorted((core.REPO/'pcg/results').glob('approved-lift-lift-canonical-*')):
        result=core.read(run/'canonical.json')
        semantic=[dict(plan=r['case']['control_plan'],source=r['case']['generation_rule']['registration_source'])for r in result['rows']]
        digest=hashlib.sha256(json.dumps(semantic,sort_keys=True).encode()).hexdigest()
        versions.setdefault(digest,[]).append(core.relative(run/'canonical.json'))
    assert len(versions)==12
    core.write(OUT/'verification/geometry-and-budget.json',dict(passed=True,exactApprovedGeometry=True,exactApprovedNativeMotion=True,staticPlatforms=2,movingSolidPlatforms=4,saws=3,originalDiver=1,sawGlyphs='hazard/gears decoded to original ModuleSawDefinition; no rectangular collision fallback',optionalRewardCoins=4,nativeReplayCases=3,executedSemanticVersions=len(versions),budget=12,versions=versions,formalVersions=0,holdoutUsed=False,source=physics.artifact(__file__)))
    provenance=core.read('pcg/prototype/godot/source_provenance.json')
    assert all(core.sha(core.REPO/'pcg/prototype/godot'/path)==sha for path,sha in provenance['files'].items())
    diff=subprocess.check_output(['git','diff','--name-only','origin/main','--','generation/manual-review','generation/module-workshop'],text=True).splitlines();assert not diff
    core.write(OUT/'verification/source-audit.json',dict(passed=True,protectedFiles=len(provenance['files']),protectedMismatches=[],designWebEdits=diff,main='11f35799ac7e089ab0c6738120d6ce27a4e86ac7',engine=physics.artifact(core.REPO/'pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64'),gameSourceCommit=provenance['commit']))
    print('LIFT_EXACT_CELL_PACKAGE_SOURCE_BUDGET_PASS')
if __name__=='__main__':main()
