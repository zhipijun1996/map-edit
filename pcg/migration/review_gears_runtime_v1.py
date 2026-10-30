"""Additive data/Cell compiler extension, reusing native compilation/execution."""
import copy,sys,types
from pathlib import Path
from . import godot_package as base
from pcg.manual_review.first30_content_v2 import decode
VERSION='foundation-data-runtime/review-gears-v1'
SCENES=[('module','module_loader_review_gears_v1.gd'),('demo','package_demo_v3.gd')]


def required(doc,cases):
    return any(o.get('mechanics',{}).get('kind')=='retractable_gears/v1' for o in doc.get('objects',[]))


def audit_cases(doc,cases,*,require_replay=True):
    content=decode(doc);ordinary=copy.deepcopy(doc);inputs=copy.deepcopy(cases)
    ordinary['objects']=[o for o in ordinary['objects'] if o.get('mechanics',{}).get('kind')!='retractable_gears/v1']
    for c in inputs:
        c['latches']=[l for l in c['latches']if l.get('kind')!='retractable_gears/v1'];c.pop('retractable_groups',None)
    _,audit=base.audit_cases(ordinary,inputs,require_replay=require_replay,_extension=True)
    for c in cases:
        base._equal(c.get('retractable_groups'),content['retractable_groups'],'exact_synchronous_hazard_groups',c['id'])
        base._equal(c['latches'],content['latches'],'group_receiver_binding',c['id'])
    audit.update(retractableGroups='exact authored bands; original projectile eligibility and original contact-damage emitter',platformGeometryUnchanged=True)
    return content,audit


def dependencies(project):
    rows=base._dependencies(project,base.EXTENDED_VERSION)
    for name in ('pcg/migration/runtime/module_loader_review_gears_v1.gd','pcg/manual_review/runtime/retractable_gears_v1.gd'):
        rows.append(dict(path=name,sha256=base.sha(base.ROOT/name)))
    return sorted(rows,key=lambda r:r['path'])


def decorate_manifest(manifest,stage):
    manifest['reviewGearBinding']=dict(compiler=dict(path='pcg/migration/review_gears_runtime_v1.py',sha256=base.sha(__file__)),
        decoder=dict(path='pcg/manual_review/first30_content_v2.py',sha256=base.sha(base.ROOT/'pcg/manual_review/first30_content_v2.py')),
        projectileEligibility='original ShotLatch receiver',damage='original DemoContactEmitter and FrameDamagePolicy',
        scriptedResourceWrites=False,platformsRemoved=False)


def verify_package(output_dir,require_loaded=True):
    return base.verify_package(output_dir,require_loaded=require_loaded,_extension=sys.modules[__name__])


def run_package_validation(*args,**kwargs):
    runner=types.FunctionType(base.run_package_validation.__code__,{**base.__dict__,'verify_package':verify_package},argdefs=base.run_package_validation.__defaults__)
    runner.__kwdefaults__=base.run_package_validation.__kwdefaults__
    return runner(*args,**kwargs)
