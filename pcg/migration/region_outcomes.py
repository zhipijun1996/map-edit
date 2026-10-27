"""Actual original region chest OR transactions for migration world outcomes.

No choices required means historical behavior is unchanged. Balances are the
native Wallet/Meta balances logged by the frozen original consumer; an accepted
interact records the pre-choice balances even when both events occur at frame0.
"""
from __future__ import annotations
import math

SERVICE='DemoApp._region_interact/_claim_region_chest'


def _balances(value):
    values=[value.get('coins'),value.get('notes')]
    if any(type(n)not in(int,float)or not math.isfinite(n)or n<0 for n in values):return None
    return tuple(values)


def _snapshot(raw):
    return raw.get('original_region_chests',raw.get('package',{}).get('original_region_chests',{}))


def evaluate(case,raw):
    required=case.get('required_region_chest_choices',[])
    if not required:return dict(ok=True,required=[],transactions=[],scope='No new region chest requirement; legacy outcome unchanged.')
    reasons=[];proofs=[];state=_snapshot(raw)
    if state.get('bound')is not True or state.get('consumer')!=SERVICE or state.get('interaction_radius')!=80 or state.get('choice')!='OR' or state.get('resources_reset')is not False or state.get('modal_open')is not False:
        return dict(ok=False,reasons=['actual_original_region_consumer_or_finished_modal_missing'],required=required,transactions=[])
    events=state.get('events',[]);final=_balances(state)
    if final is None or not events or _balances(events[-1])!=final:
        reasons.append('actual_final_native_balances_missing_or_inconsistent')
    # Event array order is authoritative within a physics frame; frame0 may
    # contain both interact and choose, so a first frame is not a pre-balance.
    if any(type(e.get('frame'))not in(int,float)or not math.isfinite(e['frame'])for e in events)or any(a['frame']>b['frame']for a,b in zip(events,events[1:])):
        reasons.append('native_region_event_order_invalid')
    if len({w.get('id')for w in required})!=len(required):reasons.append('multiple_required_OR_choices_for_one_chest')
    for wanted in required:
        identifier,kind=wanted.get('id'),wanted.get('kind')
        definitions=[c for c in case.get('original_region_chests',[])if c.get('id')==identifier]
        observed=[c for c in state.get('chests',[])if c.get('id')==identifier]
        if len(definitions)!=1 or len(observed)!=1 or kind not in('coin','note'):
            reasons.append('required_original_region_chest_or_kind_missing');continue
        definition,chest=definitions[0],observed[0]
        resources=definition.get('resources',[])
        amounts=[r.get('amount')for r in resources if r.get('kind')==kind]
        if len(amounts)!=1 or type(amounts[0])not in(int,float)or not math.isfinite(amounts[0])or amounts[0]<=0:
            reasons.append('required_original_region_amount_invalid');continue
        amount=amounts[0]
        if chest.get('claimed')is not True or chest.get('resources')!=resources:
            reasons.append('required_region_chest_not_claimed_with_exact_source_resources');continue
        choices=[(i,e)for i,e in enumerate(events)if e.get('type')=='native_region_choose'and e.get('id')==identifier and e.get('accepted')is True]
        if len(choices)!=1 or choices[0][1].get('kind')!=kind:
            reasons.append('required_same_chest_same_kind_native_choice_missing');continue
        index,event=choices[0]
        openings=[i for i,e in enumerate(events[:index])if e.get('type')=='native_region_interact'and e.get('id')==identifier and e.get('accepted')is True and e.get('modal_open')is True]
        if not openings:
            reasons.append('actual_native_pre_choice_interaction_missing');continue
        start=openings[-1];opening=events[start]
        intervening=events[start+1:index]
        before,after=_balances(opening),_balances(event)
        if before is None or after is None or any(e.get('accepted')is True or _balances(e)!=before for e in intervening):
            reasons.append('native_pre_choice_balance_or_transaction_ambiguous');continue
        expected=(amount,0)if kind=='coin'else(0,amount)
        if tuple(b-a for a,b in zip(before,after))!=expected:
            reasons.append('native_OR_wallet_meta_delta_not_exact');continue
        instance=chest.get('instance_id')
        if not isinstance(instance,str)or not instance or event.get('selected')!=instance+'/resource/'+kind or event.get('modal_open')is not False:
            reasons.append('actual_native_choice_offer_or_modal_not_matched');continue
        # At least one actual recorded final/frame balance must carry the
        # granted amount. Events alone cannot manufacture the outcome.
        if final is None or any(f<a for f,a in zip(final,after)):
            reasons.append('native_event_without_actual_wallet_meta_resources');continue
        proofs.append(dict(id=identifier,kind=kind,amount=amount,interactionEventIndex=start,choiceEventIndex=index,
            interactionFrame=opening['frame'],choiceFrame=event['frame'],beforeWalletMeta=list(before),
            afterWalletMeta=list(after),deltaWalletMeta=list(expected),selected=event['selected'],
            balancesConsumer='Original RunWallet.balance and MetaProgression.snapshot().notes',
            prebalanceSource='Accepted native_region_interact event, before native choice; not inferred from frame0.'))
    return dict(ok=not reasons,reasons=sorted(set(reasons)),required=required,transactions=proofs,
        scope='Exact required same-chest/same-kind OR outcome; another valid resource choice is a different outcome.')


def satisfied(case,raw):return evaluate(case,raw)['ok']
