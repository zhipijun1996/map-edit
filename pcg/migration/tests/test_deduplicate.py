"""Transaction fault tests only; mocked proofs never certify actual content."""
import copy,os,tempfile,unittest
from contextlib import ExitStack
from pathlib import Path
from unittest import mock
from pcg.migration import core,deduplicate as dedup

class CurrentDeduplicationTransactions(unittest.TestCase):
    def setUp(self):
        self.stack=ExitStack();self.addCleanup(self.stack.close)
        self.root=Path(self.stack.enter_context(tempfile.TemporaryDirectory()))
        self.active=self.root/'modules';self.recycle=self.root/'modules-recycle';self.state=self.root/'state';self.legacy=self.root/'legacy';self.journal=self.state/'ledger.json'
        self.stack.enter_context(mock.patch.multiple(core,REPO=self.root,ACTIVE=self.active,RECYCLE=self.recycle,STATE=self.state,LEGACY=self.legacy,JOURNAL=self.journal))
        self.source=self.active/'duplicate';self.primary=self.active/'primary'
        for folder,ident,version in [(self.source,'duplicate','2'),(self.primary,'primary','3')]:
            folder.mkdir(parents=True);core.write(folder/'module.mapnote.json',dict(generationContract=dict(contentVersion='sha256:'+version*64,ports=[dict(id='entry'),dict(id='door'if ident=='duplicate'else'exit')])));core.write(folder/'migration.json',dict(moduleId=ident,sourcePath='legacy/'+ident));(folder/'module.tscn').write_text('actual fixture bytes '+ident)
        (self.source/'archive.json').write_text('historical receipt remains exact')
        self.source_files=core._tree_files(self.source)
        self.before=dict(schema='test-ledger',entries={'legacy/duplicate':dict(migrationStatus='active',moduleId='duplicate',archive='modules-recycle/duplicate/original',destination='modules/duplicate'),'other':dict(migrationStatus='active',moduleId='other')},relocations={'legacy/duplicate':'modules-recycle/duplicate/original','other-original':'other-archive'})
        core.write(self.journal,self.before);self.old_catalog=b'{"modules":["duplicate","primary"],"old":true}\n';(self.active/'catalog.json').write_bytes(self.old_catalog)
        self.proof_path=self.state/'proof.json';core.write(self.proof_path,dict(duplicateId='duplicate',primaryId='primary'))
        self.artifact=dict(path=core.relative(self.proof_path),sha256=core.sha(self.proof_path))
        self.proof=dict(schema=dedup.SCHEMA,exact=True,duplicateId='duplicate',primaryId='primary',duplicateContentVersion='sha256:'+'2'*64,primaryContentVersion='sha256:'+'3'*64,portMapping={'entry':'entry','door':'exit'},routeMapping={'main':'main'})
        self.stack.enter_context(mock.patch.object(dedup,'verify_proof',side_effect=lambda _:copy.deepcopy(self.proof)))
        self.stack.enter_context(mock.patch.object(core,'validate',side_effect=self.validate_fixture))
        self.stack.enter_context(mock.patch.object(core,'build_catalog',side_effect=self.build_fixture))

    def validate_fixture(self,folder,require_certified=False):
        folder=Path(folder);doc=core.read(folder/'module.mapnote.json');meta=core.read(folder/'migration.json')
        return dict(moduleId=meta['moduleId'],contentVersion=doc['generationContract']['contentVersion'],certified=True,mapReady=False)

    def build_fixture(self):
        value=dict(modules=sorted(p.name for p in self.active.iterdir()if p.is_dir()));core.write(self.active/'catalog.json',value);return value

    def assert_rolled_back(self):
        self.assertEqual(core._tree_files(self.source),self.source_files);self.assertEqual(core.read(self.journal),self.before)
        self.assertFalse((self.recycle/'duplicate'/('duplicate-'+'2'*64)).exists());self.assertFalse((self.active/'aliases.json').exists())
        self.assertEqual((self.active/'catalog.json').read_bytes(),self.old_catalog)

    def test_merge_reloads_alias_and_keeps_original_source_relocation(self):
        result=dedup.merge(self.artifact);self.assertEqual(result['status'],'merged');self.assertFalse(self.source.exists())
        resolved=dedup.resolve('duplicate',['entry','door'],'sha256:'+'2'*64)
        self.assertEqual(resolved['primaryId'],'primary');self.assertEqual(resolved['mappedPorts'],['entry','exit'])
        journal=core.read(self.journal);self.assertEqual(journal['relocations']['legacy/duplicate'],self.before['relocations']['legacy/duplicate']);self.assertEqual(journal['entries']['legacy/duplicate']['archive'],self.before['entries']['legacy/duplicate']['archive'])
        self.assertEqual(journal['entries']['legacy/duplicate']['migrationStatus'],'exact_duplicate')
        archived=core.REPO/result['archive'];self.assertEqual((archived/'archive.json').read_text(),'historical receipt remains exact');self.assertTrue((archived/'migration-archive.json').exists())
        self.assertEqual(dedup.merge(self.artifact)['status'],'already_merged')

    def test_every_fault_boundary_restores_exact_bytes(self):
        for checkpoint in ('after_archive','after_aliases','after_ledger','after_catalog'):
            with self.subTest(checkpoint=checkpoint):
                def failure(label):
                    if label==checkpoint:raise OSError('injected '+label)
                with mock.patch.object(dedup,'_checkpoint',side_effect=failure):
                    with self.assertRaisesRegex(OSError,'injected'):dedup.merge(self.artifact)
                self.assert_rolled_back()

    @unittest.skipUnless(hasattr(os,'fork'),'requires POSIX process death')
    def test_process_death_at_each_boundary_recovers_before_proof_lookup(self):
        for checkpoint in ('after_archive','after_aliases','after_ledger','after_catalog'):
            with self.subTest(checkpoint=checkpoint):
                pid=os.fork()
                if pid==0:
                    with mock.patch.object(dedup,'_checkpoint',side_effect=lambda label:os._exit(73)if label==checkpoint else None):dedup.merge(self.artifact)
                    os._exit(74)
                _,status=os.waitpid(pid,0);self.assertEqual(os.waitstatus_to_exitcode(status),73)
                path=self.state/'transactions/deduplicate-duplicate.json'
                self.assertEqual(dedup.recover(path)['status'],'rolled_back');self.assert_rolled_back()

    def test_completion_record_failure_also_rolls_back(self):
        original=core._save_transaction
        def save(path,transaction):
            if transaction['status']=='complete':raise OSError('completion rejected')
            return original(path,transaction)
        with mock.patch.object(core,'_save_transaction',side_effect=save):
            with self.assertRaisesRegex(OSError,'completion'):dedup.merge(self.artifact)
        self.assert_rolled_back()

    def test_preexisting_alias_registry_bytes_survive_rollback(self):
        before=b'{ "schema": "pcg/module-aliases/v1", "aliases": {"older": {"primaryId": "primary"}} }\n'
        (self.active/'aliases.json').write_bytes(before)
        with mock.patch.object(dedup,'_checkpoint',side_effect=lambda label:(_ for _ in ()).throw(OSError('alias fault'))if label=='after_aliases'else None):
            with self.assertRaises(OSError):dedup.merge(self.artifact)
        self.assertEqual((self.active/'aliases.json').read_bytes(),before)
        self.assertEqual(core.read(self.journal),self.before)

    @unittest.skipUnless(hasattr(os,'fork'),'requires POSIX process death')
    def test_recovery_preserves_unrelated_enrollment_after_crash(self):
        pid=os.fork()
        if pid==0:
            with mock.patch.object(dedup,'_checkpoint',side_effect=lambda label:os._exit(73)if label=='after_ledger'else None):dedup.merge(self.artifact)
            os._exit(74)
        _,status=os.waitpid(pid,0);self.assertEqual(os.waitstatus_to_exitcode(status),73)
        (self.active/'fresh').mkdir();journal=core.read(self.journal);journal['entries']['fresh-original']=dict(migrationStatus='active');journal['relocations']['fresh-original']='fresh-archive';core.write(self.journal,journal)
        dedup.recover(self.state/'transactions/deduplicate-duplicate.json')
        restored=core.read(self.journal);self.assertEqual(restored['entries']['fresh-original'],dict(migrationStatus='active'));self.assertEqual(restored['relocations']['fresh-original'],'fresh-archive')
        self.assertEqual(core.read(self.active/'catalog.json')['modules'],['duplicate','fresh','primary'])

    def test_changed_alias_mapping_is_rejected(self):
        dedup.merge(self.artifact);registry=core.read(self.active/'aliases.json');registry['aliases']['duplicate']['portMapping']['door']='entry';core.write(self.active/'aliases.json',registry)
        with self.assertRaisesRegex(ValueError,'alias_not_bound'):dedup.resolve('duplicate',['door'])

    def test_stale_target_version_is_rejected(self):
        dedup.merge(self.artifact);doc=core.read(self.primary/'module.mapnote.json');doc['generationContract']['contentVersion']='sha256:'+'4'*64;core.write(self.primary/'module.mapnote.json',doc)
        with self.assertRaisesRegex(ValueError,'alias_target_content_version_changed'):dedup.resolve('duplicate')

    def test_caller_wrong_old_version_and_unknown_port_are_rejected(self):
        dedup.merge(self.artifact)
        with self.assertRaisesRegex(ValueError,'requested_alias_content_version_mismatch'):dedup.resolve('duplicate',expected_version='sha256:'+'5'*64)
        with self.assertRaisesRegex(ValueError,'unknown_aliased_port'):dedup.resolve('duplicate',['not-a-port'])

    def test_semantic_role_words_are_not_renamed_as_port_ids(self):
        result=dedup._canonical(dict(id='door',sourceRoles=['exit'],role='main'),{'door':'PORT1','exit':'PORT9','main':'ROUTE0'})
        self.assertEqual(result,dict(id='PORT1',sourceRoles=['exit'],role='main'))

if __name__=='__main__':unittest.main()
