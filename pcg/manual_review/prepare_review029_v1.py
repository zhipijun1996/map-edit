"""Exact approved revision 029; reuse the established materializer and decoder."""
import argparse,copy,inspect
from pcg.migration import core,physics,godot_package
from pcg.prototype.workshop.rules import cmd,settle
from . import prepare_first40_v1 as shared,prepare_review_refresh_v1 as refresh
AUTH=core.REPO/'feedback/manual-review/implementation-results/review-029-v1/authorization'
CURRENT=None

def dock(p):return [p['position'][0]-24*p['normal'][0],p['position'][1]+14]
def at(x,y):return refresh.at(x,y)
def end(x,y):return refresh.end(x,y)

def decode(doc):
    n=CURRENT['reviewId']
    for o in doc['objects']:
        m=o.setdefault('mechanics',{})
        if o['type']=='gate'and m.get('openSeconds')=='UNKNOWN':m['openSeconds']=0.0
        if n=='175'and o['type']=='bell'and o.get('sourceId')=='key-control':
            host=next(v for v in doc['objects']if v.get('sourceId')=='key-carrier');o['hostId']=host['id'];m.setdefault('runtimeParameters',{})['carrier_mount']='key-carrier';m['localReceiverOffset']=[0,-46]
    refresh.CURRENT=CURRENT;refresh.NOTES=[]
    return refresh.decode(doc)

def plan_for(n,target,source,design):
    p=copy.deepcopy(source[0]['control_plan']);a,z=[next(v for v in design['ports']if v['id']==target[k])for k in ('from','to')];x,y=dock(z)
    if n in ('161','162','163','165'):p=refresh.core_plan(source,design['bounds'])
    if n=='163':
        p=at(120,282)+[cmd('shoot',aim_cell=dict(kind='bell',id='windchime_plains_windchime_sequence')),cmd('wait',30),cmd('shoot',aim_cell=dict(kind='bell',id='windchime_plains_windchime_sequence',receiver='second')),cmd('wait',30)]
    if n=='173':
        if target['from']=='entry':p=at(80,484)+p
        else:p=at(350,100)+[settle(150),dict(op='wait',trigger=dict(state='grounded',timeout=600))]
    elif n=='174':p=at(110,420)+p
    elif n=='175':p=at(750,420)+p
    elif n=='176':p=at(180,420)+p
    elif n=='179':p=at(190,168)+p
    elif n=='191':p=at(180,448)+p
    elif n=='193':
        if target['from']=='entry':p=at(210,420)+p
        else:p=[] # bounded initial diagnostic; actual reverse must be authored
    elif n=='194':p=at(200,420)+p
    return p+end(x,y),source[0]

def prepare(row):
    global CURRENT
    CURRENT=row
    text=inspect.getsource(shared.prepare)
    text=text.replace("'pcg/manual_review/first40_r'+n+'_v1.py'","'pcg/manual_review/review029_author_v1.py'")
    text=text.replace("match['generation_rule']['registration_source']","match.get('generation_rule',{}).get('registration_source',row['sourceModule']['file'])")
    text=text.replace("c['generation_rule']['registration_source']=","c.setdefault('generation_rule',{})['registration_source']=")
    scope={**shared.__dict__,'AUTH':AUTH,'dock':dock,'plan_for':plan_for,'decode':decode}
    exec(compile(text,__file__,'exec'),scope);scope['prepare'](row)
    folder=core.REPO/row['outputDirectory'];cases=core.read(folder/'cases.json')['cases'];doc=core.read(folder/'module.mapnote.json')
    for c in cases:
        c['id']=c['id'].replace('approved-first30','approved-review029-v1');c['max_frames']=3000
        c['route_spec']['require_bell']=row['reviewId']in ('161','162','163','165','191','194')
        for key in list(c):
            if key.startswith('migration_')or key in ('decoder_pending_behavior','validation_summary','review_alias','source_module','source_case'):c.pop(key,None)
        if row['reviewId']=='173'and c['route_spec']['from_port']=='exit':c['required_rewards']=[];c['expected_reward']=0
    doc=godot_package.bind_case_behavior(doc,cases)
    core.write(folder/'module.mapnote.json',doc);core.contract(folder/'module.mapnote.json',refresh=True);core.write(folder/'cases.json',dict(cases=cases))
    core.write(folder/'parameters.json',dict(designVersion=row['designVersion'],content=decode(doc),controls=[dict(route=c['route_spec'],control_plan=c['control_plan'],max_frames=c['max_frames'])for c in cases],notes=['UNKNOWN permanent gate durations resolved to original permanent 0s for safe_lesson,sequence,shot_recoil_combo; 162 timed gate retains 3s','175 mounted original ShotLatch follows real carrier; no player/clock/resource writes']))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('ids',nargs='*');a=p.parse_args()
    for row in core.read(AUTH/'handoff.json')['rows']:
        if row['reviewId']!='171'and (not a.ids or row['reviewId']in a.ids):prepare(row)
