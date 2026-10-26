"""Second source revision: explicit negotiated refuge request, not held tuning."""
import copy,json
from pathlib import Path
from pcg.prototype.creative_batches.plains50_machinery import recipes_v1 as old
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.rules import settle
HERE=Path(__file__).parent
RECIPE='evacuate-rejoin'

def candidate():
    c=old.source(RECIPE,1)
    c['platforms'][1]=[630,245,180,60]
    old.move_receiver(c,2,1350,438,240,1465)
    c['id']='plains50-machinery-evacuate-rejoin-wide-refuge-v2'
    c['production_recipe']=RECIPE;c['parent_family']=RECIPE;c['capabilities']=['move','jump','shot_recoil'];c['trace_all']=False
    c['rule_parameters']=dict(relationship=RECIPE,interface='wide-refuge-negotiated',refuge=[630,245,180,60],receiver=[1350,438,240,100],
        prior_unsatisfied_request='v1 wide lower refuge y250 had moderate7/12 calibration; no holdout run',
        negotiated='Map may accept wider island at y245 instead of requested lower island y250; farther receiver frontage retained',
        old_relationship_not_new_family=True)
    c['generation_rule']=dict(id='plains50/machinery/'+RECIPE,version=2,source_type='actual_current_codex_subagent',author_task='/root/plains50_machinery',parameters=c['rule_parameters'])
    c['rule_source_path']=str(Path(__file__).relative_to(ROOT.parent));c['layout_title']='在宽避险岛重接同台 / 协商接口'
    return c

def specification():
    s=old.specification(RECIPE,1);c=candidate()
    s.update(id='plains50/machinery/evacuate-rejoin/wide-refuge-negotiated/v2',objective=copy.deepcopy(c['rule_parameters']),rise=0)
    return s

def compiler(request):
    c=candidate();s=specification();c['map_specification']=s;c['idea_ids']=['plains50-machinery/evacuate-rejoin']
    return dict(status='requires_physics',specifications=[s],cases=[c])

def extra_sources():return old.extra_sources()+[HERE/'recipes_v1.py',HERE/'protocol-v2.json']

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--probe',action='store_true');p.add_argument('--name',required=True);a=p.parse_args()
    if a.probe:
        e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__)]+extra_sources(),runner_script=old.OLD/'dock_runner_v11.gd');rows=[]
        for c,r,ev in e.run([candidate()],'wide-refuge-repair-probe'):
            q=old.purpose(c,r);row=dict(id=c['id'],ok=q['ok'],purpose=q,reason=r.get('reason'),evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
        (e.out/'summary.json').write_text(json.dumps(rows,indent=2))
    else:
        from pcg.prototype.workshop.production_loop import run
        run(a.name,requests=[dict(recipe=RECIPE)],cycles=1,library_root=ROOT/'map_directed/library',compiler=compiler,checker=old.purpose,counter_builder=old.alternatives,source_file=Path(__file__),extra_sources=extra_sources(),runner_script=old.OLD/'dock_runner_v11.gd',export_script=old.OLD/'dock_export_v13.mjs')
