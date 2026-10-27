"""Real frozen v5 native receipts plus adversarial outcome mutations."""
import copy
import unittest
from pcg.migration import core,region_outcomes as outcomes


class RegionOutcomeTests(unittest.TestCase):
    def actual(self,profile='1j2s'):
        run=core.REPO/'pcg/results'/('foundation-migration-native-package-v5-release-'+profile)
        return core.read(run/'cases.json')['cases'][0],core.read(run/'package/load-evidence/case-0/receipt.json')

    def test_legacy_case_without_requirement_does_not_change(self):
        self.assertTrue(outcomes.satisfied({},{}))
        self.assertTrue(outcomes.satisfied({'required_region_chest_choices':[]},{'original_region_chests':{'bad':'ignored'}}))

    def test_actual_coin_and_note_receipts_have_exact_native_OR_delta(self):
        for profile,expected in [('1j2s',[6,0]),('2j2s',[0,2])]:
            with self.subTest(profile=profile):
                case,raw=self.actual(profile);result=outcomes.evaluate(case,raw)
                self.assertTrue(result['ok'],result)
                self.assertEqual(result['transactions'][0]['deltaWalletMeta'],expected)
                self.assertEqual(result['transactions'][0]['interactionFrame'],0)
                self.assertEqual(result['transactions'][0]['choiceFrame'],0)
                self.assertEqual(raw['frames'][0]['package']['original_region_chests']['coins'],raw['package']['original_region_chests']['coins'])

    def test_real_services_receipt_retains_existing_wallet_on_note_choice(self):
        raw=core.read(core.REPO/'pcg/results/foundation-migration-native-services-v5-final-1j2s/receipt.json')
        row=next(r for r in raw['results']if r['kind']=='original_region_note_choice')
        snapshot=row['result'];case=dict(original_region_chests=snapshot['chests'],required_region_chest_choices=[dict(id='cache',kind='note')])
        result=outcomes.evaluate(case,{'original_region_chests':snapshot})
        self.assertTrue(result['ok'],result)
        self.assertEqual(result['transactions'][0]['beforeWalletMeta'],[6,0])
        self.assertEqual(result['transactions'][0]['afterWalletMeta'],[6,2])

    def test_missing_claim_wrong_id_kind_and_amount_are_not_same_outcome(self):
        for mutation in ('missing','wrong_id','wrong_kind','wrong_amount','only_claimed','event_without_balance','wrong_offer','OR_both_grants'):
            with self.subTest(mutation=mutation):
                case,raw=self.actual();state=raw['package']['original_region_chests']
                if mutation=='missing':state['chests'][0]['claimed']=False
                if mutation=='wrong_id':state['chests'][0]['id']='other'
                if mutation=='wrong_kind':state['events'][-1]['kind']='note'
                if mutation=='wrong_amount':state['events'][-1]['coins']=5;state['coins']=5
                if mutation=='only_claimed':state['events']=[]
                if mutation=='event_without_balance':state['coins']=0
                if mutation=='wrong_offer':state['events'][-1]['selected']='other/resource/coin'
                if mutation=='OR_both_grants':state['events'][-1]['notes']=2;state['notes']=2
                self.assertFalse(outcomes.satisfied(case,raw))

    def test_another_valid_OR_kind_is_a_different_required_outcome(self):
        case,_=self.actual('1j2s');_,note=self.actual('2j2s')
        self.assertFalse(outcomes.satisfied(case,note))

    def test_actual_open_invalid_repeated_and_shared_reload_states(self):
        receipt=core.read(core.REPO/'pcg/results/foundation-migration-native-services-v5-final-1j2s/receipt.json')
        choice=next(r for r in receipt['results']if r['kind']=='original_region_coin_choice')
        spec=choice['chosen']['chests'];case=dict(original_region_chests=spec,required_region_chest_choices=[dict(id='cache',kind='coin')])
        for key,expected in [('open',False),('invalid',False),('chosen',True),('repeated',True)]:
            with self.subTest(key=key):
                self.assertEqual(outcomes.satisfied(case,{'original_region_chests':choice[key]}),expected)
        reload=next(r for r in receipt['results']if r['kind']=='shared_state_reload_does_not_farm')['result']
        self.assertFalse(outcomes.satisfied(case,{'original_region_chests':reload}))

    def test_forged_prebalance_unaccepted_event_wrong_source_and_unfinished_modal(self):
        for mutation in ('prebalance','unaccepted','consumer','reset','modal','source_resources','no_interact'):
            with self.subTest(mutation=mutation):
                case,raw=self.actual();state=raw['package']['original_region_chests']
                if mutation=='prebalance':state['events'][0]['coins']=6
                if mutation=='unaccepted':state['events'][-1]['accepted']=False
                if mutation=='consumer':state['consumer']='proxy'
                if mutation=='reset':state['resources_reset']=True
                if mutation=='modal':state['modal_open']=True
                if mutation=='source_resources':state['chests'][0]['resources'][0]['amount']=7
                if mutation=='no_interact':state['events'].pop(0)
                self.assertFalse(outcomes.satisfied(case,raw))


if __name__=='__main__':unittest.main()
