"""Aim within actual enemy body, keep the player grounded and alternate shots."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import inspect,copy
from pcg.migration import core,godot_package,physics
from pcg.manual_review.repair_clarified_three_v1 import OUT,rows
from pcg.manual_review import search_clarified_three_v1 as old
from pcg.manual_review.prepare_review029_v1 import at,end
from pcg.manual_review.repair_review029_v2 import axis

def programs(n,base):
 for offset in [-8,-10,-6]:
  plans=[]
  for c in base:
   right=c['route_spec']['from_port']=='entry';x=476 if right else 548;order=['design-ambush-left','design-ambush-right']if right else['design-ambush-right','design-ambush-left'];p=at(x,420)+[axis(0)]
   for _ in range(3):
    for ident in order:p.append(dict(op='shoot',aim_cell=dict(kind='enemy',id=ident,body_offset=[0,offset]),trigger=dict(state='shot_ready',timeout=150)))
   plans.append(p+end(616 if right else 408,420))
  yield dict(startX=476,enemyBodyOffsetY=offset,pendingShotGuard=True,originalControllerCooldownWindow=True),plans
if __name__=='__main__':
 row=next(r for r in rows()if r['reviewId']=='171');folder=core.REPO/row['outputDirectory'];cs=core.read(folder/'cases.json')['cases'];core.write(folder/'history/pre-driver-v3-cases.json',dict(cases=cs))
 for c in cs:c['generation_rule']['registration_source']='pcg/manual_review/clarified_three_author_v3.py'
 core.write(folder/'cases.json',dict(cases=cs));d=godot_package.bind_case_behavior(core.read(folder/'module.mapnote.json'),cs);core.write(folder/'module.mapnote.json',d);core.contract(folder/'module.mapnote.json',refresh=True)
 core.write(OUT/'development/171-native-ready-window-v3.json',dict(reason='Original Controller advances cooldown before consuming a shot. Use its actual next-tick window; aim upper body to keep recoil into floor rather than waiting through a false airborne refill. Original weapon, resources, enemy health, geometry unchanged.',fixedOffsets=[-8,-10,-6],maximumTrials=78,noJump=True,alternatingShots=True,noHoldoutObserved=True))
 source=inspect.getsource(old.run).replace("n+'-domain.json'","n+'-ready-domain-v3.json'").replace("'approved-c3-'+n+'-screen-'","'approved-c3-'+n+'-ready-screen-'").replace("folder/('search/candidate-'","folder/('search-ready/candidate-'")
 scope={**old.__dict__,'programs':programs};exec(compile(source,__file__,'exec'),scope);scope['run'](row)
