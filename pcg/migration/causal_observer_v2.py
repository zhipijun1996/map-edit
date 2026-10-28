"""Narrow observer corrections for actual gate episodes in new candidates.

Original causal checkers and every unrelated assertion remain authoritative.
No trace filtering, action-count payment, geometry change, resource grant or
physics replacement is performed. Old frozen observer/runtime files stay intact.
"""
from __future__ import annotations
import copy
import inspect
from pathlib import Path
from . import core,causal_observer
from pcg.prototype.factory.core.quality import digest

METHOD='pcg/actual-causal-episode-observer/v2'
MACRO_SOURCE='pcg/prototype/workshop/macro.py'
TRAPDOOR_SOURCE='pcg/prototype/creative_batches/resource_routes/recipes-v7.py'


def _trapdoor_episode(case,raw):
    frames=raw.get('frames',[])
    for latch,hit,episode in causal_observer._bell_episodes(case,raw):
        if episode['airborne']or episode['previous'].get('grounded')is not True:continue
        gx,gy,gw,gh=latch['gate'];origin=episode['origin'];previous=episode['previous']
        if gh>32 or gw<48:continue
        x,y=origin['origin']
        if x-12<gx or x+12>gx+gw or abs(y+18-gy)>1:continue
        support=previous.get('support_id')
        if not support:continue
        # A coincident ordinary bank would make 'own removable support'
        # ambiguous. The original collider must be the grounded bridge.
        if any(abs(r[1]-gy)<1 and r[0]-12<x<r[0]+r[2]+12 for r in case.get('platforms',[])):continue
        prior=next((b for b in previous.get('plains',{}).get('bells',[])if b.get('id')==latch['id']),None)
        if not prior or prior.get('open')is not False:continue
        opened=[f for f in frames if f['frame']>=hit['frame']and any(b.get('id')==latch['id']and b.get('open')is True
            and b.get('open_count')==hit.get('count')for b in f.get('plains',{}).get('bells',[]))]
        if not opened:continue
        lost=next((f for f in opened if f.get('grounded')is False and f.get('support_id')!=support and f['y']>y),None)
        if lost is None:continue
        below=next((f for f in opened if f['frame']>=lost['frame']and f['y']-18>=gy+gh
                    and f['x']-12>=gx and f['x']+12<=gx+gw),None)
        if below is None:continue
        through=[f for f in frames if hit['frame']<=f['frame']<=below['frame']and f['y']+18>gy and f['y']-18<gy+gh
                 and f['x']+12>gx and f['x']-12<gx+gw]
        if not through or any(not any(b.get('id')==latch['id']and b.get('open')is True and b.get('open_count')==hit.get('count')
                for b in f.get('plains',{}).get('bells',[]))for f in through):continue
        return dict(method=METHOD,kind='grounded_shot_removes_own_actual_gate_support',bellId=latch['id'],
            shotId=origin['shot_id'],shotFrame=origin['frame'],impactFrame=episode['impact']['frame'],hitFrame=hit['frame'],
            gate=latch['gate'],bodySize=[24,36],standingOnClosedGate=True,originalSupportId=support,
            preShotBodyFeet=y+18,actualSupportLostFrame=lost['frame'],wholeBodyBelowGateFrame=below['frame'],
            bodyGateOverlapFrames=[f['frame']for f in through],actualGateOpenDuringEveryBodyOverlap=True,
            rawTraceFiltered=False)
    return None


def correct(case,raw,check,*,assertion_source):
    reason=None;proof=None;family=case.get('family');route=case.get('route_spec',{}).get('id')
    if assertion_source==MACRO_SOURCE and family=='gate-brake-return'and route in('gate','outbound','cache','loop'):
        reason='airborne_same_shot_gate_missing'
        if reason in check.get('reasons',[]):proof=causal_observer._timed_crossing(case,raw)
    elif assertion_source==TRAPDOOR_SOURCE and family=='trapdoor-commit':
        reason='self_support_removal_missing'
        if reason in check.get('reasons',[]):proof=_trapdoor_episode(case,raw)
    if proof is None:return check
    value=copy.deepcopy(check);proof=copy.deepcopy(proof)
    proof.update(method=METHOD,assertionSource=assertion_source,assertionSourceSha256=core.sha(core.REPO/assertion_source),
                 originalRouteId=route,extraActionsDoNotConferPermission=True)
    value['reasons']=[r for r in value['reasons']if r!=reason]
    value.setdefault('causal',{}).setdefault('observerCorrections',[]).append(dict(originalReason=reason,proof=proof))
    value['ok']=not value['reasons'];return value


def _assertion_source(author):
    source=inspect.getsourcefile(author.purpose)
    if source is None:raise ValueError('causal_assertion_source_unavailable')
    return core.relative(source)


def bind(document,input_cases):
    """New version/source binding, preserving exact original runtime per case."""
    from .physics import author_for,runner_for
    doc,cases=copy.deepcopy(document),copy.deepcopy(input_cases);records=[]
    directory=Path(__file__).parent/'episode_observers'
    for case in cases:
        if case.get('family')not in('gate-brake-return','trapdoor-commit'):continue
        author=author_for(case);registration=core.relative(author.__file__);assertion=_assertion_source(author)
        expected=MACRO_SOURCE if case['family']=='gate-brake-return'else TRAPDOOR_SOURCE
        if assertion!=expected:raise ValueError('unsupported_specific_episode_assertion_source:'+assertion)
        runner=core.relative(runner_for(case,author))
        token=digest(dict(author=registration,runner=runner,observer=core.sha(__file__),assertion=assertion))[:20]
        wrapper=directory/('binding_'+token+'.py')
        source=('from pathlib import Path\nfrom importlib import import_module\n'
            +'from pcg.migration.causal_observer_v2 import correct\n'
            +'_original=import_module('+repr(registration.removesuffix('.py').replace('/','.'))+')\n'
            +'RUNNER_SCRIPT=Path(__file__).resolve().parents[3]/'+repr(runner)+'\n'
            +'SOURCE_DEPENDENCIES=[Path(_original.__file__),*getattr(_original,"SOURCE_DEPENDENCIES",[]),Path(__file__).parents[1]/"causal_observer_v2.py"]\n'
            +'def purpose(case,raw):\n'
            +'    return correct(case,raw,_original.purpose(case,raw),assertion_source='+repr(assertion)+')\n')
        directory.mkdir(parents=True,exist_ok=True)
        if wrapper.exists()and wrapper.read_text()!=source:raise ValueError('immutable_episode_observer_binding_changed')
        if not wrapper.exists():wrapper.write_text(source)
        case.setdefault('generation_rule',{})['registration_source']=core.relative(wrapper)
        binding=dict(schema='pcg/specific-causal-observer-binding/v2',caseId=case['id'],originalRegistration=registration,
            originalAssertionSource=assertion,originalAssertionSha256=core.sha(core.REPO/assertion),
            observerSource=core.relative(__file__),observerSha256=core.sha(__file__),wrapperSource=core.relative(wrapper),
            runtimeSourceUnchanged=runner,rawFiltering=False,genericExtraActionPermission=False,
            semanticChange='Bind actual projectile/gate/body episode; preserve every original challenge and outcome assertion.')
        case['migration_episode_observer_v2']=binding;records.append(binding)
    if records:doc['generationContract']['generation']['migration']['specificEpisodeObservers']=records
    return doc,cases,records
