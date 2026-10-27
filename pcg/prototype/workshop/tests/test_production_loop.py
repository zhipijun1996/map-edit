import copy,json,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from pcg.prototype.workshop.production_loop import compile_request,static_preflight
from pcg.prototype.workshop.production_recipes import candidates,specification
from pcg.prototype.workshop.engine import ROOT
from pcg.prototype.workshop.library import WorkshopLibrary
from pcg.prototype.workshop.evidence import geometry_key,counter_records

class ProductionBoundaries(unittest.TestCase):
    def test_recipe_proposals_consume_existing_failure_feedback(self):
        from pcg.prototype.workshop.intake import propose
        feedback=dict(production_recipe='bell-floor-drop',flag='unneeded_mechanic')
        p=propose(dict(production_recipe='bell-floor-drop'),[feedback])[0]
        self.assertEqual(p['status'],'revision_required');self.assertEqual(p['selection_weight'],0)
    def test_unsupported_cannot_self_implement(self):
        r=compile_request(dict(recipe='unimplemented',implemented=True));self.assertEqual(r['status'],'needs_design');self.assertEqual(r['cases'],[])
    def test_no_unbounded_or_duplicate_interface_budget(self):
        for value in [[0,0],[0,1,2],[True],[3],[],None]:
            self.assertEqual(compile_request(dict(recipe='refund-turnback',interfaces=value))['status'],'unsatisfied')
    def test_resource_contract_is_hard_constraint(self):
        specs=[specification('refund-turnback',i)for i in range(2)];specs[0]['resource_state']['entry']='airborne without charges'
        self.assertEqual(compile_request(dict(recipe='refund-turnback',specifications=specs))['status'],'unsatisfied')
    def test_duplicate_reward_is_rejected_before_godot(self):
        c=candidates('refund-turnback',0)[0];c['reward_sites']*=2
        with self.assertRaisesRegex(ValueError,'duplicate_reward'):static_preflight(SimpleNamespace(out=Path('/unused')),[c])
    def test_whole_port_body_must_be_supported(self):
        c=candidates('refund-turnback',0)[0];c['exit_port'][0]=118
        with self.assertRaisesRegex(ValueError,'port_body_not_supported'):static_preflight(SimpleNamespace(out=Path('/unused')),[c])

class ActualProductionLoop(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=ROOT/'results/workshop-production-loop-v2/round-00'
        if not(cls.source/'review_cases.json').exists():raise unittest.SkipTest('restore workshop-production-loop-v1 archive')
    def test_published_exact_phase_has_counter_binding(self):
        cs=json.loads((self.source/'review_cases.json').read_text())['cases'];rs=counter_records('workshop-production-loop-v2/round-00')
        for c in cs:
            bound=[r for r in rs if r['base_id']==c['id']and r['geometry_sha256']==geometry_key(c)]
            self.assertGreaterEqual(len(bound),18);self.assertTrue(all(not r['safe_stable']for r in bound))
    def test_full_resource_demand_prevents_coarse_index_hit(self):
        s=specification('refund-turnback',0);lib=WorkshopLibrary()
        self.assertEqual(len(lib.find_single_exact(s)),1);s['resource_state']['entry']='zero air shots and no ground contact'
        self.assertEqual(lib.find_single_exact(s),[])
    def test_warm_process_uses_no_physics_or_regeneration(self):
        p=ROOT/'results/workshop-production-loop-warm-v1/summary.json'
        if not p.exists():self.skipTest('run warm production process')
        s=json.loads(p.read_text());self.assertEqual(s['physics_cases'],0);self.assertEqual(s['new_candidates'],0);self.assertEqual(len(s['unique_reused_versions']),2)
        self.assertTrue(any(r['stage']=='blocked_by_feedback'for r in s['ledger']))

if __name__=='__main__':unittest.main()
