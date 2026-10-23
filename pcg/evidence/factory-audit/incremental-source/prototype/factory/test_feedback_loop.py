"""Explicitly synthetic end-to-end feedback -> mutation -> actual Godot check.
Never writes a real human store, approval, or production candidate catalog.
"""
import argparse,copy,json
from pathlib import Path
from .core.engine import ROOT,Engine
from .core.feedback import ingest,repair_job,FeedbackError
from .core.producer import mutate,compact
from .core.quality import module_hash

def run(catalog_path,cases_path,feedback_path,name):
 catalog=json.loads(Path(catalog_path).read_text());cases=json.loads(Path(cases_path).read_text())['cases'];raw=json.loads(Path(feedback_path).read_text());submissions=raw['submissions']
 if any(s['source_kind']!='synthetic_test'for s in submissions):raise ValueError('Only synthetic UI fixtures allowed in this test')
 out=ROOT/'results'/name
 if out.exists():raise ValueError('Refuse existing test evidence')
 # Initialize Engine before writing the scoped test store; exact source snapshot.
 engine=Engine(out,12);store=ingest(out/'test-only-store.json',submissions,catalog,test_mode=True)
 job=repair_job(store,catalog,diagnostic=True);(out/'test-only-job.json').write_text(json.dumps(job,indent=2))
 if not job['test_only']:raise AssertionError('Synthetic job lost isolation')
 originals={c['factory_id']:c for c in cases};children=[]
 for i,task in enumerate(job['tasks']):
  base=originals[task['candidate_uid']]
  if module_hash(base)!=task['module_sha256']:raise ValueError('test fixture module mismatch')
  if task['target']not in ('unreadable_landing','excessive_wait'):continue
  child=mutate(dict(case=base,uid=task['candidate_uid']),50000+i,target=task['target']);child['diagnostic_test_only']=True;children.append(child)
 receipts=[]
 for c,r,e in engine.run(children,'synthetic_repair_validation'):receipts.append(compact(c,r,e))
 result=dict(schema='pcg/synthetic-feedback-loop/v1',test_only=True,source_kind='synthetic_test',submissions=len(submissions),repair_tasks=len(job['tasks']),children_revalidated=len(receipts),children_purpose_pass=sum(r['purpose']['ok']for r in receipts),real_human_feedback=0,approved_offline=0,production_candidates_written=0,scope='Actual keyboard UI/export and actual Godot diagnostic mutation; not a human review or approval.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'validation.json').write_text(json.dumps(receipts,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--catalog',required=True);p.add_argument('--cases',required=True);p.add_argument('--feedback',required=True);p.add_argument('--name',default='factory-feedback-loop-test-v1');a=p.parse_args();run(a.catalog,a.cases,a.feedback,a.name)
