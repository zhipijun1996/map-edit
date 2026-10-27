"""Disposition reporting must not turn preparation or stale evidence into admission."""
import copy,unittest
from pathlib import Path
from unittest.mock import patch
from pcg.migration import migration_status as s

class MigrationStatusTests(unittest.TestCase):
    def source(self):return dict(sourceKey='source/old',sourceVersion='sha256:old',sourceType='repository_generated',title='fixture')
    def candidate(self):return dict(contentVersion='sha256:new',sourceVersion='sha256:old',folder='cache/new',mtime=2,status='prepared',staticFormatPassed=True,document=dict(path='missing',sha256='doc'),physicsInput=dict(sha256='input'),humanReview='UNKNOWN')
    def event(self,**kwargs):return dict(kind='full_physics',contentVersion='sha256:new',mtime=3,stage='calibration_failed',passed=False,conflicts=['moderate_gate'],artifact=dict(path='failure-receipt',sha256='bound'),**kwargs)
    def test_stale_old_program_failure_is_not_current_program_failure(self):
        e=self.event();e['contentVersion']='sha256:old_revision'
        r=s._disposition(self.source(),{},[self.candidate()],[e])
        self.assertEqual(r['stage'],'new_standard_version_prepared_pending_actual_validation')
        self.assertEqual(r['latestPreviousExperiment'],e)
        self.assertIsNone(r['latestEvidence'])
    def test_same_version_different_input_bytes_are_reported_as_conflict(self):
        r=s._disposition(self.source(),{},[self.candidate()],[self.event(physicsInput=dict(sha256='changed'))])
        self.assertEqual(r['stage'],'evidence_binding_conflict');self.assertFalse(r['latestEvidence']['passed'])
    def test_full_physics_not_overridden_by_later_clean_only(self):
        clean=self.event();clean.update(kind='clean_preflight',mtime=4,stage='clean_preflight_passed_pending_full_quality',passed=True)
        r=s._disposition(self.source(),{},[self.candidate()],[self.event(),clean])
        self.assertEqual(r['stage'],'calibration_failed')
    def test_later_native_package_failure_overrides_full_pass(self):
        full=self.event();full.update(passed=True,stage='full_physics_passed_awaiting_native_package_or_enrollment')
        package=self.event();package.update(kind='campaign_error',mtime=4,stage='native_package_projection_failed')
        r=s._disposition(self.source(),{},[self.candidate()],[full,package])
        self.assertEqual(r['stage'],'native_package_projection_failed')
    def test_full_pass_awaiting_admission_is_never_active(self):
        full=self.event();full.update(passed=True,stage='full_physics_passed_awaiting_native_package_or_enrollment')
        r=s._disposition(self.source(),{},[self.candidate()],[full])
        self.assertNotEqual(r['disposition'],'active')
        self.assertIn('awaiting_native_package',r['stage'])
    def test_active_or_alias_cannot_be_demoted_by_historical_failure(self):
        for status in ('active','exact_duplicate','recycled'):
            r=s._disposition(self.source(),dict(migrationStatus=status),[self.candidate()],[self.event()])
            self.assertEqual(r['disposition'],status)
    def test_human_hold_and_initial_gaps_are_preserved_separately(self):
        r=s._disposition(self.source(),dict(migrationStatus='human_design_hold',gaps=['old_size']),[self.candidate()],[self.event()])
        self.assertTrue(r['humanHoldPreserved']);self.assertEqual(r['initialGaps'],['old_size']);self.assertEqual(r['currentConflicts'],['moderate_gate'])
    def test_older_version_receipt_copy_does_not_outrank_new_revision(self):
        old=self.candidate();old.update(contentVersion='sha256:older',mtime=1)
        copy_old=copy.deepcopy(old);copy_old['mtime']=100
        new=self.candidate();new['mtime']=2
        self.assertEqual(s._latest_candidate([old,copy_old,new])['contentVersion'],'sha256:new')
    def test_missing_original_experiment_byte_image_is_explicit(self):
        e=self.event(experimentDocument=dict(path='missing-original-image',sha256='original-bytes'))
        r=s._disposition(self.source(),{},[self.candidate()],[e])
        self.assertFalse(r['experimentDocumentByteImage']['availableAtBoundPath'])
        self.assertFalse(r['experimentDocumentByteImage']['sameAsCurrentPreparedDocument'])
    def test_actual_failure_reasons_include_causal_failure_not_only_gate(self):
        q=dict(rows=[dict(level='moderate',trial=2,purpose=dict(ok=False,reasons=['bell_not_hit']))],quality_gate=dict(status='failed',reasons=['moderate_below_threshold']))
        with patch.object(s,'_ref',return_value=(q,None)):
            result=s._quality(dict(path='actual-calibration'))
        self.assertEqual(result['observedFailureReasons'],['bell_not_hit'])
    def test_all_311_sources_and_72_dependency_owners_are_explicit(self):
        fixed,originals=s.registry();deps=s.dependency_rows(originals)
        self.assertEqual(len(fixed),311);self.assertEqual(len(deps),72)
        self.assertTrue(all(d['moduleReferenceOwners'] and not d['countedAsPendingModule'] and not d['moved'] for d in deps))

if __name__=='__main__':unittest.main()
