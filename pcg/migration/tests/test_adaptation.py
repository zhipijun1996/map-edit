import copy
import unittest
from pcg.migration.adaptation import adapt


def fixture(top2=300, top_port=False):
    rects = [[0,200,160,80],[400,top2,120,40]]
    objects = [dict(id=f'p{i}',type='terrain',x=x,y=y,w=w,h=h,rotation=0)
               for i,(x,y,w,h) in enumerate(rects)]
    objects += [dict(id='entry',type='entry',x=8,y=164,w=24,h=36),
                dict(id='exit',type='exit',x=448,y=top2-36,w=24,h=36),
                dict(id='reward',type='reward',x=442,y=top2-36,w=36,h=36,
                     mechanics=dict(source=dict(id='cache',position=[460,top2-18],region=[440,top2-22,40,8],amount=3)))]
    ports=[dict(id='A',position=[20,182],normal=[-1,0],objectId='entry',support=dict(objectId='p0')),
           dict(id='B',position=[460,top2-18],normal=[0,-1]if top_port else[1,0],objectId='exit',support=dict(objectId='p1'))]
    doc=dict(id='example',objects=objects,generationContract=dict(kind='module',ports=ports,
        composition=dict(cells=[],components=[]),space=dict(bounds=dict(x=-100,y=0,w=800,h=600),
        actionClearance=dict(regions=[]),occupancy=dict(objectIds=[o['id']for o in objects if o['type']=='terrain'],regions=[]),dynamicEnvelopes=[],seams=[])))
    case=dict(id='original',platforms=copy.deepcopy(rects),spawn=[20,182],entry_port=[20,182],exit_port=[460,top2-18],
        goal=[451,top2-23,18,10],ports=[dict(id='A',support_index=0),dict(id='B',support_index=1)],
        reward_sites=[dict(id='cache',position=[460,top2-18],region=[440,top2-22,40,8],amount=3)],
        one_way_platform_indices=[],thorns=[],control_plan=[dict(op='shoot',direction=[-.8,.6]),dict(op='settle',target_x=460)],recorded_frames=[{'x':1,'y':2}])
    return doc,[case]


