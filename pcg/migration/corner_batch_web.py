"""Export a small, version-bound review snapshot; never certify a configuration.

Only current base versions are shown. Frozen proposal documents are visual
review assets under generation/, outside the authoritative Module catalog.
"""
from __future__ import annotations
import argparse
from collections import Counter
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
from . import core

SCHEMA = 'map-notes/corner-batch-status/v1'


def _optional(path, default):
    return core.read(path) if path.is_file() else default


def _capture_stage(folder, name):
    path=folder/(name+'.json')
    if not path.is_file():return {},None
    # Read once: parsing and SHA must describe the same immutable byte image,
    # even if the running batch replaces the live phase file immediately after.
    raw=path.read_bytes();value=json.loads(raw);digest=hashlib.sha256(raw).hexdigest()
    target=core.REPO/'generation/module-review/corner-batches'/folder.name/'states'/(name+'-'+digest+'.json')
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():
        if core.sha(target)!=digest:raise ValueError('immutable_corner_stage_snapshot_changed')
    else:
        with tempfile.NamedTemporaryFile(dir=target.parent,delete=False) as stream:
            stream.write(raw);stream.flush();os.fsync(stream.fileno());temporary=Path(stream.name)
        temporary.replace(target)
    return value,dict(path=core.relative(target),sha256=digest,sourcePath=core.relative(path))


def export(batch=None, *, write_status=True):
    catalog = core.read(core.ACTIVE/'catalog.json')
    entries = {e['id']: e for e in catalog['modules']}
    states = core.STATE/'corner-batches'
    plans = sorted(states.glob('*/plan.json'), key=lambda p:(p.stat().st_mtime_ns, str(p)))
    folder = states/core.safe_id(batch) if batch else (plans[-1].parent if plans else None)
    sources = {}
    stages = {}
    for name in ('plan', 'preparation', 'preflight', 'qualification'):
        value,reference = _capture_stage(folder,name) if folder else ({},None)
        stages[name] = value
        if reference:sources[name] = reference
    plan=stages['plan']
    by_stage = {name:{r['key']:r for r in value.get('rows', [])}
                for name,value in stages.items() if name != 'plan'}
    rows = []; stale = 0
    for option in plan.get('options', []):
        entry = entries.get(option['moduleId'])
        if not entry or (entry['contentVersion'], entry['contentSha256']) != (
                option['baseContentVersion'], option['baseDocumentSha256']):
            stale += 1; continue
        row = {key:option[key] for key in ('key','moduleId','portId','corner',
                'baseContentVersion','baseDocumentSha256','targetFace')}
        row.update(status='not_started', preview=None)
        prepared = by_stage['preparation'].get(option['key'])
        latest = None
        for stage in ('preparation', 'preflight', 'qualification'):
            result = by_stage[stage].get(option['key'])
            if result:
                row['status'] = result['status']; row['stage'] = stage; latest = result
        if latest:
            if latest.get('conflict'): row['reason'] = str(latest['conflict'])
            for key in ('configurationId','actualAttempts'):
                if key in latest: row[key] = latest[key]
            row['failures'] = dict(routes=len(latest.get('routeFailures', [])),
                boundaryProbes=len(latest.get('probeFailures', [])),
                counters=len(latest.get('invalidatingCounters', [])))
            if latest.get('preparationError'): row['reason'] = latest['preparationError']
        if row['status'] == 'verified':
            ref = latest.get('receipt') if latest else None
            indexed = isinstance(ref, dict) and any(r.get('path')==ref.get('path') and r.get('sha256')==ref.get('sha256')
                                for r in entry.get('cornerConfigurationReceipts', []))
            if not indexed: row['status'] = 'verified_pending_index'
            if not isinstance(ref, dict) or not ref.get('path') or not ref.get('sha256'):
                row['status'] = 'verification_pending'
            else:
                receipt_path = core.REPO/ref['path']
                if not receipt_path.is_file() or core.sha(receipt_path)!=ref['sha256']:
                    row['status'] = 'verification_pending'
                else:
                    receipt=core.read(receipt_path)
                    if (receipt.get('moduleId')!=row['moduleId'] or receipt.get('baseContentVersion')!=row['baseContentVersion']
                            or receipt.get('baseDocumentSha256')!=row['baseDocumentSha256']
                            or not any(r.get('portId')==row['portId'] and r.get('corner')==row['corner'] for r in receipt.get('relocations',[]))):
                        row['status'] = 'verification_pending'
        if prepared and prepared.get('status') == 'prepared' and row['status'] != 'verified':
            source = core.REPO/prepared['prepared']/'module.mapnote.json'
            if not source.resolve().is_relative_to(core.REPO.resolve()):
                raise ValueError('corner_review_source_outside_repository')
            core.safe_id(option['key'])
            destination = core.REPO/'generation/module-review/corner-batches'/folder.name/(option['key']+'.mapnote.json')
            digest = prepared['documentSha256']
            # A later certification may rewrite evidence fields. Preserve the
            # earlier frozen proposal instead of relabelling those new bytes.
            if not destination.exists() and source.is_file() and core.sha(source)==digest:
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
            if destination.is_file() and core.sha(destination)==digest:
                row['preview'] = dict(path=core.relative(destination), sha256=digest,
                    contentVersion=prepared['contentVersion'], certified=False)
        rows.append(row)
    modules = []
    for entry in catalog['modules']:
        document = core.REPO/entry['file'].removeprefix('./')
        if core.sha(document) != entry['contentSha256']:
            raise ValueError('current_review_document_changed:'+entry['id'])
        doc = core.read(document)
        modules.append(dict(id=entry['id'], contentVersion=entry['contentVersion'],
            documentSha256=entry['contentSha256'],
            certifiedConfigurations=len(entry.get('cornerConfigurationReceipts', [])),
            mirrorStatus=doc['generationContract'].get('mirror', {}).get('status','UNKNOWN')))
    counts = dict(Counter(r['status'] for r in rows))
    data = dict(schema=SCHEMA, createdUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        catalogSha256=core.sha(core.ACTIVE/'catalog.json'), batchId=folder.name if folder else None,
        currentTemplates=len(modules), totalOptions=len(plan.get('options', [])),
        currentOptions=len(rows), staleOptionsOmitted=stale, counts=counts,
        actualAttempts=sum(v.get('actualAttempts',0) for k,v in stages.items() if k in ('preflight','qualification')),
        stagesComplete={k:v.get('complete',False) for k,v in stages.items() if k!='plan'},
        sources=sources, modules=modules, rows=rows,
        scope='Visual review and recorded progress only. Catalog-listed certificates alone expose usable configurations; proposals and mirror previews never grant Map rights.')
    if write_status:core.write(core.ACTIVE/'corner-batch-status.json', data)
    return data


