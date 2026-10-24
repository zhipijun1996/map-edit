"""Paired parent replay against an already frozen child holdout.
This diagnostic never feeds its results into search or changes the chosen child.
"""
import argparse,json
from .core.engine import ROOT,Engine
from .core.producer import instantiate,compact
from .core.quality import counts,candidate_hash

def run(source,name):
 source=ROOT/'results'/source;entries=json.loads((source/'discovery_entries.json').read_text());by={e['uid']:e for e in entries};catalog=json.loads((source/'catalog.json').read_text())
 children=[by[r['uid']]for r in catalog['candidates']if by[r['uid']]['case'].get('factory_parent')and by[r['uid']]['case']['family']=='carrier_double']
 if len(children)!=1:raise ValueError('explicit diagnostic child selection required')
 child=children[0];parent=by[child['case']['factory_parent']];engine=Engine(ROOT/'results'/name,16)
 seed=catalog['seed']+900000;cases=[];labels={}
 for level in ('clean','mild','moderate'):
  for trial in range(12):
   c,l=instantiate(parent['case'],seed,level,trial);c['id']=parent['uid'][:16]+'-'+c['id'];cases.append(c);labels[c['id']]=l
 rows=[]
 for c,r,e in engine.run(cases,'parent_holdout'):
  row=compact(c,r,e);row.update(labels[c['id']]);rows.append(row)
 child_record=next(r for r in catalog['candidates']if r['uid']==child['uid'])
 value=dict(schema='pcg/paired-repair/v1',parent_uid=parent['uid'],child_uid=child['uid'],mutation=child['case']['factory_mutation'],phase_noise_seed=seed,parent={k:counts([r for r in rows if r['level']==k])for k in ('clean','mild','moderate')},child=child_record['validation'],child_evidence_reused_from=str(source.relative_to(ROOT)),new_physics_cases=36,search_feedback=False,scope='Same automated policy and paired initial phase/noise schedules; does not establish human fun.')
 (engine.out/'summary.json').write_text(json.dumps(value,indent=2));(engine.out/'rows.json').write_text(json.dumps(rows));print(json.dumps(value,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',default='factory-production-v1');p.add_argument('--name',default='factory-parent-comparison-v1');a=p.parse_args();run(a.source,a.name)
