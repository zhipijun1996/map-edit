from pcg.migration import core,godot_package
from .continue_revision053_v1 import rows,label

def main():
    row=next(r for r in rows()if label(r)=='three');f=core.REPO/row['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-control-v3-cases.json',dict(cases=cs))
    for c in cs:
        c['id']=c['id'].replace('r053-v2','r053-v3');c['generation_rule']['registration_source']='pcg/manual_review/revision053_three_author_v3.py'
        if c['route_spec']['to_port']!='B':continue
        p=c['control_plan'];i=next(i for i,v in enumerate(p)if v.get('chain_window',{}).get('id')=='enemy-3');p[i]['trigger']['state']='chain_third';p[i-1]['third_target']=True
        p.insert(i+2,dict(op='shoot',direction=[0,1],height_threshold=160,final_x=320,trigger=dict(after=4,state='top_finish',timeout=300)))
    core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs));core.contract(f/'module.mapnote.json',refresh=True)
if __name__=='__main__':main()
