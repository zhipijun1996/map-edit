"""A restored small sample must not require unrelated large-map raw archives."""
import json
from pathlib import Path
import tempfile
import unittest
from pcg.map_directed.director import REPO
from pcg.map_directed.library import CandidateLibrary

class CatalogRestoreFilterTests(unittest.TestCase):
    def fixture(self,root):
        # Synthetic registry only; this is not a physics admission witness.
        catalog=root/'catalog';(catalog/'documents').mkdir(parents=True)
        (catalog/'documents/manifest.json').write_text(json.dumps({'modules':[{'nodeId':'foreign'}]}))
        record=root/'map-instances'/'fixture'/'record.json';record.parent.mkdir(parents=True)
        record.write_text(json.dumps(dict(technical_status='whole_map_instance_passed',production_admitted=False,
            catalog=str(catalog.relative_to(REPO)),evidence=[dict(path=str((root/'not-restored.trace').relative_to(REPO)),sha256='fixture')])))

    def test_unrelated_catalog_can_stay_unrestored(self):
        with tempfile.TemporaryDirectory(dir=REPO/'pcg/results')as raw:
            root=Path(raw);self.fixture(root)
            self.assertIsNone(CandidateLibrary(root).find_direct_instance([dict(node_id='requested')]))

    def test_matching_catalog_still_requires_its_real_evidence(self):
        with tempfile.TemporaryDirectory(dir=REPO/'pcg/results')as raw:
            root=Path(raw);self.fixture(root)
            with self.assertRaises(FileNotFoundError):
                CandidateLibrary(root).find_direct_instance([dict(node_id='foreign')])
