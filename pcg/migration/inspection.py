"""Read-only content audits. Similarity and non-visitation never delete Cells."""
import collections
import gzip
import json
from functools import lru_cache
from . import core
from pcg.prototype.factory.core.quality import digest


@lru_cache(maxsize=2)
def raw_results(path):
    with gzip.open(path, 'rt') as stream:
        return json.load(stream)['results']


def normalized_objects(doc):
    prefix = doc['id']+'/'
    def normalize(value):
        if isinstance(value, str): return value.replace(prefix, 'module/')
        if isinstance(value, list): return [normalize(v) for v in value]
        if isinstance(value, dict): return {k: normalize(v) for k,v in value.items() if k not in ('label','note')}
        return value
    return normalize(doc['objects'])


def platform_audit(folder):
    folder = core.resolve_artifact(core.relative(folder)+'/module.mapnote.json').parent
    doc = core.read(folder/'module.mapnote.json'); cases = core.legacy_cases(folder)
    support_counts = collections.Counter(); limitations = []
    for case in cases:
        evidence = case.get('factory_evidence', {})
        run = doc['generationContract']['generation']['source'].get('run')
        if not run or not evidence.get('output'):
            limitations.append('canonical_raw_reference_missing:'+case['id']); continue
        path = core.resolve_artifact(run+'/'+evidence['output'])
        if not path.is_file():
            limitations.append('canonical_raw_missing:'+case['id']); continue
        result = raw_results(str(path))[evidence['index']]
        if result['id'] != case['id']:
            limitations.append('canonical_result_identity_mismatch:'+case['id']); continue
        support_counts.update(f.get('support_id') for f in result.get('frames',[]) if f.get('grounded'))
    platforms = []
    for index, rect in enumerate(cases[0].get('platforms', [])):
        roles = set()
        for case in cases:
            for port in case.get('ports', []):
                if port.get('support_index') == index: roles.add('port_support:'+port['id'])
            for thorn in case.get('thorns', []):
                if thorn.get('platform_index') == index: roles.add('hazard_host')
        if support_counts.get('Platform'+str(index)): roles.add('observed_canonical_support')
        x,y,w,h = rect
        contained_by = [j for j,(a,b,c,d) in enumerate(cases[0]['platforms']) if j != index
                        and a<=x and b<=y and a+c>=x+w and b+d>=y+h]
        platforms.append(dict(index=index, rect=rect, roles=sorted(roles),
            observedSupportFrames=support_counts.get('Platform'+str(index),0),
            containedBy=contained_by, decision='retain',
            review='overlapping_collider_review' if contained_by else 'nominal_unvisited_not_proven_redundant' if not roles else 'identified_use'))
    return dict(source=core.relative(folder), title=doc['title'], platforms=platforms,
        limitations=limitations+['Canonical successes do not cover all failure recovery or alternate strategies.',
            'No platform is removed by this audit.'], newPhysicsCases=0)


def run():
    groups = collections.defaultdict(list); near = collections.defaultdict(list); platforms=[]
    journal = core.ledger()
    folders = sorted(core.LEGACY.glob('*/record.json'))
    folders += [core.resolve_artifact(path+'/record.json') for path, entry in journal['entries'].items()
                if entry.get('migrationStatus') == 'active']
    for file in folders:
        folder = file.parent; doc=core.read(folder/'module.mapnote.json'); cases=core.legacy_cases(folder)
        # Conservative exact key includes recorded strategies and all runtime
        # input fields except identity, display, provenance and recording caches.
        ignored = {'id','recorded_frames','factory_id','factory_evidence','module_sha256',
            'layout_title','play_hint','review_alias','generation_rule','map_specification',
            'source_map_request','map_request_response','layout_uid','rule_parameters',
            'idea_ids','native_scene','native_block_scene','interface'}
        programs=[{k:v for k,v in case.items() if k not in ignored} for case in cases]
        identity = dict(objects=normalized_objects(doc), programs=programs,
            physicsSource=doc['generationContract']['generation']['source'].get('physicsSourceCommit'),
            capabilities=doc['capabilityRequirements'])
        groups[digest(identity)].append(core.relative(folder))
        family=cases[0].get('family','UNKNOWN');near[family].append(core.relative(folder))
        platforms.append(platform_audit(folder))
    report=dict(schema='pcg/module-migration-content-audit/v1',
        inspected=len(folders), exactDuplicateGroups=[v for v in groups.values() if len(v)>1],
        similarityReviewGroups=[dict(family=k,modules=v,status='needs_human_comparison')
                               for k,v in near.items() if len(v)>1],
        platformAudits=platforms, automaticPlatformRemovals=0,
        warnings=['Family grouping is a retrieval clue, not a duplicate verdict.',
                  'Only complete equivalence may merge templates; mirror intent is insufficient.'])
    core.write(core.STATE/'content-audit.json',report)
    return {k:v for k,v in report.items() if k not in ('platformAudits','similarityReviewGroups')}
