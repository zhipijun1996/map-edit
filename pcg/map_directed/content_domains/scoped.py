"""Read existing quarantine records as new content inputs, never general passes."""
import copy,json
from pathlib import Path
from ..director import REPO
from ..direct_join.canonical import reload_catalog
from ..library import withdrawn_versions
from pcg.prototype.factory.core.engine import file_sha

def discover():
    root=REPO/'pcg/map_directed/library';cache={};audit=[];rewards=[];withdrawn=withdrawn_versions()
    for record in sorted((root/'payloads').glob('*/*/record.json')):
        r=json.loads(record.read_text());catalog=REPO/r['catalog'];version=r['contentVersion'];reason=[]
        if version in withdrawn:reason.append('withdrawn')
        if not(catalog/'source.json').exists():reason.append('archived_payload_requires_restore')
        row=dict(version=version,record=str(record.relative_to(REPO)),scope=r['scope'],status='content_source_only_pending_fresh_validation',reasons=reason)
        if reason:audit.append(row);continue
        if catalog not in cache:cache[catalog]=reload_catalog(catalog)
        m=next(m for m in cache[catalog]if m['id']==r['node_id'])
        if m['content_version']!=version:raise ValueError('scoped_payload_version_drift')
        row.update(ports=len(m['ports']),family=m.get('selection_family',m['case']['family']),hazards=len(m['case'].get('thorns',[])),chests=len(m['case'].get('reward_sites',[])))
        # A concrete one-Port excursion is useful as a reward-return input.
        # Require its actual parent case trace declarations to include the
        # same Port entering and leaving; do not infer all-to-all connectivity.
        if len(m['ports'])==1 and len(m['case'].get('reward_sites',[]))==1 and m['case'].get('thorns'):
            for proof in r['evidence']:
                p=REPO/proof['path']
                if not p.exists()or file_sha(p)!=proof['sha256']:raise ValueError('scoped_parent_evidence_missing_or_drift')
            parent=catalog.parent;cases=json.loads((parent/'cases.json').read_text())['cases'];observed=False
            for c in cases:
                steps=c['r2_semantics']['logical_route']
                for a,b in zip(steps,steps[1:]):
                    if a['to']==m['id']==b['from']and a['edge_id']==b['edge_id']:observed=True
            if observed:
                m=copy.deepcopy(m);key=next(iter(m['ports']));m['port_transitions']={key+'>'+key:copy.deepcopy(m['port_to_center'][key]+m['center_to_port'][key])};m['center_port']=key
                m['variant_id']='scoped-source/'+version[7:19];m.setdefault('adaptation',{})['scope_import']='Original concrete context only; fresh independent and whole-Map validation required';m['source_version']=version;rewards.append(m);row['usable_input']='one-port challenge and physically observed foldback'
        audit.append(row)
    return rewards,audit
