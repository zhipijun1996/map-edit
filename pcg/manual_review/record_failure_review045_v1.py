"""Actual failed-route footage. Remove only recorder's success prerequisite."""
import inspect,gzip,json
from pcg.migration import core,physics
from pcg.prototype.workshop import record as recorder
from pcg.prototype.factory.core.quality import module_hash
from .record_approved_batch001 import review_only
from .refresh_review045_v1 import rows,OUT
from .finalize_review045_v1 import folder_for

def run(row):
 n=row['reviewId'];root=core.REPO/'pcg/results'/('approved-r045-'+n+'-partial-delivery-v1');entry=core.read(root/'canonical.json')['rows'][0];assert not entry['check']['ok'];e=entry['evidence'];raw=json.loads(gzip.decompress((root/e['output']).read_bytes()))['results'][e['index']];assert not raw['ok']
 c=physics._recording(entry['case'],raw);c['max_frames']=len(raw['frames']);c['factory_evidence']=e;c['review_alias']=n+' FAILED / '+c['route_spec']['id'];c['module_sha256']=module_hash(c);core.write(root/'review_cases.json',dict(cases=[c]));out=OUT/'videos'/(n+'-failed-'+c['route_spec']['id']+'-v1')
 source=inspect.getsource(recorder.record).replace("and r['ok']","");scope={**recorder.__dict__};exec(compile(source,__file__,'exec'),scope)
 try:scope['record'](root.name,core.relative(out),display=':104',case_id=c['id'],main_scene=core.REPO/'pcg/manual_review/runtime/review045_movie_v1.tscn')
 except AssertionError as error:review_only(root,out,c,str(error))
 m=core.read(out/'manifest.json');m['scope']=dict(base_module_id=row['moduleId'],designVersion=row['designVersion'],contentVersion=core.read(folder_for(row)/'module.mapnote.json')['generationContract']['contentVersion'],orientation='identity',connected_port_subset=[c['route_spec']['from_port'],c['route_spec']['to_port']],closure_profile=None,closed_ports=[],route=c['route_spec'],initialConditions='frozen failed clean input, unchanged original resources',foundationDocumentVersion='1.2',serializedFoundationVersion='1.0',playbackInput=physics.artifact(out/'review_cases.json'),movieConsumer=physics.artifact(core.REPO/'pcg/manual_review/runtime/review045_movie_v1.gd'),engine=physics.artifact(core.REPO/'pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64'),gameSourceCommit='12f6cb006d7119598e3235f4ca4f7323e4c9d092',purpose='FAILED ROUTE visual evidence',wholeModuleQualification='UNQUALIFIED',humanPlaytest='UNKNOWN',productionApproval=False,endHoldSeconds=1,editorialCuts=[])
 m['failedPhysicsCheck']=entry['check'];core.write(out/'manifest.json',m);print(n,'FAILED_ROUTE_FILMED',flush=True)
if __name__=='__main__':
 import sys
 for r in rows():
  if r['reviewId']in sys.argv[1:]:run(r)
