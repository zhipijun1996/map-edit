"""Import review JSON, emit bound repair jobs, or record explicit curator decisions."""
import argparse,json
from pathlib import Path
from .core.feedback import ingest,repair_job,decide

def main():
 p=argparse.ArgumentParser();sub=p.add_subparsers(dest='op',required=True)
 for name in ('import','repair-job','decide'):
  c=sub.add_parser(name);c.add_argument('--catalog',required=True);c.add_argument('--store',required=True)
  if name=='import':c.add_argument('--file',required=True)
  if name=='repair-job':c.add_argument('--out',required=True)
  if name=='decide':
   c.add_argument('--candidate',required=True);c.add_argument('--decision',choices=['retain','rework','reject'],required=True);c.add_argument('--curator',required=True);c.add_argument('--reason',required=True);c.add_argument('--human-confirmed',action='store_true')
 args=p.parse_args();catalog=json.loads(Path(args.catalog).read_text())
 if args.op=='import':
  raw=json.loads(Path(args.file).read_text());rows=raw.get('submissions')if isinstance(raw,dict)and raw.get('schema')=='pcg/feedback-export/v1'else[raw]
  store=ingest(args.store,rows,catalog);print(json.dumps(dict(imported_total=len(store['submissions']),automatic_approvals=0)))
 else:
  store=json.loads(Path(args.store).read_text())
  if args.op=='repair-job':Path(args.out).write_text(json.dumps(repair_job(store,catalog),ensure_ascii=False,indent=2))
  else:
   result=decide(store,catalog,args.candidate,args.decision,args.curator,args.reason,human_confirmed=args.human_confirmed);Path(args.store).write_text(json.dumps(store,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
