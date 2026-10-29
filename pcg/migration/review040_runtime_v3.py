"""v2 physical consumer with read-only opened-plate presentation."""
import sys,types
from . import godot_package as base,review040_runtime_v2 as previous
VERSION='foundation-data-runtime/review040-v3'
SCENES=[('module','module_loader_review040_v3.gd'),('demo','package_demo_review_first30_v2.gd')]
audit_cases=previous.audit_cases
air_terminal=previous.air_terminal
def dependencies(project):
 rows=previous.dependencies(project)
 for name in ['pcg/migration/runtime/module_loader_review040_v3.gd','pcg/manual_review/runtime/review040_release_overlay_v1.gd']:rows.append(dict(path=name,sha256=base.sha(base.ROOT/name)))
 return sorted(rows,key=lambda r:r['path'])
def decorate_manifest(manifest,stage):
 previous.decorate_manifest(manifest,stage)
 manifest['releasePresentation']=dict(source='pcg/manual_review/runtime/review040_release_overlay_v1.gd',readsOnly='actual committed_release.released',collisionAndInputsChanged=False)
def compile_package(*args,**kwargs):return base.compile_package(*args,**kwargs,_extension=sys.modules[__name__])
def verify_package(output_dir,require_loaded=True):return base.verify_package(output_dir,require_loaded=require_loaded,_extension=sys.modules[__name__])
def run_package_validation(*args,**kwargs):
 runner=types.FunctionType(base.run_package_validation.__code__,{**base.__dict__,'verify_package':verify_package},argdefs=base.run_package_validation.__defaults__);runner.__kwdefaults__=base.run_package_validation.__kwdefaults__;return runner(*args,**kwargs)
