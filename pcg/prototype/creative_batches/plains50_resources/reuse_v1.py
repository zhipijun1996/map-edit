"""Fresh-process exact demand lookup against original persistent library."""
import argparse,json
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT
from pcg.prototype.workshop.library import WorkshopLibrary
from pcg.prototype.factory.core.engine import file_sha
RUNS=['workshop-plains50-resources-production-v1/round-01','workshop-plains50-resources-production-v1/round-02','workshop-plains50-resources-sightline-production-v2/round-00','workshop-plains50-resources-lowray-production-v2/round-00']
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();out=ROOT/'results'/a.name
 if out.exists():raise ValueError('immutable_retrieval_receipt')
 rows=[];library=WorkshopLibrary(ROOT/'module_library/store')
 for run in RUNS:
  root=ROOT/'results'/run
  for item in json.loads((root/'modules/manifest.json').read_text())['modules']:
   version=item['contentVersion'];folder=ROOT/'module_library/store/candidates'/version.removeprefix('sha256:');c=json.loads((folder/'case.json').read_text());spec=c['map_specification'];hits=library.find_single_exact(spec)
   assert any(h['record']['contentVersion']==version for h in hits),version
   rows.append(dict(recipe=c['production_recipe'],interface=c['interface'],specification=spec['id'],contentVersion=version,matches=[h['record']['contentVersion']for h in hits],document_sha256=file_sha(folder/'module.mapnote.json'),record_sha256=file_sha(folder/'record.json'),generator_called=False,new_physics_cases=0))
 result=dict(schema='pcg/plains50-resource-retrieval/v1',library='pcg/module_library/store',retrieved=len(rows),expected=8,fresh_process=True,rows=rows,generator_called=False,new_physics_cases=0,production_admitted=False)
 out.mkdir(parents=True);(out/'receipt.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
