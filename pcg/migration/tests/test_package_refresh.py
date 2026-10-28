"""Refresh transaction tests with fake certificates, never real content approval."""
import copy
import os
import shutil
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest import mock

from pcg.migration import core


class CompiledPackageRefresh(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack(); self.addCleanup(self.stack.close)
        self.root = Path(self.stack.enter_context(tempfile.TemporaryDirectory()))
        self.active = self.root/'modules'; self.recycle = self.root/'modules-recycle'
        self.state = self.root/'state'; self.legacy = self.root/'legacy'
        self.journal = self.state/'ledger.json'
        self.stack.enter_context(mock.patch.multiple(core, REPO=self.root,
            ACTIVE=self.active, RECYCLE=self.recycle, STATE=self.state,
            LEGACY=self.legacy, JOURNAL=self.journal))
        self.version = 'sha256:'+'2'*64
        self.key = core.relative(self.legacy/('1'*64))
        self.original_archive = self.recycle/'sample'/('1'*64)
        self.original_archive.mkdir(parents=True)
        (self.original_archive/'original.json').write_text('unchanged legacy bytes')
        self.current = self.active/'sample'; self.current.mkdir(parents=True)
        core.write(self.current/'module.mapnote.json', {
            'title': 'same Module', 'generationContract': {'contentVersion': self.version}})
        core.write(self.current/'migration.json', dict(moduleId='sample',
            sourcePath=self.key, sourceVersion='sha256:'+'1'*64,
            sourceFiles={'original.json': core.sha(self.original_archive/'original.json')},
            physicsReport={'path': 'fixed-original-physics', 'sha256': 'f'*64},
            humanReview='UNKNOWN', productionAdmitted=False))
        self.make_manifest(self.current, 1)
        self.old_manifest = core.sha(self.current/'godot-package.json')
        self.archive = self.recycle/'sample'/('compiled-'+self.old_manifest)
        self.ready = self.root/'ready'; shutil.copytree(self.current, self.ready)
        self.make_manifest(self.ready, 2)
        self.new_manifest = core.sha(self.ready/'godot-package.json')
        self.before = dict(entries={self.key: dict(migrationStatus='active', moduleId='sample',
            destination=core.relative(self.current), archive=core.relative(self.original_archive),
            contentVersion=self.version, humanReview='UNKNOWN')},
            relocations={self.key: core.relative(self.original_archive)})
        core.write(self.journal, self.before)
        self.old_catalog = b'{ "old": true, "modules": [] }\n'
        (self.active/'catalog.json').write_bytes(self.old_catalog)
        self.old_files = core._tree_files(self.current)
        self.stack.enter_context(mock.patch.object(core, 'validate', side_effect=self.validate))
        self.stack.enter_context(mock.patch.object(core, 'build_catalog', side_effect=self.build))

    def make_manifest(self, folder, compiler):
        core.write(folder/'compiled-content.json', {'compiler': compiler})
        core.write(folder/'godot-package.json', dict(compiler_version=compiler,
            artifacts={'compiled-content.json': core.sha(folder/'compiled-content.json')}))

    def validate(self, folder, require_certified=False):
        """Only a local hash check in this test; not a Godot certificate."""
        folder = Path(folder); manifest = core.read(folder/'godot-package.json')
        if core.sha(folder/'compiled-content.json') != manifest['artifacts']['compiled-content.json']:
            raise ValueError('fake_package_artifact_changed')
        doc = core.read(folder/'module.mapnote.json'); meta = core.read(folder/'migration.json')
        return dict(certified=True, moduleId=meta['moduleId'],
                    contentVersion=doc['generationContract']['contentVersion'])

    def build(self):
        self.validate(self.current, True)
        core.write(self.active/'catalog.json', {'manifest': core.sha(self.current/'godot-package.json')})

    def assert_original_current(self):
        self.assertEqual(core._tree_files(self.current), self.old_files)
        self.assertFalse(self.archive.exists())
        self.assertEqual(core.read(self.journal), self.before)
        self.assertEqual((self.active/'catalog.json').read_bytes(), self.old_catalog)
        self.assertEqual(core.resolve_artifact(self.key+'/original.json'), self.original_archive/'original.json')

    def test_same_content_refresh_and_repeat_add_history_once(self):
        result = core.refresh_package(self.ready)
        self.assertEqual(result['status'], 'package_refreshed')
        self.assertEqual(result['contentVersion'], self.version)
        self.assertEqual(core.sha(self.current/'godot-package.json'), self.new_manifest)
        self.assertEqual(core.sha(self.current/'module.mapnote.json'), self.old_files['module.mapnote.json'])
        core._check_tree(self.archive, self.old_files, ('archive.json',))
        state = core.read(self.journal)
        self.assertEqual(state['relocations'], self.before['relocations'])
        history = state['entries'][self.key]['packageHistory']
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['previousManifestSha256'], self.old_manifest)
        self.assertEqual(history[0]['manifestSha256'], self.new_manifest)
        self.assertEqual(core.refresh_package(self.ready)['status'], 'already_current')
        self.assertEqual(core.read(self.journal), state)
        self.assertEqual(len(list((self.recycle/'sample').glob('compiled-*'))), 1)

    def test_identical_current_manifest_needs_no_archive(self):
        identical = self.root/'identical'; shutil.copytree(self.current, identical)
        self.assertEqual(core.refresh_package(identical)['status'], 'already_current')
        self.assertFalse(self.archive.exists())
        self.assertEqual(core.read(self.journal), self.before)

    def test_different_content_version_rejected_before_move(self):
        doc = core.read(self.ready/'module.mapnote.json')
        doc['generationContract']['contentVersion'] = 'sha256:'+'3'*64
        core.write(self.ready/'module.mapnote.json', doc)
        with self.assertRaisesRegex(ValueError, 'content_version_changed'):
            core.refresh_package(self.ready)
        self.assert_original_current()

    def test_different_module_id_rejected(self):
        original = self.validate
        def wrong_id(folder, require_certified=False):
            result = original(folder, require_certified)
            if Path(folder) == self.ready:
                result['moduleId'] = 'another'
            return result
        with mock.patch.object(core, 'validate', side_effect=wrong_id):
            with self.assertRaisesRegex(ValueError, 'module_id_changed'):
                core.refresh_package(self.ready)
        self.assert_original_current()

    def test_changed_document_even_with_same_version_rejected(self):
        doc = core.read(self.ready/'module.mapnote.json'); doc['title'] = 'different bytes'
        core.write(self.ready/'module.mapnote.json', doc)
        with self.assertRaisesRegex(ValueError, 'module_document_changed'):
            core.refresh_package(self.ready)
        self.assert_original_current()

    def test_physics_proof_cannot_be_replaced_by_compiler_update(self):
        meta = core.read(self.ready/'migration.json'); meta['physicsReport']['path'] = 'different'
        core.write(self.ready/'migration.json', meta)
        with self.assertRaisesRegex(ValueError, 'metadata_changed:physicsReport'):
            core.refresh_package(self.ready)
        self.assert_original_current()

    def test_old_package_integrity_required(self):
        (self.current/'compiled-content.json').write_text('corrupt')
        corrupted = core._tree_files(self.current)
        with self.assertRaisesRegex(ValueError, 'fake_package_artifact_changed'):
            core.refresh_package(self.ready)
        self.assertEqual(core._tree_files(self.current), corrupted)
        self.assertFalse(self.archive.exists())

    def test_staging_validation_failure_preserves_old_package(self):
        original = self.validate
        def staged(folder, require_certified=False):
            if Path(folder).parent == self.state/'staging':
                raise ValueError('injected staging failure')
            return original(folder, require_certified)
        with mock.patch.object(core, 'validate', side_effect=staged):
            with self.assertRaisesRegex(ValueError, 'staging failure'):
                core.refresh_package(self.ready)
        self.assert_original_current()

    def test_journal_commit_failure_rolls_back_new_install(self):
        original = core.write; failed = False
        def write(path, value):
            nonlocal failed
            if (Path(path) == self.journal and not failed
                    and value.get('entries', {}).get(self.key, {}).get('packageHistory')):
                failed = True
                raise OSError('injected ledger failure')
            return original(path, value)
        with mock.patch.object(core, 'write', side_effect=write):
            with self.assertRaisesRegex(OSError, 'ledger failure'):
                core.refresh_package(self.ready)
        self.assert_original_current()
        self.assertEqual(core.refresh_package(self.ready)['status'], 'package_refreshed')

    def test_catalog_failure_after_write_restores_old_bytes(self):
        def build():
            self.build()
            raise OSError('injected catalog failure')
        with mock.patch.object(core, 'build_catalog', side_effect=build):
            with self.assertRaisesRegex(OSError, 'catalog failure'):
                core.refresh_package(self.ready)
        self.assert_original_current()

    @unittest.skipUnless(hasattr(os, 'fork'), 'POSIX interruption test')
    def test_process_death_after_old_archive_before_new_install_recovers(self):
        pid = os.fork()
        if pid == 0:
            original = Path.rename
            def rename(path, target):
                result = original(path, target)
                if path == self.current and Path(target) == self.archive:
                    os._exit(73)
                return result
            with mock.patch.object(Path, 'rename', rename):
                core.refresh_package(self.ready)
            os._exit(74)
        _, status = os.waitpid(pid, 0)
        self.assertEqual(os.waitstatus_to_exitcode(status), 73)
        self.assertFalse(self.current.exists())
        self.assertTrue(self.archive.exists())
        self.assertEqual(core.refresh_package(self.ready)['status'], 'package_refreshed')
        self.assertEqual(len(core.read(self.journal)['entries'][self.key]['packageHistory']), 1)
        self.assertEqual(core.refresh_package(self.ready)['status'], 'already_current')

    @unittest.skipUnless(hasattr(os, 'fork'), 'POSIX interruption test')
    def test_process_death_with_new_package_installed_recovers(self):
        pid = os.fork()
        if pid == 0:
            original = core.write
            def write(path, value):
                if (Path(path) == self.journal
                        and value.get('entries', {}).get(self.key, {}).get('packageHistory')):
                    os._exit(73)
                return original(path, value)
            with mock.patch.object(core, 'write', side_effect=write):
                core.refresh_package(self.ready)
            os._exit(74)
        _, status = os.waitpid(pid, 0)
        self.assertEqual(os.waitstatus_to_exitcode(status), 73)
        self.assertEqual(core.sha(self.current/'godot-package.json'), self.new_manifest)
        self.assertEqual(core.read(self.journal), self.before)
        self.assertEqual(core.refresh_package(self.ready)['status'], 'package_refreshed')
        self.assertEqual(len(core.read(self.journal)['entries'][self.key]['packageHistory']), 1)


if __name__ == '__main__':
    unittest.main()
