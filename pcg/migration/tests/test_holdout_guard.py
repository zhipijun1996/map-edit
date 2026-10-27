"""Experiment bookkeeping adversaries; fixture reports certify no gameplay."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from pcg.migration import core,physics,holdout_guard as guard


class HoldoutGuardTests(unittest.TestCase):
    def setUp(self):
        protocols=[core.read(physics.PROTOCOL),core.read(physics.FULL_PROTOCOL)]
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.addCleanup(patch.stopall)
        patch.object(core,'REPO',self.root).start()
        patch.object(guard,'LOCKS',self.root/'state/locks.json').start()
        patch.object(guard,'POOLS',self.root/'state/pools').start()
        legacy=self.root/'state/protocol.json';full=self.root/'state/protocol-full-v2.json'
        core.write(legacy,protocols[0]);core.write(full,protocols[1])
        patch.object(physics,'PROTOCOL',legacy).start();patch.object(physics,'FULL_PROTOCOL',full).start()
        self.seed=core.read(physics.FULL_PROTOCOL)['holdoutSeed']

    def candidate(self,name='first',source='a'*64,version='b'*64,width=256):
        folder=self.root/'.cache'/name;folder.mkdir(parents=True)
        core.write(folder/'migration.json',{'sourceVersion':'sha256:'+source,'sourcePath':'original/'+source})
        core.write(folder/'module.mapnote.json',{'generationContract':{'contentVersion':'sha256:'+version}})
        core.write(folder/'cases.json',{'cases':[{'id':name,'platforms':[[0,64,width,32]],'spawn':[20,46],
            'goal':[200,40,20,10],'capabilities':['move','jump','shot_recoil'],
            'control_plan':[{'op':'settle','trigger':{'after':0},'target_x':210,'deadband':3}]}]})
        core.write(folder/'adaptation.json',{})
        return folder

    def report(self,folder,name='evidence',with_holdout=True,passed=False):
        run=self.root/'pcg/results'/name;run.mkdir(parents=True)
        doc=core.read(folder/'module.mapnote.json')
        core.write(run/'input-binding.json',{'module':{'path':core.relative(folder/'module.mapnote.json'),'sha256':core.sha(folder/'module.mapnote.json')},
            'cases':{'path':core.relative(folder/'cases.json'),'sha256':core.sha(folder/'cases.json')}})
        core.write(run/'protocol.json',core.read(physics.FULL_PROTOCOL))
        core.write(run/'holdout.json',{'quality_gate':{'status':'awaiting_human_review'if passed else'rework'}})
        holdout={'path':core.relative(run/'holdout.json'),'sha256':core.sha(run/'holdout.json')}if with_holdout else'NOT_RUN'
        core.write(run/'migration-physics.json',{'schema':'pcg/foundation-migration-physics/v1','contentVersion':doc['generationContract']['contentVersion'],
            'passed':passed,'routes':[{'routeId':'main','passed':passed,'holdout':holdout}],
            'protocol':{'path':core.relative(run/'protocol.json'),'sha256':core.sha(run/'protocol.json')}})
        return run/'migration-physics.json'

    def test_same_original_is_locked_after_template_and_route_renaming(self):
        old=self.candidate();self.report(old)
        new=self.candidate('renamed',version='c'*64)
        cases=core.read(new/'cases.json');cases['cases'][0]['route_spec']={'id':'renamed-route'};core.write(new/'cases.json',cases)
        with self.assertRaises(guard.HoldoutConflict)as error:guard.check(new)
        self.assertEqual(error.exception.details['phase'],'holdout_guard')
        self.assertEqual(error.exception.details['previousEvidence'][0]['routeId'],'main')

    def test_calibration_only_failure_keeps_original_pool_unobserved(self):
        candidate=self.candidate();self.report(candidate,with_holdout=False)
        self.assertTrue(guard.check(candidate)['mayStartNewPhysics'])
        self.assertEqual(guard.refresh()['counts']['observedRoutes'],0)

    def test_unchanged_full_report_reanalysis_and_packaging_remain_allowed(self):
        candidate=self.candidate();report=self.report(candidate)
        result=guard.check(candidate,existing_report=report)
        self.assertTrue(result['allowed']);self.assertFalse(result['mayStartNewPhysics'])
        self.assertEqual(result['status'],'read_only_evidence_reuse')

    def test_existing_report_does_not_authorize_another_content_version(self):
        candidate=self.candidate();report=self.report(candidate)
        other=self.candidate('new',version='c'*64,width=300)
        with self.assertRaises(guard.HoldoutConflict):guard.check(other,existing_report=report)

    def test_changing_seed_without_independent_registration_is_blocked(self):
        candidate=self.candidate();self.report(candidate)
        new=self.candidate('new',version='c'*64,width=300)
        protocol=core.read(physics.FULL_PROTOCOL);protocol['holdoutSeed']+=123
        core.write(self.root/'renamed-protocol.json',protocol)
        with self.assertRaises(guard.HoldoutConflict)as error:guard.check(new,protocol_path=self.root/'renamed-protocol.json')
        self.assertIn('new_seed_is_not_an_independently_preregistered_pool_for_this_frozen_candidate',error.exception.details['conflicts'])

    def test_observer_or_title_only_change_cannot_buy_a_new_random_seed(self):
        candidate=self.candidate();self.report(candidate)
        new=self.candidate('metadata-only',version='c'*64)
        with self.assertRaisesRegex(ValueError,'observer_only_change'):guard.register_pool(new,'pool1')

    def test_pool_is_allocated_once_after_real_candidate_freeze(self):
        candidate=self.candidate();self.report(candidate)
        new=self.candidate('changed',version='c'*64,width=300)
        with patch.object(guard.secrets,'randbelow',return_value=123456)as entropy:
            first=guard.register_pool(new,'pool1');second=guard.register_pool(new,'another-name')
        self.assertEqual(entropy.call_count,1);self.assertFalse(first['requiresRuntimeProtocolIntegration'])
        self.assertEqual(second['status'],'already_registered_no_reroll')
        protocol=self.root/first['registration']['protocol']['path']
        self.assertEqual(guard.check(new,protocol_path=protocol)['status'],'independent_registered_pool')
        self.assertEqual(guard.check(new)['status'],'independent_registered_pool')
        self.assertIn('allocationNonce',core.read(self.root/first['registration']['declaration']['path']))

    def test_registered_conditions_do_not_follow_later_program_changes(self):
        candidate=self.candidate();self.report(candidate)
        new=self.candidate('changed',version='c'*64,width=300)
        result=guard.register_pool(new,'pool1');protocol=self.root/result['registration']['protocol']['path']
        value=core.read(new/'cases.json');value['cases'][0]['control_plan'][0]['target_x']=250;core.write(new/'cases.json',value)
        with self.assertRaises(guard.HoldoutConflict):guard.check(new,protocol_path=protocol)

    def test_original_source_path_alias_is_not_a_new_source(self):
        candidate=self.candidate();self.report(candidate)
        new=self.candidate('alias',version='c'*64,width=300)
        metadata=core.read(new/'migration.json');metadata['sourcePath']='another-copy';core.write(new/'migration.json',metadata)
        with self.assertRaises(guard.HoldoutConflict):guard.check(new)

    def test_completed_historical_report_cannot_be_silently_rewritten(self):
        candidate=self.candidate();report=self.report(candidate);guard.refresh()
        value=core.read(report);value['passed']=True;core.write(report,value)
        with self.assertRaisesRegex(ValueError,'historical_holdout_report_changed'):guard.refresh()

if __name__=='__main__':unittest.main()


class QualificationEntryPointGuardTests(unittest.TestCase):
    setUp=HoldoutGuardTests.setUp
    candidate=HoldoutGuardTests.candidate

    def test_qualifier_stops_before_starting_physics_when_pool_is_locked(self):
        import contextlib
        import shutil
        from pcg.migration import qualify
        candidate=self.candidate('one')
        prepared=self.root/'prepared';prepared.mkdir();shutil.copytree(candidate,prepared/'one')
        folder=prepared/'one';core.write(self.root/'diagnostic.json',{'diagnosticOnly':True})
        core.write(self.root/'replay.json',core.read(folder/'cases.json'))
        campaign=self.root/'clean.json'
        core.write(campaign,{'plan':[{'source':'one','documentSha256':core.sha(folder/'module.mapnote.json'),'casesSha256':core.sha(folder/'cases.json')}],
            'rows':[{'source':'one','status':'passed','report':{'path':'diagnostic.json','sha256':core.sha(self.root/'diagnostic.json')},
                'replayCases':{'path':'replay.json','sha256':core.sha(self.root/'replay.json')}}],
            'counts':{'passed':1},'complete':True})
        conflict=guard.HoldoutConflict({'phase':'holdout_guard','conflicts':['observed_pool']})
        with patch.object(core,'STATE',self.root/'state'),patch.object(core,'batch_enrollment',return_value=contextlib.nullcontext()),\
                patch.object(guard,'check',side_effect=conflict),patch.object(physics,'run')as run,patch.object(core,'certify')as certify:
            result=qualify.run(prepared,campaign,'test-guard')
        run.assert_not_called();certify.assert_not_called()
        self.assertEqual(result['rows'][0]['status'],'holdout_pool_locked')
        self.assertEqual(result['rows'][0]['actualAttempts'],0)
