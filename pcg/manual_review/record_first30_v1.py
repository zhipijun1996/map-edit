"""Actual Godot movies; preserve exact comparison failure and all differences."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import argparse,gzip,json
from pcg.migration import core,physics
from pcg.prototype.factory.core.quality import module_hash
from pcg.prototype.workshop.record import record
from .record_approved_batch001 import review_only
from .finalize_first30_v1 import folder_for,AUTH

def run(row):
    n=row['reviewId']
    name=('approved-b001-first30-'+n+'-delivery-canonical-v7')if int(n)<4 else('approved-b001-first30-'+n+'-delivery-final-v1')
    root=core.REPO/'pcg/results'/name;entries=core.read(root/'canonical.json')['rows']
    # Prefer the retracted upper route, AIR exits, and the repaired high branch.
    index=1 if n in('03','06','23')else 0;entry=entries[index];e=entry['evidence']
    raw=json.loads(gzip.decompress((root/e['output']).read_bytes()))['results'][e['index']]
    c=core.read(root/'physics'/(e['batch']+'.input.json'))['cases'][e['index']]
    c=physics._recording(c,raw);c['factory_evidence']=e;c['review_alias']=n+' / '+c['route_spec']['id'];c['module_sha256']=module_hash(c)
    core.write(root/'review_cases.json',dict(cases=[c]));relative='feedback/manual-review/implementation-results/first-30-v2/videos/'+n+'-v1';out=core.REPO/relative
    try:record(root.name,relative,display=':99',case_id=c['id'],main_scene=core.REPO/'pcg/manual_review/runtime/first30_movie_v1.tscn')
    except AssertionError as exc:review_only(root,out,c,str(exc))
    manifest=core.read(out/'manifest.json');manifest['scope']=dict(base_module_id=row['moduleId'],designVersion=row['designVersion'],contentVersion=core.read((folder_for(row)if int(n)>5 else core.REPO/('pcg/manual_review/implementation/first-30-v2'if n=='01'else'pcg/manual_review/implementation/first-30-v4')/row['moduleId'])/'module.mapnote.json')['generationContract']['contentVersion'],orientation='identity',connected_port_subset=[c['route_spec']['from_port'],c['route_spec']['to_port']],closure_profile=None,closed_ports=[],unusedPorts='open; closure configurations UNKNOWN',route=c['route_spec'],initialConditions='frozen actual fixture',foundationVersion='1.0',playbackInput=physics.artifact(out/'review_cases.json'),movieConsumer=physics.artifact(core.REPO/'pcg/manual_review/runtime/first30_movie_v1.gd'),scene=physics.artifact(core.REPO/'pcg/manual_review/runtime/first30_movie_v1.tscn'),gameSourceCommit='12f6cb006d7119598e3235f4ca4f7323e4c9d092',endHoldSeconds=1,editorialCuts=[],purpose='AI/user visual review; does not certify unfilmed routes',humanPlaytest='UNKNOWN',productionApproval=False)
    core.write(out/'manifest.json',manifest);print(n,'video','STRICT'if not manifest.get('reviewOnly')else'REVIEW_ONLY',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('ids',nargs='+');a=p.parse_args()
    for row in core.read(AUTH/'handoff.json')['rows']:
        if row['reviewId']in a.ids:run(row)
