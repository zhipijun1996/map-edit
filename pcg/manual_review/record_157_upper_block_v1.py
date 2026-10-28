"""Native uncut movie of the authorized 6x2 revision; strict differences retained."""
import gzip,json
from pcg.migration import core,physics
from pcg.prototype.factory.core.quality import module_hash
from pcg.prototype.workshop.record import record
from .record_approved_batch001 import review_only
from .repair_157_upper_block_v1 import ROOT,folder,row

def main():
    run=core.REPO/'pcg/results/approved-u157-delivery-final-v1';entry=core.read(run/'canonical.json')['rows'][0];e=entry['evidence'];raw=json.loads(gzip.decompress((run/e['output']).read_bytes()))['results'][e['index']];c=core.read(run/'physics'/(e['batch']+'.input.json'))['cases'][e['index']];c=physics._recording(c,raw);c.update(factory_evidence=e,review_alias='157 / TOP +1 Block / entry-to-exit');c['module_sha256']=module_hash(c);core.write(run/'review_cases.json',dict(cases=[c]));out=ROOT/'videos/157-upper-block-v1';scene=core.REPO/'pcg/manual_review/runtime/refresh_movie_v1.tscn'
    try:record(run.name,core.relative(out),display=':102',case_id=c['id'],main_scene=scene)
    except AssertionError as error:review_only(run,out,c,str(error))
    m=core.read(out/'manifest.json');m['scope']=dict(base_module_id='game-plains-twin-gears',reviewId='157',designVersion=row()['designVersion'],contentVersion=core.read(folder()/'module.mapnote.json')['generationContract']['contentVersion'],authorizedChange='TOP +1 Block, 6x1 to 6x2',bounds=dict(x=0,y=76,w=768,h=256),allWorldObjectsAndSidePortPositionsUnchanged=True,orientation='identity',connected_port_subset=['entry','exit'],closure_profile=None,mirror='UNKNOWN',humanPlaytest='UNKNOWN',productionApproval=False,movieConsumer=physics.artifact(scene.with_suffix('.gd')),scene=physics.artifact(scene),endHoldSeconds=1,speed=1,editorialCuts=[]);core.write(out/'manifest.json',m);print('VIDEO_REVIEW_ONLY'if m.get('reviewOnly')else'VIDEO_STRICT',flush=True)
if __name__=='__main__':main()
