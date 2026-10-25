"""Real persisted-library integrity and bounded-feedback checks; no fake physics."""
import argparse,copy,json,shutil
from pathlib import Path
from .run import design,resolve
from .ideas import RULES,demand_key
from ..library import CandidateLibrary
from ..director import REPO
from ..run import write

def run(batch,out):
    batch=Path(batch).resolve();out=Path(out).resolve()
    if out.exists():raise ValueError('immutable_check_output_exists')
    out.mkdir(parents=True);lib=CandidateLibrary(batch/'library');_,specs,_,_,old=design('integrity',1.2)
    source=CandidateLibrary().find_direct_instance(old);by={m['id']:m for m in source['modules']}
    rows=[];events=[]
    def emit(event,**fields):events.append(dict(event=event,**fields))
    # Unsupported ideas stay unmet even when a nearby playable Module exists.
    unsupported=copy.deepcopy(next(s for s in specs if s['node_id']=='arch'))
    unsupported['design_contract']['relationships']=[copy.deepcopy(next(r for r in RULES if r['id']=='thorn-slot'))]
    module,calls=resolve(unsupported,lib,by['arch'],emit)
    rows.append(dict(check='unsupported_idea_does_not_substitute_content',passed=module is None and calls==1))
    window=copy.deepcopy(next(s for s in specs if s['node_id']=='arch'));window['design_contract']['gate_window_seconds']=.05
    module,calls=resolve(copy.deepcopy(window),lib,by['arch'],emit)
    rows.append(dict(check='infeasible_unnegotiated_window_stops',passed=module is None and calls==1))
    window['negotiation']=dict(allow_gate_window_revision=True,allowed_gate_windows=[1.2])
    module,calls=resolve(window,lib,by['arch'],emit)
    rows.append(dict(check='one_explicit_director_revision',passed=module is not None and calls==2 and window['design_contract']['gate_window_seconds']==1.2,
        scope='Generated proposal only; not enrolled or asserted physically passed'))
    ports=copy.deepcopy(specs[0]);ports['ports'][0]['normal']=[0,1]
    module,calls=resolve(ports,lib,by[ports['node_id']],emit)
    rows.append(dict(check='incompatible_port_rejected',passed=module is None and calls==1))
    caps=copy.deepcopy(specs[0]);caps['capabilities']['allOf']=['move','jump']
    module,calls=resolve(caps,lib,by[caps['node_id']],emit)
    rows.append(dict(check='missing_recoil_not_renamed_as_supported',passed=module is None and calls==1))
    rows.append(dict(check='production_cannot_consume_unknown_interfaces',passed=lib.find_payload(specs[0])==[]))
    # Mutate ONLY newly created copies. Original evidence is immutable.
    record_path=REPO/lib.find_payload(specs[0],isolated_experiment=True)[0]['record']
    record=json.loads(record_path.read_text());bad=out/'tampered-evidence.json';bad.write_text('{}')
    record['evidence'][0]['path']=str(bad.relative_to(REPO))
    fake=CandidateLibrary(out/'tampered-library');path=fake.root/'payloads'/demand_key(specs[0])/'bad'/'record.json';write(path,record)
    reason=None
    try:fake.find_payload(specs[0],isolated_experiment=True)
    except ValueError as error:reason=str(error)
    rows.append(dict(check='changed_evidence_rejected',passed=reason=='payload_evidence_drift',reason=reason))
    alias=copy.deepcopy(specs[0]);alias['id']='another-map/local-request';alias['node']['label']='Different presentation name'
    rows.append(dict(check='prose_ids_do_not_force_regeneration',passed=bool(lib.find_payload(alias,isolated_experiment=True))))
    write(out/'events.json',events);write(out/'summary.json',dict(rows=rows,all_passed=all(r['passed']for r in rows),
        scope='Real library/source and demand-boundary checks; these checks are not physical traversal evidence'))
    return rows

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--batch',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    result=run(a.batch,a.out);print(json.dumps(result,ensure_ascii=False,indent=2))
    if not all(r['passed']for r in result):raise SystemExit(2)
