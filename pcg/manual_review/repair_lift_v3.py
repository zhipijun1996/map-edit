from pcg.migration import core,godot_package
from .lift_idea_v1 import rows

def main():
    f=core.REPO/rows()[0]['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-v4-cases.json',dict(cases=cs))
    for c in cs:
        c['id']=c['id'].replace('newlift-v3','newlift-v4');c['generation_rule']['registration_source']='pcg/manual_review/lift_author_v3.py'
    core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs));core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs))
if __name__=='__main__':main()
