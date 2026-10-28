"""Local transaction fixtures only; mock equivalence grants no real approval."""
import copy,os,unittest
from pathlib import Path
from unittest.mock import patch
from pcg.migration import core,deduplicate as dup,metadata_alias_rebind as a,metadata_diagnostics_reconcile as d
from pcg.migration.tests import test_metadata_diagnostics_reconcile as fixture

class MetadataAliasRebinding(unittest.TestCase):
    def setUp(self):
        fixture.MetadataDiagnosticsTests.setUp(self);p=patch.object(core,'RECYCLE',self.root/'modules-recycle');p.start();self.addCleanup(p.stop)
        self.archived=core.RECYCLE/'duplicate/archive';self.archived.mkdir(parents=True)
        core.write(self.archived/'migration.json',dict(moduleId='duplicate'))
        core.write(self.archived/'module.mapnote.json',dict(generationContract=dict(contentVersion=self.version,ports=[dict(id='entry')])))
        doc=core.read(self.folder/'module.mapnote.json');doc['generationContract']['ports']=[dict(id='entry')];core.write(self.folder/'module.mapnote.json',doc)
        self.journal['relocations']['modules/duplicate']=core.relative(self.archived);core.write(core.JOURNAL,self.journal)
        self.compare_patch=patch.object(dup,'_compare',side_effect=self.compare);self.compare_patch.start();self.addCleanup(self.compare_patch.stop)
        self.checked.side_effect=lambda folder,require_certified=False:dict(certified=True,moduleId=Path(folder).name,contentVersion=self.version,mapReady=False)
        self.old_proof=dict(schema=dup.SCHEMA,exact=True,duplicateId='duplicate',primaryId='sample',duplicateContentVersion=self.version,primaryContentVersion=self.version,**self.compare(self.archived,self.folder))
        self.proof_path=self.state/'original-proof.json';core.write(self.proof_path,self.old_proof)
        self.alias_file=self.active/'aliases.json';core.write(self.alias_file,dict(schema=dup.ALIASES_SCHEMA,aliases={'duplicate':dict(primaryId='sample',sourceContentVersion=self.version,targetContentVersion=self.version,archivedPackage=core.relative(self.archived),portMapping={'entry':'entry'},routeMapping={'main':'main'},proof=dict(path=core.relative(self.proof_path),sha256=core.sha(self.proof_path)))}))
        self.old_alias_bytes=self.alias_file.read_bytes();self.old_meta_bytes=(self.folder/'migration.json').read_bytes();self.before=core._tree_files(self.folder)
    def compare(self,source,primary):
        return dict(semanticFingerprint='same-actual-fixture',portMapping={'entry':'entry'},routeMapping={'main':'main'},runtimeDependencyFingerprint='same-runtime',actualPhysicsSourceFingerprint='same-physics',nonPhysicsToolingDeltas=[],physicsSourceFiles=3,identicalPhysicsAndCausalFiles=3,
            sourceValidation=dict(moduleId='duplicate',contentVersion=self.version),primaryValidation=dict(moduleId='sample',contentVersion=self.version),
            artifacts=[dict(path=core.relative(Path(p)/'migration.json'),sha256=core.sha(Path(p)/'migration.json'))for p in (source,primary)])
    def assert_restored(self):
        self.assertEqual((self.folder/'migration.json').read_bytes(),self.old_meta_bytes);self.assertEqual(self.alias_file.read_bytes(),self.old_alias_bytes)
        dup.resolve('duplicate')
    def test_alias_proof_is_rederived_rebound_and_freshly_retrievable(self):
        result=d.reconcile_one(self.folder,self.journal);self.assertEqual(result['aliasRebinding']['affectedAliases'],['duplicate'])
        aliases=dup._aliases();entry=aliases['aliases']['duplicate'];self.assertEqual(len(entry['proofHistory']),1)
        self.assertNotEqual(entry['proof']['sha256'],core.sha(self.proof_path));self.assertEqual(core.read(self.proof_path),self.old_proof)
        self.assertEqual(core.resolve_artifact(entry['proofHistory'][0]['previousPrimaryMetadata']['path']).read_bytes(),self.old_meta_bytes)
        self.assertEqual(core.resolve_artifact(entry['proofHistory'][0]['previousAliasRegistry']['path']).read_bytes(),self.old_alias_bytes)
        self.assertEqual(dup.resolve('duplicate')['primaryId'],'sample')
        self.assertEqual(core.read(core.resolve_artifact(result['aliasRebinding']['transaction']['path']))['status'],'complete')
        self.assertEqual(d.reconcile_one(self.folder,self.journal)['status'],'already_aligned')
    def test_failure_after_metadata_or_alias_install_rolls_back_both(self):
        for phase in ('after_metadata','after_aliases'):
            with self.subTest(phase=phase):
                def fail(name):
                    if name==phase:raise OSError('injected '+phase)
                with patch.object(a,'_checkpoint',side_effect=fail):
                    with self.assertRaisesRegex(OSError,'injected'):d.reconcile_one(self.folder,self.journal)
                self.assert_restored()
    @unittest.skipUnless(hasattr(os,'fork'),'POSIX interruption test')
    def test_process_death_at_both_write_phases_recovers_without_losing_alias(self):
        for phase in ('after_metadata','after_aliases'):
            # A second fresh fixture is unnecessary: recover to identical input
            # bytes, then explicitly leave this attempt rolled back for next loop.
            pid=os.fork()
            if pid==0:
                def die(name):
                    if name==phase:os._exit(73)
                with patch.object(a,'_checkpoint',side_effect=die):d.reconcile_one(self.folder,self.journal)
                os._exit(74)
            _,status=os.waitpid(pid,0);self.assertEqual(os.waitstatus_to_exitcode(status),73)
            a.recover_pending();self.assert_restored()
        d.reconcile_one(self.folder,self.journal);self.assertEqual(dup.resolve('duplicate')['primaryId'],'sample')
    def test_semantic_or_other_artifact_delta_never_gets_rebound(self):
        original=self.compare
        def bad(source,primary):
            value=original(source,primary)
            if core.read(self.folder/'migration.json').get('diagnosticsReconciliationHistory'):value['semanticFingerprint']='changed'
            return value
        with patch.object(dup,'_compare',side_effect=bad):
            with self.assertRaisesRegex(ValueError,'equivalence_changed'):d.reconcile_one(self.folder,self.journal)
        self.assert_restored()
    def test_completion_wal_failure_restores_alias_and_metadata(self):
        original=core._save_transaction
        def fail(path,value):
            if value.get('schema')==a.SCHEMA and value['status']=='complete':raise OSError('injected completion')
            return original(path,value)
        with patch.object(core,'_save_transaction',side_effect=fail):
            with self.assertRaisesRegex(OSError,'injected completion'):d.reconcile_one(self.folder,self.journal)
        self.assert_restored()

if __name__=='__main__':unittest.main()
