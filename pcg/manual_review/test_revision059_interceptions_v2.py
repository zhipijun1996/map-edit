import copy
from pathlib import Path
from pcg.migration import core,physics
from .continue_revision059_v1 import rows,label,OUT
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose

def main():
 r=next(r for r in rows()if label(r)=='hq02');f=core.REPO/r['outputDirectory'];fixture=core.REPO/'pcg/manual_review/implementation/revision-059-fixtures-v1/hq02-interception';cs=core.read(f/'cases.json')['cases'][:1]
 for c in cs:c['generation_rule']['registration_source']='pcg/manual_review/revision059_interception_author_v1.py'
 for name in ['module.mapnote.json','migration.json']:core.write(fixture/name,core.read(f/name))
 core.write(fixture/'cases.json',dict(cases=cs));eng,cs,authors=physics._engine(fixture,'approved-r059-hq02-original-intercept-v2',physics.FULL_PROTOCOL)
 # Driver is input-identical; this supplementary fixture only observes original collision/disposal.
 checks=[]
 for c,raw,e in eng.run([physics.fresh(cs[0],'original-intercept')],'original-live-projectile-interception'):
  events=raw.get('workshop',{}).get('interceptions',[]);hits=[x for x in events if x['type']=='original_enemy_projectile_intercepted'and x.get('disposed')and x['remaining_after']>0 and x['platform_id']=='P'];checks.append(dict(passed=bool(hits),original_events=events,evidence=e,route=checked_purpose(authors[0],c,raw)))
 core.write(eng.out/'interception-check.json',dict(passed=all(x['passed']for x in checks),rows=checks,newPhysicsAttempts=1,readOnlyObserver=True));print('HQ02_REAL_INTERCEPT',checks[0]['passed'])
if __name__=='__main__':main()
