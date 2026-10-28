"""Filesystem transaction tests only; mock certificates never qualify content."""
import copy
import json
import os
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest import mock

from pcg.migration import core


class RelocationTransactions(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.root = Path(self.stack.enter_context(tempfile.TemporaryDirectory()))
        self.active = self.root/'modules'
        self.recycle = self.root/'modules-recycle'
        self.state = self.root/'state'
        self.legacy = self.root/'legacy'
        self.journal = self.state/'ledger.json'
        self.stack.enter_context(mock.patch.multiple(core, REPO=self.root,
            ACTIVE=self.active, RECYCLE=self.recycle, STATE=self.state,
            LEGACY=self.legacy, JOURNAL=self.journal))
        self.source = self.legacy/('1'*64)
        self.source.mkdir(parents=True)
        (self.source/'payload.json').write_text('{"unchanged": true}\n')
        # An existing archive.json must not be overwritten by the new receipt.
        (self.source/'archive.json').write_text('{"historical": true}\n')
        self.source_files = core._tree_files(self.source)
        self.source_key = core.relative(self.source)
        self.prepared = self.root/'prepared'
        self.prepared.mkdir()
        core.write(self.prepared/'module.mapnote.json', {
            'generationContract': {'contentVersion': 'sha256:'+'2'*64}})
        core.write(self.prepared/'migration.json', dict(moduleId='sample',
            sourcePath=self.source_key, sourceVersion='sha256:'+'1'*64,
            sourceFiles=self.source_files, humanReview='UNKNOWN'))
        self.before = dict(schema='test-ledger', entries={
            self.source_key: {'migrationStatus': 'needs_verification'},
            'other': {'migrationStatus': 'pending'}}, relocations={})
        core.write(self.journal, self.before)
        self.active.mkdir()
        self.old_catalog = b'{ "modules": [], "old": true }\n'
        (self.active/'catalog.json').write_bytes(self.old_catalog)
        self.stack.enter_context(mock.patch.object(core, 'validate',
                                                   side_effect=self.fake_validate))
        self.stack.enter_context(mock.patch.object(core, 'build_catalog',
                                                   side_effect=self.fake_build))
        self.reason = self.root/'reason.json'
        core.write(self.reason, {'reason': 'explicit test disposal'})

    def fake_validate(self, folder, require_certified=False):
        """No Godot/schema claim: only assert evidence is still resolvable."""
        folder = Path(folder)
        self.assertTrue(core.resolve_artifact(self.source_key+'/payload.json').is_file())
        doc = core.read(folder/'module.mapnote.json')
        return dict(moduleId='sample', certified=True,
                    contentVersion=doc['generationContract']['contentVersion'])

    def fake_build(self):
        value = {'modules': sorted(p.name for p in self.active.iterdir()
                                   if p.is_dir())}
        core.write(self.active/'catalog.json', value)
        return value

    def assert_rolled_back(self):
        self.assertEqual(core._tree_files(self.source), self.source_files)
        self.assertFalse((self.active/'sample').exists())
        self.assertFalse((self.recycle/'sample'/('1'*64)).exists())
        self.assertEqual(core.read(self.journal), self.before)
        self.assertEqual((self.active/'catalog.json').read_bytes(), self.old_catalog)

    def fail_commit_once(self, status):
        original = core.write
        fired = False

        def write(path, value):
            nonlocal fired
            entry = value.get('entries', {}).get(self.source_key, {})
            if Path(path) == self.journal and entry.get('migrationStatus') == status and not fired:
                fired = True
                raise OSError('injected journal commit failure')
            return original(path, value)
        return mock.patch.object(core, 'write', side_effect=write)

    def test_promote_success_and_repeat_preserve_original_and_evidence(self):
        self.assertEqual(core.promote(self.prepared)['status'], 'active')
        target = self.recycle/'sample'/('1'*64)
        self.assertFalse(self.source.exists())
        self.assertEqual((target/'archive.json').read_text(), '{"historical": true}\n')
        self.assertTrue((target/'migration-archive.json').is_file())
        self.assertEqual(core.sha(core.resolve_artifact(self.source_key+'/payload.json')),
                         self.source_files['payload.json'])
        self.assertEqual(core.promote(self.prepared)['status'], 'already_active')
        self.assertEqual(len(list((self.recycle/'sample').iterdir())), 1)

    def test_target_validation_failure_does_not_move_original(self):
        def validate(folder, require_certified=False):
            if Path(folder) != self.prepared:
                raise ValueError('injected target validation failure')
            return self.fake_validate(folder, require_certified)
        with mock.patch.object(core, 'validate', side_effect=validate):
            with self.assertRaisesRegex(ValueError, 'target validation'):
                core.promote(self.prepared)
        self.assert_rolled_back()

    def test_journal_failure_restores_original_ledger_and_index_then_retries(self):
        with self.fail_commit_once('active'):
            with self.assertRaisesRegex(OSError, 'journal commit'):
                core.promote(self.prepared)
        self.assert_rolled_back()
        self.assertEqual(core.promote(self.prepared)['status'], 'active')

    def test_index_failure_after_write_is_inside_transaction(self):
        def build():
            self.fake_build()
            raise OSError('injected catalog failure after write')
        with mock.patch.object(core, 'build_catalog', side_effect=build):
            with self.assertRaisesRegex(OSError, 'catalog failure'):
                core.promote(self.prepared)
        self.assert_rolled_back()

    def test_complete_record_failure_also_rolls_back(self):
        original = core._save_transaction
        def save(path, value):
            if value['status'] == 'complete':
                raise OSError('injected completion failure')
            return original(path, value)
        with mock.patch.object(core, '_save_transaction', side_effect=save):
            with self.assertRaisesRegex(OSError, 'completion failure'):
                core.promote(self.prepared)
        self.assert_rolled_back()

    @unittest.skipUnless(hasattr(os, 'fork'), 'POSIX process interruption test')
    def test_process_death_before_ledger_recovers_before_evidence_validation(self):
        self.kill_during_commit(lambda: core.promote(self.prepared), 'active')
        self.assertFalse(self.source.exists())
        self.assertEqual(core.read(self.journal), self.before)
        self.assertEqual(core.promote(self.prepared)['status'], 'active')
        self.assertEqual(core.promote(self.prepared)['status'], 'already_active')

    @unittest.skipUnless(hasattr(os, 'fork'), 'POSIX process interruption test')
    def test_process_death_after_ledger_recovers_and_does_not_double_archive(self):
        pid = os.fork()
        if pid == 0:
            with mock.patch.object(core, 'build_catalog', side_effect=lambda: os._exit(73)):
                core.promote(self.prepared)
            os._exit(74)
        _, status = os.waitpid(pid, 0)
        self.assertEqual(os.waitstatus_to_exitcode(status), 73)
        self.assertEqual(core.read(self.journal)['entries'][self.source_key]['migrationStatus'], 'active')
        self.assertEqual(core.promote(self.prepared)['status'], 'active')
        self.assertEqual(len(list((self.recycle/'sample').iterdir())), 1)

    def kill_during_commit(self, action, status):
        pid = os.fork()
        if pid == 0:
            original = core.write
            def write(path, value):
                entry = value.get('entries', {}).get(self.source_key, {})
                if Path(path) == self.journal and entry.get('migrationStatus') == status:
                    os._exit(73)
                return original(path, value)
            with mock.patch.object(core, 'write', side_effect=write):
                action()
            os._exit(74)
        _, result = os.waitpid(pid, 0)
        self.assertEqual(os.waitstatus_to_exitcode(result), 73)

    def test_discard_journal_failure_keeps_failed_original_in_place(self):
        with self.fail_commit_once('recycled'):
            with self.assertRaisesRegex(OSError, 'journal commit'):
                core.archive(self.source, 'explicitly_discarded', core.relative(self.reason))
        self.assert_rolled_back()
        self.assertFalse((self.recycle/'discarded'/self.source.name).exists())

    def test_discard_success_repeat_and_exact_duplicate_remains_blocked(self):
        reason = core.relative(self.reason)
        self.assertEqual(core.archive(self.source, 'explicitly_discarded', reason)['status'], 'recycled')
        self.assertEqual(core.archive(self.source, 'explicitly_discarded', reason)['status'], 'already_recycled')
        self.assertTrue(core.resolve_artifact(self.source_key+'/payload.json').is_file())
        with self.assertRaisesRegex(ValueError, 'reviewed_equivalence'):
            core.archive(self.legacy/'another', 'exact_duplicate', reason)

    @unittest.skipUnless(hasattr(os, 'fork'), 'POSIX process interruption test')
    def test_discard_death_recovers_even_when_reason_is_inside_original(self):
        internal = self.source/'decision.json'
        core.write(internal, {'reason': 'test internal evidence'})
        self.source_files = core._tree_files(self.source)
        reason = core.relative(internal)
        self.kill_during_commit(lambda: core.archive(self.source, 'explicitly_discarded', reason), 'recycled')
        self.assertFalse(self.source.exists())
        self.assertEqual(core.archive(self.source, 'explicitly_discarded', reason)['status'], 'recycled')
        self.assertEqual(core.archive(self.source, 'explicitly_discarded', reason)['status'], 'already_recycled')
        self.assertTrue(core.resolve_artifact(reason).is_file())

    def test_library_root_cannot_be_discarded(self):
        with self.assertRaisesRegex(ValueError, 'original_module_package'):
            core.archive(self.legacy, 'explicitly_discarded', core.relative(self.reason))
        self.assertTrue(self.source.is_dir())

    def test_changed_original_is_not_moved(self):
        (self.source/'payload.json').write_text('changed')
        with self.assertRaisesRegex(ValueError, 'source_changed'):
            core.promote(self.prepared)
        self.assertTrue(self.source.is_dir())
        self.assertFalse((self.active/'sample').exists())


if __name__ == '__main__':
    unittest.main()
