"""Aim within actual enemy body, keep the player grounded and alternate shots."""
import inspect,copy
from pcg.migration import core,godot_package,physics
from pcg.manual_review.repair_clarified_three_v1 import OUT,rows
from pcg.manual_review import search_clarified_three_v1 as old
from pcg.manual_review.prepare_review029_v1 import at,end
from pcg.manual_review.repair_review029_v2 import axis

def programs(n,base):
 for offset in [-8,-10]:
  plans=[]
  for c in base:
   right=c['route_spec']['from_port']=='entry';x=476 if right else 548;order=['design-ambush-left','design-ambush-right']if right else['design-ambush-right','design-ambush-left'];p=at(x,420)+[axis(0)]
   for _ in range(3):
    for ident in order:p += [dict(op='shoot',aim_cell=dict(kind='enemy',id=ident,body_offset=[0,offset]),trigger=dict(state='shot_ready',timeout=150)),axis(-1 if ident.endswith('left')else 1)]
   plans.append(p+end(616 if right else 408,420))
  yield dict(startX=476,enemyBodyOffsetY=offset,pendingShotGuard=True,originalControllerCooldownWindow=True),plans
if __name__=='__main__':
 row=next(r for r in rows()if r['reviewId']=='171');folder=core.REPO/row['outputDirectory'];cs=core.read(folder/'cases.json')['cases'];core.write(folder/'history/pre-walk-policy-v6-cases.json',dict(cases=cs))
 for c in cs:c['generation_rule']['registration_source']='pcg/manual_review/clarified_three_author_v5.py'
 core.write(folder/'cases.json',dict(cases=cs));d=godot_package.bind_case_behavior(core.read(folder/'module.mapnote.json'),cs);core.write(folder/'module.mapnote.json',d);core.contract(folder/'module.mapnote.json',refresh=True)
 core.write(OUT/'development/171-counter-recoil-walk-v6.json',dict(reason='Keep the same no-jump alternating shots; hold movement toward the fired side between shots to counter recoil and move away from the opposite incoming projectile. Native recoil, speed, cooldown, health and geometry unchanged.',fixedOffsets=[-8,-10],maximumTrials=78,noJump=True,alternatingShots=True,noHoldoutObserved=True))
 source=inspect.getsource(old.run).replace("n+'-domain.json'","n+'-walk-domain-v6.json'").replace("'approved-c3-'+n+'-screen-'","'approved-c3-'+n+'-walk-screen-'").replace("folder/('search/candidate-'","folder/('search-walk/candidate-'")
 scope={**old.__dict__,'programs':programs};exec(compile(source,__file__,'exec'),scope);scope['run'](row)
