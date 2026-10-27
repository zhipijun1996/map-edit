"""Design regressions; no synthetic fixture is presented as Godot evidence."""
import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from pcg.map_directed.director import REPO,regional
from pcg.map_directed.block_grid.plan import allocate
from pcg.map_directed.block_grid.policy import load,review,branch_review,principal_routes,demands,materialization_review
from pcg.map_directed.content_domains.region_holdout import run as holdout
from pcg.prototype.factory.core.quality import digest


def planned(kinds=None):
    g=regional.construct('block-region-eval-0/design-0','plains',20,reward_expeditions=6,
        reward_return_modes=kinds or ['foldback','loop_back','merge']*2,core_edge_factor=1.05,
        approach_steps=(7,14),reuse_perimeter_anchors=True)
    allocate(g,'requirements-regression')
    return g


def old_region():
    return json.loads((REPO/'generation/maps/content-domains-region-v1/correspondence.json').read_text())['graph']


def identity_fixture(g):
    return dict(exploration_graph=copy.deepcopy(g),modules=[dict(id=n['id'],ports={e['id']:{}for e in g['edges']if n['id']in [e['from'],e['to']]})for n in g['nodes']],seams=[dict(id=e['id'])for e in g['edges']])


class MapDesignAcceptance(unittest.TestCase):
    def test_actual_regional_planner_meets_structural_targets_without_claiming_playability(self):
        r=review(planned(),load())
        self.assertTrue(r['ok'],r['errors'])
        self.assertEqual(set(r['actual_return_kinds']),{'foldback','loop_back','merge'})
        self.assertFalse(r['declared_requirements_satisfied'])
        self.assertIn('whole_map_physics_not_verified',r['unknown'])
        self.assertIn('actual_boss_encounter_missing',r['unknown'])

    def test_six_individually_legal_foldbacks_cannot_replace_three_required_kinds(self):
        g=planned(['foldback']*6)
        self.assertTrue(all(not branch_review(g,b)for b in g['branches']))
        r=review(g,load())
        self.assertIn('required_return_kind_missing/loop_back',r['errors'])
        self.assertIn('required_return_kind_missing/merge',r['errors'])

    def test_branch_label_cannot_disguise_wrong_return_destination(self):
        g=planned();b=next(b for b in g['branches']if b['kind']=='merge');b['kind']='foldback'
        self.assertIn('foldback_must_return_to_entry',branch_review(g,b))

    def test_merge_into_another_optional_branch_is_not_a_main_route_merge(self):
        g=planned();b=next(b for b in g['branches']if b['kind']=='merge');b['rejoin']=g['branches'][0]['nodes'][0]
        regional.base.add_edge(g,b['reward'],b['rejoin'],purpose='reward_merge')
        self.assertIn(b['id']+'/merge_not_on_main_network',review(g,load())['errors'])

    def test_one_way_return_cannot_have_a_direct_reverse_bypass(self):
        g=planned();b=next(b for b in g['branches']if b['kind']=='loop_back')
        regional.base.add_edge(g,b['entry'],b['reward'],purpose='accidental_bypass',bidirectional=False)
        self.assertIn('loop_return_has_reverse_bypass',branch_review(g,b))

    def test_loop_back_and_merge_can_use_a_real_multi_module_return_path(self):
        for kind in ['loop_back','merge']:
            g=planned();b=next(b for b in g['branches']if b['kind']==kind);end=b['rejoin'];key='return-corridor'
            g['edges']=[e for e in g['edges']if not(e['from']==b['reward']and e['to']==end)]
            g['nodes'].append(dict(id=key,role='challenge',grants=[],opens=[],reward=0,risk=2))
            b['return_nodes']=[key]
            regional.base.add_edge(g,b['reward'],key,purpose='reward_return',bidirectional=False)
            regional.base.add_edge(g,key,end,purpose='reward_return',bidirectional=True)
            self.assertEqual(branch_review(g,b),[],kind)
            request=next(r for r in demands(g,load())if r['objective']['node']==key)
            self.assertIn(b['id'],request['route_membership']['branches'])
            self.assertIn(b,request['return_conditions']['branches'])

    def test_native_declared_routes_are_validated_without_reclassifying_their_edges(self):
        g=planned();g['principal_routes']=principal_routes(g)
        for e in g['edges']:
            if e['purpose']=='regional_route':e['purpose']='main_route'
        r=review(g,load())
        self.assertTrue(r['ok'],r['errors'])

    def test_duplicate_and_disconnected_main_route_claims_are_rejected(self):
        g=planned();route=principal_routes(g)[0];g['principal_routes']=[copy.deepcopy(route),copy.deepcopy(route)]
        self.assertIn('duplicate_principal_route',review(g,load())['errors'])
        g['principal_routes'][1]['nodes']=[g['entry'],g['goal']]
        self.assertIn('principal_route_directed_edge_missing',review(g,load())['errors'])

    def test_optional_challenge_cannot_be_claimed_as_required_main_route(self):
        g=planned();g['principal_routes']=principal_routes(g);g['principal_routes'][0]['nodes'].insert(1,g['branches'][0]['reward'])
        self.assertIn('principal_route_enters_optional_branch',review(g,load())['errors'])

    def test_module_demands_bind_the_actual_graph_and_preserve_boss_and_branch_responsibilities(self):
        g=planned();p=load();rows=demands(g,p)
        self.assertTrue(all(r['exploration_sha256']==digest(g)and r['policy_sha256']==digest(p)for r in rows))
        boss=next(r for r in rows if r['objective']['node']==g['goal'])
        self.assertEqual(boss['objective']['roles'],['boss'])
        for b in g['branches']:
            r=next(r for r in rows if r['objective']['node']==b['reward'])
            self.assertIn(b['id'],r['route_membership']['branches'])
            self.assertIn(b,r['return_conditions']['branches'])

    def test_materialization_cannot_drop_nodes_edges_or_ordered_port_interfaces(self):
        g=planned();c=identity_fixture(g)
        self.assertTrue(materialization_review(g,c)['ok'])
        c['modules'].pop();c['seams'].pop();c['modules'][0]['ports'].clear()
        errors=materialization_review(g,c)['errors']
        self.assertIn('blueprint_placement_nodes_mismatch',errors)
        self.assertIn('blueprint_seams_mismatch',errors)
        self.assertTrue(any(e.startswith('blueprint_edge_port_missing/')for e in errors))

    def test_changing_the_graph_to_make_assembly_easier_is_rejected(self):
        g=planned();c=identity_fixture(g);c['exploration_graph']['edges'].pop()
        self.assertIn('exploration_graph_changed_during_materialization',materialization_review(g,c)['errors'])

    def test_previous_43_node_map_stays_rejected_even_when_physics_is_all_passed(self):
        r=review(old_region(),load(),physical={'all_passed':True})
        self.assertFalse(r['ok']);self.assertFalse(r['declared_requirements_satisfied'])
        self.assertIn('required_return_kind_missing/loop_back',r['errors'])
        self.assertIn('required_return_kind_missing/merge',r['errors'])
        self.assertIn('main_route_length_outside_target',r['errors'])
        self.assertIn('reward_branches_outside_target',r['errors'])

    def test_physics_entry_rejects_the_old_map_before_starting_godot(self):
        with tempfile.TemporaryDirectory()as tmp:
            root=Path(tmp);parent=root/'source';parent.mkdir()
            (root/'pcg/results').mkdir(parents=True)
            (parent/'summary.json').write_text(json.dumps(dict(all_passed=True)))
            (parent/'compiled.json').write_text(json.dumps(dict(exploration_graph=old_region())))
            with patch('pcg.map_directed.content_domains.region_holdout.REPO',root),patch('pcg.map_directed.content_domains.region_holdout.ContentEngine')as engine:
                out=holdout('rejected','source')
            engine.assert_not_called()
            summary=json.loads((out/'summary.json').read_text())
            self.assertEqual(summary['status'],'design_rejected')
            self.assertEqual(summary['physics'],'NOT_RUN')
            self.assertFalse(summary['regional_requirements_satisfied'])


if __name__=='__main__':unittest.main()
