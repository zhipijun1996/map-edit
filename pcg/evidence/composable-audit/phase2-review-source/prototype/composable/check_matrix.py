"""Exhaustive six-ID contract matrix; NOT six-ID level generation completeness."""
import json,itertools
from contracts import Registry,ContractError
from simulator import ROOT,Simulator

def run():
    names=list(Registry().items);cases=[];expected=[]
    for mask in range(1<<len(names)):
        caps=[n for i,n in enumerate(names) if mask&(1<<i)]
        try:Registry().resolve(caps);valid=True
        except ContractError:valid=False
        cases.append(dict(id=f'matrix-{mask}',capabilities=caps,spawn=[80,420],platforms=[[-120,438,260,60]],wall_platform_indices=[],hooks=[],hazards=[],goal=[70,396,20,48],max_frames=20,settle_frames=6))
        expected.append(valid)
    for caps in (['move','teleport'],['jump','jump']):
        c=dict(cases[0]);c.update(id='invalid-'+str(len(cases)),capabilities=caps);cases.append(c);expected.append(False)
    sim=Simulator(ROOT/'results/composable-contract-matrix-v2');rs=sim.run(cases,'matrix')
    mismatches=[]
    for c,r,valid in zip(cases,rs,expected):
        if (not r.get('rejected',False))!=valid or (valid and not r['ok']):mismatches.append(dict(id=c['id'],expected=valid,result=r))
        if valid:
            s=r['capability_snapshot']
            for cap,field in [('move','move_enabled'),('jump','jump_enabled'),('shot_recoil','shoot_enabled'),('double_jump','double_enabled'),('grapple','grapple_enabled'),('wall_climb','wall_enabled')]:
                if s[field]!=(cap in c['capabilities']):mismatches.append(dict(id=c['id'],field=field))
    summary=dict(subsets=64,legal_subsets=sum(expected),invalid_subsets=64-sum(expected),additional_negative_cases=2,physical_stationary_positive_cases=sum(r['ok'] for r in rs),mismatches=mismatches,scope='Binding and rejection matrix; only 16 move+jump optional-capability sets have generated challenge coverage.')
    (sim.out/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
    if mismatches:raise SystemExit(1)
if __name__=='__main__':run()
