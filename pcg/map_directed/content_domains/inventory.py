"""Per-version adaptation ledger over the existing catalog, not a second library."""
import argparse,copy,json
from pathlib import Path
from .catalog import describe
from .build import load
from ..catalog_feed.catalog import load as catalog
from ..direct_join.canonical import export_reload
from ..director import REPO
from ..run import write
from pcg.prototype.factory.core.engine import file_sha


def run(name,sources):
    out=REPO/'pcg/results'/name
    if out.exists():raise ValueError('immutable_inventory_exists')
    out.mkdir();pool,rejections=load(sources);items=catalog();versions={x['record']['contentVersion']for x in items}
    pool=[m for m in pool if m['source_version']in versions]
    selected={}
    for m in pool:selected.setdefault(m['source_version'],m)
    attempts={}
    for source in sources:
        p=REPO/source
        if not(p/'adaptation-audit.json').exists():continue
        for r in json.loads((p/'adaptation-audit.json').read_text()):attempts.setdefault(r['version'],[]).append(dict(run=source,**r))
    canonical=[]
    for version,m in selected.items():
        m=copy.deepcopy(m);m['id']='block-'+version[7:23];m['spec']['node_id']=m['id'];canonical.append(m)
    canonical=export_reload(canonical,out/'module-library',producer='pcg/map_directed/content_domains/inventory.py')
    documents={m['source_version']:m['canonical_document']for m in canonical};rows=[]
    for item in items:
        version=item['record']['contentVersion'];d=describe(item);m=selected.get(version)
        row=dict(source=d,source_document_sha256=item['record']['document_sha256'],status='passed_scoped_block_interface'if m else'needs_design_or_verification',
                 attempts=attempts.get(version,[]),source_qualification=[r for r in rejections if r['version']==version],
                 canonical=documents.get(version),variant=m['variant_id']if m else None,
                 directed_pairs=list(m.get('port_transitions',{}))if m else[],production_admitted=False,human_quality='unreviewed')
        rows.append(row);write(out/'versions'/(version[7:]+'.json'),row)
    write(out/'inventory.json',dict(schema='pcg/full-library-block-adaptation-ledger/v1',rows=rows,sources=sources))
    write(out/'summary.json',dict(versions=len(items),processed=len(rows),qualified=len(selected),blocked=len(items)-len(selected),
          all_adapted=len(selected)==len(items),production_admitted=False,
          scope='Exact finite directions under bound abilities; every new placement needs whole-Map physics; no general state guarantee'))
    write(out/'source-provenance.json',[dict(path=x['row']['record'],sha256=file_sha(REPO/x['row']['record']))for x in items])


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--sources',nargs='+',required=True);a=p.parse_args();run(a.name,a.sources)
