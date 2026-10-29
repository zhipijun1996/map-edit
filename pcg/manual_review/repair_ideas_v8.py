"""Use actual native velocity at the capped orbit's observed turning point."""
from pcg.migration import core,godot_package
from .new_ideas_v1 import rows,label

def main():
 r=next(r for r in rows()if label(r)=='enemies-3');f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-repair-v8-cases.json',dict(cases=cs))
 for c in cs:c['id']=c['id'].replace('newideas-v10','newideas-v11');c['generation_rule']['registration_source']='pcg/manual_review/ideas_author_v7.py'
 d=godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs);core.write(f/'module.mapnote.json',d);core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs))
if __name__=='__main__':main()
