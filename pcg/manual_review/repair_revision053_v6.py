"""Keep the native12px hook sweep clear of the pillar, then recontact the real ring."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core,godot_package
from .continue_revision053_v1 import rows,label
from .prepare_review045_v1 import end

def main():
    r=next(r for r in rows()if label(r)=='50');f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-control-v4-cases.json',dict(cases=cs))
    for c in cs:
        if c['route_spec']['from_port']!='C':continue
        p=c['control_plan'];i=next(i for i,v in enumerate(p)if v.get('hook_count')==3);p=p[:i+1]
        for v in p:
            if v['op']=='shoot':v['direction']=[.1,.9949874371]
        c['control_plan']=p+end(*c['exit_port']);c['expected_hook_sequence']=['lower_window_ring','upper_window_ring','upper_window_ring'];c['route_spec']['via_ports']=[];c['id']=c['id'].replace('r053-v3','r053-v4')
    core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs));core.contract(f/'module.mapnote.json',refresh=True)
if __name__=='__main__':main()
