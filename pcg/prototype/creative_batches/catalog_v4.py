"""Isolated selected20 launcher/query interface, preserving catalog_v1 sources.

prepare creates a new augmented catalog plus twenty independent single-case
inputs. --play N opens the owner scene in true manual mode; --dry-run only
checks and prints the command. --query uses unchanged WorkshopLibrary.
"""
import argparse,json,os,subprocess,sys
from pathlib import Path
from pcg.module_library.paths import DEFAULT_LIBRARY
from pcg.prototype.creative_batches import catalog_v1 as base
from pcg.prototype.factory.core.engine import ENGINE,PROJECT,file_sha
from pcg.prototype.factory.core.quality import module_hash
from pcg.prototype.workshop.library import WorkshopLibrary
from pcg.module_library.library import verified_document,verify_case_binding


def prepare(out):
 catalog=base.read(out/'catalog.json');selection=base.read(base.path(catalog['selected']));rows=[]
 for original in catalog['candidates']:
  row=dict(original);original_scene=dict(row['scene']);row['native_owner_scene']=original_scene
  replacement={'pcg/prototype/creative_batches/resource_routes/main-sequence-v1.tscn':'pcg/prototype/creative_batches/creative_catalog/main-sequence-portable-v1.tscn','pcg/prototype/workshop/main.tscn':'pcg/prototype/creative_batches/creative_catalog/main-capability-ui-v1.tscn'}.get(original_scene['path'])
  if replacement:row['scene']=dict(path=replacement,sha256=file_sha(base.path(replacement)),scope='portable presentation adapter; identical mechanics and canonical case',replaces=original_scene)
  root=DEFAULT_LIBRARY/'candidates'/row['contentVersion'][7:];case=base.read(root/'case.json');target=out/'play-inputs-v4'/f"{row['index']:02d}.input.json"
  base.write_new(target,dict(cases=[case]));row.update(version=row['contentVersion'],scene=row['scene'],casepath=base.relative(root/'case.json'),recordpath=base.relative(root/'record.json'),docpath=base.relative(root/'module.mapnote.json'),modelsource=row['proposal_source'],spec=row['map_specification'],play_casepath=base.relative(target),play_case_sha256=file_sha(target),play_mode='manual',verified_interfaces=dict(count=1,scope='exact selected canonical single interface only; no two-interface claim'),assembly_status='UNKNOWN / blocked without new placement and contract validation')
  rows.append(row)
 catalog.update(selection_review=selection['review'],selection_review_sha256=selection['review_sha256'],supersedes_selection=selection.get('supersedes','UNKNOWN'),pacing_held=selection.get('pacing_held',[]),single_interface_scope='one exact canonical interface per selected relationship; other interfaces and whole-map assembly UNKNOWN',schema='pcg/creative20-unified-candidate-catalog/v3',candidates=rows,launcher=dict(path=base.relative(__file__),sha256=file_sha(__file__),list='python3 -m pcg.prototype.creative_batches.catalog_v4 --list',play='python3 -m pcg.prototype.creative_batches.catalog_v4 --play N',dry_run='python3 -m pcg.prototype.creative_batches.catalog_v4 --play N --dry-run',query='python3 -m pcg.prototype.creative_batches.catalog_v4 --query SPEC.json',new_physics_during_catalog=0),base_catalog=base.relative(out/'catalog.json'),base_catalog_sha256=file_sha(out/'catalog.json'),presentation_only_scene_adaptation=True,physics_or_case_changed=False)
 base.write_new(out/'catalog-v3.json',catalog);return dict(status='prepared',catalog=base.relative(out/'catalog-v3.json'),single_case_inputs=len(rows),new_physics_cases=0)


def load(out):return base.read(out/'catalog-v3.json')
def unsupported(catalog,conflicts):return dict(status='unsupported',conflicts=conflicts,searched_library=catalog['library'],searched_versions=[r['contentVersion']for r in catalog['candidates']],negotiable=['one of the twenty frozen exact single-interface mechanical specifications','new isolated design/physics validation for changed geometry, state, abilities or interface'],map_assembly='UNKNOWN; no assembly pass',new_physics_cases=0)

