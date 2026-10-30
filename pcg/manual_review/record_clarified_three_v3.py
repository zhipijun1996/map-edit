"""Actual uncut Godot movies; existing strict comparison and complete failures."""
import argparse,gzip,json
from pcg.migration import core,physics
from pcg.prototype.factory.core.quality import module_hash
from pcg.prototype.workshop.record import record
from .record_approved_batch001 import review_only
AUTH='feedback/manual-review/implementation-results/clarified-three-v1/authorization/handoff.json'

def run(row):
    n=row['reviewId'];version='v1';root=core.REPO/'pcg/results'/('approved-c3-'+n+'-delivery-final-'+version)
    entry=core.read(root/'canonical.json')['rows'][0];e=entry['evidence']
    raw=json.loads(gzip.decompress((root/e['output']).read_bytes()))['results'][e['index']]
    c=core.read(root/'physics'/(e['batch']+'.input.json'))['cases'][e['index']]
    c=physics._recording(c,raw);c['factory_evidence']=e;c['review_alias']=n+' / '+c['route_spec']['id'];c['module_sha256']=module_hash(c)
    core.write(root/'review_cases.json',dict(cases=[c]));relative='feedback/manual-review/implementation-results/clarified-three-v1/videos/'+n+'-v3';out=core.REPO/relative
    scene=core.REPO/'pcg/manual_review/runtime/clarified_three_movie_v3.tscn'
    try:record(root.name,relative,display=':104',case_id=c['id'],main_scene=scene)
    except AssertionError as exc:review_only(root,out,c,str(exc))
    folder=core.REPO/('pcg/manual_review/implementation/clarified-three-final-'+version)/row['moduleId']
    manifest=core.read(out/'manifest.json');manifest['scope']=dict(base_module_id=row['moduleId'],designVersion=row['designVersion'],contentVersion=core.read(folder/'module.mapnote.json')['generationContract']['contentVersion'],orientation='identity',connected_port_subset=sorted(set([c['route_spec']['from_port'],c['route_spec']['to_port']])),closure_profile=None,closed_ports=[],unusedPorts='open; closure configurations UNKNOWN',route=c['route_spec'],initialConditions='frozen actual fixture; real Cell consumers',foundationVersion='1.2',playbackInput=physics.artifact(out/'review_cases.json'),movieConsumer=physics.artifact(scene.with_suffix('.gd')),movieParent=physics.artifact(scene.with_name('first30_movie_v1.gd')),scene=physics.artifact(scene),engine=physics.artifact(core.REPO/'pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64'),gameSourceCommit='12f6cb006d7119598e3235f4ca4f7323e4c9d092',endHoldSeconds=1,editorialCuts=[],purpose='AI/user visual review; no certification of unfilmed routes',humanPlaytest='UNKNOWN',productionApproval=False)
    core.write(out/'manifest.json',manifest);print(n,'video','REVIEW_ONLY'if manifest.get('reviewOnly')else'STRICT',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('ids',nargs='+');a=p.parse_args()
    for row in core.read(AUTH)['rows']:
        if row['reviewId']in a.ids:run(row)
