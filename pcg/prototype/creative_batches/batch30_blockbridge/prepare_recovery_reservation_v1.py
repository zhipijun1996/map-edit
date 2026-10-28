"""Freeze parent recovery hints before new recovery runs; no physics."""
import gzip,hashlib,json
from pathlib import Path
from pcg.map_directed.block_grid.contracts import raster
HERE=Path(__file__).parent;REPO=HERE.parents[3]
def prepare():
 out=HERE/'source-recovery-reservation-v1.json'
 if out.exists():raise ValueError('immutable recovery reservation already exists')
 root=REPO/'pcg/results/workshop-batch30-c01-recovery-v1';data={i:dict(body=set(),margin=set(),frames=0,cases=0)for i in [0,1]}
 for b in json.loads((root/'batches.json').read_text()):
  packed=(root/b['gzip_path']).read_bytes();assert hashlib.sha256(packed).hexdigest()==b['gzip_sha256'];raw=gzip.decompress(packed);assert hashlib.sha256(raw).hexdigest()==b['raw_output_sha256']
  for r in json.loads(raw)['results']:
   if not r.get('ok')or r.get('hp')!=5:continue
   for i in [0,1]:
    if not r['id'].startswith(f'b30-c01-v3-i{i}-c0'):continue
    data[i]['cases']+=1
    for f in r['frames']:
     rect=[f['x']-12,f['y']-18-86,24,36];data[i]['body']|=raster(rect);data[i]['margin']|=raster([rect[0]-32,rect[1]-32,88,100]);data[i]['frames']+=1
 result=dict(schema='pcg/source-recovery-reservation-hints/v1',source_run=str(root.relative_to(REPO)),batches_sha256=hashlib.sha256((root/'batches.json').read_bytes()).hexdigest(),interfaces={str(i):dict(source_body_cells=sorted(map(list,d['body'])),owner_margin_cells=sorted(map(list,d['margin'])),source_frames=d['frames'],source_success_cases=d['cases'])for i,d in data.items()},scope='Oldframesonlyseednewreservation; prohibitedAneighbor isnotowned, newrealrearm/returncontrol must physically avoid it. No transferredpass.')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':prepare()
