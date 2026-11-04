if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core,physics
from .continue_revision059_v1 import rows,label
from .prepare_review045_v1 import at,axis
from pcg.prototype.workshop.rules import cmd

def main():
 r=next(r for r in rows()if label(r)=='hq02');f=core.REPO/r['outputDirectory'];fixture=core.REPO/'pcg/manual_review/implementation/revision-059-fixtures-v1/hq02-live-middle';c=core.read(f/'cases.json')['cases'][0];c.update(id='r059-hq02-original-middle-dodge',spawn=[112,338],entry_port=[112,338],goal=[108,335,8,6]);c['generation_rule']['registration_source']='pcg/manual_review/revision059_interception_author_v2.py';p=[axis(0)]
 for i in range(6):p+=[dict(op='wait',trigger=dict(after=1,state='hq_native_seed',timeout=600)),cmd('jump'),cmd('jump_release',24),cmd('shoot',4,direction=[0,1])]+at(112,338)
 c['control_plan']=p
 for name in ['module.mapnote.json','migration.json']:core.write(fixture/name,core.read(f/name))
 core.write(fixture/'cases.json',dict(cases=[c]));eng,cs,_=physics._engine(fixture,'approved-r059-hq02-original-intercept-v3',physics.FULL_PROTOCOL)
 for c,raw,e in eng.run(cs,'six-original-seeds-native-dodge'):
  events=raw.get('workshop',{}).get('interceptions',[]);hits=[x for x in events if x['type']=='original_enemy_projectile_intercepted'and x.get('disposed')and x['remaining_after']>0 and x['platform_id']=='P'];result=dict(passed=bool(hits),original_events=events,evidence=e,playerHp=raw.get('hp'),reason=raw.get('reason'),newPhysicsAttempts=1,originalPhaseAndTimingUnchanged=True,supplementaryLocalFixtureNotWholeRoute=True);core.write(eng.out/'interception-check.json',result);print('REAL_MOVING_TERRAIN_INTERCEPTION',result['passed'],result['playerHp'],result['reason'])
if __name__=='__main__':main()
