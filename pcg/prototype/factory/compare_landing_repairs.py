"""Paired equal-budget blind vs trajectory-guided repair, fresh final holdout."""
import argparse,collections,copy,gzip,hashlib,json,time
from pathlib import Path
from .core.engine import ROOT,Engine
from .core.producer import evaluate,mutate
from .core.quality import POLICY,rate,gate,candidate_hash,module_hash
from .guided_landing import children,body_half_size
from evaluate_dynamic import alternatives
from generators import actual_word

def assign_groups(entries,owners):
 groups=collections.defaultdict(list)
 for e in entries:
  for owner in owners[e['uid']]:groups[owner].append(e)
 return groups

def run(name,historical):
 start=time.perf_counter();old=Path(historical);entries=json.loads((old/'discovery_entries.json').read_text())
 parents=[e for e in entries if e['case']['family']=='carrier_double'and e['witness']is None and not all(r['purpose']['ok']for r in e['rows'])]
 if len(parents)!=6:raise ValueError('This preregistered pilot expects the six frozen failed carriers')
 out=ROOT/'results'/name;engine=Engine(out,16);half=body_half_size(ROOT/'prototype/godot/scenes/player/player.tscn');variants={};owners=collections.defaultdict(set);derivations=[];cache={}
 for i,parent in enumerate(parents):
  fs=[];refs=[]
  for row in parent['rows']:
   if row['purpose']['ok']:continue
   ev=row['evidence'];p=old/ev['output']
   if p not in cache:
    raw=gzip.decompress(p.read_bytes());assert hashlib.sha256(raw).hexdigest()==ev['raw_output_sha256'];cache[p]=json.loads(raw)['results']
   fs.append(cache[p][ev['index']]['frames']);refs.append(ev)
  guided,why=children(parent,fs,half);blind=[mutate(parent,600000+i*2+j)for j in range(2)]
  derivations.append(dict(parent_uid=parent['uid'],evidence=refs,derivation=why,blind=[c['factory_mutation']for c in blind],guided=[c['factory_mutation']for c in guided]))
  uid=candidate_hash(parent['case']);variants[uid]=parent['case'];owners[uid].add((parent['uid'],'parent'))
  for arm,cs in(('blind',blind),('guided',guided)):
   for c in cs[:2]:
    uid=candidate_hash(c);variants[uid]=c;owners[uid].add((parent['uid'],arm))
 (out/'protocol.json').write_text(json.dumps(dict(schema='pcg/landing-repair-protocol/v2',parent_uids=[p['uid']for p in parents],calibration_seed=884000,holdout_seed=984100,candidates_per_arm_per_parent=2,calibration_trials=4,holdout_trials=12,unique_candidates=len(variants),group_candidate_counts={p['uid']:{a:sum((p['uid'],a)in own for own in owners.values())for a in('parent','blind','guided')}for p in parents},selection='discovery quality then uid; holdout not used for selection',identity='Each content candidate simulated once and fanned out to all parent/arm memberships',scope='Six related carrier_double parents; limited geometric repair, not six independent gameplay families',derivations=derivations),indent=2))
 calibration=evaluate(engine,list(variants.values()),884000,4,'repair-calibration');groups=assign_groups(calibration,owners)
 assert len(groups)==18,'All six parents must have all three comparison groups'
 chosen={k:sorted(v,key=lambda e:(-e['quality'],e['uid']))[0]for k,v in groups.items()}
 # All selected revisions are fixed before any new holdout is run.
 held=evaluate(engine,list({e['uid']:e['case']for e in chosen.values()}.values()),984100,12,'repair-holdout',levels=('clean','mild','moderate'));held={e['uid']:e for e in held};altcases=[];altowner={};seen=set()
 for key,e in chosen.items():
  if key[1]=='parent':continue
  if e['uid']in seen:continue
  seen.add(e['uid'])
  witness=held[e['uid']]['witness']
  if not witness:continue
  for c in alternatives(witness['case']):c['id']=e['uid'][:16]+'-'+c['id'];altcases.append(c);altowner[c['id']]=e['uid']
 shortcuts=collections.defaultdict(list)
 def cost(w):return {a for a in w if a not in('ground_jump',)},len(w)
 for c,r,ev in engine.run(altcases,'repair-alternatives'):
  uid=altowner[c['id']];expected=next(e['best']['word']for e in chosen.values()if e['uid']==uid);w=list(actual_word(r));a,n=cost(expected);b,m=cost(w)
  if r['ok']and(b<a or(a==b and m<n)):shortcuts[uid].append(dict(word=w,evidence=ev))
 rows=[];review=[]
 for (parent,arm),e in chosen.items():
  h=held[e['uid']];g=gate(h['discovery'],shortcuts[e['uid']],True,POLICY,requested_tier='regular');rows.append(dict(parent_uid=parent,arm=arm,uid=e['uid'],mutation=e['case'].get('factory_mutation'),calibration=e['discovery'],validation=h['discovery'],admission=g,shortcut_witnesses=shortcuts[e['uid']]))
  if arm!='parent'and g['status']=='awaiting_human_review'and h['witness']:
   w=h['witness'];c=copy.deepcopy(w['case']);c['recorded_frames']=w['recorded_frames'];c.pop('noise',None);c['factory_id']=e['uid'];c['module_sha256']=module_hash(c);c['title']=c['review_alias']=f'{arm} {len(review)+1:02}';review.append(c)
 arms={}
 for arm in('parent','blind','guided'):
  rs=[r for r in rows if r['arm']==arm];arms[arm]=dict(parents=len(rs),regular_pass=sum(r['admission']['status']=='awaiting_human_review'for r in rs),purpose_valid={level:sum(r['validation'][level]['purpose_valid']for r in rs)for level in('clean','mild','moderate')},trials_per_level=len(rs)*12)
 summary=dict(schema='pcg/landing-repair-comparison/v1',arms=arms,physics_cases=engine.sim.cases,batches=len(engine.batches),wall_seconds=time.perf_counter()-start,human_video_feedback=0,human_playtests=0,approved_offline=0,scope='Related-parent pilot, fresh paired phase/noise schedules, selected using calibration only; no human fun claim')
 for filename,data in [('summary',summary),('comparison',rows),('calibration',calibration),('review_cases',dict(cases=review))]:(out/(filename+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2 if filename!='calibration'else None))
 print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--historical',default=str(ROOT/'results/factory-production-v1'));a=p.parse_args();run(a.name,a.historical)
