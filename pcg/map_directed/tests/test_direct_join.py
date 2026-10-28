"""Reject accidental connector terrain and altered Module placements."""
import copy
import json
from pathlib import Path
import unittest
from pcg.map_directed.direct_join.audit import audit

ROOT=Path(__file__).resolve().parents[3]

class DirectContactGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture=json.loads((ROOT/'pcg/map_directed/direct_join/guard-fixture.json').read_text())

    def test_original_module_objects_are_accounted_for(self):
        self.assertTrue(audit(self.fixture)['all_instance_geometry_exact'])

    def test_added_short_platform_is_rejected(self):
        changed=copy.deepcopy(self.fixture)
        changed['case']['platforms'].append([50,50,32,8])
        with self.assertRaisesRegex(ValueError,'orphan_map_platform'):audit(changed)

    def test_one_unit_seam_gap_is_rejected(self):
        changed=copy.deepcopy(self.fixture)
        changed['modules'][1]['spec']['placement'][0]+=1
        # Preserve source/object agreement so that the seam guard is exercised.
        for rect,owners in zip(changed['case']['platforms'],changed['object_provenance']):
            if owners[0]['module']=='b':rect[0]+=1
        with self.assertRaisesRegex(ValueError,'module_ports_are_not_flush'):audit(changed)

    def test_module_geometry_cannot_be_stretched_to_bridge_a_gap(self):
        changed=copy.deepcopy(self.fixture)
        changed['case']['platforms'][0][2]+=1
        with self.assertRaisesRegex(ValueError,'map_changed_module_geometry'):audit(changed)

    def test_dynamic_hazard_cannot_sweep_into_neighbor(self):
        changed=copy.deepcopy(self.fixture)
        changed['modules'][0]['case']['saws']=[dict(origin=[96,50],travel=[8,0],radius=8)]
        with self.assertRaisesRegex(ValueError,'module_saw_sweeps_into_neighbor'):audit(changed)
