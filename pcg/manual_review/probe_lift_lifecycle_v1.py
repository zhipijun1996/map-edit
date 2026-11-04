"""Real enemy depletion, retreat/reentry and unchanged post-death ascent policy."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy
from pcg.migration import core,physics
from .lift_idea_v1 import rows,AUTH
from .prepare_review045_v1 import at
from pcg.prototype.workshop.rules import cmd

def main():
    row=rows()[0];folder=core.REPO/row['outputDirectory'];eng,cases,_=physics._engine(folder,'approved-lift-lifecycle-v1',physics.FULL_PROTOCOL)
    c=physics.fresh(cases[0],'depletion-retreat-reentry')
    doc=core.read(folder/'module.mapnote.json');port=next(p for p in doc['generationContract']['ports']if p['id']=='A');neighbor=physics.exterior_floor(c,port);outside=[192,neighbor['floor'][1]-18]
    original=copy.deepcopy(c['control_plan']);c['control_plan']=[]
    for _ in range(20):
        c['control_plan']+=[dict(op='shoot',aim_cell=dict(kind='enemy',id='air-enemy'),direction=[0,-1],trigger=dict(after=40,state='grounded_shot_ready',timeout=120))]+at(192,846)
    c['control_plan']+=[cmd('wait',60),cmd('drop_through',1)]+at(*outside)+[cmd('jump'),cmd('jump_release',24)]+at(192,846)+original
    c['max_frames']=4800
    results=[]
    for case,raw,evidence in eng.run([c],'original-enemy-lifecycle'):
        enemies=[f['plains']['enemies'][0]for f in raw['frames']]
        dead_at=next((i for i,e in enumerate(enemies)if e['dead']),None)
        dead_after=dead_at is not None and all(e['dead'] and e['hp']==0 for e in enemies[dead_at:])
        outside_frames=[f['frame']for f in raw['frames']if f['y']-18>896 and abs(f['x']-192)<=20]
        check=dict(realEnemyDeath=dead_at is not None,firstDeadFrame=dead_at,deathPersists=dead_after,outsideRetreatFrames=outside_frames,actualActorEpochs=sorted({f['actor_epoch']for f in raw['frames']}),worldReturns=raw['returns'],postDepletionAscentReached=raw['ok'],reason=raw['reason'],hp=raw['hp'],alternateDeadEnemyControls='UNKNOWN',autoRespawnAdded=False,nominalPolicyChanged=False)
        results.append(dict(check=check,evidence=evidence));print(check,flush=True)
    core.write(eng.out/'lifecycle-checks.json',dict(rows=results,authorization=physics.artifact(AUTH/'request.json'),simulationTrials=1,independentHoldout=False))
if __name__=='__main__':main()
