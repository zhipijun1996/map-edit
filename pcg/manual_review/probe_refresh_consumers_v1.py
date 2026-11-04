"""Three preregistered actual mechanism probes, separate from route qualification."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy
from pcg.migration import core,physics
from pcg.prototype.workshop.engine import WorkshopEngine
from pcg.prototype.workshop.rules import cmd,settle
from .prepare_review_refresh_v1 import at,end
from .probe_review_refresh_v1 import AUTH

def main():
    rows={r['reviewId']:r for r in core.read(AUTH/'handoff.json')['rows']};cases=[]
    for n in ('116','147','147'):
        c=copy.deepcopy(core.read(core.REPO/rows[n]['outputDirectory']/'cases.json')['cases'][0]);c['generation_rule']['registration_source']='pcg/manual_review/review_refresh_author_v2.py';c['migration_counter']=dict(kind='mechanism-observation',notNominalRoute=True);c['max_frames']=1400;cases.append(c)
    c=cases[0];c['id']='approved-r024-116-real-carrier-support-probe';bell=c['latches'][0]['id'];c['control_plan']=at(130,282)+[cmd('shoot',aim_cell=dict(kind='bell',id=bell)),settle(24),cmd('wait',240)]+end(24,282);c['goal']=[19,278,10,8]
    source=cases[1];bell=source['latches'][0]['id'];first=next(i for i,v in enumerate(source['control_plan'])if v.get('aim_cell',{}).get('kind')=='bell');prefix=copy.deepcopy(source['control_plan'][:first+1])
    source['id']='approved-r024-147-expiry-reopen-restart';source['control_plan']=prefix+[cmd('wait',300),cmd('shoot',aim_cell=dict(kind='bell',id=bell)),cmd('wait',40),cmd('shoot',aim_cell=dict(kind='bell',id=bell)),cmd('wait',300)]+end(180,282);source['goal']=[175,278,10,8]
    c=cases[2];c['id']='approved-r024-147-body-safe-close';c['control_plan']=copy.deepcopy(prefix)+at(520,282)+[dict(op='wait',latch_id=bell,seconds_left=.08,trigger=dict(state='latch_expiring',timeout=480)),cmd('jump'),cmd('jump_release'),cmd('wait',60)]+end(520,282);c['goal']=[515,278,10,8]
    author=physics.author_for(cases[0]);runner=physics.runner_for(cases[0],author);eng=WorkshopEngine(core.REPO/'pcg/results/approved-r024-consumer-probes-v1',batch_size=3,extra_sources=[__file__,*physics.author_sources([author],runner)],runner_script=runner);physics.deduplicate_snapshot(eng.out)
    core.write(eng.out/'protocol.json',dict(maximumAttempts=3,cases=cases,newIndependentHoldout=False,criteria=['real enemy/platform carry through native move_and_collide, actual relative feet retained','G1 expires, can reopen after expiry, another hit while open restarts timer; G2 stays closed','expired G1 remains open while actual body overlaps, closes after clearance; hp5/no reset'],stopping='three fixed clean probes; no retries'))
    results=[]
    for i,(c,r,e)in enumerate(eng.run(cases,'actual-mechanism-observations')):
        fs=r.get('frames',[]);proof=dict(id=c['id'],evidence=e,rawOk=r.get('ok'),rawReason=r.get('reason'),hp=r.get('hp'),returns=r.get('returns'),notNominalRoute=True)
        if i==0:
            active=[f for f in fs if f.get('refresh_consumers')and f['refresh_consumers'][0]['carried_frames']>0];dist=max((f['refresh_consumers'][0]['carried_distance']for f in active),default=0);support=[]
            for f in active:
                enemy=f['plains']['enemies'][0];p=f['moving_platforms'][0];support.append(abs((enemy['y']+16)-(p['position'][1]-12)))
            proof.update(carriedDistance=dist,maximumFeetError=max(support,default=None),passed=dist>=50 and bool(support)and max(support)<=.3)
        else:
            g1=c['latches'][0]['id'];g2=c['latches'][1]['id'];opens=[v for v in r.get('plains',{}).get('events',[])if v.get('type')=='bell_open'and v['id']==g1];state=lambda f,ident:next(v for v in f['plains']['bells']if v['id']==ident)
            if i==1:
                closed_between=bool(len(opens)>=2 and any(not state(f,g1)['open']for f in fs if opens[0]['frame']<f['frame']<opens[1]['frame']));proof.update(actualOpenEvents=opens,closedBetween=closed_between,G2NeverOpened=all(not state(f,g2)['open']for f in fs),passed=r.get('ok')and r.get('hp')==5 and not r.get('returns')and len(opens)==3 and closed_between and all(not state(f,g2)['open']for f in fs))
            else:
                gate=c['latches'][0]['gate'];gx,gy,w,h=gate;deadline=opens[0]['frame']+240 if opens else 10**9;overlap=[f for f in fs if f['frame']>=deadline and f['x']+12>gx and f['x']-12<gx+w and f['y']+18>gy and f['y']-18<gy+h];proof.update(expiryFrame=deadline,overlapFrames=[f['frame']for f in overlap],closedAtEnd=bool(fs and not state(fs[-1],g1)['open']),passed=r.get('ok')and r.get('hp')==5 and not r.get('returns')and bool(overlap)and all(state(f,g1)['open']for f in overlap)and not state(fs[-1],g1)['open'])
        results.append(proof);print(proof['id'],proof['passed'],proof.get('rawReason'),flush=True)
    core.write(eng.out/'mechanism-checks.json',dict(rows=results,passed=all(v['passed']for v in results),newIndependentHoldout=False,notRouteQualification=True))
if __name__=='__main__':main()
