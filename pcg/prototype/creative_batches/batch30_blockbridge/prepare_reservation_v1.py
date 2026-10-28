"""Read frozen parent traces as reservation hints; no physics or qualification."""
import gzip,hashlib,json
from pathlib import Path
from pcg.map_directed.block_grid.contracts import raster
HERE=Path(__file__).parent
REPO=HERE.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def prepare():
 out=HERE/'source-reservation-v1.json'
 if out.exists():raise ValueError('immutable reservation source exists')
 root=REPO/'pcg/results/workshop-batch30-c01-full-v1/paired-support-transfer'
 batches=json.loads((root/'batches.json').read_text());data={i:dict(body=set(),margin=set(),frames=0,cases=0)for i in [0,1]}
 for b in batches:
  packed=root/b['gzip_path'];blob=packed.read_bytes();assert hashlib.sha256(blob).hexdigest()==b['gzip_sha256'];raw=gzip.decompress(blob);assert hashlib.sha256(raw).hexdigest()==b['raw_output_sha256']
  for r in json.loads(raw)['results']:
   if not r.get('ok')or r.get('hp')!=5:continue
   for i in [0,1]:
    if not r['id'].startswith(f'b30-c01-v3-i{i}-c0'):continue
    data[i]['cases']+=1
    for f in r['frames']:
     rect=[f['x']-12,f['y']-18-86,24,36];data[i]['body']|=raster(rect);data[i]['margin']|=raster([rect[0]-32,rect[1]-32,88,100]);data[i]['frames']+=1
 result=dict(schema='pcg/frozen-parent-reservation-hints/v1',source=dict(path=str(root.relative_to(REPO)),batches_sha256=sha(root/'batches.json')),translation=[0,-86],interfaces={str(i):dict(source_body_cells=sorted(map(list,d['body'])),owner_margin_cells=sorted(map(list,d['margin'])),source_frames=d['frames'],source_success_cases=d['cases'])for i,d in data.items()},qualification='Parent frames only seed declared conservative new ownership; new geometry and controls require fresh actual physics. Not new boundary evidence.')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(out)
if __name__=='__main__':prepare()
