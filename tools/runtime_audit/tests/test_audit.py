import hashlib, importlib.util, json, tempfile, unittest, zipfile
from pathlib import Path
from tools.runtime_audit.check_inputs import checked_zip, dependencies
from tools.runtime_audit.geometry import (
    owned_point,
    excluded_centers,
    fully_blocked_claim_region,
)


class ReadOnlyAudit(unittest.TestCase):
    def test_actual_wind_offsets_are_distinct(self):
        self.assertEqual(owned_point([24, 282], dict(x=0, y=76)), [24, 206])
        self.assertEqual(owned_point([-104, 282], dict(x=-128, y=76)), [24, 206])
        self.assertEqual(owned_point([64, 282], dict(x=-128, y=76)), [192, 206])

    def test_actual_claim_region_has_no_collision_free_body_center(self):
        self.assertEqual(
            excluded_centers([256, 0, 128, 32], [24, 36]), [244, -18, 152, 68]
        )
        self.assertTrue(
            fully_blocked_claim_region([300, -10, 80, 56], [256, 0, 128, 32], [24, 36])
        )

    def test_noncontained_region_is_not_mislabeled_unreachable(self):
        self.assertFalse(
            fully_blocked_claim_region([400, 0, 80, 56], [256, 0, 128, 32], [24, 36])
        )

    def test_hash_is_checked_before_zip_parsing(self):
        with tempfile.TemporaryDirectory() as name:
            p = Path(name) / "invalid.zip"
            p.write_bytes(b"not a zip")
            with self.assertRaisesRegex(ValueError, "BEFORE_READING"):
                checked_zip(p, "0" * 64)

    def test_manifest_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory() as name:
            p = Path(name) / "x.zip"
            with zipfile.ZipFile(p, "w") as z:
                z.writestr(
                    "manifest.json", json.dumps({"files": {"data.json": "0" * 64}})
                )
                z.writestr("data.json", "{}")
            with self.assertRaisesRegex(ValueError, "manifest_hash_mismatch"):
                checked_zip(p, hashlib.sha256(p.read_bytes()).hexdigest())

    def test_unsafe_member_is_rejected(self):
        with tempfile.TemporaryDirectory() as name:
            p = Path(name) / "x.zip"
            with zipfile.ZipFile(p, "w") as z:
                z.writestr("../escape", "{}")
            with self.assertRaisesRegex(ValueError, "unsafe_or_duplicate"):
                checked_zip(p, hashlib.sha256(p.read_bytes()).hexdigest())

    def test_undeclared_host_resource_is_rejected(self):
        with tempfile.TemporaryDirectory() as name:
            p = Path(name) / "x.zip"
            with zipfile.ZipFile(p, "w") as z:
                for lock in ["host-lock.json", "host-lock-current-game.json"]:
                    z.writestr("runtime/" + lock, json.dumps({"files": {}}))
                z.writestr(
                    "runtime/test.gd",
                    'extends Node\nconst X=preload("res://missing.tres")',
                )
            with zipfile.ZipFile(p) as z:
                with self.assertRaisesRegex(AssertionError, "missing.tres"):
                    dependencies(z, {"files": {}})
