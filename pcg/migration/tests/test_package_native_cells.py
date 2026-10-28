"""Regression cases use persisted actual generated content, not synthetic passes."""
import copy, os, tempfile, unittest
from pathlib import Path
from pcg.migration import core, godot_package as package

class NativeCellTests(unittest.TestCase):
    def fixture(self,prefix):
        source=next(core.LEGACY.glob(prefix+'*'),None)
        if source is None:
            original=next(k for k in core.ledger()['relocations']if k.rsplit('/',1)[-1].startswith(prefix))
            source=core.resolve_artifact(original+'/module.mapnote.json').parent
        doc=core.read(source/'module.mapnote.json');cases=core.legacy_cases(source)
        return package.bind_case_behavior(doc,cases),cases

    def test_cached_sha_detects_same_size_edit_even_if_mtime_restored(self):
        with tempfile.TemporaryDirectory()as folder:
            file=Path(folder)/'runtime.gd';file.write_bytes(b'old!');stamp=file.stat();before=package.sha(file)
            file.write_bytes(b'new!');os.utime(file,ns=(stamp.st_atime_ns,stamp.st_mtime_ns))
            self.assertNotEqual(package.sha(file),before)

    def test_cached_sha_detects_atomic_file_replacement(self):
        with tempfile.TemporaryDirectory()as folder:
            file=Path(folder)/'runtime.gd';file.write_bytes(b'old!');before=package.sha(file)
            replacement=Path(folder)/'new.gd';replacement.write_bytes(b'new!');replacement.replace(file)
            self.assertNotEqual(package.sha(file),before)

    def test_all_generated_native_cell_payloads_match_objects(self):
        # Includes mounted receivers, full body thorns, original movers,
        # sentries, ordered bells and each existing sensor mechanism.
        for prefix in ('4aa99','82d2','ab5d60','a1af65','9bd1cf','747d7f','dbb99f','2c5246','3db498'):
            with self.subTest(prefix=prefix):
                doc,cases=self.fixture(prefix)
                content,audit=package.audit_cases(doc,cases)
                self.assertTrue(audit['passed'])
                self.assertGreater(len(audit['cases']),0)

    def test_binding_adds_behavior_without_modifying_source(self):
        doc,cases=self.fixture('4aa99');before=copy.deepcopy(doc)
        package.bind_case_behavior(doc,cases)
        self.assertEqual(doc,before)
        enemy=next(o for o in doc['objects']if o['type']=='enemy')
        self.assertEqual(enemy['mechanics']['runtimeParameters']['initial_idle_cooldown'],cases[0]['enemies'][0]['initial_idle_cooldown'])

    def test_one_pixel_moving_track_edit_is_rejected(self):
        doc,cases=self.fixture('82d2')
        next(o for o in doc['objects']if o['type']=='trackLine')['points'][1]['x']+=1
        with self.assertRaises(package.PackageError)as error:package.audit_cases(doc,cases)
        self.assertEqual(error.exception.code,'geometry_mismatch')

    def test_thorn_detached_from_real_host_is_rejected(self):
        doc,cases=self.fixture('ab5d60')
        next(o for o in doc['objects']if o['type']=='spike')['y']+=1
        with self.assertRaises(package.PackageError)as error:package.audit_cases(doc,cases)
        self.assertEqual(error.exception.code,'thorn_not_attached')

    def test_silently_ignored_future_behavior_is_rejected(self):
        doc,cases=self.fixture('82d2');cases=copy.deepcopy(cases)
        cases[0]['moving_platforms'][0]['control_mode']='teleport'
        with self.assertRaises(package.PackageError)as error:package.audit_cases(doc,cases)
        self.assertEqual(error.exception.code,'unsupported_native_behavior')

    def test_stale_sensor_geometry_is_rejected(self):
        doc,cases=self.fixture('dbb99f')
        sensor=next(o for o in doc['objects']if o['type']=='switch')
        sensor['mechanics']['runtimeParameters']['carrier_dock']['rect'][0]+=1
        with self.assertRaises(package.PackageError)as error:package.audit_cases(doc,cases)
        self.assertEqual(error.exception.code,'geometry_mismatch')

if __name__=='__main__':unittest.main()
