import json, shutil, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from module_pipeline import library as l, package


class LibraryTransactions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = Path(
            tempfile.mkdtemp(prefix="production-tests-", dir=l.ROOT / "build")
        )
        shutil.copytree(l.MODULES, cls.temp / "modules")
        cls.actual = l.MODULES
        (cls.temp / "build").mkdir()
        for name in ["tools", "runtime", "integration", "evidence"]:
            (cls.temp / name).symlink_to(l.ROOT / name, target_is_directory=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp)

    def setUp(self):
        self.override = patch.object(l, "MODULES", self.temp / "modules")
        self.root_override = patch.object(l, "ROOT", self.temp)
        self.override.start()
        self.root_override.start()

    def tearDown(self):
        self.override.stop()
        self.root_override.stop()

    def test_current_index_matches_and_retirement_is_a_tombstone(self):
        index = l.build_catalog(False)
        self.assertEqual(index, l.read(l.MODULES / "catalog.json"))
        current = {v["id"] for v in index["modules"]}
        self.assertTrue(current)
        self.assertEqual(len(current), len(index["modules"]))
        for f, r in l.records():
            if r["lifecycle"] == "withdrawn":
                self.assertEqual([p.name for p in f.iterdir()], ["record.json"])
                self.assertNotIn(r["id"], current)

    def test_failed_revision_keeps_the_entire_old_tree(self):
        mid = l.read(l.MODULES / "catalog.json")["modules"][0]["id"]
        before = {
            p.relative_to(l.MODULES).as_posix(): l.sha(p)
            for p in l.MODULES.rglob("*")
            if p.is_file()
        }
        bad = self.temp / "bad.json"
        bad.write_text('{"id":"wrong-identity"}')
        with self.assertRaises(ValueError):
            l.replace_source(mid, bad)
        after = {
            p.relative_to(l.MODULES).as_posix(): l.sha(p)
            for p in l.MODULES.rglob("*")
            if p.is_file()
        }
        self.assertEqual(before, after)

    def test_duplicate_and_missing_source_fail(self):
        original = l.read(l.MODULES / "catalog.json")["modules"][0]["id"]
        copy = l.MODULES / "duplicate-test"
        shutil.copytree(l.MODULES / original, copy)
        try:
            with self.assertRaisesRegex(ValueError, "invalid_module_record"):
                l.records()
        finally:
            shutil.rmtree(copy)
        p = l.MODULES / original / "module.mapnote.json"
        backup = p.read_bytes()
        p.unlink()
        try:
            with self.assertRaisesRegex(ValueError, "missing_or_changed_source"):
                l.build_catalog(False)
        finally:
            p.write_bytes(backup)

    def test_successful_revision_invalidates_old_evidence_atomically(self):
        mid = l.read(l.MODULES / "catalog.json")["modules"][0]["id"]
        source = self.temp / "revision.json"
        doc = l.read(l.MODULES / mid / "module.mapnote.json")
        doc["title"] += " test revision"
        doc["id"] = "editor-local-draft"
        doc["intent"]["operation"] = "modify_existing"
        doc["baselineObjects"] = doc["objects"]
        l.write(source, doc)
        l.replace_source(mid, source)
        r = l.read(l.MODULES / mid / "record.json")
        self.assertEqual(r["review"]["implementationApproval"], "needs_review")
        self.assertEqual(r["runtime"]["deliveryStatus"], "pending")
        self.assertEqual(r["qualification"]["status"], "verified_scoped")
        self.assertIn("metadataEquivalence", r["qualification"])
        self.assertTrue((l.MODULES / mid / "validation/cases.json").exists())
        self.assertEqual(
            l.read(l.MODULES / mid / "validation/origin.json")["status"],
            "input_template_requires_current_source_check",
        )
        self.assertFalse(package.eligible(r))
        # Restore the fixture so other checks see the same snapshot.
        shutil.rmtree(l.MODULES / mid)
        shutil.copytree(self.actual / mid, l.MODULES / mid)
        l.build_catalog()

    def test_editor_collision_change_cannot_be_silently_ignored(self):
        mid = l.read(l.MODULES / "catalog.json")["modules"][0]["id"]
        doc = l.read(l.MODULES / mid / "module.mapnote.json")
        obj = next(o for o in doc["objects"] if o["type"] == "terrain")
        obj["type"] = "platform"
        source = self.temp / "ignored-type.json"
        l.write(source, doc)
        with self.assertRaisesRegex(ValueError, "changed_object_field_not_bound"):
            l.replace_source(mid, source)

    def test_wrong_record_version_fails(self):
        p = (
            l.MODULES
            / l.read(l.MODULES / "catalog.json")["modules"][0]["id"]
            / "record.json"
        )
        raw = p.read_bytes()
        r = json.loads(raw)
        r["source"]["contentVersion"] = "sha256:" + "0" * 64
        l.write(p, r)
        try:
            with self.assertRaisesRegex(ValueError, "current_source_version_mismatch"):
                l.build_catalog(False)
        finally:
            p.write_bytes(raw)


class DeliveryIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = Path(
            tempfile.mkdtemp(prefix="delivery-tests-", dir=l.ROOT / "build")
        )
        cls.bundle = cls.temp / "bundle"
        package.stage(
            cls.bundle, "0.0.0-test", "9b712fe814ef228b368c0eb9adf660e39de29e37", False
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp)

    def test_archive_is_byte_reproducible(self):
        self.assertEqual(
            package.archive(self.bundle, self.temp / "a.zip"),
            package.archive(self.bundle, self.temp / "b.zip"),
        )

    def test_missing_and_mutated_files_fail(self):
        p = self.bundle / "catalog.json"
        raw = p.read_bytes()
        p.unlink()
        try:
            with self.assertRaisesRegex(ValueError, "file_set_mismatch"):
                package.verify(self.bundle)
        finally:
            p.write_bytes(raw)
        p.write_bytes(raw + b" ")
        try:
            with self.assertRaisesRegex(ValueError, "checksum_mismatch"):
                package.verify(self.bundle)
        finally:
            p.write_bytes(raw)

    def test_duplicate_delivery_id_and_undeclared_dependency_fail_even_with_new_checksums(
        self,
    ):
        catalog = self.bundle / "catalog.json"
        manifest = self.bundle / "manifest.json"
        raw = catalog.read_bytes()
        saved = manifest.read_bytes()
        data = l.read(catalog)
        data["modules"].append(data["modules"][0])
        l.write(catalog, data)
        m = l.read(manifest)
        m["files"]["catalog.json"] = l.sha(catalog)
        l.write(manifest, m)
        try:
            with self.assertRaisesRegex(ValueError, "duplicate_delivery_id"):
                package.verify(self.bundle)
        finally:
            catalog.write_bytes(raw)
            manifest.write_bytes(saved)
        script = next(
            (self.bundle / "runtime/module_runtime").glob("module_loader_v3*")
        )
        raw = script.read_bytes()
        script.write_bytes(
            raw + b'\nconst INVALID=preload("res://undeclared/missing.gd")\n'
        )
        m = l.read(manifest)
        m["files"][script.relative_to(self.bundle).as_posix()] = l.sha(script)
        l.write(manifest, m)
        try:
            with self.assertRaisesRegex(ValueError, "undeclared_host_dependency"):
                package.verify(self.bundle)
        finally:
            script.write_bytes(raw)
            manifest.write_bytes(saved)


if __name__ == "__main__":
    unittest.main()


class DesignAndWithdrawal(unittest.TestCase):
    def test_new_design_is_preserved_then_withdrawn_with_immutable_recovery(self):
        actual_root = l.ROOT
        temp = Path(tempfile.mkdtemp(prefix="lifecycle-", dir=actual_root / "build"))
        (temp / "build").mkdir()
        shutil.copytree(l.MODULES, temp / "modules")
        for name in ["tools", "runtime", "integration", "evidence"]:
            (temp / name).symlink_to(actual_root / name, target_is_directory=True)
        source = temp / "incoming.json"
        l.write(
            source, l.read(actual_root / "modules/idea-plains-large-01-001/design.json")
        )
        try:
            with patch.object(l, "ROOT", temp), patch.object(
                l, "MODULES", temp / "modules"
            ):
                mid = l.add(source, identifier="test-new-design")
                r = l.read(l.MODULES / mid / "record.json")
                self.assertEqual(r["lifecycle"], "development")
                self.assertEqual(r["runtime"]["deliveryStatus"], "not_implemented")
                self.assertTrue((l.MODULES / mid / "thumbnail.svg").is_file())
                original = (l.MODULES / mid / "design.json").read_bytes()
                saved = l.preserve_current(l.MODULES / mid)
                saved_path = temp / saved["file"]
                saved_bytes = saved_path.read_bytes()
                saved_path.write_bytes(b"corrupt archive")
                with self.assertRaisesRegex(
                    ValueError, "immutable_module_archive_corrupt"
                ):
                    l.withdraw(mid, "test must preserve current content")
                self.assertTrue((l.MODULES / mid / "design.json").exists())
                saved_path.write_bytes(saved_bytes)
                l.withdraw(mid, "test explicit withdrawal")
                r = l.read(l.MODULES / mid / "record.json")
                self.assertEqual(r["lifecycle"], "withdrawn")
                self.assertFalse((l.MODULES / mid / "design.json").exists())
                archive = temp / r["history"]["withdrawalArchive"]["file"]
                self.assertTrue(archive.exists())
                import zipfile

                with zipfile.ZipFile(archive) as z:
                    self.assertEqual(z.read("design.json"), original)
                self.assertFalse(
                    any(
                        v["id"] == mid
                        for v in l.read(l.MODULES / "catalog.json")["designs"]
                    )
                )
        finally:
            shutil.rmtree(temp)
