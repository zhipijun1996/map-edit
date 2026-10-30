if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy
from pcg.migration import core,physics
from .continue_revision060_v1 import rows,label,OUT
from .prepare_revision060_v1 import aim,wait
from .prepare_review045_v1 import at,end
from .prepare_revision058_v2 import jump
from .prepare_ideas_v1 import settle
from pcg.prototype.workshop.rules import cmd

def main():
 r=next(r for r in rows()if label(r)=='hq09');f=core.REPO/r['outputDirectory'];c=copy.deepcopy(core.read(f/'cases.json')['cases'][0]);out=OUT/'fixtures/hq09-v1';assert not out.exists();doc=core.read(f/'module.mapnote.json');core.write(out/'module.mapnote.json',doc)
 blocked=copy.deepcopy(c);blocked.update(id='r060-hq09-original-child-blocked',control_plan=at(100,334)+[aim(176,352),cmd('wait',120)]+end(24,334));blocked['generation_rule']['registration_source']='pcg/manual_review/revision060_fixture_author_v1.py'
 cross=copy.deepcopy(c);cross.update(id='r060-hq09-player-cross-projectile-only',control_plan=at(90,334)+jump(320,24),max_frames=90);cross['generation_rule']['registration_source']='pcg/manual_review/revision060_fixture_author_v1.py'
 core.write(out/'cases.json',dict(cases=[blocked,cross]));eng,cs,authors=physics._engine(out,'approved-r060-hq09-native-cell-fixtures-v1',physics.FULL_PROTOCOL);rr=[]
 for c,raw,e in eng.run(cs,'original-cell-fixtures'):rr.append(dict(case=c,raw=raw,evidence=e))
 b,x=rr;child=[v for v in b['raw'].get('barrier_evidence',[])if v['faction']=='turret_shot'and v['original_spent']and v['remaining_after_dispose']>0];assert child
 events=[e for s in b['raw']['workshop']['approved_hq']for e in s.get('events',[])];assert any(e['type']=='turret_child_emitted'for e in events)and not any(e['type']=='native_thorns_retracted'for e in events)
 overlaps=[f for f in x['raw']['frames']if abs(f['x']-320)<20 and 166<f['y']<314 and not f['grounded']and f['support_id']!='P'];assert overlaps
 core.write(out/'report.json',dict(passed=True,kind='targeted original Cell evidence; not route qualification',projectile=child,playerPassThroughFrames=[f['frame']for f in overlaps],expectedPlayerProbeMayEndOutside=True,routeProbeOutcome=x['raw']['reason'],receipts=[dict(id=r['case']['id'],evidence=r['evidence'])for r in rr],originalPhysics=True,actorResourcesChanged=False));print('HQ09_CELL_FIXTURES_PASS',len(overlaps),flush=True)
if __name__=='__main__':main()
