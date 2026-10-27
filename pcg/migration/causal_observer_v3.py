"""Narrow actual-support attribution for the original recipes-v5 trapdoor.

Reuse the frozen v2 physical predicate; never edit original trials or excuse
extra inputs. Every unrelated purpose assertion remains in force.
"""
import copy
from . import core, causal_observer_v2

SOURCE='pcg/prototype/creative_batches/resource_routes/recipes-v5.py'


def correct(case, raw, check, *, assertion_source):
    reason='self_support_removal_missing'
    if assertion_source!=SOURCE or case.get('family')!='trapdoor-commit' or reason not in check.get('reasons',[]):
        return check
    proof=causal_observer_v2._trapdoor_episode(case,raw)
    if proof is None:return check
    value=copy.deepcopy(check);proof=copy.deepcopy(proof)
    proof.update(method='pcg/actual-causal-episode-observer/v3',assertionSource=SOURCE,
        assertionSourceSha256=core.sha(core.REPO/SOURCE),
        originalRouteId=case.get('route_spec',{}).get('id'),extraActionsDoNotConferPermission=True)
    value['reasons']=[r for r in value['reasons']if r!=reason]
    value.setdefault('causal',{}).setdefault('observerCorrections',[]).append(dict(originalReason=reason,proof=proof))
    value['ok']=not value['reasons']
    return value
