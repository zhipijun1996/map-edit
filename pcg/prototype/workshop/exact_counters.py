"""Counterexamples at the exact published enemy initial states, no selection."""
import argparse,copy,json
from .engine import ROOT
from .experiments import counter_run

def run(name):
    source=ROOT/'results/workshop-five-holdout-v1/review_cases.json';raw=json.loads(source.read_text())['cases'];cases=[]
    for c in raw:
        if c['family']!='air-refund':continue
        c=copy.deepcopy(c)
        for key in ['module_sha256','factory_id','factory_evidence','recorded_frames','validation_summary','review_alias']:c.pop(key,None)
        c['id']=c['id'].removesuffix('-clean-0');cases.append(c)
    return counter_run(name,['air-refund'],([c['map_specification']for c in cases],cases))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();print(run(a.name))
