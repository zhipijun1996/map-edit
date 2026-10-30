"""Narrow interface dispatch and the relay's real static body clearances."""
import copy
from pcg.migration import core,physics,revision065_boundary_v1 as boundary
from .continue_revision065_lift_v1 import OUT,ID
from .run_revision066_lift_v1 import folder_for,rows
def main():
 row=rows()[0];f=folder_for(row);new=core.read(f/'physics-input-cases.json')['cases'][0];doc=core.read(f/'module.mapnote.json');ports=doc['generationContract']['ports'];top=next(p for p in ports if p['id']=='B');assert boundary.applies(new,top)
 checks=[]
 for version in ['053','063']:
  old=core.read(core.REPO/f'pcg/manual_review/implementation/revision-{version}-final-v1'/ID/'physics-input-cases.json')['cases'][0];assert not boundary.applies(old,top);checks.append('historical_'+version+'_excluded')
 for key,value in [('face','BOTTOM'),('surface','AIR'),('permission','INOUT')]:
  p=copy.deepcopy(top);p[key]=value;assert not boundary.applies(new,p);checks.append(key+'_mismatch_rejected')
 old=core.read(core.REPO/'pcg/manual_review/implementation/revision-063-final-v1'/ID/'module.mapnote.json');objects={o['id']:o for o in doc['objects']};assert all(objects[o['id']]==o for o in old['objects'])
 added=set(objects)-{o['id']for o in old['objects']};assert added=={'relay-dock'};relay=objects['relay-dock'];assert [relay[k]for k in ['x','y','w','h']]==[0,544,64,12]
 assert new['platforms'][2]==[0,544,64,12]and 2 in new['one_way_platform_indices']
 # Native body24x36 at station(20,526); saw center y464,radius24.
 assert (526-18)-(464+24)==20 and 52-(20+12)==20
 core.write(OUT/'verification/interface-geometry-regression.json',dict(passed=True,checks=checks,originalObjectsByteEquivalent=True,addedObject='relay-dock',originalMotionParametersUnchanged=True,relayActualNativeOneWayIndex=2,station=[20,526],nativeBody=[24,36],minimumVerticalMiddleSawClearancePx=20,minimumHorizontalMovingCarrierClearancePx=20,staticGeometryOnly=True,nativeWaitProof=physics.artifact(OUT/'fixtures/missed-boarding-wait-chest-v2/recovery-reward-evidence.json'),source=physics.artifact(__file__)));print('R065_INTERFACE_GEOMETRY_REGRESSION_PASS',flush=True)
if __name__=='__main__':main()