def list_candidates(catalog):
 return dict(status='supported',count=len(catalog['candidates']),candidates=[dict(index=r['index'],relation_id=r['relation_id'],name=r['name'],version=r['contentVersion'],scene=r['scene']['path'],casepath=r['casepath'],spec_id=r['map_specification']['id'],assembly='UNKNOWN')for r in catalog['candidates']],new_physics_cases=0)

def query(catalog,specfile):
 try:
  spec=base.read(specfile);matches=WorkshopLibrary(DEFAULT_LIBRARY).find_single_exact(spec);allowed={r['contentVersion']for r in catalog['candidates']};matches=[m for m in matches if m['record']['contentVersion']in allowed]
  if not matches:return unsupported(catalog,[dict(field='mechanical_specification',reason='no exact selected single-interface match',requested=spec)])
  return dict(status='supported',matches=[dict(contentVersion=m['record']['contentVersion'],record=m['path'],case_id=m['case']['id'],scope=m['record']['technical_scope'])for m in matches],searched_library=catalog['library'],map_assembly='UNKNOWN; isolated new placement validation required',new_physics_cases=0,generator_called=False)
 except (KeyError,ValueError,TypeError,OSError,subprocess.CalledProcessError)as e:return unsupported(catalog,[dict(field='query',reason=str(e))])

def play(catalog,index,out,display,dry):
 row=next((r for r in catalog['candidates']if r['index']==index),None)
 if row is None:return unsupported(catalog,[dict(field='index',reason='outside frozen selected20 domain',requested=index)])
 root=DEFAULT_LIBRARY/'candidates'/row['contentVersion'][7:]
 for name,sha in row['file_sha256'].items():
  if file_sha(root/name)!=sha:raise ValueError('candidate byte drift before manual launch')
 doc=verified_document(root/'module.mapnote.json');case=base.read(root/'case.json');verify_case_binding(case,doc)
 single=base.path(row['play_casepath'])
 if file_sha(single)!=row['play_case_sha256']or base.read(single)['cases']!=[case]:raise ValueError('independent single-case input drift')
 scene=base.path(row['scene']['path'])
 if file_sha(scene)!=row['scene']['sha256']:raise ValueError('owner scene changed since catalog')
 command=[str(ENGINE),'--path',str(PROJECT),str(scene),'--','--cases-json',str(single),'--case','0']
 result=dict(status='prepared'if dry else'manual_launched',index=index,relation_id=row['relation_id'],version=row['contentVersion'],command=command,casepath=row['play_casepath'],canonical_case_hash=case['module_sha256'],scene=row['scene']['path'],manual_mode=True,trace_replay=False,counts_as_physics_validation=False)
 if not dry:
  log=out/'manual-logs'/f'{index:02d}-{os.getpid()}.log';log.parent.mkdir(parents=True,exist_ok=True)
  with log.open('x')as f:p=subprocess.Popen(command,stdout=f,stderr=subprocess.STDOUT,env=dict(os.environ,DISPLAY=display,LIBGL_ALWAYS_SOFTWARE='1'))
  result.update(pid=p.pid,log=base.relative(log))
 return result

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',nargs='?',choices=['prepare']);g=p.add_mutually_exclusive_group();g.add_argument('--list',action='store_true');g.add_argument('--play',type=int);g.add_argument('--query',type=Path);p.add_argument('--dry-run',action='store_true');p.add_argument('--display',default=os.environ.get('DISPLAY',':103'));p.add_argument('--out',type=Path,default=base.REPO/'pcg/results/workshop-creative20-catalog-v2');a=p.parse_args()
 if a.command=='prepare':result=prepare(a.out)
 else:
  catalog=load(a.out)
  if a.list:result=list_candidates(catalog)
  elif a.play is not None:result=play(catalog,a.play,a.out,a.display,a.dry_run)
  elif a.query:result=query(catalog,a.query)
  else:p.error('choose prepare, --list, --play N or --query SPEC.json')
 print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result['status']!='unsupported'else 2
if __name__=='__main__':sys.exit(main())
