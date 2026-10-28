"""Batch bookkeeping tests; test doubles never claim a Godot certificate."""
import copy
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import Mock, patch

from pcg.migration import core, corner_batch
import pcg.migration as migration_package


class CornerBatchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.state = self.repo/'pcg/migration/foundation-v1'
        self.state.mkdir(parents=True)
        core.write(self.state/'protocol-full-v2.json', dict(maximumAttemptsThisBatch=60000))
        self.patches = [patch.object(core, 'REPO', self.repo), patch.object(core, 'STATE', self.state)]
        for p in self.patches: p.start(); self.addCleanup(p.stop)
        self.doc = dict(id='TEST-ONLY', generationContract=dict(contentVersion='sha256:'+'a'*64,
            foundation=dict(blockSize=128), space=dict(bounds=dict(x=-128,y=128,w=256,h=256)),
            ports=[dict(id='left', position=[-128,192], face='LEFT', surface='ROCK',permission='INOUT'),
                   dict(id='right',position=[128,320],face='RIGHT',surface='ROCK',permission='INOUT')]))
        self.folder = self.repo/'modules/test-module'; self.folder.mkdir(parents=True)
        core.write(self.folder/'module.mapnote.json',self.doc)
        core.write(self.folder/'cases.json',dict(cases=[dict(id='TEST-ONLY-NOT-REAL-PHYSICS')]))
        self.entry = dict(id='test-module',contentSha256=core.sha(self.folder/'module.mapnote.json'),
            contentVersion=self.doc['generationContract']['contentVersion'],ports=copy.deepcopy(self.doc['generationContract']['ports']))
        self.catalog = dict(modules=[self.entry]); core.write(self.repo/'modules/catalog.json',self.catalog)
        source = self.repo/'test-adapter.py'; source.write_text('# Test-only preparation, not a physics adapter\n')
        def fake_prepare(source_folder, target, port_id, corner):
            target.mkdir(parents=True)
            core.write(target/'module.mapnote.json',core.read(source_folder/'module.mapnote.json'))
            core.write(target/'cases.json',core.read(source_folder/'cases.json'))
            core.write(target/'corner-adaptation.json',dict(testOnly=True))
        self.adapter = types.SimpleNamespace(__file__=str(source),prepare=Mock(side_effect=fake_prepare))
        p=patch.object(migration_package,'corner_batch_adapter',self.adapter,create=True)
        p.start();self.addCleanup(p.stop)

    def test_four_corner_targets_use_actual_negative_origin_and_stable_keys(self):
        rows=corner_batch.inventory_options(self.catalog,self.repo)
        self.assertEqual([(r['portId'],r['corner'],r['targetFace'])for r in rows],
            [('left','TOP_LEFT','TOP'),('right','BOTTOM_RIGHT','BOTTOM')])
        self.assertEqual(rows,corner_batch.inventory_options(self.catalog,self.repo))
        self.assertEqual(len({r['key']for r in rows}),2)

    def test_current_catalog_certified_option_is_not_duplicated_by_default(self):
        self.entry['ports'][0]['cornerRelocations']={'TOP_LEFT':dict(allowed=True,profileId='already-certified')}
        self.assertEqual(len(corner_batch.inventory_options(self.catalog,self.repo)),1)
        self.assertEqual(len(corner_batch.inventory_options(self.catalog,self.repo,include_certified=True)),2)

    def test_durable_verified_receipt_prevents_retest_before_catalog_rebuild(self):
        path=self.folder/'port-configurations/test-only/receipt.json'
        core.write(path,dict(relocations=[dict(portId='left',corner='TOP_LEFT')]))
        ref=dict(path=path.relative_to(self.repo).as_posix(),sha256=core.sha(path))
        with patch('pcg.migration.corners.verified_receipts',return_value=[ref])as verifier:
            rows=corner_batch.inventory_options(self.catalog,self.repo)
        verifier.assert_called_once()
        self.assertEqual([(r['portId'],r['corner'])for r in rows],[('right','BOTTOM_RIGHT')])

    def test_changed_catalog_bytes_fail_closed(self):
        (self.folder/'module.mapnote.json').write_text('{}')
        with self.assertRaisesRegex(ValueError,'catalog_document_changed'):
            corner_batch.inventory_options(self.catalog,self.repo)

    def test_preparation_does_not_grant_admission_and_is_idempotent(self):
        first=corner_batch.prepare('test-batch')
        self.assertEqual(first['counts'],{'prepared':2})
        self.assertFalse(first['technicalAdmission'])
        self.assertTrue(all('allowed'not in row for row in first['rows']))
        self.assertEqual(self.adapter.prepare.call_count,2)
        self.assertEqual(corner_batch.prepare('test-batch'),first)
        self.assertEqual(self.adapter.prepare.call_count,2)

    def test_source_change_is_rejected_before_a_resumed_preparation(self):
        corner_batch.prepare('test-batch')
        core.write(self.folder/'cases.json',dict(cases=[dict(id='CHANGED-INPUT')]))
        with self.assertRaisesRegex(ValueError,'frozen_corner_base_changed'):
            corner_batch.prepare('test-batch')

    def test_adapter_change_cannot_reuse_a_frozen_plan(self):
        corner_batch.prepare('test-batch')
        Path(self.adapter.__file__).write_text('# changed test fixture adapter\n')
        with self.assertRaisesRegex(ValueError,'policy_or_adapter_changed'):
            corner_batch.prepare('test-batch')

    def test_v3_plan_binds_its_own_source_and_cannot_rebind_v2_batch(self):
        v3_file=self.repo/'test-adapter-v3.py';v3_file.write_text('# TEST-ONLY isolated version 3\n')
        v3=types.SimpleNamespace(__file__=str(v3_file),prepare=self.adapter.prepare)
        with patch.object(migration_package,'corner_batch_adapter_v3',v3,create=True):
            corner_batch.prepare('test-v3',adapter_version='v3')
            state,_=corner_batch._paths('test-v3');plan=core.read(state/'plan.json')
            self.assertEqual(plan['adapterVersion'],'v3')
            self.assertEqual(plan['adapterSource']['sha256'],core.sha(v3_file))
            with self.assertRaisesRegex(ValueError,'policy_or_adapter_changed'):
                corner_batch.prepare('test-v3')
            corner_batch.prepare('test-v2')
            with self.assertRaisesRegex(ValueError,'policy_or_adapter_changed'):
                corner_batch.prepare('test-v2',adapter_version='v3')

    def test_legacy_v2_plan_without_version_field_resumes_without_rewrite(self):
        first=corner_batch.prepare('test-legacy')
        state,_=corner_batch._paths('test-legacy');plan=core.read(state/'plan.json')
        plan.pop('adapterVersion');core.write(state/'plan.json',plan)
        frozen=core.read(state/'frozen-inputs.json')
        frozen['plan']['sha256']=core.sha(state/'plan.json');core.write(state/'frozen-inputs.json',frozen)
        before=(state/'plan.json').read_bytes()
        self.assertEqual(corner_batch.prepare('test-legacy'),first)
        self.assertEqual((state/'plan.json').read_bytes(),before)

    def test_selected_v4_subset_and_helpers_are_frozen_before_preparation(self):
        v4_file=self.repo/'test-adapter-v4.py';v4_file.write_text('# TEST-ONLY isolated v4\n')
        helper=self.repo/'test-helper.py';helper.write_text('# TEST-ONLY helper\n')
        v4=types.SimpleNamespace(__file__=str(v4_file),prepare=self.adapter.prepare,SOURCE_DEPENDENCIES=[helper])
        keys=[r['key']for r in corner_batch.inventory_options(self.catalog,self.repo)]
        with patch.object(migration_package,'corner_batch_adapter_v4',v4,create=True):
            result=corner_batch.prepare('test-subset',adapter_version='v4',only_keys=[keys[0]])
            self.assertEqual(len(result['rows']),1)
            state,_=corner_batch._paths('test-subset');plan=core.read(state/'plan.json')
            self.assertEqual(plan['onlyKeys'],[keys[0]])
            self.assertEqual(plan['implementationDependencies'][0]['sha256'],core.sha(helper))
            with self.assertRaisesRegex(ValueError,'policy_or_adapter_changed'):
                corner_batch.prepare('test-subset',adapter_version='v4',only_keys=keys)
            helper.write_text('# changed helper\n')
            with self.assertRaisesRegex(ValueError,'adapter_dependencies_changed'):
                corner_batch.prepare('test-subset',adapter_version='v4',only_keys=[keys[0]])

    def test_unknown_preparation_subset_key_creates_no_frozen_plan(self):
        with self.assertRaisesRegex(ValueError,'requested_key_not_in_inventory'):
            corner_batch.prepare('test-invalid-subset',only_keys=['does-not-exist'])
        state,_=corner_batch._paths('test-invalid-subset')
        self.assertFalse((state/'plan.json').exists())

    def test_preparation_failure_is_tooling_gap_not_measured_failure(self):
        self.adapter.prepare.side_effect=ValueError('TEST_ONLY_MISSING_ADAPTER')
        result=corner_batch.prepare('test-batch')
        self.assertEqual(result['counts'],{'tooling_gap':2})
        self.assertEqual(result['actualAttempts'],0)
        self.assertFalse(result['technicalAdmission'])

    def test_prepared_input_tamper_never_launches_the_harness(self):
        result=corner_batch.prepare('test-batch')
        for row in result['rows']:
            (self.repo/row['prepared']/'cases.json').write_text('{}')
        with patch('pcg.migration.physics.run_clean')as run:
            status=corner_batch.preflight('test-batch',workers=1)
        run.assert_not_called()
        self.assertEqual(status['counts'],{'tooling_gap':2})
        self.assertEqual(status['actualAttempts'],0)

    def test_partial_old_experiment_is_preserved_and_not_rerun(self):
        result=corner_batch.prepare('test-batch')
        for row in result['rows']:
            path=self.repo/'pcg/results'/corner_batch._run_name('test-batch','pre',row['key'])
            path.mkdir(parents=True);core.write(path/'batches.json',[dict(cases=3)])
        with patch('pcg.migration.physics.run_clean')as run:
            status=corner_batch.preflight('test-batch',workers=1)
        run.assert_not_called()
        self.assertTrue(all('interrupted_corner_preflight'in r['conflict']for r in status['rows']))
        self.assertEqual(status['actualAttempts'],6)
        self.assertFalse(status['technicalAdmission'])

    def test_representative_subset_is_not_reported_as_all_options_complete(self):
        result=corner_batch.prepare('test-batch'); first=result['rows'][0]
        path=self.repo/'pcg/results'/corner_batch._run_name('test-batch','pre',first['key'])
        path.mkdir(parents=True);core.write(path/'batches.json',[dict(cases=1)])
        status=corner_batch.preflight('test-batch',workers=1,only_keys=[first['key']])
        self.assertEqual(len(status['rows']),1)
        self.assertFalse(status['complete'])

    def test_subset_cannot_inject_an_unregistered_candidate(self):
        corner_batch.prepare('test-batch')
        with patch('pcg.migration.physics.run_clean')as run:
            with self.assertRaisesRegex(ValueError,'requested_key_not_in_frozen'):
                corner_batch.preflight('test-batch',only_keys=['unregistered-input'])
        run.assert_not_called()

    def test_failed_preflight_never_consumes_holdout_or_installs(self):
        result=corner_batch.prepare('test-batch')
        state,_=corner_batch._paths('test-batch')
        core.write(state/'preflight.json',dict(actualAttempts=2,rows=[dict(key=r['key'],status='preflight_failed')for r in result['rows']]))
        with patch('pcg.migration.physics.run')as run,patch('pcg.migration.holdout_guard.register_pool')as register,patch.object(corner_batch,'install_configuration')as install:
            status=corner_batch.qualify('test-batch',workers=1)
        run.assert_not_called();register.assert_not_called();install.assert_not_called()
        self.assertEqual(status['rows'],[])

    def test_dynamic_clean_trials_cannot_be_hidden_under_the_350_budget(self):
        # Five dynamic routes require 360 cal/held trials before any seams.
        dynamic=[dict(moving_platforms=[dict(platform_id='TEST-ONLY')])for _ in range(5)]
        with patch('pcg.migration.physics.seam_cases',return_value=[]),patch('pcg.migration.physics.counter_cases',return_value=[]):
            self.assertGreater(corner_batch._full_attempt_bound(dynamic,self.doc),350)
            self.assertLess(corner_batch._full_attempt_bound([{}for _ in range(5)],self.doc),350)


if __name__=='__main__':unittest.main()
