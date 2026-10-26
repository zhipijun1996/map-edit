"""Topology intent and design rejection, separate from actual Godot witnesses."""
import copy,unittest
from pcg.map_directed.graph_landforms.graph import create
from pcg.map_directed.graph_landforms.quality import screen
from pcg.map_directed.director import regional
from pcg.prototype.plains.graph_landforms import fork,ascent,descent,switchback,merge

class SameGraph(unittest.TestCase):
    def test_mission_has_two_distinct_approaches_real_merge_and_return(self):
        g=create('contract');self.assertEqual(regional.base.validate_graph(g)[0],[])
        upper,lower=[r['nodes']for r in g['principal_routes']]
        self.assertEqual(set(upper)&set(lower),{'start','landmark'})
        arc=regional.base.expand_arcs(g)
        self.assertTrue(any(n=='cache'for n,_ in arc['cliff']))
        self.assertTrue(any(n=='cliff'for n,_ in arc['cache']))
        self.assertFalse(any('placement'in n or'ideal'in n for n in g['nodes']))

    def test_actual_recipe_ports_include_different_elevations_and_no_unused_hub_ports(self):
        f=fork();d=descent();u=ascent();h=switchback();m=merge()
        self.assertEqual(len(f['ports']),2);self.assertEqual(len(d['ports']),3);self.assertEqual(len(m['ports']),2)
        self.assertEqual(u['ports']['out']['position'][1]-u['ports']['in']['position'][1],-256)
        self.assertEqual(h['ports']['out']['position'][1]-h['ports']['in']['position'][1],-512)
        self.assertNotEqual(f['case']['platforms'],m['case']['platforms'])

    def test_missing_blueprint_node_cannot_pass_design_review(self):
        self.assertEqual(screen(create('missing'),[])['errors'],['blueprint_node_mismatch'])

if __name__=='__main__':unittest.main()
