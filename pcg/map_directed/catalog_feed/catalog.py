import copy,json,subprocess
from pathlib import Path
from ..director import REPO
from ..library import withdrawn_versions
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.factory.core.quality import module_hash

def load():
    current=REPO/'generation/workshop/plains-recoil-current/catalog.json'
    view=json.loads((current if current.exists()else REPO/'generation/workshop/plains-recoil-v1/catalog.json').read_text());withdrawn=withdrawn_versions();items=[]
    names={e['contentVersion']:e['title']for e in json.loads((REPO/'library/workshop/catalog.json').read_text())['modules']}
    for row in view['rows']:
        root=(REPO/row['record']).parent;r=json.loads((root/'record.json').read_text());doc=json.loads((root/'module.mapnote.json').read_text())
        casefile=root/('case.json'if(root/'case.json').exists()else'cases.json');raw=json.loads(casefile.read_text());cases=[raw]if casefile.name=='case.json'else raw['cases']
        if file_sha(root/'module.mapnote.json')!=r['document_sha256']or file_sha(casefile)!=r['case_sha256'if casefile.name=='case.json'else'cases_sha256']:raise ValueError('library_bytes_drift')
        if doc['generationContract']['contentVersion']!=r['contentVersion']:raise ValueError('library_version_drift')
        for c in cases:
            if module_hash(c)!=c['module_sha256']:raise ValueError('library_module_hash_drift/'+c['id'])
        result=subprocess.run(['node',str(REPO/'pcg/map_directed/library_bridge.mjs'),'--validate',str(root/'module.mapnote.json')],capture_output=True,text=True,check=True,cwd=REPO)
        if not json.loads(result.stdout)['versionMatches']:raise ValueError('library_document_stale')
        missing=[a['path']for a in r.get('evidence',[])if not(REPO/a['path']).exists()]
        items.append(dict(row=row,record=r,document=doc,cases=cases,title=names.get(r['contentVersion'],row['family']),withdrawn=r['contentVersion']in withdrawn,original_evidence_missing=missing))
    return items
