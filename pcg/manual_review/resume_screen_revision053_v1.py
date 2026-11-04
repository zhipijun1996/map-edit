"""Resume only unexecuted registered screen inputs after orchestration freeze rejection."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import gzip,sys,collections
from pcg.migration import core,physics
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
from .continue_revision053_v1 import rows,label

def main():
 r=next(r for r in rows()if label(r)=='50');f=core.REPO/r['outputDirectory'];prior=core.REPO/'pcg/results/approved-r053-50-control-screen-v-next';eng,cs,authors=physics._engine(f,'approved-r053-50-control-screen-v-next-resumed',physics.FULL_PROTOCOL)
 # The old process loaded its orchestration before a later source edit. Only
 # Python fixture orchestration changed; every executable runtime/author stayed frozen.
 old=core.read(prior/'source_binding.json');new=core.read(eng.out/'source_binding.json')
 changes=[k for k,v in old['source_files'].items()if new['source_files'].get(k)!=v];assert changes==['migration/physics.py'],changes
 inputs=[];labels={};counts={c['route_spec']['id']:dict(clean=0,mild=0,moderate=0)for c in cs};reports=[];seen=set()
 for i,c in enumerate(cs):
  for level,total in [('clean',1),('mild',6),('moderate',6)]:
   for j in range(total):
    v=instantiate(physics.fresh(c,'screen-v-next'),271028029,level,j);inputs.append(v);labels[v['id']]=(i,level)
 def add(c,raw,e):
  assert c['id']not in seen;seen.add(c['id']);i,level=labels[c['id']];q=checked_purpose(authors[i],c,raw);counts[cs[i]['route_spec']['id']][level]+=q['ok'];reports.append(dict(route=cs[i]['route_spec']['id'],level=level,check=q,evidence=e))
 for b in core.read(prior/'batches.json'):
  name=b['batch'];inp=core.read(prior/'physics'/(name+'.input.json'))['cases'];raw=core.read if False else __import__('json').loads(gzip.decompress((prior/b['gzip_path']).read_bytes()))['results']
  for i,(c,v)in enumerate(zip(inp,raw)):add(c,v,dict(batch=name,index=i,priorRun=core.relative(prior),output=b['gzip_path'],rawSha256=b['raw_output_sha256']))
 pending=[v for v in inputs if v['id']not in seen];core.write(eng.out/'resume.json',dict(prior=physics.artifact(prior/'batches.json'),completed=len(seen),pending=len(pending),sourceChanges=changes,unchangedRuntime=True,noRepeatedConditions=True))
 for c,raw,e in eng.run(pending,'remaining-registered-screen'):add(c,raw,e)
 assert len(seen)==13*len(cs);passed=all(v['clean']==1 and v['mild']==6 and v['moderate']>=5 for v in counts.values());core.write(eng.out/'screen.json',dict(passed=passed,counts=counts,rows=reports,sourceCases=physics.artifact(f/'cases.json'),resumedFrom=physics.artifact(prior/'batches.json')));print('50',passed,counts,flush=True)
if __name__=='__main__':main()
