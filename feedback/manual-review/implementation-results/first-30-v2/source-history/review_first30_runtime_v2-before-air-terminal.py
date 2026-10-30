"""Approved first-30 Cell/data adapters; original compiler and real native executor."""
import copy,sys,types
from . import godot_package as base
from pcg.manual_review.first30_content_v2 import decode
VERSION='foundation-data-runtime/review-first30-v2'
SCENES=[('module','module_loader_review_first30_v2.gd'),('demo','package_demo_review_first30_v2.gd')]


def required(doc,cases):return any(c.get('approved_first30')for c in cases)


def audit_cases(doc,cases,*,require_replay=True):
    content=decode(doc);ordinary=copy.deepcopy(doc);inputs=copy.deepcopy(cases)
    ordinary['objects']=[o for o in ordinary['objects'] if not(o.get('mechanics',{}).get('kind')=='retractable_gears/v1' or
        (o.get('type')=='bell'and o.get('mechanics',{}).get('service')=='ShotLatch.add_access_bell'and o['mechanics'].get('returnSideOnly')is False))]
    for c in inputs:
        c['latches']=[l for l in c['latches']if l.get('kind')!='retractable_gears/v1'];c.pop('retractable_groups',None)
        for l in c['latches']:
            if l.pop('return_access_side_policy',None)=='any':l.pop('return_access',None)
    _,audit=base.audit_cases(ordinary,inputs,require_replay=require_replay,_extension=True)
    air=[{k:p[k]for k in ('id','position','stagingPosition','face','surface','permission')}for p in doc['generationContract']['ports']if p['surface']=='AIR']
    for c in cases:
        base._equal(c.get('retractable_groups',[]),content.get('retractable_groups',[]),'authored_retractable_groups',c['id'])
        base._equal(c['latches'],content['latches'],'authored_receiver_policy',c['id'])
        base._equal(c.get('air_port_contracts',[]),air,'explicit_air_port_contract',c['id'])
    audit.update(originalProjectileAndDamageConsumers=True,
        airGoal='complete 24x36 body downward crossing for six frames; no grounded-stability claim',
        upperAccess='Original ShotLatch.add_access_bell(..., false, false)',scriptedResourceWrites=False)
    return content,audit


def dependencies(project):
    rows=base._dependencies(project,base.EXTENDED_VERSION)
    for name in ('pcg/migration/runtime/module_loader_review_gears_v1.gd','pcg/migration/runtime/module_loader_review_first30_v2.gd',
        'pcg/migration/runtime/package_demo_review_first30_v2.gd','pcg/manual_review/runtime/retractable_gears_v1.gd'):
        rows.append(dict(path=name,sha256=base.sha(base.ROOT/name)))
    return sorted(rows,key=lambda r:r['path'])


def decorate_manifest(manifest,stage):
    manifest['approvedFirst30Binding']=dict(compiler=dict(path='pcg/migration/review_first30_runtime_v2.py',sha256=base.sha(__file__)),
        decoder=dict(path='pcg/manual_review/first30_content_v2.py',sha256=base.sha(base.ROOT/'pcg/manual_review/first30_content_v2.py')),
        airGoal='full-body downward crossing, not standing',originalPhysics=True,resourcesReset=False)


def verify_package(output_dir,require_loaded=True):
    return base.verify_package(output_dir,require_loaded=require_loaded,_extension=sys.modules[__name__])


def run_package_validation(*args,**kwargs):
    runner=types.FunctionType(base.run_package_validation.__code__,{**base.__dict__,'verify_package':verify_package},argdefs=base.run_package_validation.__defaults__)
    runner.__kwdefaults__=base.run_package_validation.__kwdefaults__
    return runner(*args,**kwargs)
