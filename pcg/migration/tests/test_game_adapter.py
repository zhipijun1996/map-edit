"""Original-game fidelity regressions against the actual pinned archive."""
import copy
import unittest
from pcg.migration import core, game_adapter as adapter


class OriginalGameAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=adapter.source_entries()
        cls.resources={r['id']:r for r in cls.rows if r['kind']=='resource'}

    def test_entire_finite_registry_is_accounted_for(self):
        self.assertEqual(len(self.rows),177)
        self.assertEqual(len(self.resources),72)
        self.assertEqual(sum(r['kind']=='forest'for r in self.rows),51)
        self.assertEqual(sum(r['kind']=='foundry'for r in self.rows),54)
        self.assertTrue(all(r['sourceArtifact']for r in self.rows))

    def test_all_authored_cells_preserve_exact_resource_data(self):
        for row in self.resources.values():
            original=copy.deepcopy(row['data']);case=adapter.resource_case(row)
            for key,source in [('platforms','platforms'),('hazards','danger_bounds'),
                ('thorns','surface_thorns'),('saws','saws'),('moving_platforms','ferries'),
                ('one_way_platform_indices','one_way_platform_indices')]:
                self.assertEqual(case[key],original[source],(row['id'],key))
            self.assertEqual(case['spawn'],original['entry_port']['position'])
            self.assertEqual(case['exit_port'],original['exit_port']['position'])
            self.assertEqual(row['data'],original,'decoder mutated exact source')
            self.assertNotIn('recorded_frames',case)
            self.assertNotIn('factory_evidence',case)

    def test_multiport_source_identity_not_dropped(self):
        case=adapter.resource_case(self.resources['route_junction'])
        self.assertGreaterEqual(len(case['ports']),3)
        self.assertTrue(any(p['normal']==[-1,0]for p in case['ports']))
        ids={p['id']for p in case['ports']}
        self.assertIn(case['route_spec']['from_port'],ids)
        self.assertIn(case['route_spec']['to_port'],ids)

    def test_all_nine_external_mechanisms_survive(self):
        with_latches=[adapter.resource_case(row)for row in self.resources.values()
                      if adapter.latch_config(row['id'])]
        self.assertEqual(len(with_latches),9)
        sequence=adapter.resource_case(self.resources['plains_windchime_sequence'])
        self.assertEqual(sequence['latches'][0]['sequence_offset'],[80,0])
        ferry=adapter.resource_case(self.resources['plains_bell_ferry_control'])
        self.assertEqual(ferry['latches'][0]['ferry_id'],'bell_ferry')
        self.assertTrue(ferry['route_spec']['require_bell'])

    def test_current_foundry_manifest_not_old_basis_relabel(self):
        batch=core.read(core.REPO/'library/source/game-import/resources/foundry/batch.json')
        for row in self.rows:
            if row['kind']=='foundry':self.assertEqual(row['data']['basis'],batch['basis'])

    def test_composite_has_exact_component_placements_and_phase(self):
        row=next(r for r in self.rows if r['kind']=='foundry')
        case=adapter.foundry_case(row,self.resources)
        expected=[]
        for node in row['data']['nodes']:
            dx,dy=node['offset']
            expected += [[r[0]+dx,r[1]+dy,r[2],r[3]]for r in self.resources[node['module_id']]['data']['platforms']]
        self.assertEqual(case['platforms'],expected)
        self.assertEqual(len(case['source_components']),len(row['data']['nodes']))
        self.assertEqual(case['ports'][0]['position'],case['spawn'])
        self.assertEqual(case['ports'][1]['position'],case['exit_port'])

    def test_no_fake_pass_when_mechanism_omitted(self):
        case=adapter.resource_case(self.resources['plains_windchime_sequence'])
        good_goal=dict(ok=True,hp=5,returns=[],plains=dict(events=[]))
        checked=adapter.purpose(case,good_goal)
        self.assertFalse(checked['ok'])
        self.assertIn('original_external_mechanism_not_executed',checked['reasons'])
        case['decoder_pending_behavior']=['enemy']
        self.assertIn('unbound_original_behavior',adapter.purpose(case,good_goal)['reasons'])


if __name__=='__main__':unittest.main()
