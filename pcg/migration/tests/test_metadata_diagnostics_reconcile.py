"""Display diagnostics never grant qualification or alter immutable package bytes."""
import copy,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from pcg.migration import core,metadata_diagnostics_reconcile as d

class MetadataDiagnosticsTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.active=self.root/'modules';self.state=self.root/'state';self.folder=self.active/'sample';self.folder.mkdir(parents=True)
        p=patch.multiple(core,REPO=self.root,ACTIVE=self.active,STATE=self.state,JOURNAL=self.state/'ledger.json');p.start();self.addCleanup(p.stop)
        code=self.root/'diagnostics-helper.py';code.write_bytes(Path(d.__file__).read_bytes());p=patch.object(d,'__file__',str(code));p.start();self.addCleanup(p.stop)
        self.version='sha256:'+'a'*64;self.report=self.root/'results/migration-physics.json'
        core.write(self.report,dict(passed=True,contentVersion=self.version,unknown=['mirror','full Map']))
        core.write(self.folder/'module.mapnote.json',dict(generationContract=dict(contentVersion=self.version)))
        core.write(self.folder/'godot-package.json',dict(testOnlyFake=True));core.write(self.folder/'load-evidence/index.json',dict(testOnlyFake=True))
        self.meta=dict(moduleId='sample',sourcePath='legacy/original',status='passed_scoped',humanReview='design_hold',productionAdmitted=False,
            sourceVersion='sha256:source',sourceFiles={'record.json':'source-sha'},boundaryProbe=dict(passed=True),
            unresolved=['boundary crossing','await strict qualification'],godotLoad=dict(passed=True),
            physicsReport=dict(path=core.relative(self.report),sha256=core.sha(self.report)))
        core.write(self.folder/'migration.json',self.meta)
        self.journal=dict(entries={'legacy/original':dict(migrationStatus='active',moduleId='sample',destination='modules/sample',contentVersion=self.version)},relocations={})
        core.write(core.JOURNAL,self.journal)
        p=patch.object(core,'validate',return_value=dict(certified=True));self.checked=p.start();self.addCleanup(p.stop)
        self.before=core._tree_files(self.folder)
    def report_change(self,**changes):
        r=core.read(self.report);r.update(changes);core.write(self.report,r)
        m=core.read(self.folder/'migration.json');m['physicsReport']['sha256']=core.sha(self.report);core.write(self.folder/'migration.json',m)
    def test_changes_only_diagnostic_and_history_preserving_human_hold_and_native(self):
        result=d.reconcile_one(self.folder,self.journal)
        new=core.read(self.folder/'migration.json');self.assertEqual(new['unresolved'],['mirror','full Map'])
        history=new.pop('diagnosticsReconciliationHistory');new['unresolved']=self.meta['unresolved'];self.assertEqual(new,self.meta)
        self.assertEqual(history[0]['previousUnresolved'],self.meta['unresolved'])
        receipt=core.read(core.resolve_artifact(result['receipt']['path']));self.assertEqual(receipt['previousMetadata'],self.meta)
        for name,sha in self.before.items():
            if name!='migration.json':self.assertEqual(core.sha(self.folder/name),sha)
        self.checked.assert_called_once_with(self.folder,require_certified=True)
        self.assertFalse(receipt['productionAdmittedPreserved']);self.assertEqual(receipt['humanReviewPreserved'],'design_hold')
    def test_idempotent_does_not_append_history_again(self):
        d.reconcile_one(self.folder,self.journal);before=core.sha(self.folder/'migration.json')
        self.assertEqual(d.reconcile_one(self.folder,self.journal)['status'],'already_aligned')
        self.assertEqual(core.sha(self.folder/'migration.json'),before)
        self.assertEqual(len(list(self.state.rglob('*.json'))),2)
    def test_dry_run_writes_no_receipt_or_metadata(self):
        self.assertEqual(d.reconcile_one(self.folder,self.journal,update=False)['status'],'would_reconcile')
        self.assertEqual(core._tree_files(self.folder),self.before);self.assertEqual(len(list(self.state.rglob('*.json'))),1)
    def test_report_wrong_content_version_rejected(self):
        self.report_change(contentVersion='sha256:different')
        with self.assertRaisesRegex(ValueError,'content_version_mismatch'):d.reconcile_one(self.folder,self.journal)
    def test_changed_report_sha_rejected(self):
        self.report.write_text('{"forged":true}')
        with self.assertRaisesRegex(ValueError,'missing_or_changed_evidence'):d.reconcile_one(self.folder,self.journal)
    def test_not_passed_report_rejected(self):
        for value in (False,'true',1):
            self.report_change(passed=value)
            with self.assertRaisesRegex(ValueError,'actual_passed_report_required'):d.reconcile_one(self.folder,self.journal)
    def test_nonactive_or_wrong_ledger_identity_rejected(self):
        for changes in (dict(migrationStatus='needs_repair'),dict(moduleId='other'),dict(destination='elsewhere'),dict(contentVersion='other')):
            j=copy.deepcopy(self.journal);j['entries']['legacy/original'].update(changes)
            with self.assertRaisesRegex(ValueError,'active_ledger_identity_required'):d.reconcile_one(self.folder,j)
    def test_not_native_loaded_or_not_scoped_rejected(self):
        for changes in (dict(godotLoad=dict(passed=False)),dict(status='prepared_unverified')):
            m=copy.deepcopy(self.meta);m.update(changes);core.write(self.folder/'migration.json',m)
            with self.assertRaises(ValueError):d.reconcile_one(self.folder,self.journal)
    def test_actual_native_or_physics_validator_failure_rejected_before_write(self):
        self.checked.side_effect=ValueError('raw_or_native_binding_changed')
        with self.assertRaisesRegex(ValueError,'raw_or_native_binding_changed'):d.reconcile_one(self.folder,self.journal)
        self.assertEqual(core._tree_files(self.folder),self.before)
    def test_report_unknowns_not_reinterpreted_or_removed(self):
        values=['unsearched port pairs','arbitrary entry states','full Map'];self.report_change(unknown=values)
        d.reconcile_one(self.folder,self.journal);self.assertEqual(core.read(self.folder/'migration.json')['unresolved'],values)
    def test_malformed_unknowns_rejected(self):
        self.report_change(unknown='all good')
        with self.assertRaisesRegex(ValueError,'exact_report_unknown_list_required'):d.reconcile_one(self.folder,self.journal)

if __name__=='__main__':unittest.main()
