"""Regressions for real clearance failures; these are not physics receipts."""
import copy,json,tempfile,unittest
from pathlib import Path
from pcg.map_directed.woven_region.design import load_policy,graph_for
from pcg.prototype.plains.woven_landforms import generate
from pcg.map_directed.direct_join.director import requests


class WovenRegionContracts(unittest.TestCase):
    def policy_file(self,value):
        folder=tempfile.TemporaryDirectory();self.addCleanup(folder.cleanup)
        p=Path(folder.name)/'policy.json';p.write_text(json.dumps(value));return p

    def test_unimplemented_region_language_cannot_silently_pass(self):
        p=load_policy();p['visibility_rules']={'visible_later':2}
        with self.assertRaisesRegex(ValueError,'unsupported_region_policy_fields'):load_policy(self.policy_file(p))

    def test_unavailable_ability_cannot_be_added_by_region_theme(self):
        p=load_policy();p['capabilities'].append('grapple')
        with self.assertRaisesRegex(ValueError,'unsupported_region_capabilities'):load_policy(self.policy_file(p))

    def test_floor_reserve_cannot_create_a_negative_contact_gallery(self):
        graph=dict(nodes=[dict(id=k,role='challenge',grants=[],opens=[],reward=0)for k in ['a','b']],
            edges=[dict(id='e0',**{'from':'a','to':'b'},bidirectional=True,requires=[],switch=None,cost=1)])
        layout=dict(source_graph=graph,units=[512,144],content_floor_margin=160,port_head_clearance=24,
            rooms={'a':dict(x=0,y=0,w=2,h=3),'b':dict(x=2,y=2,w=2,h=3)})
        with self.assertRaisesRegex(ValueError,'side_contact_headroom_unsatisfied'):requests(self.policy_file(layout))
        layout['content_floor_margin']=96
        _,specs,_=requests(self.policy_file(layout))
        self.assertGreaterEqual(specs[1]['ports'][0]['position'][1],24)

    def test_policy_reuses_existing_seeded_network_not_eight_slots(self):
        p=load_policy();a=graph_for('plains-weave-0',p);b=graph_for('plains-weave-0',p)
        self.assertEqual(a,b);self.assertEqual(a['initial_abilities'],p['capabilities'])
        self.assertEqual(len(a['core_nodes']),12);self.assertEqual(len(a['branches']),2)
        self.assertGreater(len(a['nodes']),8)
        for branch in a['branches']:self.assertNotEqual(branch['entry'],branch['rejoin'])

    def test_short_shaft_remainder_cannot_trap_drop_exception(self):
        spec=dict(node_id='clearance-fixture',node=dict(id='clearance-fixture',role='junction',reward=0),
            placement=[0,0],space={'core_bounds':[0,0,640,432]},floor_margin=96,boundary_policy='open',
            capabilities={'status':'defined','allOf':['move','jump','shot_recoil'],'anyOfGroups':[]},
            risk_reward={'value':0},ports=[dict(id='top',kind='vertical',normal=[0,-1],position=[190,0],column_x=128,bearing=1,aperture=[32,-80,192,160]),
                dict(id='east',kind='side',normal=[1,0],position=[640,336],aperture=[616,240,48,136])])
        m=generate(spec);c=m['case'];self.assertEqual(c['moving_platforms'],[])
        heights=sorted(c['platforms'][i][1]for i in c['one_way_platform_indices']if c['platforms'][i][0]<=128<=c['platforms'][i][0]+c['platforms'][i][2])
        # The old 36wu remainder leaves the 36wu actor intersecting a 16wu
        # platform while grounded below it. Preserve a real clearance margin.
        self.assertTrue(all(b-a>=64 for a,b in zip(heights,heights[1:])))
        self.assertEqual(m['ports']['top']['position'],[190,0])
        self.assertFalse(m['quality']['production_admitted'])
