"""Freeze original-input Foundry winners into the existing migration pipeline."""
import argparse
import copy
from pathlib import Path
from . import core,game_adapter,game_world_v4
from pcg.prototype.factory.core.quality import module_hash


def stage(prepared,discovery,out):
    prepared=Path(prepared).resolve();discovery=Path(discovery).resolve();out=Path(out).resolve()
    if out.exists():raise ValueError('foundry_selection_destination_exists')
    out.mkdir(parents=True)
    manifest=core.read(prepared/'manifest.json');entries={r['id']:r for r in manifest['rows']}
    sources={r['id']:r for r in game_adapter.source_entries()};winners=core.read(discovery)['selected'];rows=[]
    for identifier,winner in winners.items():
        entry=entries[identifier];base=core.REPO/entry['prepared'];target=out/base.name
        case=copy.deepcopy(winner['case']);game_world_v4.prepare_one(base,sources[identifier],target,case)
        # v4 field binding does not select an input runner. Restore the original
        # recording's registered scheduler before freezing the actual experiment.
        value=core.read(target/'cases.json')['cases'][0]
        value['generation_rule']=copy.deepcopy(case['generation_rule'])
        value.pop('module_sha256',None);value['module_sha256']=module_hash(value)
        core.write(target/'cases.json',dict(cases=[value]))
        doc=core.read(target/'module.mapnote.json');gc=doc['generationContract'];objects={o['id']:o for o in doc['objects']}
        for obj in doc['objects']:
            if obj['type']not in ('spike','wallSpike'):continue
            host=objects.get(obj.get('hostId'),{});index=host.get('sourceIndex')
            matches=[r for r in value.get('original_component_hazard_scopes',[])if r['platformIndex']==index and obj.get('sourceId')in(r['before'],r['after'])]
            if len(matches)==1:obj['sourceId']=matches[0]['after']
        gc['generation']['parameters']['originalNativeReplay']=value['original_replay_source']
        gc['generation']['parameters']['originalNativeReplay']['selectionEvidence']=dict(path=core.relative(discovery),sha256=core.sha(discovery),rule='first clean of two preregistered warmup contexts; no holdout used')
        gc['generation']['source']['sourceCaseId']=value['id'];gc['generation']['source']['moduleSha256']=value['module_sha256']
        gc['generation']['parameters']['controlPlan']=value['control_plan']
        gc['generation']['parameters']['originalComponentHazardScopes']=value.get('original_component_hazard_scopes',[])
        gc['generation']['parameters']['sourceComponents']=value.get('source_components',[])
        core.write(target/'module.mapnote.json',doc);core.contract(target/'module.mapnote.json',refresh=True)
        rows.append(dict(id=identifier,moduleId=target.name,prepared=core.relative(target),status='prepared_unverified',
            originalProfile=value['original_tuning_profile'],sourceReplay=value['original_replay_source']))
    report=dict(schema='pcg/original-foundry-frozen-programs/v4',rows=rows,frozenModules=len(rows),certifiedModules=0)
    core.write(out/'manifest.json',report);return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared',required=True);p.add_argument('--discovery',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    r=stage(a.prepared,a.discovery,a.out);print(r['frozenModules'])
