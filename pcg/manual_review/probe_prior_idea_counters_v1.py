"""Four remaining preregistered low-cost counters; frozen controls and holdouts untouched."""
import copy
from pcg.migration import core,physics
from .new_ideas_v1 import rows,label,AUTH
from .finalize_ideas_v1 import folder_for
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose

def main():
    for row in rows():
        if label(row)=='orbit':continue
        folder=folder_for(row);eng,cases,authors=physics._engine(folder,'approved-lift-'+label(row)+'-additional-counters-v1',physics.FULL_PROTOCOL)
        original=next(c for c in cases if c['route_spec']['id']=='A-to-B');author=authors[cases.index(original)]
        baseline=core.read(core.REPO/('pcg/results/approved-ideas-'+label(row)+'-delivery-final-v1/canonical.json'))['rows'][0]['check']
        probes=[]
        for kind in ['omit-final-shot','reuse-first-enemy']:
            c=physics.fresh(original,kind)
            if kind=='omit-final-shot':
                index=max(i for i,p in enumerate(c['control_plan'])if p['op']=='shoot');del c['control_plan'][index]
            else:
                first=True
                for command in c['control_plan']:
                    if not command.get('chain_window'):continue
                    if first:first=False;continue
                    command['aim_cell']=dict(kind='enemy',id='enemy-1');command.pop('chain_window');command['trigger']['state']='shot_ready'
            c['migration_counter']=dict(kind=kind,originalRouteId='A-to-B',finiteProbeOnly=True)
            probes.append(c)
        results=[]
        for c,r,e in eng.run(probes,'remaining-approved-counters'):
            judgment=physics._counter_judgment(c,r,author,baseline=baseline)
            results.append(dict(id=c['id'],check=judgment,evidence=e));print(label(row),c['migration_counter']['kind'],r['ok'],judgment['causalCheck']['reasons'],flush=True)
        core.write(eng.out/'counter-checks.json',dict(rows=results,authorization=physics.artifact(AUTH/'request.json'),chargedToOriginal48ExtraFixtures=2,newFormalOrHoldout=False,doesNotSelectAnotherControlVersion=True))
if __name__=='__main__':main()
