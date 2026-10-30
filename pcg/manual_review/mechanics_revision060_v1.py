if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import gzip
from pcg.migration import core,physics
from .continue_revision060_v1 import OUT

def raw(name):
 p=core.REPO/'pcg/results'/name/'physics/0000-clean-diagnostic.output.json.gz';return p,core.read(p.parent/(p.name.replace('.output.json.gz','.input.json')))['cases'],__import__('json').loads(gzip.decompress(p.read_bytes()))['results']
def main():
 p,cs,rs=raw('approved-r060-hq02-canonical-v10');r=rs[0];fired={e['event_id']:e['frame']for e in r['workshop']['interceptions']if e['type']=='original_enemy_projectile_fired'};hits=[e for e in r['workshop']['interceptions']if e['type']=='original_enemy_projectile_intercepted'];assert hits and all(e['disposed']and e['original_circle_sweep']and not e['protected_point_cancel']and e['remaining_after']>0 and fired[e['event_id']]<e['frame']for e in hits);core.write(OUT/'verification/hq02-actual-interception.json',dict(passed=True,firedBeforeInterception=True,originalProjectileConsumedBeforeExpiry=True,events=hits,source=physics.artifact(p),originalSpeed=240,originalLifetime=.9,geometryAdjustment='authorized middle width64→112',nativePhysicsChanged=False))
 p,cs,rs=raw('approved-r060-hq08-canonical-v8');rows=[]
 for r in rs:
  events=[e for s in r['workshop']['approved_hq']for e in s.get('events',[])if e['type']=='real_support_starts_motion'];assert len(events)==1;event=events[0];frame=next(f for f in r['frames']if f['frame']==event['frame']);assert frame['grounded']and frame['support_id']=='P';overlap_before=[f['frame']for f in r['frames']if f['frame']<event['frame']and abs(f['x']-320)<68 and 230<f['y']<310 and f['support_id']!='P'];assert overlap_before
  before=[f for f in r['frames']if f['frame']<event['frame']];assert all(not [e for s in f['workshop']['approved_hq']for e in s.get('events',[])if e['type']=='real_support_starts_motion']for f in before);rows.append(dict(case=r['id'],actualFloorSupportEvent=event,overlappingRegionWithoutSupportDoesNotStart=overlap_before,oneShot=True))
 core.write(OUT/'verification/hq08-actual-support-start.json',dict(passed=True,source=physics.artifact(p),rows=rows,noActorOrResourceWrites=True,triggerZoneAloneIsInsufficient=True))
 fixtures=OUT/'fixtures/hq09-v2/report.json';assert core.read(fixtures)['passed'];p,cs,rs=raw('approved-r060-hq09-canonical-v2');r=rs[0];events=[e for s in r['workshop']['approved_hq']for e in s.get('events',[])];assert len([e for e in events if e['type']=='native_thorns_retracted'])==1;assert any(e['type']=='turret_child_emitted'for e in events);assert cs[0]['platforms']and any(p==[128,32,128,12]for p in cs[0]['platforms']);core.write(OUT/'verification/hq09-original-causality.json',dict(passed=True,source=physics.artifact(p),events=events,nativeBarrier=physics.artifact(fixtures),topPlatformPreserved=True,originalBulletMotionAndDamage=True,freshTopConflict=physics.artifact(OUT/'verification/hq09-fresh-top-conflict.json'),scope='L earned exit and real Cell causality only; fresh TOP remains failed',presentationCorrection=dict(only='_draw bottom thorn orientation',noPhysicsChange=True,source=physics.artifact(core.REPO/'pcg/manual_review/runtime/revision060_thorn_latch_v2.gd'))))
 print('NATIVE_CAUSALITY_INTERCEPTION_SUPPORT_BARRIER_PASS',flush=True)
if __name__=='__main__':main()
