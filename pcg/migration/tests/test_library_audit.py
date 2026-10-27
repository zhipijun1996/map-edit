"""Protect semantic audit against false matches from geometry-only shortcuts."""
import copy,unittest
from pathlib import Path
from pcg.migration.library_audit import normalize,semantic_payload,platform_audit
from pcg.prototype.factory.core.quality import digest

class LibraryAuditTests(unittest.TestCase):
    def fixture(self):
        doc=dict(id='fixture',objects=[dict(id='floor',type='terrain',x=0,y=96,w=128,h=32)],generationContract=dict(kind='module',space=dict(bounds=dict(x=0,y=0,w=128,h=128),actorBody=dict(size=[24,36])),generation=dict(source=dict(physicsSourceCommit='fixed',sourceManifestSha256='fixed')),ports=[dict(id='A',position=[0,64],normal=[-1,0],permission='INOUT'),dict(id='B',position=[128,64],normal=[1,0],permission='INOUT')],routes=[dict(id='main',**{'from':'A','to':'B'},role='main',requiredAbilities=['move'])],relations=[dict(**{'from':'A','to':'B'},status='path',routeIds=['main'],conditions='UNKNOWN')]))
        cases=[dict(id='actual-fixture',platforms=[[0,96,128,32]],spawn=[20,78],entry_port=[20,78],exit_port=[108,78],goal=[100,74,16,8],capabilities=['move'],control_plan=[dict(op='settle',trigger=dict(after=0),target_x=108)],route_spec=dict(id='main'))]
        return doc,cases

    def test_translation_changes_points_but_never_directions_or_lengths(self):
        actual=normalize(dict(position=[130,40],direction=[-1,0],travel=[0,20],size=[24,36],offset=[80,-120],region=[100,20,90,40]),(100,20))
        self.assertEqual(actual['position'],[30,20]);self.assertEqual(actual['region'],[0,0,90,40])
        self.assertEqual(actual['direction'],[-1,0]);self.assertEqual(actual['travel'],[0,20]);self.assertEqual(actual['size'],[24,36]);self.assertEqual(actual['offset'],[80,-120])

    def test_whole_template_translation_preserves_audit_identity(self):
        doc,cases=self.fixture();before=digest(semantic_payload(doc,cases))
        shifted=copy.deepcopy(doc);other=copy.deepcopy(cases)
        shifted['generationContract']['space']['bounds'].update(x=128,y=-256)
        shifted['objects'][0].update(x=128,y=-160)
        shifted['generationContract']['ports'][0]['position']=[128,-192]
        shifted['generationContract']['ports'][1]['position']=[256,-192]
        other[0].update(platforms=[[128,-160,128,32]],spawn=[148,-178],entry_port=[148,-178],exit_port=[236,-178],goal=[228,-182,16,8])
        other[0]['control_plan'][0]['target_x']=236
        self.assertEqual(digest(semantic_payload(shifted,other)),before)

    def test_corner_relocation_permissions_are_part_of_interface(self):
        doc,cases=self.fixture();before=digest(semantic_payload(doc,cases))
        doc['generationContract']['ports'][0]['cornerRelocations']={'BOTTOM_LEFT':dict(allowed=True,targetFace='BOTTOM',targetPosition=[64,128])}
        self.assertNotEqual(digest(semantic_payload(doc,cases)),before)

    def test_full_matrix_contains_unknown_self_pairs(self):
        doc,cases=self.fixture();payload=semantic_payload(doc,cases)
        self.assertEqual(len(payload['relations']),4)
        self.assertEqual(sum(r['status']=='UNKNOWN'for r in payload['relations']),3)

    def test_initial_permissions_change_semantics_even_with_same_geometry(self):
        doc,cases=self.fixture();before=digest(semantic_payload(doc,cases));doc['generationContract']['ports'][0]['permission']='OUTPUT'
        self.assertNotEqual(digest(semantic_payload(doc,cases)),before)

    def test_foundry_capacity_profiles_do_not_collapse_to_one_geometry(self):
        doc,cases=self.fixture();before=digest(semantic_payload(doc,cases));cases[0]['original_tuning_profile']=dict(id='air_chain',overrides=dict(max_jumps=2,max_air_shots=4))
        self.assertNotEqual(digest(semantic_payload(doc,cases)),before)

    def test_changed_control_program_is_visible_for_review(self):
        doc,cases=self.fixture();before=digest(semantic_payload(doc,cases));cases[0]['control_plan'][0]['trigger']['after']=8
        self.assertNotEqual(digest(semantic_payload(doc,cases)),before)

    def test_native_thorn_enum_alias_has_same_meaning(self):
        self.assertEqual(normalize(dict(face=1)),normalize(dict(face='left')))

    def test_coincident_one_way_and_solid_are_not_declared_redundant(self):
        doc,cases=self.fixture();cases[0]['platforms'].append([0,96,128,32]);cases[0]['one_way_platform_indices']=[1]
        result=platform_audit(Path('.'),doc,cases)
        self.assertEqual(result['platforms'][0]['coincidentWith'],[1])
        self.assertEqual(result['platforms'][0]['sameCollisionFlagsContainedBy'],[])
        self.assertTrue(all(p['decision']=='retain'for p in result['platforms']))
        self.assertEqual(result['automaticRemovals'],0)

if __name__=='__main__':unittest.main()
