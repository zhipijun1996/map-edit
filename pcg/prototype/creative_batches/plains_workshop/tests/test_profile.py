import copy,json,unittest
from pathlib import Path
from unittest.mock import patch
from pcg.prototype.creative_batches.plains_workshop import catalog_v1 as catalog
from pcg.prototype.creative_batches.plains_workshop.adapt_v1 import DEMANDS,specification
from pcg.prototype.creative_batches.plains_workshop.produce_v1 import compile_plains,requests_for

PROFILE=json.loads((catalog.HERE/'profile-v1.json').read_text())

class PlainsBoundaryTests(unittest.TestCase):
    def test_advanced_ability_cannot_enter_plains(self):
        for cap in ['grapple','double_jump','wall_climb']:
            spec=specification(copy.deepcopy(DEMANDS[0]));spec['capabilities']['allOf'].append(cap)
            with patch.object(catalog,'WorkshopLibrary',side_effect=AssertionError('must reject before original retrieval')):
                answer=catalog.query(spec,PROFILE)
            self.assertEqual(answer['status'],'unsatisfied');self.assertEqual(answer['new_physics_cases'],0)
            self.assertEqual(answer['conflicts'][0]['unsupported'],[cap])
    def test_partial_or_missing_capabilities_are_not_granted(self):
        for caps in [{},None,dict(status='partial',allOf=['move','jump','shot_recoil'])]:
            self.assertTrue(catalog.capability_conflicts(dict(capabilities=caps),PROFILE))
    def test_declared_additional_requirement_is_also_filtered(self):
        cases=[dict(family='thorn-slot',capabilities=['move','jump','shot_recoil'])]
        doc=dict(capabilityRequirements=dict(allOf=['grapple']),generationContract=dict(kind='module'))
        result=catalog.disposition('not-a-stored-version',cases,doc,PROFILE,{})
        self.assertFalse(result[0]);self.assertEqual(result[3],['grapple'])
    def test_compatibility_does_not_reclassify_no_shot_as_recoil_teaching(self):
        self.assertEqual(PROFILE['supporting_roles']['M07'],'threat_timing')
        self.assertEqual(PROFILE['supporting_roles']['M08'],'hazard_timing')
        self.assertNotEqual(PROFILE['supporting_roles']['M12'],'core_recoil_practice')
        self.assertEqual(PROFILE['supporting_roles']['M19'],'ordered_world_transaction')
    def test_world_and_ability_state_changes_require_new_demand(self):
        for key,value in [('return_conditions','guaranteed without rebuilding'),('rise',999),('implemented',True)]:
            spec=specification(copy.deepcopy(DEMANDS[0]));spec[key]=value;r=compile_plains(requests_for([spec])[0])
            self.assertEqual(r['status'],'unsatisfied');self.assertFalse(r['cases'])
    def test_registered_adaptation_honors_exact_geometry(self):
        for original in DEMANDS:
            d=copy.deepcopy(original)
            r=compile_plains(requests_for([specification(d)])[0]);self.assertEqual(r['status'],'requires_physics');self.assertEqual(len(r['cases']),4)
            for c in r['cases']:
                self.assertEqual(c['capabilities'],['move','jump','shot_recoil']);self.assertEqual(c['map_specification'],specification(d))
    def test_outside_domain_returns_conflicts_without_substitution(self):
        spec=specification(copy.deepcopy(DEMANDS[0]));spec['objective']['parameters']['landing_front']=1200
        r=compile_plains(requests_for([spec])[0]);self.assertEqual(r['status'],'unsatisfied');self.assertTrue(r['conflicts']);self.assertFalse(r['cases'])
    def test_unregistered_rule_cannot_be_enabled_by_flag(self):
        spec=specification(copy.deepcopy(DEMANDS[0]));spec['required_family']='my_new_module';spec['implemented']=True
        r=compile_plains(requests_for([spec])[0]);self.assertEqual(r['status'],'unsatisfied');self.assertFalse(r['cases'])

if __name__=='__main__':unittest.main()
