import copy,json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from regions import ROOT,RegionSpecError,RegionTransformError,prepare_regions,validate_region_spec,filter_families,transform_candidate,check_candidate

CAPS=['move','jump','double_jump','wall_climb','grapple','shot_recoil']
PROFILE=ROOT/'regions/sky_islands.research.json'

def fixture():
    case=dict(id='wall-chain',family='thorn_wall',capabilities=CAPS[:],spawn=[80,420],goal=[-176,96,112,48],platforms=[[-120,438,260,60],[195,-700,32,1300],[-200,138,160,72],[-500,700,1400,48]],wall_platform_indices=[1.0],one_way_platform_indices=[2.0],hooks=[],saws=[],moving_platforms=[],hazards=[],word=['wall_contact','wall_jump','air_jump','wall_separate','wall_contact','wall_jump','air_jump'],thorns=[dict(surface_id='old-wall',platform_index=1,face='left',start_offset=100,length=40,depth=8),dict(surface_id='pressure_floor',platform_index=3,face='top',start_offset=0,length=1400,depth=20)])
    frames=[dict(frame=i,x=182.925,y=y,traversal_state='wall_attach',accepted=[]) for i,y in enumerate((400,220,40,-140))]
    return case,frames

class Regions(unittest.TestCase):
    def setUp(self):self.spec=prepare_regions(PROFILE,CAPS)
    def test_proposed_mushroom_is_inspectable_but_cannot_run(self):
        path=ROOT/'regions/mushroom_caverns.proposed.json'
        with self.assertRaisesRegex(RegionSpecError,'runtime_region_rejected.*bounce_mushroom'):prepare_regions(path,CAPS)
        draft=prepare_regions(path,CAPS,runtime=False)
        self.assertFalse(draft['runtime_eligible']);self.assertIn('spore_current',draft['unimplemented_mechanisms'])
        with self.assertRaises(RegionSpecError):transform_candidate(*fixture(),draft)
    def test_unimplemented_mechanism_cannot_be_relabelled_research(self):
        raw=json.loads(PROFILE.read_text());raw['mechanisms']['allowed'].append('bounce_mushroom')
        with self.assertRaisesRegex(RegionSpecError,'unimplemented_mechanisms'):validate_region_spec(raw,CAPS)
    def test_missing_available_capability_is_never_granted(self):
        with self.assertRaisesRegex(RegionSpecError,'missing_available'):prepare_regions(PROFILE,['move'])
        case,_=fixture();case['capabilities']=['move','jump'];codes={v['code'] for v in check_candidate(case,self.spec)}
        self.assertIn('action_uses_undeclared_capability',codes)
    def test_unused_available_abilities_are_not_required_in_each_challenge(self):
        case,frames=fixture();case['capabilities']=['move','jump','double_jump','wall_climb']
        transformed=transform_candidate(case,frames,self.spec)
        self.assertEqual(check_candidate(transformed,self.spec),[])
        self.assertNotIn('grapple',transformed['region_profile']['declared_challenge_used_subset'])
        self.assertIn('grapple',transformed['region_profile']['available_capabilities'])
        self.assertEqual(case['capabilities'],transformed['capabilities'])
    def test_long_wall_and_pressure_floor_really_change_geometry(self):
        case,frames=fixture();original=copy.deepcopy(case);out=transform_candidate(case,frames,self.spec)
        self.assertEqual(case,original);self.assertEqual(check_candidate(out,self.spec),[])
        self.assertEqual(len(out['wall_platform_indices']),4)
        self.assertTrue(all(out['platforms'][i][3]<=160 for i in out['wall_platform_indices']))
        self.assertFalse(out['thorns']);self.assertFalse(any(p[2]==1400 for p in out['platforms']))
        self.assertEqual(out['one_way_platform_indices'],[5]);self.assertEqual(out['region_profile']['old_to_new_platform_indices']['3'],[])
        self.assertFalse(out['region_profile']['formal_region_approval']);self.assertEqual(out['region_profile']['validation_status'],'requires_real_physics_revalidation')
    def test_same_colour_or_profile_name_does_not_validate_long_wall(self):
        case,_=fixture();case['region']='sky_islands';case['colour']='blue'
        self.assertIn('contiguous_wall_too_tall',{v['code'] for v in check_candidate(case,self.spec)})
    def test_touching_short_rectangles_cannot_disguise_a_tall_wall(self):
        case,_=fixture();case['platforms']=[case['platforms'][0],[195,0,32,100],[195,100,32,100],case['platforms'][2]];case['wall_platform_indices']=[1,2];case['thorns']=[];case['one_way_platform_indices']=[3]
        self.assertIn('contiguous_wall_too_tall',{v['code'] for v in check_candidate(case,self.spec)})
    def test_fake_port_label_does_not_exempt_a_large_non_support(self):
        case,frames=fixture();out=transform_candidate(case,frames,self.spec)
        out['platforms'].append([500,-500,300,50]);out['entry_port']=[600,-518]
        self.assertIn('rock_width_out_of_range',{v['code'] for v in check_candidate(out,self.spec)})
    def test_upward_profile_rejects_level_or_descending_goal(self):
        case,frames=fixture();out=transform_candidate(case,frames,self.spec);out['goal'][1]=500
        codes={v['code'] for v in check_candidate(out,self.spec)}
        self.assertIn('insufficient_goal_rise',codes);self.assertIn('region_requires_upward_route',codes)
    def test_forbidden_objects_and_fake_mushroom_names_are_rejected(self):
        case,frames=fixture();out=transform_candidate(case,frames,self.spec)
        out['saws']=[dict(source_id='gear')]
        self.assertIn('region_forbidden_mechanism',{v['code'] for v in check_candidate(out,self.spec)})
        out['saws']=[];out['mechanisms']=['bounce_mushroom']
        self.assertIn('claimed_mechanism_has_no_consumer',{v['code'] for v in check_candidate(out,self.spec)})
        out['bounce_mushrooms']=[dict(name='reskinned_anchor')]
        self.assertIn('unimplemented_candidate_mechanism',{v['code'] for v in check_candidate(out,self.spec)})
    def test_contact_bands_that_cannot_fit_are_rejected_not_cut_through(self):
        case,frames=fixture();frames=[dict(frame=i,x=182.925,y=y,traversal_state='wall_attach',accepted=[]) for i,y in enumerate(range(0,201,20))]
        with self.assertRaisesRegex(RegionTransformError,'contact_band_exceeds'):transform_candidate(case,frames,self.spec)
    def test_unobserved_long_wall_is_not_invented_as_rocks(self):
        with self.assertRaisesRegex(RegionTransformError,'no_reference_wall_contacts'):transform_candidate(fixture()[0],[],self.spec)
    def test_profile_identity_excludes_available_inventory_but_detects_mutation(self):
        other=prepare_regions(PROFILE,['move','jump']);self.assertEqual(other['profile_sha256'],self.spec['profile_sha256'])
        changed=copy.deepcopy(self.spec);changed['geometry']['min_goal_rise']=1
        with self.assertRaisesRegex(RegionSpecError,'mutated'):filter_families(changed)
    def test_family_filter_is_explicit_not_a_capability_grant(self):
        self.assertEqual(filter_families(self.spec,['carrier_double','thorn_wall','sky_ascent']),['thorn_wall','sky_ascent'])
        self.assertEqual(filter_families(self.spec,['unknown_family']),[])
    def test_known_flight_pressure_host_is_removed_and_indices_remapped(self):
        case,frames=fixture();case['platforms'].insert(2,[500,500,40,24]);case['one_way_platform_indices']=[3]
        case['thorns'][1]['platform_index']=4
        case['thorns'].append(dict(surface_id='flight_pressure_1',platform_index=2,face='top',start_offset=0,length=40,depth=20))
        out=transform_candidate(case,frames,self.spec)
        self.assertEqual(check_candidate(out,self.spec),[]);self.assertEqual(out['one_way_platform_indices'],[5])
        self.assertEqual(out['region_profile']['old_to_new_platform_indices']['2'],[])
        self.assertIn('remove_forbidden_generated_pressure_cell',[x['operation'] for x in out['region_profile']['transformations']])
    def test_unknown_pressure_names_are_not_removed(self):
        case,frames=fixture();case['platforms'].append([500,500,40,24])
        case['thorns'].append(dict(surface_id='pressure_unknown',platform_index=4,face='top',start_offset=0,length=40,depth=20))
        out=transform_candidate(case,frames,self.spec)
        self.assertTrue(out['thorns']);self.assertIn('region_forbidden_mechanism',{v['code'] for v in check_candidate(out,self.spec)})
    def test_pressure_cell_shared_role_or_unknown_signature_rejected(self):
        for mode in ('wall','one_way','shared_thorn','dimensions','port','observed_support'):
            with self.subTest(mode=mode):
                case,frames=fixture();case['platforms'].append([500,500,40,24])
                case['thorns'].append(dict(surface_id='flight_pressure_1',platform_index=4,face='top',start_offset=0,length=40,depth=20))
                if mode=='wall':case['wall_platform_indices'].append(4)
                if mode=='one_way':case['one_way_platform_indices'].append(4)
                if mode=='shared_thorn':case['thorns'].append(dict(surface_id='unknown',platform_index=4))
                if mode=='dimensions':case['platforms'][4][2]=48
                if mode=='port':case['spawn']=[520,482]
                if mode=='observed_support':frames.append(dict(x=520,y=482,grounded=True))
                with self.assertRaises(RegionTransformError):transform_candidate(case,frames,self.spec)
    def test_pressure_cell_removal_is_explicitly_opt_in(self):
        raw=json.loads(PROFILE.read_text());raw['transform']['remove_forbidden_pressure_cells']=False
        spec=validate_region_spec(raw,CAPS);case,frames=fixture();case['platforms'].append([500,500,40,24])
        case['thorns'].append(dict(surface_id='flight_pressure_1',platform_index=4,face='top',start_offset=0,length=40,depth=20))
        out=transform_candidate(case,frames,spec)
        self.assertTrue(out['thorns']);self.assertIn('region_forbidden_mechanism',{v['code'] for v in check_candidate(out,spec)})
    def test_any_direction_without_minimum_allows_descending_goal(self):
        raw=json.loads(PROFILE.read_text());raw['geometry'].pop('min_goal_rise');raw['geometry']['direction']='any'
        spec=validate_region_spec(raw,CAPS);case,frames=fixture();out=transform_candidate(case,frames,spec);out['goal'][1]=500
        self.assertNotIn('insufficient_goal_rise',{v['code'] for v in check_candidate(out,spec)})
    def test_horizontal_direction_requires_horizontal_displacement_to_dominate(self):
        raw=json.loads(PROFILE.read_text());raw['geometry'].pop('min_goal_rise');raw['geometry']['direction']='horizontal'
        spec=validate_region_spec(raw,CAPS);case,frames=fixture();out=transform_candidate(case,frames,spec)
        self.assertIn('region_requires_horizontal_route',{v['code'] for v in check_candidate(out,spec)})

if __name__=='__main__':unittest.main()
