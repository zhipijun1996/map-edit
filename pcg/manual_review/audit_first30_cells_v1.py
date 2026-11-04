"""Real Cell/contact and AIR-boundary tests, distinct from route qualification."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy
from pcg.migration import core,physics
from pcg.prototype.workshop.rules import cmd
from .finalize_first30_v1 import AUTH,folder_for

def main():
    rows={r['reviewId']:r for r in core.read(AUTH/'handoff.json')['rows']}
    folder=folder_for(rows['06']);eng,cases,_=physics._engine(folder,'approved-b001-first30-06-cell-audit-v1',physics.FULL_PROTOCOL)
    base=cases[1];test=[]
    for count in (1,2):
        c=physics.fresh(base,'cell-'+str(count)+'-projectiles');c['control_plan']=copy.deepcopy(base['control_plan'][:8])
        for _ in range(count):c['control_plan'] += [dict(op='wait',trigger=dict(state='grounded_shot_ready',timeout=120)),cmd('shoot',aim_cell=dict(kind='bell',id='upper-route-gears')),cmd('wait',30)]
        c.update(goal=[553,608,14,8],settle_frames=90,max_frames=600);test.append(c)
    c=physics.fresh(base,'cell-initial-contact-negative');c.update(spawn=[432,270],entry_port=[432,270],control_plan=[cmd('wait',120)],max_frames=120);test.append(c)
    checks=[]
    for i,(c,r,e)in enumerate(eng.run(test,'actual-projectile-toggle-and-contact')):
        groups=r.get('workshop',{}).get('retractable_groups',[])
        if i<2:
            g=groups[0]if groups else {};expected=i+1
            passed=g.get('toggle_count')==expected and g.get('extended')==(expected%2==0) and g.get('band_enabled')==[expected%2==0]*2 and r.get('hp')==5 and not r.get('returns')
        else:passed=bool(r.get('damage_commits')or r.get('returns')or r.get('hp',5)<5)
        checks.append(dict(id=c['id'],passed=passed,group=groups,hp=r.get('hp'),damage=r.get('damage_commits'),returns=r.get('returns'),evidence=e))
        print('Cell',i,passed,groups,flush=True)
    core.write(eng.out/'audit.json',dict(passed=all(c['passed']for c in checks),checks=checks,staticPlatformsChanged=False))
    for n in ('12','23'):
        folder=folder_for(rows[n]);eng,cases,_=physics._engine(folder,'approved-b001-first30-'+n+'-air-audit-v1',physics.FULL_PROTOCOL);doc=core.read(folder/'module.mapnote.json')
        probes=[c for c in physics.seam_cases(cases[0],doc)if c.get('air_goal_probe')];checks=[]
        for c,r,e in eng.run(probes,'actual-air-local-probes'):
            q=physics.crossing(c,r);checks.append(dict(id=c['id'],check=q,reason=r.get('reason'),plan_error=r.get('plan_error'),evidence=e));print('AIR',n,c['id'],q['passed'],r.get('reason'),flush=True)
        core.write(eng.out/'audit.json',dict(passed=all(v['check']['passed']for v in checks),checks=checks))

if __name__=='__main__':main()