class AdaptationTests(unittest.TestCase):
    def test_real_shores_reach_exact_boundary_without_mutating_source(self):
        source,cases=fixture(); before=copy.deepcopy((source,cases))
        doc,new,receipt=adapt(source,cases)
        self.assertEqual((source,cases),before)
        b=doc['generationContract']['space']['bounds']
        self.assertEqual(b['w']%128,0);self.assertEqual(b['h']%128,0)
        for port in doc['generationContract']['ports']:
            index=next(p['support_index']for p in new[0]['ports']if p['id']==port['id'])
            shore=new[0]['platforms'][index];x,y=port['position']
            self.assertAlmostEqual((y-b['y'])%128,64)
            self.assertAlmostEqual(shore[1]-y,32)
            self.assertEqual(x,b['x']if port['normal'][0]<0 else b['x']+b['w'])
            self.assertEqual(shore[0]if port['normal'][0]<0 else shore[0]+shore[2],x)
        self.assertEqual(receipt['status'],'adapted_unverified')
        self.assertNotIn('recorded_frames',new[0])
        self.assertEqual(new[0]['control_plan'][0]['direction'],[-.8,.6])

    def test_docked_reward_and_goal_follow_changed_floor(self):
        source,cases=fixture(300);doc,new,receipt=adapt(source,cases)
        delta=new[0]['platforms'][1][1]-cases[0]['platforms'][1][1]
        self.assertLessEqual(abs(delta),64)
        self.assertEqual(new[0]['goal'][1],cases[0]['goal'][1]+delta)
        reward=next(o for o in doc['objects']if o['id']=='reward')
        self.assertEqual(reward['mechanics']['source'],new[0]['reward_sites'][0])

    def test_left_extension_keeps_hosted_spikes_at_original_x(self):
        source,cases=fixture();source['objects'].append(dict(id='spike',type='spike',hostId='p0',sourceId='s',x=35,y=188,w=40,h=12))
        cases[0]['thorns']=[dict(surface_id='s',platform_index=0,face='top',start_offset=35,length=40,depth=12)]
        doc,new,_=adapt(source,cases)
        thorn=new[0]['thorns'][0]
        self.assertEqual(new[0]['platforms'][0][0]+thorn['start_offset'],35)

    def test_top_port_gets_actual_one_way_staircase(self):
        source,cases=fixture(300,True);doc,new,receipt=adapt(source,cases)
        port=doc['generationContract']['ports'][1]
        entry=receipt['portAdaptations'][1]
        self.assertTrue(entry['routeContinuationRequired'])
        self.assertTrue(entry['connectorPlatforms'])
        self.assertEqual(entry['after']['surface'],'ONE_WAY_PLATFORM')
        self.assertIn(entry['after']['supportIndex'],new[0]['one_way_platform_indices'])
        self.assertEqual(port['position'][1],doc['generationContract']['space']['bounds']['y'])
        for step in entry['connectorPlatforms']:
            self.assertIn(step['platformIndex'],new[0]['one_way_platform_indices'])

    def test_marker_tracks_anchor_not_body_staging(self):
        source,cases=fixture();doc,new,_=adapt(source,cases)
        for port in doc['generationContract']['ports']:
            marker=next(o for o in doc['objects']if o['id']==port['objectId'])
            self.assertEqual([marker['x']+marker['w']/2,marker['y']+marker['h']/2],port['position'])
            self.assertNotEqual(port['grid']['stagingPosition'],port['position'])

    def test_thin_connectors_preserve_original_bank_span_and_recovery(self):
        source,cases=fixture();original=copy.deepcopy(cases[0]['platforms'])
        doc,new,receipt=adapt(source,cases)
        for old,edited in zip(original,new[0]['platforms']):
            self.assertEqual(old[0],edited[0]);self.assertEqual(old[2],edited[2])
        connectors=[e for e in receipt['edits']if e['kind']=='boundary_connector']
        self.assertTrue(connectors)
        self.assertTrue(all(c['thickness']<=24 for c in connectors))

    def test_outward_endcap_window_preserves_upper_wall_and_gate(self):
        source,cases=fixture()
        source['objects'].append(dict(id='wall',type='terrain',x=520,y=100,w=30,h=228,rotation=0))
        source['objects'].append(dict(id='gate',type='gate',x=555,y=100,w=12,h=228,rotation=0))
        cases[0]['platforms'].append([520,100,30,228])
        doc,new,receipt=adapt(source,cases)
        edits=[e for e in receipt['edits']if e['kind']=='outward_endcap_body_window']
        self.assertTrue(edits)
        wall=next(o for o in doc['objects']if o['id']=='wall')
        gate=next(o for o in doc['objects']if o['id']=='gate')
        self.assertEqual(wall['y'],100);self.assertLess(wall['h'],228)
        self.assertEqual([gate[k]for k in ('x','y','w','h')],[555,100,12,228])
        self.assertTrue(all(e['validation']=='UNKNOWN'for e in edits))

    def test_world_bounds_enclose_new_rectangle_and_body_guard(self):
        source,cases=fixture();cases[0]['world_bounds']=[0,0,520,340]
        doc,new,receipt=adapt(source,cases);b=receipt['afterBounds'];world=new[0]['world_bounds']
        self.assertLessEqual(world[0],b['x']-128)
        self.assertLessEqual(world[1],b['y']-128)
        self.assertGreaterEqual(world[0]+world[2],b['x']+b['w']+128)
        self.assertGreaterEqual(world[1]+world[3],b['y']+b['h']+128)

    def test_conflicting_route_geometry_is_not_silently_overwritten(self):
        source,cases=fixture();second=copy.deepcopy(cases[0]);second['platforms'][0][2]+=20
        with self.assertRaisesRegex(ValueError,'route_geometry_disagrees'):
            adapt(source,[cases[0],second])


if __name__=='__main__':unittest.main()
