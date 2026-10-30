"""Real Godot acceptance of an archive extracted into an isolated host directory."""
import hashlib,json,os,shutil,subprocess,tempfile,urllib.request,zipfile
from pathlib import Path
from . import library as l
from . import package
from integration.install_host import install

def engine_path(explicit=None):
 lock=l.read(l.ROOT/'runtime/host-lock.json');expected=lock['godot']['sha256']
 candidates=[explicit,os.environ.get('GODOT'),shutil.which('godot'),l.ROOT/'pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64']
 for p in candidates:
  if p and Path(p).is_file():
   if l.sha(p)!=expected:
    if p in [explicit,os.environ.get('GODOT')]:raise ValueError('incompatible_godot_binary:'+str(p))
    continue
   return Path(p).resolve()
 cache=Path(os.environ.get('XDG_CACHE_HOME',Path.home()/'.cache'))/'map-edit/toolchain';cache.mkdir(parents=True,exist_ok=True);binary=cache/'Godot_v4.7.2-stable_linux.x86_64'
 if not binary.exists():
  archive=cache/'Godot_v4.7.2-stable_linux.x86_64.zip';url='https://github.com/godotengine/godot-builds/releases/download/4.7.2-stable/'+archive.name
  urllib.request.urlretrieve(url,archive)
  if l.sha(archive)!='cadd3204e728a35d3f13adb7fd0d7902636b79f6b95c40c265eb73b6c35329e4':raise ValueError('godot_download_checksum_mismatch')
  with zipfile.ZipFile(archive)as z:z.extractall(cache)
  binary.chmod(0o755)
 if l.sha(binary)!=expected:raise ValueError('godot_cache_checksum_mismatch')
 return binary

def run(archive,godot=None,host_source=None,work=None):
 engine=engine_path(godot);work=Path(work)if work else Path(tempfile.mkdtemp(prefix='module-package-acceptance-'));work.mkdir(parents=True,exist_ok=True)
 if work.resolve().is_relative_to(l.ROOT.resolve()):raise ValueError('clean_acceptance_work_must_be_outside_source_repository')
 toolchain=work/'toolchain';toolchain.mkdir();isolated_engine=toolchain/engine.name;shutil.copyfile(engine,isolated_engine);isolated_engine.chmod(0o755);engine=isolated_engine
 project=work/'project';project.mkdir(exist_ok=False);bundle=project/'module_pack';bundle.mkdir()
 with zipfile.ZipFile(archive)as z:
  for n in z.namelist():
   if Path(n).is_absolute()or'..'in Path(n).parts:raise ValueError('unsafe_archive_member:'+n)
  z.extractall(bundle)
 package.verify(bundle);tested_fingerprint=l.read(bundle/'manifest.json')['runtimeFingerprint']
 lock=bundle/'runtime/host-lock.json'
 if not host_source:
  cache=Path(os.environ.get('XDG_CACHE_HOME',Path.home()/'.cache'))/'map-edit/hosts'/l.sha(lock)
  cache.mkdir(parents=True,exist_ok=True);install(lock,cache);host_source=cache
 install(lock,project,host_source)
 (project/'project.godot').write_text('config_version=5\n[application]\nconfig/name="Isolated Module package acceptance"\nconfig/features=PackedStringArray("4.7", "GL Compatibility")\n[physics]\ncommon/physics_ticks_per_second=60\n[rendering]\nrenderer/rendering_method="gl_compatibility"\nrenderer/rendering_method.mobile="gl_compatibility"\n')
 environment=os.environ.copy();environment['XDG_DATA_HOME']=str(work/'user-data');environment['XDG_CONFIG_HOME']=str(work/'user-config');environment['GODOT_SILENCE_ROOT_WARNING']='1'
 for label,args in [('import',['--editor','--import']),('runtime',['--script','res://module_pack/integration/validate_runtime.gd','--','--report',str(work/'runtime.json')])]:
  with(work/(label+'.log')).open('w')as stream:
   command=[str(engine),'--headless','--path',str(project),*args]
   if label=='runtime':
    tracer=shutil.which('strace')
    if not tracer:raise ValueError('strace_required_for_workspace_read_audit')
    command=[tracer,'-f','-e','trace=openat,open,readlink','-o',str(work/'runtime-files.log'),*command]
   result=subprocess.run(command,cwd=project,env=environment,stdout=stream,stderr=subprocess.STDOUT,timeout=300)
  log=(work/(label+'.log')).read_text()
  if result.returncode or'SCRIPT ERROR:'in log or'ERROR:'in log:raise ValueError('godot_'+label+'_failed:'+str(work/(label+'.log')))
 trace=(work/'runtime-files.log').read_text()
 if str(l.ROOT)in trace or any(p in trace for p in ['pcg/manual_review','pcg/results','source-resource-v9']):raise ValueError('runtime_read_old_workspace:'+str(work/'runtime-files.log'))
 if tested_fingerprint!=package.runtime_fingerprint():raise ValueError('runtime_changed_during_clean_acceptance')
 report=l.read(work/'runtime.json')
 if report.get('passed')is not True:raise ValueError('portable_runtime_validation_failed')
 report.update(engineSha256=l.sha(engine),hostLockSha256=l.sha(lock),runtimeFingerprint=tested_fingerprint,archiveExtracted=True,hostFilesVerified=len(l.read(lock)['files']),oldWorkspaceRead=False,dependencyAudit='strace open/openat/readlink: no reads from the source repository or former experiment/fixture paths; resources resolve in the clean extracted project and hash-locked host.')
 return report,work

def certify(report):
 if not report.get('passed')or report['runtimeFingerprint']!=package.runtime_fingerprint():raise ValueError('changed_runtime_since_acceptance')
 evidence=l.ROOT/'evidence/module-production/portable-runtime.json';l.write(evidence,report)
 def change():
  rows={v['id']:v for v in report['modules']}
  for folder,r in l.records():
   if r['id']not in rows:continue
   if not rows[r['id']]['passed']or rows[r['id']]['sourceSha256']!=r['source']['sha256']:raise ValueError('changed_module_since_acceptance:'+r['id'])
   r['runtime'].update(deliveryStatus='ready',portableValidation=dict(sourceSha256=r['source']['sha256'],runtimeFingerprint=report['runtimeFingerprint'],report=evidence.relative_to(l.ROOT).as_posix(),reportSha256=l.sha(evidence),engineSha256=report['engineSha256'],hostLockSha256=report['hostLockSha256'],scope='Scene load, translated Ports, actual collision shapes, external player/resources, real native bell and reward service integration. Route robustness remains bound to prior physical qualification.'))
   l.write(folder/'record.json',r)
 l.transaction(change)
