"""Bind feedback/cheap-policy results to real input geometry and raw evidence."""
import gzip,hashlib,json
from .engine import ROOT
from ..factory.core.engine import file_sha
from ..factory.core.quality import digest

GEOMETRY=('capabilities','platforms','one_way_platform_indices','wall_platform_indices','hazards','thorns','saws','moving_platforms','hooks','latches','enemies','world_bounds','ports','reward_sites','spawn','entry_port','exit_port','goal')
def geometry_key(case):return digest({k:case.get(k,[])for k in GEOMETRY})

def counter_records(run):
    root=ROOT/'results'/run;records=[]
    for batch in json.loads((root/'batches.json').read_text()):
        if batch['stage']!='counterexample':continue
        packed=root/batch['gzip_path'];raw=gzip.decompress(packed.read_bytes())
        if file_sha(packed)!=batch['gzip_sha256']or hashlib.sha256(raw).hexdigest()!=batch['raw_output_sha256']:raise ValueError('counter_trace_drift')
        inp=root/'physics'/(batch['batch']+'.input.json');execution=json.loads((root/batch['execution']).read_text())
        if file_sha(inp)!=execution['input_sha256']:raise ValueError('counter_input_drift')
        cs=json.loads(inp.read_text())['cases'];rs=json.loads(raw)['results']
        if len(cs)!=len(rs):raise ValueError('counter_count_drift')
        for i,(c,r)in enumerate(zip(cs,rs)):
            if c['id']!=r['id']:raise ValueError('counter_identity_drift')
            records.append(dict(id=c['id'],base_id=c['id'].split('-counter-')[0],kind=c['counterexample_kind'],geometry_sha256=geometry_key(c),safe_stable=bool(r['ok']),reason=r['reason'],actual_shots=r.get('shots'),actual_reward=r.get('workshop',{}).get('coins'),source_run=run,evidence=dict(batch=batch['batch'],index=i,output=batch['gzip_path'],raw_output_sha256=batch['raw_output_sha256'])))
    return records
