from pcg.migration import core,godot_package
from .lift_idea_v1 import rows,wait_lift
from .prepare_ideas_v1 import settle

def main():
    f=core.REPO/rows()[0]['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-v8-cases.json',dict(cases=cs))
    for c in cs:
        c['id']=c['id'].replace('newlift-v7','newlift-v8');c['generation_rule']['registration_source']='pcg/manual_review/lift_author_v6.py'
        if c['route_spec']['id']=='A-to-B':c['control_plan'][8:8]=[settle(132),wait_lift('lift_edge','L1')]
    core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs));core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs))
if __name__=='__main__':main()
