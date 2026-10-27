"""Reject accidental connector terrain and altered Module placements."""
import copy
import json
from pathlib import Path
import unittest
from pcg.map_directed.direct_join.audit import audit
from pcg.prototype.factory.core.quality import digest

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

    def graph_fixture(self):
        c=copy.deepcopy(self.fixture)
        c['exploration_graph']=dict(nodes=[dict(id=m['id'])for m in c['modules']],edges=[dict(id=s['id'],**{'from':s['from_module'],'to':s['to_module']})for s in c['seams']])
        c['source']=dict(graph_sha256=digest(c['exploration_graph']))
        return c

    def test_post_assembly_graph_change_is_rejected_by_the_existing_auditor(self):
        c=self.graph_fixture();c['exploration_graph']['edges'].clear()
        with self.assertRaisesRegex(ValueError,'input_graph_binding_drift'):audit(c)

    def test_existing_auditor_rejects_a_missing_node_even_with_matching_graph_hash(self):
        c=self.graph_fixture();c['exploration_graph']['nodes'].append(dict(id='unrealized'))
        c['source']['graph_sha256']=digest(c['exploration_graph'])
        with self.assertRaisesRegex(ValueError,'blueprint_placement_nodes_mismatch'):audit(c)

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
