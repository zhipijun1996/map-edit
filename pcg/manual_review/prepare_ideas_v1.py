"""Reuse approved-design materializer with a format-only seed, no inherited proof."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy,inspect
from pcg.migration import core,physics,godot_package
from pcg.prototype.workshop.rules import cmd
from . import prepare_first40_v1 as shared
from .new_ideas_v1 import rows,AUTH,label
from .ideas_content_v1 import decode
from .prepare_review045_v1 import at,end,axis
TEMPLATE='modules/game-spike-gap/module.mapnote.json'
CURRENT=None

def dock(p):
 x,y=p['position'];nx,ny=p['normal']
 if nx:return[x-24*nx,y+14]
 d=core.read(CURRENT['designFile']);support=next((o for o in d['visualObjects']if o['id']==p.get('supportObjectId')),None)
 if support is None:support=min([o for o in d['visualObjects']if o['type']=='platform'and not o.get('trackId')and o['x']<=x<=o['x']+o['w']],key=lambda o:abs(o['y']-y))
 return[x,support['y']-18]
def enrich(d):
 d=copy.deepcopy(d)
 for o in d['visualObjects']:
  if o['type']=='reward':
   x,y=o['x']+o['w']/2,o['y']+o['h']/2;o['mechanics']=dict(service='SimpleRoomReward',kind='chest',amount=4,designGlyphOnly=True,source=dict(id='reward',position=[x,y],region=[x-40,y-28,80,56],amount=4))
  if o['type']in ['bell','enemy']or o.get('trackId'):o['sourceId']=o['id']
 return d

def settle(x):return dict(op='settle',target_x=x,deadband=.6,source_native_gain=5.5,trigger=dict(after=0))
def follow():return dict(op='settle',target_x=240,follow_carrier='carrier',deadband=.6,source_native_gain=5.5,trigger=dict(after=0))
def deck_ready(state='on_carrier',low=0,high=1):return dict(op='wait',carrier_window=dict(id='carrier',low=low,high=high),trigger=dict(after=4,state=state,timeout=900))
def chain_shot(identifier,side,limit):return dict(op='shoot',aim_cell=dict(kind='enemy',id=identifier),chain_window=dict(id=identifier,side=side,maximum_actor_y=limit,minimum_drop=40),trigger=dict(after=4,state='chain_shot',timeout=240))

def plan_for(n,target,source,design):
 a,z=target['from'],target['to'];ports={p['id']:dock(p)for p in design['ports']};goal=ports[z]
 if n=='idea-orbit-choice-001':
  if a=='A':p=at(84,334)+[settle(240),cmd('jump'),cmd('jump_release',24)]+at(240,230)
  elif a=='B':p=at(556,206)+[settle(240),cmd('jump'),cmd('jump_release',18),cmd('shoot',4,direction=[1,0])]+at(240,230)
  else:p=[settle(240),cmd('drop_through')]+at(240,230)
  p+=[dict(op='shoot',aim_cell=dict(kind='bell',id='bell'),trigger=dict(after=4,state='grounded_shot_ready',timeout=180)),follow(),cmd('jump',4),cmd('jump_release',24),deck_ready()]
  phase={'A':(.74,.76),'B':(.49,.51),'C':(.24,.26)}[z];p+=[follow(),deck_ready('carrier_ready',*phase)]
  if z=='C':p+=[settle(320),cmd('jump'),cmd('jump_release',8),cmd('shoot',4,direction=[0,1])]
  else:p+=[settle(goal[0]),cmd('jump'),cmd('jump_release',8),cmd('shoot',4,direction=[1 if z=='A'else-1,0])]
  return p+end(*goal),source[0]
 count=2 if n.endswith('enemies-2')else 3;floor=design['bounds']['h']-50
 if a=='B':p=[settle(goal[0]),cmd('drop_through')]
 elif z=='A':p=[settle(285),cmd('jump'),cmd('jump_release',24),cmd('wait',24)]
 else:
  p=[axis(0),cmd('jump'),cmd('jump_release',24),chain_shot('enemy-1',-1,floor-125)]
  for i in range(2,count+1):p+=[settle(300 if i%2==0 else 192),chain_shot('enemy-'+str(i),1 if i%2==0 else-1,floor-125-(i-1)*85)]
  p+=[settle(goal[0]),dict(op='shoot',direction=[0,1],height_threshold=140,trigger=dict(after=4,state='shot_ready_above',timeout=240))]
 return p+end(*goal),source[0]

def prepare(row):
 global CURRENT
 CURRENT=row;n=row['reviewId'];design=core.read(row['designFile']);template=core.read(TEMPLATE);template['id']=row['moduleId'];template['description']=design['summary'];template['canvas'].update(width=design['bounds']['w'],height=design['bounds']['h']);template['source']=dict(integration=dict(isIntegrated=False,usage='not_integrated',label='待验证候选',reason='Exact approved new idea; no production admission',evidence=[]),kind='human_approved_design',file=row['designFile'],sha256=row['designFileSha256'],sourceIdea=row['sourceIdea']);template['capabilityRequirements']=design['capabilityRequirements'];g=template['generationContract'];g['generation']=dict(source=dict(design=physics.artifact(core.REPO/row['designFile']),formatTemplate=physics.artifact(core.REPO/TEMPLATE),physicsSourceCommit='12f6cb006d7119598e3235f4ca4f7323e4c9d092'),parameters=dict(family='approved-new-idea'));template['objects']=[]
 base=dict(id='new-idea',family='orbit-choice'if label(row)=='orbit'else'recoil-chain',capabilities=['move','jump','shot_recoil'],generation_rule=dict(registration_source='pcg/manual_review/ideas_author_v1.py'),max_frames=3000,trace_all=False)
 source=inspect.getsource(shared.prepare).replace("doc=core.read(core.REPO/row['sourceModule']['file'])","doc=copy.deepcopy(TEMPLATE_DOC)").replace("source=core.read((core.REPO/row['sourceModule']['file']).parent/'cases.json')['cases']","source=[copy.deepcopy(BASE_CASE)];design=enrich(design)").replace("'pcg/manual_review/first40_r'+n+'_v1.py'","'pcg/manual_review/ideas_author_v1.py'").replace("row['sourceModule']['file']","row['designFile']").replace("row['sourceModule']['contentVersion']","row['designVersion']")
 scope={**shared.__dict__,'TEMPLATE_DOC':template,'BASE_CASE':base,'AUTH':AUTH,'enrich':enrich,'dock':dock,'decode':decode,'plan_for':plan_for};exec(compile(source,__file__,'exec'),scope);scope['prepare'](row)
 f=core.REPO/row['outputDirectory'];doc=core.read(f/'module.mapnote.json');cs=core.read(f/'cases.json')['cases']
 for c in cs:
  c['id']='approved-newideas-v1-'+label(row)+'-'+c['route_spec']['id'];c['max_frames']=3000;c['required_rewards']=[];c['expected_reward']=0;c['legal_port_mouths']=[{k:p[k]for k in ['id','position','face','surface','permission']}for p in design['ports']]
  c['layout_title']=design['title'];c['new_idea_scope']=dict(id=row['moduleId'],designVersion=row['designVersion'],familyId=row['sourceIdea']['id'],formatTemplateOnly=True)
 doc=godot_package.bind_case_behavior(doc,cs);core.write(f/'module.mapnote.json',doc);core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs));core.write(f/'parameters.json',dict(designVersion=row['designVersion'],content=decode(doc),staging='real 24x36 body stand height derived from exact support; authored diagram staging retained in authorization snapshot',optionalReward=dict(kind='original SimpleRoomReward',coins=4,required=False),controls=[dict(route=c['route_spec'],plan=c['control_plan'])for c in cs]))
if __name__=='__main__':
 for r in rows():prepare(r)
