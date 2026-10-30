"""Representative real-time films, with strict comparison failures retained."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import gzip,json
from pcg.migration import core,physics
from pcg.prototype.factory.core.quality import module_hash
from pcg.prototype.workshop.record import record
from .record_approved_batch001 import review_only
from .new_ideas_v1 import rows, OUT, label
from .finalize_ideas_v1 import folder_for
def run(row):
 n=label(row);folder=folder_for(row);root=core.REPO/'pcg/results'/('approved-ideas-'+n+'-delivery-final-v1')
 entries=[v for v in core.read(root/'canonical.json')['rows']if v['check']['ok']]
 wanted = ['A-to-C', 'A-to-B'] if n == 'orbit' else ['A-to-B', 'B-to-A']
 entries=[v for v in entries if v['case']['route_spec']['id'] in wanted]
 assert entries,(n,'no_representative_case')
 for entry in entries:
  e=entry['evidence'];raw=json.loads(gzip.decompress((root/e['output']).read_bytes()))['results'][e['index']]
  c=core.read(root/'physics'/(e['batch']+'.input.json'))['cases'][e['index']];c=physics._recording(c,raw);c['factory_evidence']=e;c['review_alias']=n+' / '+c['route_spec']['id'];c['module_sha256']=module_hash(c)
  core.write(root/'review_cases.json',dict(cases=[c]));relative=core.relative(OUT/'videos'/(n+'-'+c['route_spec']['id']+'-v1'));out=core.REPO/relative;scene=core.REPO/'pcg/manual_review/runtime/ideas_movie_v1.tscn'
  try:record(root.name,relative,display=':104',case_id=c['id'],main_scene=scene)
  except AssertionError as error:review_only(root,out,c,str(error))
  logs='\n'.join(p.read_text()for p in out.glob('*.record.log'));assert 'SCRIPT ERROR'not in logs and '\nERROR:'not in logs
  m=core.read(out/'manifest.json');m['scope']=dict(base_module_id=row['moduleId'],designVersion=row['designVersion'],contentVersion=core.read(folder/'module.mapnote.json')['generationContract']['contentVersion'],orientation='identity',connected_port_subset=sorted([c['route_spec']['from_port'],c['route_spec']['to_port']]),closure_profile=None,closed_ports=[],route=c['route_spec'],initialConditions='frozen original native fixture; current approved design',foundationDocumentVersion='1.2',serializedFoundationVersion='1.0',playbackInput=physics.artifact(out/'review_cases.json'),movieConsumer=physics.artifact(scene.with_suffix('.gd')),scene=physics.artifact(scene),engine=physics.artifact(core.REPO/'pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64'),gameSourceCommit='12f6cb006d7119598e3235f4ca4f7323e4c9d092',endHoldSeconds=1,editorialCuts=[],purpose='AI/user representative visual review',humanPlaytest='UNKNOWN',productionApproval=False,wholeModuleQualification='PASS'if (folder/'qualification.json').exists() and core.read(folder/('qualification-reanalyzed.json'if (folder/'qualification-reanalyzed.json').exists()else'qualification.json'))['passed']else'UNQUALIFIED',otherUnfilmedRoutes='not represented by this movie')
  core.write(out/'manifest.json',m);print(n,c['route_spec']['id'],'REVIEW_ONLY'if m.get('reviewOnly')else'STRICT',flush=True)
if __name__=='__main__':
 import sys
 for r in rows():
  if label(r) in sys.argv[1:]:run(r)
