"""Keep an authored downwards bell ray clear while adding a walkable shore.

Two thin real terrain lips leave a slit smaller than the real player's 24px
body. The original projectile still has to clear the physical slit in Godot;
no projectile collision rule or player movement rule is changed.
"""
import copy
from .adaptation import _append_platform


def entry_ray_slot(document,input_cases,*,port_id='entry',center_x=51.5,width=23,thickness=1):
    if not 8<=width<24 or not 0<thickness<=2:raise ValueError('ray_slot_must_be_narrower_than_real_player_body')
    doc,cases=copy.deepcopy(document),copy.deepcopy(input_cases);gc=doc['generationContract']
    port=next(p for p in gc['ports']if p['id']==port_id)
    name=port['objectId'].rsplit('/',1)[0]+'/original-floor-approach-'+port_id
    host=next((o for o in doc['objects']if o['id']==name),None)
    if host is None or host['type']!='terrain':raise ValueError('independent_entry_approach_not_found')
    index=host['sourceIndex'];before=copy.deepcopy(cases[0]['platforms'][index]);floor=before[1]
    source=gc['generation']['migration'].get('corePreservingRepair',{})
    slot_left=center_x-width/2;slot_right=center_x+width/2
    # Find the untouched original bank whose top supports the canonical core
    # start. The new lip stops at that bank, preserving its original collider.
    source_floor=next(p for p in source.get('ports',[])if p['portId']==port_id)['originalFloor']
    candidates=[r for i,r in enumerate(cases[0]['platforms'])if i!=index and abs(r[1]-source_floor)<.01
                and r[0]<=cases[0]['spawn'][0]<=r[0]+r[2]]
    if len(candidates)!=1:raise ValueError('original_small_entry_bank_ambiguous')
    bank=candidates[0]
    if not before[0]<slot_left<slot_right<bank[0]:raise ValueError('ray_slot_must_stay_outside_original_bank')
    left=[before[0],floor,slot_left-before[0],thickness];right=[slot_right,floor,bank[0]-slot_right,thickness]
    for key,value in zip(('x','y','w','h'),left):host[key]=value
    host['label']='Thin shore with visible shot slit';host['note']='23px opening: actual 24px actor spans it; actual bullets retain original collisions.'
    for case in cases:case['platforms'][index]=list(left)
    obj,new_index=_append_platform(doc,cases,name+'-shot-slot-right',right)
    receipt=dict(schema='pcg/physical-entry-shot-slot/v1',portId=port_id,
        before=before,after=[left,right],slit=[slot_left,floor,width,thickness],
        bodyWidth=24,minimumTotalFootSupport=24-width,projectilePhysicsUnchanged=True,
        originalCoreGeometryUnchanged=True,originalProgramUnchanged=True,validation='UNKNOWN')
    gc['generation']['migration']['entryShotClearance']=receipt
    for validation in gc['validations']:validation.update(result='UNKNOWN',artifacts=[],method='pending_actual_body_and_bullet_slit_validation')
    return doc,cases,receipt