def export_all():
    """Latest frozen plan wins per logical option, regardless of result quality.

    Plans are created once and never overwritten; their creation mtimes define
    batch order, with path as a deterministic tie-break. Historical phase byte
    images remain referenced, including failed and superseded results.
    """
    plans=sorted((core.STATE/'corner-batches').glob('*/plan.json'),
                 key=lambda p:(p.stat().st_mtime_ns,str(p)))
    if not plans:return export()
    fragments=[export(plan.parent.name,write_status=False) for plan in plans]
    if len({part['catalogSha256']for part in fragments})!=1:
        raise ValueError('current_catalog_changed_during_corner_snapshot')
    latest={};history={}
    for part in fragments:
        for row in part['rows']:
            identity=(row['baseDocumentSha256'],row['moduleId'],row['portId'],row['corner'])
            history.setdefault(identity,[]).append(dict(batchId=part['batchId'],status=row['status'],
                contentVersion=(row.get('preview')or{}).get('contentVersion'),stage=row.get('stage')))
            latest[identity]={**row,'sourceBatchId':part['batchId']}
    rows=[]
    for identity,row in latest.items():
        rows.append({**row,'history':history[identity]})
    rows.sort(key=lambda r:(r['moduleId'],r['portId'],r['corner']))
    data={**fragments[-1], 'batchId':'all-batches',
        'batchIds':[part['batchId']for part in fragments],
        'mergePolicy':'Latest frozen plan in creation order wins per current base SHA / Module / Port / corner; never choose the best result.',
        'rows':rows,'counts':dict(Counter(row['status']for row in rows)),
        'totalOptions':len(rows),'currentOptions':len(rows),
        'staleOptionsOmitted':sum(part['staleOptionsOmitted']for part in fragments),
        'actualAttempts':sum(part['actualAttempts']for part in fragments),
        'sources':{part['batchId']:part['sources']for part in fragments},
        'stagesCompleteByBatch':{part['batchId']:part['stagesComplete']for part in fragments}}
    data.pop('stagesComplete',None)
    core.write(core.ACTIVE/'corner-batch-status.json',data)
    return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    choice=parser.add_mutually_exclusive_group();choice.add_argument('--batch');choice.add_argument('--all-batches',action='store_true')
    args = parser.parse_args(); result = export_all() if args.all_batches else export(args.batch)
    print({key:result[key] for key in ('batchId','currentTemplates','totalOptions','counts','actualAttempts')})
