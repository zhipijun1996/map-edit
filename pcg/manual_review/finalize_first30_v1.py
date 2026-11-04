"""Freeze reviewed implementations, then use existing full protocol and packages.

No geometry selection, threshold changes or automatic retries are performed.
"""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import argparse,copy,shutil
from pcg.migration import core,physics,holdout_guard,godot_package
from pcg.prototype.factory.core.quality import digest
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
from .first30_content_v2 import decode

AUTH=core.REPO/'feedback/manual-review/implementation-results/first-30-v2/authorization'
ROOT=core.REPO/'pcg/manual_review/implementation/first-30-final-v1'

def folder_for(row):return ROOT/row['moduleId']

def freeze(row):
    n=row['reviewId'];old=core.REPO/row['outputDirectory'];folder=folder_for(row)
    if folder.exists():raise ValueError('already_frozen:'+n)
    doc=core.read(old/'module.mapnote.json');g=doc['generationContract'];cases=core.read(old/'cases.json')['cases']
    if n=='17':
        # Fresh C is not the design's earned-return state. Keep its failed
        # diagnostics and qualify outbound only; the actual loop is separate.
        cases=cases[:1]
        core.write(folder/'same-world-return-cases.json',core.read(old/'same-world-return-cases.json'))
        for route in g['routes']:
            if route['from']=='C':route['initialConditions']=dict(status='partial',requires='bridge state earned in same-world A-C-A',freshC='UNKNOWN',witness='same-world-return-cases.json')
    b=g['space']['bounds'];ports={}
    for p in g['ports']:
        x,y=p['position'];nx,ny=p['normal'];edge={'LEFT':'W','RIGHT':'E','TOP':'N','BOTTOM':'S'}[p['face']]
        cell=[int((x-b['x'])//128),int((y-b['y'])//128)]
        if edge=='E':cell[0]-=1
        if edge=='S':cell[1]-=1
        grid=dict(cell=cell,edge=edge,stagingPosition=p['stagingPosition'])
        if p['surface']=='ROCK':grid['profile']='ground64/v1'
        elif p['surface']=='AIR':grid['profile']='UNKNOWN'
        p['grid']=grid
        if p['surface']=='AIR':
            p['motion']=dict(ingress=dict(directions=[[0,1]],modes=['fall'])if p['permission']=='INPUT'else dict(directions=[],modes=[]),egress=dict(directions=[[0,1]],modes=['fall'])if p['permission']=='OUTPUT'else dict(directions=[],modes=[]))
        ports[p['id']]=dict(id=p['id'],position=p['position'],normal=p['normal'],stagingPosition=p['stagingPosition'],grid=grid,crossing_offset=p.get('crossing_offset',[0,0]),aperture=[x-32,y-32,64,64])
    for c in cases:
        c['block_ports']=copy.deepcopy(ports);c['id']='approved-first30-final-v1-'+n+'-'+c['route_spec']['id']
        for k in ('module_sha256','recorded_frames','factory_evidence','noise'):c.pop(k,None)
    if n=='17':
        loop=core.read(folder/'same-world-return-cases.json')
        for c in loop['cases']:c['block_ports']=copy.deepcopy(ports)
        core.write(folder/'same-world-return-cases.json',loop)
    impl=g['generation']['approvedImplementation'];impl.update(runtimeSource=physics.artifact(core.REPO/'pcg/manual_review/runtime/first30_runner_v2.gd'),decoderSource=physics.artifact(core.REPO/'pcg/manual_review/first30_content_v2.py'),observerSource=physics.artifact(core.REPO/'pcg/manual_review/first30_author_v2.py'),controlProgramsSha256=digest([c['control_plan']for c in cases]))
    g['staticChecks']['result']='UNKNOWN'
    core.write(folder/'module.mapnote.json',doc);static=core.contract(folder/'module.mapnote.json',refresh=True)
    core.write(folder/'static-check.json',static)
    core.write(folder/'cases.json',dict(cases=cases));core.write(folder/'physics-input-cases.json',dict(cases=cases))
    core.write(folder/'migration.json',core.read(old/'migration.json'))
    core.write(folder/'parameters.json',dict(designVersion=row['designVersion'],authorization=physics.artifact(AUTH/'request.json'),designGeometryChanged=False,content=decode(doc),ports=g['ports'],controls=[dict(route=c['route_spec'],control_plan=c['control_plan'],max_frames=c['max_frames'])for c in cases],conditionalReturn=n=='17'))
    core.write(folder/'frozen.json',{k:physics.artifact(folder/v)for k,v in dict(module='module.mapnote.json',cases='physics-input-cases.json',parameters='parameters.json').items()})
    print(n,'frozen',len(cases),flush=True)

def qualify(row):
    folder=folder_for(row);n=row['reviewId'];frozen=core.read(folder/'frozen.json');core.verify_artifacts(list(frozen.values()))
    cases=core.read(folder/'physics-input-cases.json')['cases'];doc=core.read(folder/'module.mapnote.json')
    costs=dict(routes=sum((36 if c.get('enemies')or c.get('saws')or c.get('moving_platforms')else 25)*2 for c in cases),boundaries=len(physics.seam_cases(cases[0],doc))+2*len(cases),counters=sum(len(physics.counter_cases(c))for c in cases))
    assert sum(costs.values())<=core.read(physics.FULL_PROTOCOL)['maximumAttemptsPerModule']
    guard=holdout_guard.check(folder,protocol_path=physics.FULL_PROTOCOL)
    core.write(folder/'preflight.json',dict(protocol=physics.artifact(physics.FULL_PROTOCOL),guard=guard,costs=costs,maximumAttempts=sum(costs.values()),selection='one frozen implementation; no retries or holdout selection',canonicalEvidence='preserved preceding canonical and native runs',stopping='calibration failure skips that route holdout; all failures retained'))
    report=physics.run(folder,'approved-b001-first30-'+n+'-qualified-final-v1',protocol_path=physics.FULL_PROTOCOL)
    core.write(folder/'qualification.json',dict(report=physics.artifact(core.REPO/'pcg/results'/('approved-b001-first30-'+n+'-qualified-final-v1/migration-physics.json')),passed=report['passed'],actualAttempts=report['actualAttempts']))
    print(n,'qualified',report['passed'],report['actualAttempts'],flush=True)

def deliver(row):
    folder=folder_for(row);n=row['reviewId']
    eng,cases,authors=physics._engine(folder,'approved-b001-first30-'+n+'-delivery-final-v1',physics.FULL_PROTOCOL)
    items=[];checks=[]
    for i,(c,r,e)in enumerate(eng.run([physics.fresh(c,'delivery-final')for c in cases],'native-delivery-final')):
        q=checked_purpose(authors[i],c,r);checks.append(dict(case=c,check=q,evidence=e))
        if q['ok']:items.append(physics._recording(c,r))
        print(n,c['route_spec']['id'],q['ok'],q['reasons'],flush=True)
    core.write(eng.out/'canonical.json',dict(rows=checks,passed=len(items)==len(cases)))
    if len(items)!=len(cases):raise ValueError('canonical_delivery_failed')
    core.write(folder/'playback-cases.json',dict(cases=items))
    godot_package.compile_package(folder/'module.mapnote.json',folder/'playback-cases.json',folder/'playable',stable_id=row['moduleId'])
    result=godot_package.run_package_validation(folder/'playable');core.write(folder/'package-result.json',result)
    print(n,'native',result['passed'],len(items),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['freeze','qualify','deliver']);p.add_argument('ids',nargs='+');a=p.parse_args()
    for row in core.read(AUTH/'handoff.json')['rows']:
        if row['reviewId']in a.ids:globals()[a.action](row)
