"""Compare actual shared pre-decision physical traces; not reachability inference."""
import gzip,json
from pathlib import Path
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.factory.core.quality import digest
from pcg.prototype.workshop.engine import ROOT
from pcg.prototype.workshop.experiments import write
source=ROOT/'results/junction-windgap-probe-v2/physics/0000-probe.output.json.gz'
rows=json.loads(gzip.open(source,'rt').read())['results'];byid={r['id']:r for r in rows}
keys=['frame','x','y','vx','vy','axis','grounded','hp','energy','shot_charges','shot_cooldown','jumps_used','jump_maximum','support_id','normal_velocity','real_velocity','platform_velocity','traversal_state','returns','dead','module_clock','saws','moving_platforms']
reports=[]
for interface in [0,1]:
 routes=[byid[f'junction-windgap-{interface}-{rid}']for rid in ['a-b','a-c','a-b-c']]
 prefix_end=min(r['fired_commands'][5]['frame']for r in routes)-1
 traces=[[{k:f.get(k)for k in keys}for f in r['frames']if f['frame']<=prefix_end]for r in routes]
 assert traces[0]==traces[1]==traces[2]
 last=traces[0][-1];assert last['grounded'] and last['support_id']=='Platform2'
 reports.append(dict(interface=interface,compared_routes=[r['id']for r in routes],prefix_frames=len(traces[0]),last_common_physical_state=last,physical_prefix_sha256=digest(traces[0]),same_supported_actor_resource_world_state=True,branch_after_prefix='west lower B versus ascending east C; continuous visit-B case shares same prefix'))
write(ROOT/'results/junction-windgap-common-prefix-v3.json',dict(schema='pcg/junction-choice-prefix/v1',source=dict(path=str(source.relative_to(ROOT.parent)),sha256=file_sha(source)),scope='exact clean v2 cases; v3 physical geometry and nominal controls byte-equivalent per source comparison, formal production separately replays v3',observations=reports,universal_entering_states=False,original_reverse_relations='UNKNOWN'))
print(json.dumps(reports,ensure_ascii=False),flush=True)
