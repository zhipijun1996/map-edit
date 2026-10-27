"""Metadata correction guards; local fake receipts grant no content admission."""
import copy,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from pcg.migration import core,evidence_refresh as e

class AvailableCorrection(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.old=self.root/'modules/sample';self.new=self.root/'prepared';self.old.mkdir(parents=True);self.new.mkdir()
        self.patch=patch.multiple(core,REPO=self.root,RECYCLE=self.root/'modules-recycle');self.patch.start();self.addCleanup(self.patch.stop)
        helper=self.root/'evidence_refresh.py';helper.write_bytes(Path(e.__file__).read_bytes())
        helper_patch=patch.object(e,'__file__',str(helper));helper_patch.start();self.addCleanup(helper_patch.stop)
        self.version='sha256:'+'a'*64
        self.doc=dict(id='same',title='same',objects=[dict(type='terrain',x=0,y=64,w=128,h=32)],generationContract=dict(contentVersion=self.version,space=dict(actorBody=dict(size=[24,36])),ports=[dict(id='entry',position=[0,64])],validations=[dict(id='v',kind='physics',routeId='main',result='pass',artifacts=[],coverage=dict(fullMap='UNKNOWN'),entryState=dict(grounded='UNKNOWN'),capabilityConfiguration=dict(available=['move','jump'],equipment='UNKNOWN'))]))
        self.cases=dict(cases=[dict(id='frozen',route_spec=dict(id='main'),capabilities=['move','jump','double_jump'],control_plan=[dict(op='jump')])])
        for folder in (self.old,self.new):
            core.write(folder/'module.mapnote.json',self.doc);core.write(folder/'physics-input-cases.json',self.cases);core.write(folder/'godot-package.json',dict(testOnlyFakeReceipt=True))
        self.report=self.root/'results/migration-physics.json';core.write(self.report,dict(contentVersion=self.version,routes=[dict(routeId='main')]))
        core.write(self.report.parent/'input-binding.json',dict(contentVersion=self.version,cases=dict(sha256=core.sha(self.old/'physics-input-cases.json'))))
        meta=dict(moduleId='sample',physicsReport=dict(path=core.relative(self.report),sha256=core.sha(self.report)))
        for folder in (self.old,self.new):core.write(folder/'migration.json',meta)
        self.validate=patch.object(core,'validate',return_value=dict(certified=True));self.mock_validate=self.validate.start();self.addCleanup(self.validate.stop)
        self.correct()
    def correct(self):
        d=core.read(self.new/'module.mapnote.json');d['generationContract']['validations'][0]['capabilityConfiguration']['available']=self.cases['cases'][0]['capabilities'];core.write(self.new/'module.mapnote.json',d)
    def change(self,fn):
        d=core.read(self.new/'module.mapnote.json');fn(d);core.write(self.new/'module.mapnote.json',d)
    def test_only_actual_caps_pass_and_native_validation_is_required_twice(self):
        proof=e.prove_available_correction(self.old,self.new)
        self.assertEqual(proof['changes'][0]['after'],['move','jump','double_jump']);self.assertEqual(proof['newPhysicsExperiments'],0)
        self.assertEqual(self.mock_validate.call_count,2)
        self.assertEqual(proof['canonicalInputs'][0]['sha256'],proof['canonicalInputs'][1]['sha256'])
        self.assertEqual(proof['archivedPreviousDocument']['sha256'],core.sha(self.old/'module.mapnote.json'))
    def test_rejects_geometry_port_body_and_every_other_document_field(self):
        for fn in (lambda d:d['objects'][0].update(x=1),lambda d:d['generationContract']['ports'][0].update(position=[0,65]),lambda d:d['generationContract']['space']['actorBody'].update(size=[24,35]),lambda d:d.update(title='renamed'),lambda d:d.update(source=dict(integration='forged'))):
            with self.subTest(fn=fn):
                core.write(self.new/'module.mapnote.json',self.doc);self.correct();self.change(fn)
                with self.assertRaisesRegex(ValueError,'other_document_field_changed'):e.prove_available_correction(self.old,self.new)
    def test_rejects_entry_equipment_result_status_coverage_and_artifacts(self):
        for field,value in [('entryState',dict(grounded=True)),('result','UNKNOWN'),('status','pass'),('coverage',dict(fullMap='verified')),('artifacts',[dict(path='fake',sha256='fake')])]:
            with self.subTest(field=field):
                core.write(self.new/'module.mapnote.json',self.doc);self.correct();self.change(lambda d:d['generationContract']['validations'][0].update({field:value}))
                with self.assertRaisesRegex(ValueError,'other_document_field_changed'):e.prove_available_correction(self.old,self.new)
        core.write(self.new/'module.mapnote.json',self.doc);self.correct();self.change(lambda d:d['generationContract']['validations'][0]['capabilityConfiguration'].update(equipment='gun'))
        with self.assertRaisesRegex(ValueError,'other_document_field_changed'):e.prove_available_correction(self.old,self.new)
    def test_rejects_forged_or_reordered_actual_caps(self):
        for caps in (['move','jump','double_jump','dash'],['double_jump','move','jump'],['move'],['UNKNOWN']):
            self.change(lambda d:d['generationContract']['validations'][0]['capabilityConfiguration'].update(available=caps))
            with self.assertRaisesRegex(ValueError,'actual_bound_route_caps'):e.prove_available_correction(self.old,self.new)
    def test_rejects_changed_canonical_case_even_if_same_version(self):
        altered=copy.deepcopy(self.cases);altered['cases'][0]['capabilities'].append('dash');core.write(self.new/'physics-input-cases.json',altered)
        with self.assertRaisesRegex(ValueError,'bound_cases_changed'):e.prove_available_correction(self.old,self.new)
    def test_rejects_replaced_physics_report(self):
        m=core.read(self.new/'migration.json');m['physicsReport']['sha256']='forged';core.write(self.new/'migration.json',m)
        with self.assertRaisesRegex(ValueError,'original_physics_report_changed'):e.prove_available_correction(self.old,self.new)
    def test_rejects_validation_route_or_identity_changes(self):
        self.change(lambda d:d['generationContract']['validations'][0].update(routeId='different'))
        with self.assertRaisesRegex(ValueError,'other_document_field_changed'):e.prove_available_correction(self.old,self.new)
    def test_rejects_bool_numeric_substitutions_in_unchanged_fields(self):
        self.change(lambda d:d['objects'][0].update(x=False))
        with self.assertRaisesRegex(ValueError,'other_document_field_changed'):e.prove_available_correction(self.old,self.new)
    def test_failed_actual_native_or_physics_validation_blocks_proof(self):
        self.mock_validate.side_effect=ValueError('actual_native_replay_failed')
        with self.assertRaisesRegex(ValueError,'actual_native_replay_failed'):e.prove_available_correction(self.old,self.new)
    def test_unchanged_or_cosmetic_document_does_not_open_exception(self):
        core.write(self.new/'module.mapnote.json',self.doc)
        with self.assertRaisesRegex(ValueError,'no_available_correction'):e.prove_available_correction(self.old,self.new)

# Run these after applying the reviewed draft, or against its in-memory isolated
# module in the documented draft test command. No frozen core.py write is needed.
import inspect,os
from unittest import mock
from pcg.migration.tests import test_package_refresh as transaction_fixture

@unittest.skipUnless('evidence_update' in inspect.signature(core.refresh_package).parameters,'Draft core patch is not applied')
class AvailableCorrectionTransaction(transaction_fixture.CompiledPackageRefresh):
    def setUp(self):
        super().setUp()
        for folder in (self.current,self.ready):
            d=core.read(folder/'module.mapnote.json');d['generationContract']['validations']=[dict(capabilityConfiguration=dict(available=['move']))];core.write(folder/'module.mapnote.json',d)
        self.old_files=core._tree_files(self.current)
        self.proof=dict(schema='test-only-proof-not-physics-certification',changes=[dict(before=['move'],after=['move','jump'])])
    def corrected(self):
        d=core.read(self.ready/'module.mapnote.json');d['generationContract']['validations'][0]['capabilityConfiguration']['available'].append('jump');core.write(self.ready/'module.mapnote.json',d)
    def test_explicit_correction_records_same_wal_and_history_and_repeats(self):
        self.corrected()
        with mock.patch('pcg.migration.evidence_refresh.prove_available_correction',return_value=self.proof) as proof:
            r=core.refresh_package(self.ready,evidence_update=True)
        self.assertEqual(r['status'],'package_refreshed');proof.assert_called_once_with(self.current,self.ready)
        history=core.read(self.journal)['entries'][self.key]['packageHistory']
        self.assertTrue(history[0]['evidenceUpdate']);self.assertEqual(history[0]['evidenceUpdateProof'],self.proof)
        wal=core.read(self.root/history[0]['transaction']);self.assertEqual(wal['evidenceUpdateProof'],self.proof)
        self.assertEqual(core.refresh_package(self.ready,evidence_update=True)['status'],'already_current')
        self.assertEqual(len(core.read(self.journal)['entries'][self.key]['packageHistory']),1)
    def test_default_rejects_available_correction(self):
        self.corrected()
        with self.assertRaisesRegex(ValueError,'module_document_changed'):core.refresh_package(self.ready)
        self.assert_original_current()
    def test_helper_rejection_cannot_move_any_package(self):
        self.corrected()
        with mock.patch('pcg.migration.evidence_refresh.prove_available_correction',side_effect=ValueError('forged_available')):
            with self.assertRaisesRegex(ValueError,'forged_available'):core.refresh_package(self.ready,evidence_update=True)
        self.assert_original_current()
    def test_correction_ledger_failure_rolls_back_using_existing_wal(self):
        self.corrected();original=core.write
        def fail(path,value):
            if Path(path)==self.journal and value.get('entries',{}).get(self.key,{}).get('packageHistory'):raise OSError('injected refresh ledger failure')
            return original(path,value)
        with mock.patch('pcg.migration.evidence_refresh.prove_available_correction',return_value=self.proof),mock.patch.object(core,'write',side_effect=fail):
            with self.assertRaisesRegex(OSError,'injected refresh ledger failure'):core.refresh_package(self.ready,evidence_update=True)
        self.assert_original_current()
    @unittest.skipUnless(hasattr(os,'fork'),'POSIX interruption test')
    def test_correction_process_death_recovers_with_original_wal(self):
        self.corrected();pid=os.fork()
        if pid==0:
            original=Path.rename
            def rename(path,target):
                result=original(path,target)
                if path==self.current and Path(target)==self.archive:os._exit(73)
                return result
            with mock.patch('pcg.migration.evidence_refresh.prove_available_correction',return_value=self.proof),mock.patch.object(Path,'rename',rename):core.refresh_package(self.ready,evidence_update=True)
            os._exit(74)
        _,status=os.waitpid(pid,0);self.assertEqual(os.waitstatus_to_exitcode(status),73)
        with mock.patch('pcg.migration.evidence_refresh.prove_available_correction',return_value=self.proof):
            self.assertEqual(core.refresh_package(self.ready,evidence_update=True)['status'],'package_refreshed')
        self.assertEqual(len(core.read(self.journal)['entries'][self.key]['packageHistory']),1)

if __name__=='__main__':unittest.main()
