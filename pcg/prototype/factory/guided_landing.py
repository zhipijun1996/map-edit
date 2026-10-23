"""Infer bounded receiver shifts from failed, pre-damage real trajectories."""
import copy,math,re,statistics
from .core.quality import candidate_hash

def body_half_size(player_scene):
 text=player_scene.read_text();m=re.search(r'\[sub_resource type="RectangleShape2D" id="shape"\]\s*size = Vector2\(([^,]+),\s*([^\)]+)\)',text)
 if not m:raise ValueError('Unsupported actual player shape; no guessed fallback')
 return float(m[1])/2,float(m[2])/2

def crossing_xs(frames,surface_y,half_height):
 """First descending crossing after a real second jump, before any return."""
 found=[]
 for a,b in zip(frames,frames[1:]):
  if b.get('returns',0)or b.get('damage_commits',0)or b.get('hp',5)<5:break
  if a.get('actor_epoch')!=b.get('actor_epoch')or b.get('jumps_used',0)<2 or b.get('grounded')or b.get('vy',0)<=0:continue
  ay=a['y']+half_height;by=b['y']+half_height
  if ay<surface_y<=by and by>ay:
   f=(surface_y-ay)/(by-ay);found.append(a['x']+(b['x']-a['x'])*f)
 return found[-1:]

def children(parent,frames_by_failure,half_size):
 c=parent['case']
 if c.get('family')!='carrier_double':raise ValueError('Guided landing currently supports carrier_double only')
 hw,hh=half_size
 receiver=min(range(len(c['platforms'])),key=lambda i:abs(c['platforms'][i][1]-(c['goal'][1]+42))+abs(c['platforms'][i][0]+c['platforms'][i][2]/2-c['goal'][0]-c['goal'][2]/2))
 p=c['platforms'][receiver];xs=[x for fs in frames_by_failure for x in crossing_xs(fs,p[1],hh)]
 if not xs:return [],dict(reason='no_clean_second_jump_crossing',crossings=[])
 xs.sort();q25=xs[math.floor((len(xs)-1)*.25)];median=statistics.median(xs)
 proposals=[]
 for i,(target,margin)in enumerate(((q25,4),(median,12))):
  left,right=target+hw+margin-p[2],target-hw-margin
  wanted=max(left,min(p[0],right));dx=max(-96,min(96,round((wanted-p[0])/8)*8))
  child=copy.deepcopy(c)
  for key in('recorded_frames','module_sha256','factory_id','factory_evidence','review_alias','title','review_warnings','admission_status','validation_summary'):child.pop(key,None)
  child['id']+=f'-guided{i}';child['factory_parent']=parent['uid'];child['factory_mutation']=f'trajectory_receiver_shift_{dx}'
  child['platforms'][receiver][0]+=dx;child['goal'][0]+=dx;child['exit_port'][0]+=dx
  for step in child['control_plan']:
   if step['op']=='settle':step['target_x']+=dx
  if dx and candidate_hash(child)not in {candidate_hash(q)for q in proposals}:proposals.append(child)
 return proposals,dict(crossings=xs,receiver_index=receiver,half_size=list(half_size),max_shift=96,grid=8,source='failed discovery traces only; pre-damage first actor epoch',offspring_budget=2)
