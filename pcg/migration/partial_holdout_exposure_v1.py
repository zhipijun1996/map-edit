"""Conservatively lock completed holdout batches from interrupted campaigns.
A complete migration report is not required for conditions to have been seen.
No seeds, candidate selection, simulation or quality thresholds are changed.
"""
import gzip,hashlib
from pathlib import Path
from . import core

def ingest_run(state,root,guard):
 from . import physics
 root=Path(root)
 if (root/'migration-physics.json').exists():return 0
 required=['input-binding.json','protocol.json','batches.json']
 if not all((root/p).is_file()for p in required):return 0
 batches=[b for b in core.read(root/'batches.json')if b.get('stage')=='migration-holdout']
 if not batches:return 0
 binding=core.read(root/'input-binding.json');folder=core.resolve_artifact(binding['module']['path']).parent;identity=guard._identity(folder);canonical=core.resolve_artifact(binding['cases']['path']);core.verify_artifacts([binding['module'],binding['cases']]);values=core.read(canonical);cases=values['cases']if isinstance(values,dict)else values;route_indices={c['route_spec']['id']:i for i,c in enumerate(cases)};protocol=core.read(root/'protocol.json');pool=guard._pool(protocol);pool_key=guard.digest(pool);signature=guard._program_signature(cases);seen=state.setdefault('partialExposures',{});added=0
 for batch in batches:
  name=batch['batch'];input_path=root/'physics'/(name+'.input.json');execution=root/batch['execution'];packed=root/batch['gzip_path'];receipt=core.read(execution)
  assert receipt['exit_code']==0 and receipt['input_sha256']==core.sha(input_path)
  assert core.sha(packed)==batch['gzip_sha256'];data=gzip.decompress(packed.read_bytes());assert hashlib.sha256(data).hexdigest()==batch['raw_output_sha256'];assert len(data)==batch['raw_output_bytes']
  inputs=core.read(input_path)['cases'];assert len(inputs)==batch['cases'];route_ids=sorted({c['route_spec']['id']for c in inputs})
  for route_id in route_ids:
   assert route_id in route_indices;key=core.relative(root)+'/'+name+'/'+route_id;proof=dict(execution=physics.artifact(execution),input=physics.artifact(input_path),raw=physics.artifact(packed),protocol=physics.artifact(root/'protocol.json'))
   if key in seen:
    assert seen[key]==proof,'partial_holdout_evidence_changed:'+key;continue
   i=route_indices[route_id];state['observations'].append(dict(source=identity,pool=pool,poolKey=pool_key,routeId=route_id,routeIndex=i,actualHoldoutSeed=protocol['holdoutSeed']+i*1009,contentVersion=binding['contentVersion'],programSignature=signature,report=proof['execution'],holdout=proof['execution'],protocol=proof['protocol'],sourceInputBinding=physics.artifact(root/'input-binding.json'),failed=False,qualityStatus='UNKNOWN_AGGREGATE_NOT_REQUIRED_FOR_EXPOSURE',exposureKind='completed_holdout_batch_before_full_report',actualCases=sum(c['route_spec']['id']==route_id for c in inputs),rawEvidence=proof));seen[key]=proof;added+=1
 return added

def ingest_all(state,guard):
 return sum(ingest_run(state,p.parent,guard)for p in sorted((core.REPO/'pcg/results').glob('*/batches.json')))
