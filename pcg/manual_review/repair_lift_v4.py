from pcg.migration import core,godot_package
from .lift_idea_v1 import rows

def main():
    f=core.REPO/rows()[0]['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-v5-cases.json',dict(cases=cs))
    for c in cs:
        c['id']=c['id'].replace('newlift-v4','newlift-v5');c['generation_rule']['registration_source']='pcg/manual_review/lift_author_v4.py'
        if c['route_spec']['id']=='A-to-B':
            for p in c['control_plan']:
                if p['op']=='settle' and p.get('target_x')==104:p['selected_upper']=True
                if p.get('lift_window',{}).get('id')=='L2':p['lift_window']['id']='selected_upper'
    core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs));core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs))
if __name__=='__main__':main()
