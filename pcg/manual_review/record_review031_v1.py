"""Real-time native movies for every qualified route; strict failures retained."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import gzip,json
from pcg.migration import core,physics
from pcg.prototype.factory.core.quality import module_hash
from pcg.prototype.workshop.record import record
from .record_approved_batch001 import review_only
from .prepare_review031_v1 import OUT,rows
from .finalize_review031_v1 import folder_for
def run(row):
 n=row['reviewId'];root=core.REPO/'pcg/results'/('approved-r031-'+n+'-delivery-final-v1');folder=folder_for(row)
 for entry in core.read(root/'canonical.json')['rows']:
  assert entry['check']['ok'];e=entry['evidence'];raw=json.loads(gzip.decompress((root/e['output']).read_bytes()))['results'][e['index']]
  c=core.read(root/'physics'/(e['batch']+'.input.json'))['cases'][e['index']];c=physics._recording(c,raw);c['factory_evidence']=e;c['review_alias']=n+' / '+c['route_spec']['id'];c['module_sha256']=module_hash(c)
  core.write(root/'review_cases.json',dict(cases=[c]));relative=core.relative(OUT/'videos'/(n+'-'+c['route_spec']['id']+'-v1'));out=core.REPO/relative;scene=core.REPO/'pcg/manual_review/runtime/clarified_three_movie_v3.tscn'
  try:record(root.name,relative,display=':104',case_id=c['id'],main_scene=scene)
  except AssertionError as error:review_only(root,out,c,str(error))
  m=core.read(out/'manifest.json');m['scope']=dict(base_module_id=row['moduleId'],designVersion=row['designVersion'],contentVersion=core.read(folder/'module.mapnote.json')['generationContract']['contentVersion'],orientation='identity',connected_port_subset=sorted([c['route_spec']['from_port'],c['route_spec']['to_port']]),closure_profile=None,closed_ports=[],route=c['route_spec'],initialConditions='frozen original native fixture; current approved design',foundationDocumentVersion='1.2',serializedFoundationVersion='1.0',playbackInput=physics.artifact(out/'review_cases.json'),movieConsumer=physics.artifact(scene.with_suffix('.gd')),scene=physics.artifact(scene),engine=physics.artifact(core.REPO/'pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64'),gameSourceCommit='12f6cb006d7119598e3235f4ca4f7323e4c9d092',endHoldSeconds=1,editorialCuts=[],purpose='AI/user visual review',humanPlaytest='UNKNOWN',productionApproval=False)
  core.write(out/'manifest.json',m);print(n,c['route_spec']['id'],'REVIEW_ONLY'if m.get('reviewOnly')else'STRICT',flush=True)
if __name__=='__main__':
 import sys
 for r in rows():
  if r['reviewId']in sys.argv[1:]:run(r)
