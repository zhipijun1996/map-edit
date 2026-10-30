"""Read real native events and mounted receiver traces; never simulate them."""
import gzip,json
from pcg.migration import core,physics
from .continue_revision063_v1 import rows,label,OUT
from .record_revision063_native_v1 import folder_for
def main():
 folders={label(r):folder_for(r)for r in rows()};facts={}
 d=core.read(folders['s04']/'playable/load-evidence/case-0/receipt.json');events=[]
 for group in d['package']['approved_hq']:
  for e in group.get('events',[]):
   if e['type']=='atomic_group_motion':
    ids=[v['id']for v in e['before']];assert ids in [['P'],['Q']];events.append(e)
 assert {e['before'][0]['id']for e in events}=={'P','Q'}
 facts['s04']=dict(independentNativeGroups=True,events=events,receipt=physics.artifact(folders['s04']/'playable/load-evidence/case-0/receipt.json'))
 count=0;cases=0;refs=[]
 root=core.resolve_artifact(core.read(folders['s06']/'qualification.json')['report']['path']).parent
 for p in sorted((root/'physics').glob('*.output.json.gz')):
  d=json.load(gzip.open(p));refs.append(physics.artifact(p))
  for result in d['results']:
   cases+=1
   for frame in result['frames']:
    for b in frame['review029_mounted_bells']:
     assert b['carrier_id']=='P'and b['real_receiver_child_of_carrier']and all(abs(b['receiver_offset'][i]-[0,64][i])<.0001 for i in range(2))
     assert all(abs(b['receiver_global'][i]-b['carrier_global'][i]-[0,64][i])<.0001 for i in range(2));count+=1
 assert cases>=172 and count>1000
 facts['s06']=dict(realNativeReceiverChild=True,offset=[0,64],rawCasesIncludingOriginalFailedFixtures=cases,frameObservations=count,raw=refs)
 out=[]
 for p in sorted((folders['s09']/'playable/load-evidence').glob('case-*/receipt.json')):
  d=core.read(p);events=d['package']['plains']['events'];dead=[e['frame']for e in events if e['type']=='enemy_defeated'];air=[e for e in events if e['type']=='enemy_hit'and e['player_airborne']and e['fired_airborne']]
  assert d['passed']and d['hp']==5 and dead and max(dead)<d['actual_frames']
  if p.parent.name=='case-0':assert len(air)==3
  out.append(dict(receipt=physics.artifact(p),deadFrame=max(dead),endFrame=d['actual_frames'],airborneHits=len(air),sameWorld=True,automaticRespawn=False))
 facts['s09']=out
 f=folders['hq09'];doc=core.read(f/'module.mapnote.json');assert next(p for p in doc['generationContract']['ports']if p['id']=='T')['permission']=='OUTPUT'
 d=core.read(f/'playable/load-evidence/case-0/receipt.json');events=[e for group in d['package']['approved_hq']for e in group.get('events',[])if e['type']=='native_thorns_retracted'];assert events and all(e['platform_removed']is False for e in events)
 facts['hq09']=dict(initialTopOutput=True,thornsRetractedByNativeEvents=events,topPlatformRetained=True)
 bonus=OUT/'fixtures/lift-optional-chest-v1/reward-evidence.json';assert core.read(bonus)['actualCoins']==4
 facts['lift']=dict(realOptionalReward=physics.artifact(bonus),formalQualified=False)
 core.write(OUT/'verification/native-mechanics-audit.json',dict(passed=True,rows=facts,playerOrResourcesWritten=False,readOnly=True,source=physics.artifact(__file__)))
 print('R063_NATIVE_MECHANICS_AUDIT_PASS',cases,count,flush=True)
if __name__=='__main__':main()
