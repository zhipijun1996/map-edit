import copy
import json
from pathlib import Path
import tempfile
import unittest

from pcg.map_directed.director import design,challenge_specs,inspect_library,REPO
from pcg.map_directed.composition import assemble
from pcg.map_directed.library import CandidateLibrary,fits,verify_case_binding
from pcg.prototype.factory.core.quality import module_hash
from pcg.map_directed.fill import _spec_errors


class MapDirectedContracts(unittest.TestCase):
    def test_region_cycle_uses_existing_algorithm_and_reachable_reward(self):
        plan=design('map-growth-01')
        self.assertEqual(plan['source_algorithm'],'map-notes/region-network-v2')
        self.assertEqual(len(set(plan['source_cycle'])),4)
        self.assertTrue(plan['logic_validation']['ok'])
        g=plan['exploration_graph']
        self.assertTrue(any(e['from']=='reward'and e['to']=='entry'for e in g['edges']))
        self.assertFalse(any(e['from']=='exit'or e['bidirectional']for e in g['edges']))

    def test_current_library_is_scoped_and_cannot_satisfy_demanded_rise(self):
        fork,ascent=challenge_specs(design())
        a=inspect_library(fork);b=inspect_library(ascent)
        self.assertEqual(len(a['matches']),2)
        self.assertTrue(all(not m['productionInterfaceEligible']for m in a['matches']))
        self.assertEqual(b['matches'],[])

    def test_bad_spec_is_rejected_before_physics(self):
        spec=challenge_specs(design())[1]
        self.assertEqual(_spec_errors(spec),[])
        spec['capabilities']['allOf'].append('grapple')
        self.assertTrue(_spec_errors(spec))
        spec=challenge_specs(design())[1];spec['space']['max_width']=float('inf')
        self.assertTrue(_spec_errors(spec))

    def test_recorded_success_cannot_auto_promote(self):
        record={'technical_status':'passed_scoped','human_reviews':[]}
        self.assertIn('human_quality_review_missing',CandidateLibrary.promotion_reasons(record,True))
        self.assertIn('canonical_assembly_interface_not_admitted',CandidateLibrary.promotion_reasons(record,False))

    def test_mutated_candidate_bytes_are_rejected(self):
        with tempfile.TemporaryDirectory(dir=REPO/'pcg/results')as t:
            p=Path(t)/'candidates/a';p.mkdir(parents=True)
            (p/'record.json').write_text(json.dumps({'technical_status':'passed_scoped','production_admitted':False,
                'case_sha256':'0'*64,'document_sha256':'0'*64}))
            (p/'case.json').write_text('{}');(p/'module.mapnote.json').write_text('{}')
            with self.assertRaisesRegex(ValueError,'content_drift'):CandidateLibrary(t).find(challenge_specs(design())[1])

    def test_unsupported_objects_are_not_silently_translated(self):
        fake={'family':'plains_three_port_fork','hooks':[{'x':1,'y':2}]}
        with self.assertRaisesRegex(ValueError,'unsupported_component_geometry'):assemble(design(),{'main':fake},fake)

    def test_different_fork_geometries_cannot_be_combined_as_one_module(self):
        a={'platforms':[[0,0,100,20]],'capabilities':['move','jump','shot_recoil']}
        b=copy.deepcopy(a);b['platforms'][0][2]=200
        with self.assertRaisesRegex(ValueError,'share_one_geometry'):assemble(design(),{'main':a,'upper':b},a)

    def test_known_geometry_does_not_ignore_width_or_height(self):
        spec=challenge_specs(design())[1]
        c={'family':'bell_lift','platforms':[[0,0,1600,510]],'entry_port':[80,420],
            'exit_port':[400,320],'capabilities':['move','jump','shot_recoil']}
        self.assertFalse(fits(c,spec))
        spec['space']['max_width']=2000
        self.assertTrue(fits(c,spec))
        spec['space']['max_height']=400
        self.assertFalse(fits(c,spec))

    def test_valid_document_cannot_authorize_another_raw_geometry(self):
        c={'id':'actual-case','factory_id':'actual-id','platforms':[[0,0,100,20]]}
        c['module_sha256']=module_hash(c)
        doc={'id':'generated-actual-id','generationContract':{'generation':{'source':{
            'moduleSha256':c['module_sha256'],'sourceCaseId':c['id']}}}}
        verify_case_binding(c,doc)
        c['platforms'][0][2]=1000;c['module_sha256']=module_hash(c)
        with self.assertRaisesRegex(ValueError,'canonical_physics_source'):verify_case_binding(c,doc)

    def test_reverse_demand_is_not_silently_satisfied_by_forward_witness(self):
        spec=challenge_specs(design())[1]
        spec['relations'].append({'from':'exit','to':'entry','role':'return'})
        self.assertTrue(any(x['condition']=='relations'for x in _spec_errors(spec)))


if __name__=='__main__':unittest.main()
