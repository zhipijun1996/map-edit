if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core,godot_package
from .lift_idea_v1 import rows
from .prepare_ideas_v1 import settle
from .prepare_review045_v1 import axis

def main():
    f=core.REPO/rows()[0]['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-v9-cases.json',dict(cases=cs))
    for c in cs:
        c['id']=c['id'].replace('newlift-v8','newlift-v9');c['generation_rule']['registration_source']='pcg/manual_review/lift_author_v7.py'
        if c['route_spec']['id']=='A-to-B':c['control_plan'][2]=axis(0);c['control_plan'][6:6]=[settle(66)]
    core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs));core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs))
if __name__=='__main__':main()
