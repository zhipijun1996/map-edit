"""First recoil-only demand-adaptation trial, using original production loop.

Two existing action relationships, not new families. Four declared geometry
requests; one frozen rule handles each relationship's bounded parameter domain.
This tests local adaptation, not method-level generalization or whole Map play.
"""
import argparse,copy,json,math
from pathlib import Path
from pcg.prototype.workshop.rules import thorn,brake,launch,settle,cmd,wait_x,reward,specifications
from pcg.prototype.workshop.evaluate import purpose
from pcg.prototype.workshop.counterexamples import alternatives
from pcg.prototype.workshop.production_loop import run
from pcg.prototype.workshop.engine import ROOT
from pcg.map_directed.library import fits

CAPS=['move','jump','shot_recoil']
DEMANDS=[
 dict(id='plains-slot-gap-475-rise8',family='thorn-slot',parameters=dict(landing_front=475,landing_y=430)),
 dict(id='plains-slot-gap-505-rise0',family='thorn-slot',parameters=dict(landing_front=505,landing_y=438)),
 dict(id='plains-brake-lip250-drop273',family='brake-under-ledge',parameters=dict(lip_x=250,pocket_y=453,target_x=100)),
 dict(id='plains-brake-lip246-drop286',family='brake-under-ledge',parameters=dict(lip_x=246,pocket_y=466,target_x=115))]

def specification(d):
    s=copy.deepcopy(next(s for s in specifications()if s['required_family']==d['family']))
    s.update(id=d['id'],objective=dict(relationship=d['family'],parameters=d['parameters'],content_role='recoil practice',method_trial='new geometric demands, original two action relationships'))
    s['rise']=(438 if d['family']=='thorn-slot'else 180)-(d['parameters']['landing_y']if d['family']=='thorn-slot'else d['parameters']['pocket_y'])
    s['budget']=dict(generator_candidates=4,director_revisions=0)
    s['return_conditions']='UNKNOWN; forward exact-demand trial only, lower recovery terrain is not a proven retry route'
    return s

def compiler(request):
    d=request.get('demand',{});f=d.get('family');p=d.get('parameters',{})
    def missing(reason):return dict(status='unsatisfied',gaps=[reason],conflicts=[dict(field='mechanical_demand',reason=reason)],searched=dict(families=['thorn-slot','brake-under-ledge'],maximum_control_candidates=4),negotiable=['declared bounded geometry and recoil-only capabilities; changed direction/recovery needs separate implementation'],cases=[])
    if f not in ['thorn-slot','brake-under-ledge']:return missing('missing recoil-only adaptation rule')
    if f=='thorn-slot':
        if set(p)!= {'landing_front','landing_y'}or not 460<=p.get('landing_front',0)<=510 or not 418<=p.get('landing_y',0)<=450:return missing('outside slot domain: front460..510, top418..450')
    elif set(p)!= {'lip_x','pocket_y','target_x'}or not 240<=p.get('lip_x',0)<=260 or not 438<=p.get('pocket_y',0)<=470 or not 95<=p.get('target_x',0)<=120:return missing('outside brake domain: lip240..260, pocket top438..470, exitx95..120')
    spec=specification(d)
    if request.get('specification',spec)!=spec:return missing('full Challenge Specification mismatch; no substituted abilities, reward, geometry or direction')
    cases=[]
    for i in range(4):
        c=thorn(0)if f=='thorn-slot'else brake(0)
        c['id']=d['id']+'-control-'+str(i);c['parent_family']=f
        if f=='thorn-slot':
            front=p['landing_front'];surface=p['landing_y'];x=front+105;y=surface-18
            c['platforms'][1]=[front,surface,220,160];c['platforms'][2][2]=front-220;c['thorns'][0]['length']=front-220
            hold,shot,takeoff=[(8,16,205),(10,18,205),(8,16,195),(10,18,215)][i]
            c['control_plan']=launch(hold,shot,.15,takeoff)+[settle(x,6)]
        else:
            lip=p['lip_x'];surface=p['pocket_y'];x=p['target_x'];y=surface-18
            c['platforms'][0][2]=lip+160;c['platforms'][1]=[x-60,surface,100,65]
            advance,turn=[(105,9),(100,9),(110,9),(105,11)][i]
            c['control_plan']=[cmd('axis',value=1),wait_x(lip+advance),cmd('shoot',direction=[1,0]),cmd('axis',value=-1,after=turn),settle(x,6)]
        c['exit_port']=[x,y];c['goal']=[x-25,y-4,50,8];c['reward_sites']=[];reward(c,x,y,8 if f=='thorn-slot'else 10)
        c['map_specification']=copy.deepcopy(spec);c['rule_parameters']=dict(p,control_candidate=i)
        c['generation_rule']=dict(id='plains/recoil-demand-adaptation/'+f,version=1,source_path=str(Path(__file__).relative_to(ROOT.parent)),parameters=c['rule_parameters'],source_type='current_codex_session_rule_extension',new_action_family=False)
        c['idea_ids']=['human-plains-recoil-priority-v1'];c['capabilities']=CAPS[:]
        if not fits(c,spec):return missing('materialized geometry exceeds requested actual space/ports/capabilities')
        cases.append(c)
    return dict(status='requires_physics',specifications=[spec],cases=cases)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--name',required=True);a=ap.parse_args()
    requests=[dict(recipe=d['id'],demand=d,specification=specification(d))for d in DEMANDS]
    run(a.name,requests=requests,cycles=4,source_file=Path(__file__),extra_sources=[Path(__file__).with_name('adapt-protocol-v1.json')],compiler=compiler,checker=purpose,counter_builder=alternatives)
if __name__=='__main__':main()
