"""Demand integrity tests; no synthetic test is labeled a physics witness."""
import copy
import unittest
from pcg.map_directed.ecosystem.run import design,generate
from pcg.map_directed.ecosystem.ideas import RULES,demand_key

class EcosystemContracts(unittest.TestCase):
    def setUp(self):
        _,self.specs,_,_,_=design('unit-only',1.2)
        self.spec=copy.deepcopy(self.specs[0])
        self.source={'id':self.spec['node_id'],'spec':copy.deepcopy(self.spec),
            'case':{'capabilities':['move','jump','shot_recoil'],'reward_sites':[]}}

    def test_label_changes_do_not_hide_a_library_hit(self):
        other=copy.deepcopy(self.spec);other['id']='another-demand';other['node']['label']='Presentation only'
        self.assertEqual(demand_key(self.spec),demand_key(other))

    def test_direction_capability_and_resource_changes_invalidate_match(self):
        for field in ['ports','capabilities','design_contract']:
            other=copy.deepcopy(self.spec)
            if field=='ports':other[field][0]['normal']=[0,-1]
            elif field=='capabilities':other[field]['allOf'].remove('shot_recoil')
            else:other[field]['resource_policy']='teleport or refill at seam'
            self.assertNotEqual(demand_key(self.spec),demand_key(other))

    def test_a_proposal_cannot_claim_its_own_producer_is_implemented(self):
        idea=copy.deepcopy(next(r for r in RULES if r['id']=='thorn-slot'));idea['implemented']=True
        self.spec['design_contract']['relationships']=[idea]
        self.assertEqual(generate(self.spec,self.source)['conditions'][0]['reason'],'producer_not_implemented')

    def test_real_but_wrong_relationship_cannot_be_substituted(self):
        self.spec['design_contract']['relationships']=[copy.deepcopy(next(r for r in RULES if r['id']=='timed-cache'))]
        self.assertEqual(generate(self.spec,self.source)['conditions'][0]['reason'],'producer_cannot_realize_requested_relationship_in_this_shape')

    def test_unknown_ability_expression_fails_closed(self):
        self.spec['capabilities']['anyOfGroups']=[['grapple','double_jump']]
        self.assertEqual(generate(self.spec,self.source)['conditions'][0]['reason'],'unknown_or_disjunctive_state_not_supported')

    def test_reward_requirement_is_not_a_prose_label(self):
        self.spec['risk_reward']['value']=100
        self.assertEqual(generate(self.spec,self.source)['conditions'][0]['reason'],'reward_value_requires_explicit_content_revision')

    def test_geometric_request_cannot_silently_keep_old_ports(self):
        self.spec['ports'][0]['normal']=[0,1]
        self.assertEqual(generate(self.spec,self.source)['conditions'][0]['reason'],'bootstrap_adapter_geometry_domain_exceeded')

if __name__=='__main__':unittest.main()
