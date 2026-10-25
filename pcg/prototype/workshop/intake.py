"""Versioned idea intake and failure-aware proposals beside existing feedback.

Human idea, video observation, manual report and production approval are never
interchangeable. Manual ratings/curation still use factory.core.feedback.
"""
import argparse,copy,json,re
from pathlib import Path
from .engine import ROOT,HERE
from .rules import FAMILIES
from .experiments import write
from ..factory.core.quality import digest
from ..factory.core.feedback import FLAGS

def ingest(record,root):
    if record.get('source_type')!='human_idea'or not isinstance(record.get('original_text'),str)or not record['original_text']:raise ValueError('human_idea_original_text_required')
    if not re.fullmatch(r'[A-Za-z0-9_-]{3,100}',record.get('id','')):raise ValueError('stable_idea_id_required')
    if type(record.get('source_revision'))is not int or record['source_revision']<1:raise ValueError('positive_idea_revision_required')
    value=copy.deepcopy(record);value['original_text_sha256']=digest(record['original_text']);value['human_approval']='UNKNOWN'
    path=Path(root)/record['id']/('v'+str(record['source_revision'])+'.json')
    if path.exists():
        if json.loads(path.read_text())!=value:raise ValueError('immutable_idea_revision')
        return path
    write(path,value);return path

def propose(request,observations):
    source=json.loads((HERE/'ideas.json').read_text());out=[];registered=FAMILIES
    if request.get('content_kind')=='macro':
        from .macro import FAMILY
        idea=json.loads((HERE/'macro-proposal-v1.json').read_text());idea['rule']='workshop/macro/'+FAMILY
        source=dict(sources=[],proposals=[idea]);registered=(FAMILY,)
    for idea in source['sources']+source['proposals']:
        family=idea['rule'].split('/')[-1]
        if request.get('family')and request['family']!=family:continue
        signals=[o for o in observations if o.get('family')==family]
        # An unresolved cheap route / boring observation changes selection. A
        # changed title or seed cannot clear it: explicit geometry revision and
        # new evidence must resolve the source observation.
        blocked=[s for s in signals if s.get('flag')in FLAGS and not s.get('resolved_by')]
        out.append(dict(id='proposal-'+digest(dict(idea=idea,request=request,signals=signals))[:20],source_id=idea['id'],novelty_family=family,
            status='revision_required'if blocked else'executable_rule_requires_physics'if family in registered else'missing_generation_rule',
            source_type=idea['source_type'],idea=idea,feedback=signals,selection_weight=0 if blocked else 1,
            missing_conditions=[s.get('next_revision','new geometry/rule and independent evidence')for s in blocked],human_video_observation='unreviewed',human_playtest='unreviewed',production_admitted=False))
    if request.get('family')not in registered and request.get('family'):
        return [dict(status='missing_generation_rule',requested=request['family'],missing_conditions=['No registered Cell/generator causal rule; do not substitute an existing room'],selection_weight=0)]
    return out

def run(out_name):
    out=ROOT/'results'/out_name
    if out.exists():raise ValueError('immutable_intake_experiment')
    out.mkdir(parents=True);sources=json.loads((HERE/'ideas.json').read_text());paths=[str(ingest(r,out/'idea-sources').relative_to(ROOT))for r in sources['sources']]
    observations=[dict(id='technical-fork-shortcut-v1',type='technical_experiment',family='one-shot-two-routes',flag='unexpected_shortcut',
        source_run='workshop-counters-v1',evidence='ordinary-jump-180-20 reached high reward without a shot',next_revision='raise receiver above ordinary jump and retest both interfaces',
        resolved_by=dict(rule_revision='rules.py raised high ports to 232/212',counter_run='workshop-counters-v2',holdout_run='workshop-five-holdout-v1'))]
    for p in sorted((ROOT/'feedback/workshop').glob('*.json')):
        value=json.loads(p.read_text())
        if value.get('type')=='technical_experiment'and value.get('family')in FAMILIES:observations.append(value)
    # Preserve the actual before/after prioritization using the same observations.
    unresolved=copy.deepcopy(observations)
    for row in unresolved:row.pop('resolved_by',None)
    write(out/'observations.json',observations);write(out/'proposals-before-repair.json',propose({},unresolved));write(out/'proposals-after-repair.json',propose({},observations))
    links=[]
    from pcg.map_directed.library import CandidateLibrary
    withdrawn=CandidateLibrary().withdrawn
    for run in ['workshop-a1-holdout-v1','workshop-five-holdout-v1','workshop-carrier-rework-v2/holdout','workshop-gate-window-v2']:
        root=ROOT/'results'/run;manifest=json.loads((root/'modules/manifest.json').read_text())
        for m in manifest['modules']:
            links.append(dict(family=m['family'],contentVersion=m['contentVersion'],document=str((root/'modules'/m['file']).relative_to(ROOT)),experiment=run,
                source_ids=[r['id']for r in sources['sources']+sources['proposals']if r['rule'].endswith('/'+m['family'])],technical_status='withdrawn_after_counterexample'if m['contentVersion']in withdrawn else'passed_scoped',
                video_observation='unreviewed',manual_playtest='unreviewed',production_admitted=False))
    write(out/'traceability.json',dict(schema='pcg/idea-to-content-lineage/v1',idea_revisions=paths,candidates=links,observations=observations,
        original_text_preserved=True,human_ideas_are_not_approval=True,online_model_service=False))
    return out
if __name__=='__main__':
    p=argparse.ArgumentParser();group=p.add_mutually_exclusive_group(required=True);group.add_argument('--name');group.add_argument('--idea',help='JSON with id/source_type=human_idea/source_revision/original_text; interpretation separate')
    p.add_argument('--store',default=str(ROOT/'feedback/workshop/idea-sources'));a=p.parse_args()
    print(ingest(json.loads(Path(a.idea).read_text()),Path(a.store))if a.idea else run(a.name))
