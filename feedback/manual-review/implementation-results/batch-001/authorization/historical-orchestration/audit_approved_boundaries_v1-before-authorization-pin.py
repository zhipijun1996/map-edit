"""Complete observer metadata; reanalyse seen trajectories without new holdout.

No collision, spawn, control, resource, or geometry value is changed. The first
N06 qualifier's budget violation remains invalid, even when observations pass.
"""
import copy
import gzip
import json
from pcg.migration import core, physics
from pcg.prototype.creative_batches.batch30_blockpilot.rules_v1 import block_port


def metadata():
    for row in core.read(core.REPO/'feedback/manual-review/implementation-handoff-v1.json')['rows']:
        folder=core.REPO/row['outputDirectory'];before=core.read(folder/'cases.json')['cases'];cases=copy.deepcopy(before)
        if (folder/'physics-input-cases.json').exists():raise ValueError('immutable_boundary_metadata_exists')
        for c in cases:
            for key,p in c['block_ports'].items():
                cell=[int(p['position'][0]//128)-(1 if p['face']=='RIGHT' else 0),int(p['position'][1]//128)]
                c['block_ports'][key]=dict(block_port(key,cell,'W' if p['face']=='LEFT' else 'E',p['stagingPosition']),face=p['face'],surface=p['surface'],permission=p['permission'])
        assert [{k:v for k,v in c.items() if k!='block_ports'} for c in before]==[{k:v for k,v in c.items() if k!='block_ports'} for c in cases]
        core.write(folder/'physics-input-cases.json',dict(cases=cases))
        core.write(folder/'boundary-binding.json',dict(before=physics.artifact(folder/'cases.json'),after=physics.artifact(folder/'physics-input-cases.json'),
            changedFields=['block_ports.*.aperture','block_ports.*.grid','block_ports.*.crossing_offset'],
            physicalProgramChanged=False,geometryChanged=False,source=physics.artifact(__file__)))


def audit01():
    row=core.read(core.REPO/'feedback/manual-review/implementation-handoff-v1.json')['rows'][0];folder=core.REPO/row['outputDirectory']
    previous=core.REPO/'pcg/results/approved-b001-01-qualified-v2';report=core.read(previous/'migration-physics.json')
    out=core.REPO/'pcg/results/approved-b001-01-boundary-audit-v3'
    engine,cases,authors=physics._engine(folder,out.name,physics.FULL_PROTOCOL)
    core.write(out/'protocol.json',dict(maximumAdditionalCases=84,maximumCumulativeFrozenCases=984,
        selection='No new calibration/holdout, no parameter selection; reanalyse existing 36 probes, run 12 missing ingress and 72 original counter policies.',
        priorInvalidQualifier=physics.artifact(previous/'migration-physics.json'),
        priorViolation='900 actual attempts exceed selected legacy v1 maximum 350; original qualification remains INVALID_BUDGET',
        source=physics.artifact(__file__)))
    replay=[]
    for item in core.read(previous/'boundary-probes.json'):
        ev=item['evidence'];raw=json.loads(gzip.decompress((previous/ev['output']).read_bytes()))['results'][ev['index']]
        c=core.read(previous/'physics'/(ev['batch']+'.input.json'))['cases'][ev['index']]
        c['block_ports']=copy.deepcopy(cases[0]['block_ports'])
        replay.append(dict(id=c['id'],check=physics.crossing(c,raw),evidence=ev,run=previous.name))
    probes=[]
    for c,r,e in engine.run([physics.continuous_entry(c,core.read(folder/'module.mapnote.json')) for c in cases],'missing-ingress'):
        probes.append(dict(id=c['id'],check=physics.crossing(c,r),evidence=e))
    canonical=core.REPO/'pcg/results/approved-b001-01-canonical-v2';baselines={}
    for item in core.read(canonical/'canonical.json')['rows']:
        e=item['evidence'];raw=json.loads(gzip.decompress((canonical/e['output']).read_bytes()))['results'][e['index']];baselines[item['routeId']]=raw
    counters=physics._run_counters(engine,cases,authors,'fixed-counters-no-new-holdout',baselines)
    core.write(out/'boundary-reanalysis.json',dict(previousRaw=physics.artifact(previous/'batches.json'),metadata=physics.artifact(folder/'boundary-binding.json'),reanalysed=replay,newIngress=probes))
    core.write(out/'counterexamples.json',counters)
    core.write(out/'audit-result.json',dict(actualAdditionalAttempts=engine.sim.cases,priorAttempts=report['actualAttempts'],
        boundaryObservationsPass=all(v['check']['passed'] for v in replay+probes),
        countersInvalidating=sum(v['adjudication']['invalidates_design'] for v in counters),
        qualification='INVALID_BUDGET_PRESERVED',freshIndependentHoldout=False,
        directionalObservations=[dict(routeId=v['routeId'],observedRegularRatesPassed=v['passed']) for v in report['routes']]))
    assert engine.sim.cases==84


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('action',choices=['metadata','audit01']);a=p.parse_args();globals()[a.action]()
