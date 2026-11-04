"""Correct third receiver to original any-side API. Preserve original formal version."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core,godot_package,physics
from .continue_revision058_v1 import rows,label,AUTH

def main():
 r=next(r for r in rows()if label(r)=='s11');f=core.REPO/r['outputDirectory'];d=core.read(f/'module.mapnote.json');cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-third-receiver-v2.json',dict(module=d,cases=cs))
 next(o for o in d['objects']if o['id']=='bottom-access')['mechanics']['returnSideOnly']=False
 for c in cs:c['generation_rule']['registration_source']='pcg/manual_review/revision058_author_v12.py';c['id']+='-receiver-v2'
 core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(d,cs));core.contract(f/'module.mapnote.json',refresh=True)
 core.write(AUTH/'s11-receiver-binding-correction.json',dict(reason='Native 3-receiver fixture exposed bottom access rejected by wrong right-side predicate. Use original add_access_bell(...,false,false) for bottom, keep right access right-side-only.',geometryChanged=False,formalVersionUsed=1,noSecondFormal=True,oldFinal='pcg/manual_review/implementation/revision-058-final-v1/'+r['moduleId'],newFinal='pcg/manual_review/implementation/revision-058-receiver-v2/'+r['moduleId'],evidence=physics.artifact(core.REPO/'pcg/results/approved-r058-s11-three-access-v1/access-checks.json')))
if __name__=='__main__':main()
