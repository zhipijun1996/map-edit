"""Behavior archives and explicit finite-sample technical admission.

No bot score establishes human fun or formal game/region readiness.
"""
import copy,hashlib,json,math

SCENARIO_FIELDS=('capabilities','platforms','one_way_platform_indices','wall_platform_indices','spawn','goal','hooks','hazards','thorns','saws','moving_platforms','entry_port','exit_port','world_bounds','warmup_frames','settle_frames','max_frames')
PUBLIC_HASH_EXCLUDED={'module_sha256','factory_id','title','review_alias','review_warnings','admission_status','validation_summary','provenance','metadata_correction','factory_evidence'}
POLICY={
 'schema':'pcg/factory-policy/v1','version':1,
 'validation_trials':12,'clean_min':.9,
 'regular':{'mild_min':.85,'moderate_min':.65},
 'precision_review':{'mild_min':.70,'moderate_min':.40},
 'minimum_human_reviewers':2,
 'scope':'Experimental engineering thresholds; not calibrated human difficulty or fun.'}

def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def digest(value):return hashlib.sha256(canonical(value)).hexdigest()
def scenario_hash(case):return digest({k:case.get(k)for k in SCENARIO_FIELDS})
def candidate_hash(case):return digest({k:case.get(k)for k in SCENARIO_FIELDS+('word','control_plan','noise')})
def module_hash(case):return digest({k:v for k,v in case.items()if k not in PUBLIC_HASH_EXCLUDED})
def wilson(success,total):
 if not total:return [0.,1.]
 z=1.96;p=success/total;d=1+z*z/total
 center=(p+z*z/(2*total))/d;half=z*math.sqrt(p*(1-p)/total+z*z/(4*total*total))/d
 return [max(0.,center-half),min(1.,center+half)]
def rate(row):return row['purpose_valid']/row['trials']if row['trials']else 0.
def counts(rows):
 n=len(rows);good=sum(bool(r['purpose']['ok'])for r in rows)
 return dict(trials=n,purpose_valid=good,safe_stable=sum(bool(r['safe_stable'])for r in rows),rate=good/n if n else 0.,wilson95=wilson(good,n))

def descriptor(frames,word):
 """Only observed executed actions/motion; never geometry labels or IDs."""
 mask=sum(bit for action,bit in [('wall_jump',1),('air_jump',2),('recoil',4)]if action in word)
 if any(a in word for a in ('hook_hang','hook_bounce','anchor_jump')):mask|=8
 signs=[];last=0;run=0
 for a,b in zip(frames,frames[1:]):
  dx=b['x']-a['x'];sign=1 if dx>.4 else -1 if dx<-.4 else 0
  if sign==last:run+=1
  else:last=sign;run=1
  if sign and run==3 and (not signs or signs[-1]!=sign):signs.append(sign)
 turns=max(0,len(signs)-1)
 last_action=max((i for i,f in enumerate(frames)if f.get('accepted')),default=len(frames)-1)
 active=frames[:last_action+1]
 stationary=sum(abs(f.get('real_velocity',[f.get('vx',0),f.get('vy',0)])[0])+abs(f.get('real_velocity',[f.get('vx',0),f.get('vy',0)])[1])<2 for f in active)
 wait=stationary/max(1,len(active));wait_bin=0 if wait<.05 else 1 if wait<.25 else 2
 key=[mask,digest(list(word))[:12],min(turns,3),wait_bin]
 return dict(cell=key,source='executed_action_word_and_real_motion',actual_word=list(word),direction_changes=turns,stationary_fraction=wait,seconds=len(frames)/60.,skill_mask=mask)

def constraint_distance(case,result,purpose,word):
 expected=[a for a in case['word']if a not in ('wall_contact','wall_separate')]
 prefix=0
 for a,b in zip(expected,word):
  if a!=b:break
  prefix+=1
 word_loss=(len(expected)-prefix)/max(1,len(expected))
 goal=min(1.,max(0.,float(result.get('minimum_goal_distance',1e6)))/1000.)
 harm=int(not result.get('safe',False)or result.get('dead',False))
 continuous=int(not purpose.get('uninterrupted',False))if not case['family'].startswith('carrier_')else 0
 ride=0.
 if case['family'].startswith('carrier_'):
  ride=max(0.,1-purpose.get('neutral_support_frames',0)/30.,1-purpose.get('neutral_carried_displacement',0)/100.,1-purpose.get('moving_supported_frames',0)/20.)
 completion=int(not result.get('settled_goal',False)or not result.get('plan_completed',False)or bool(result.get('plan_error')))
 return dict(total=harm*4+word_loss*2+continuous+ride+goal+completion,unsafe=harm,word_prefix_loss=word_loss,continuous_violation=continuous,ride_violation=ride,completion_violation=completion,goal_distance_normalized=goal)

def discovery_quality(stats,features):
 # Calibration only; independent validation is never fed back into search.
 return .55*rate(stats['clean'])+.40*rate(stats['mild'])-.05*features.get('stationary_fraction',0)

def gate(stats,shortcuts,dynamic,policy=POLICY):
 reasons=[];minimum=policy['validation_trials']
 for level in ('clean','mild','moderate'):
  need=minimum if level!='clean'or dynamic else 1
  if stats[level]['trials']<need:reasons.append('insufficient_'+level+'_trials')
 if rate(stats['clean'])<policy['clean_min']:reasons.append('unreliable_clean_policy')
 if shortcuts:reasons.append('lower_cost_route_requires_design_review')
 if reasons:return dict(status='rework',reasons=reasons,offline_approved=False,formal_game_ready=False)
 for tier,rules in [('regular',policy['regular']),('precision_review',policy['precision_review'])]:
  if rate(stats['mild'])>=rules['mild_min']and rate(stats['moderate'])>=rules['moderate_min']:
   return dict(status='awaiting_human_review',engineering_tier=tier,reasons=[],offline_approved=False,formal_game_ready=False)
 return dict(status='rework',reasons=['insufficient_perturbation_robustness'],offline_approved=False,formal_game_ready=False)

class BehaviorArchive:
 """Small MAP-Elites baseline with a separate constraint-distance archive."""
 def __init__(self):self.feasible={};self.infeasible={};self.history=[]
 def insert(self,entry):
  key=tuple(entry['features']['cell']);stats=entry['discovery']
  good=stats['clean']['trials']>0 and rate(stats['clean'])==1 and rate(stats['mild'])>=.75
  target=self.feasible if good else self.infeasible
  old=target.get(key)
  better=old is None or (entry['quality']>old['quality']if good else entry['violation']<old['violation'])
  if better:target[key]=copy.deepcopy(entry)
  self.history.append(dict(candidate=entry['uid'],cell=list(key),partition='feasible'if good else'infeasible',replaced=better))
  return good,better
