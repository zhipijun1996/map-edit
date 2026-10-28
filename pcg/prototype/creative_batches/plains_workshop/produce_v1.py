"""Recoil-only request entry for the two tested bounded adaptation recipes.

Uses the original production loop and store. Unsupported specifications retain
conflicts and gaps; no substitution, model impersonation, or Map generation.
"""
import argparse,json
from pathlib import Path
from .adapt_v1 import compiler,specification,DEMANDS,purpose,alternatives
from .catalog_v1 import capability_conflicts
from pcg.prototype.workshop.production_loop import run
from pcg.prototype.workshop.engine import ROOT
from pcg.prototype.factory.core.engine import file_sha

HERE=Path(__file__).parent

def requests_for(specs):
    if not isinstance(specs,list)or not 1<=len(specs)<=4:raise ValueError('one_to_four_explicit_specifications_required')
    if len({s['id']for s in specs})!=len(specs):raise ValueError('unique_demand_ids_required')
    return [dict(recipe=s['id'],demand=dict(id=s['id'],family=s.get('required_family'),parameters=s.get('objective',{}).get('parameters',{})),specification=s)for s in specs]

def compile_plains(request):
    profile=json.loads((HERE/'profile-v1.json').read_text());conflicts=capability_conflicts(request.get('specification',{}),profile)
    if conflicts:return dict(status='unsatisfied',gaps=['plains supports move/jump/shot_recoil only'],conflicts=conflicts,searched=dict(allowed_capabilities=profile['allowed_tested_capabilities']),negotiable=['recoil-only demand or explicit later-region task'],cases=[])
    return compiler(request)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--name');p.add_argument('--specifications',type=Path);p.add_argument('--examples',action='store_true');a=p.parse_args()
    if a.examples:print(json.dumps([specification(d)for d in DEMANDS],ensure_ascii=False,indent=2));return
    if not a.name or not a.specifications:p.error('--name and --specifications required')
    specs=json.loads(a.specifications.read_text());requests=requests_for(specs);preflight=[]
    for request in requests:
        response=compile_plains(request);preflight.append(dict(request=request,**{k:v for k,v in response.items()if k!='cases'},candidate_ids=[c['id']for c in response.get('cases',[])]))
    intake=ROOT/'results'/(a.name+'-intake');intake.mkdir()
    (intake/'responses.json').write_text(json.dumps(dict(schema='pcg/plains-generation-intake/v1',responses=preflight,source_file_sha256=file_sha(HERE/'adapt_v1.py'),new_action_families=0),ensure_ascii=False,indent=2)+'\n')
    run(a.name,requests=requests,cycles=len(requests),source_file=HERE/'adapt_v1.py',extra_sources=[Path(__file__),HERE/'adapt-protocol-v1.json',HERE/'profile-v1.json',HERE/'catalog_v1.py'],compiler=compile_plains,checker=purpose,counter_builder=alternatives)
if __name__=='__main__':main()
