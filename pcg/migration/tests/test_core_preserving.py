import copy
import unittest
from pcg.migration.adaptation import adapt
from pcg.migration.core_preserving import bottom_pocket, side_interfaces, restore_core_shores


def fixture():
    rectangles=[[-160,438,400,310],[430,438,400,310],[180,-500,120,890],[240,718,190,70]]
    objects=[dict(id='p'+str(i),type='terrain',x=x,y=y,w=w,h=h,rotation=0,sourceIndex=i)
             for i,(x,y,w,h)in enumerate(rectangles)]
    objects += [dict(id='in',type='entry',x=68,y=402,w=24,h=36),dict(id='out',type='exit',x=323,y=682,w=24,h=36),
        dict(id='gate',type='gate',x=240,y=438,w=190,h=20),dict(id='bell',type='bell',x=356,y=228,w=28,h=34),
        dict(id='cache',type='reward',x=317,y=682,w=36,h=36)]
    ports=[dict(id='entry',objectId='in',position=[80,420],normal=[-1,0],support=dict(objectId='p0',face='top')),
           dict(id='exit',objectId='out',position=[335,700],normal=[1,0],support=dict(objectId='p3',face='top'))]
    doc=dict(id='trap',objects=objects,generationContract=dict(kind='module',ports=ports,
        generation=dict(migration={}),validations=[dict(result='pass',artifacts=[dict(path='old')])],
        routes=[dict(id='main',from_='entry',to='exit')],composition=dict(cells=[]),
        space=dict(bounds=dict(x=-200,y=-500,w=1200,h=1300),actionClearance=dict(regions=[]),
            occupancy=dict(objectIds=[o['id']for o in objects if o['type']not in('entry','exit')],regions=[]),dynamicEnvelopes=[],seams=[])))
    doc['generationContract']['routes'][0]['from']=doc['generationContract']['routes'][0].pop('from_')
    case=dict(id='original',platforms=copy.deepcopy(rectangles),ports=[dict(id='entry',support_index=0,position=[80,420]),dict(id='exit',support_index=3,position=[335,700])],
        spawn=[80,420],entry_port=[80,420],exit_port=[335,700],goal=[310,696,50,8],capabilities=['move','jump','shot_recoil'],
        latches=[dict(id='key',bell=[370,245],gate=[240,438,190,20],open_seconds=0)],
        reward_sites=[dict(id='cache',position=[335,700],region=[305,695,60,10],amount=14)],
        control_plan=[dict(op='axis',trigger=dict(after=0),value=1),dict(op='shoot',trigger=dict(after=4),aim_cell=dict(kind='bell',id='key')),dict(op='settle',trigger=dict(after=6),target_x=335,deadband=4)],
        route_spec=dict(id='main',from_port='entry',to_port='exit'),world_bounds=[-1200,-1000,4000,2400],max_frames=1200,
        one_way_platform_indices=[],thorns=[])
    original=copy.deepcopy(doc);source=[copy.deepcopy(case)];doc,cases,_=adapt(doc,[case]);gc=doc['generationContract'];b=gc['space']['bounds']
    gc['foundation']=dict(blockSize=128,widthBlocks=b['w']//128,heightBlocks=b['h']//128)
    for p in gc['ports']:p.update(stagingPosition=p['grid']['stagingPosition'],face='LEFT'if p['normal'][0]<0 else'RIGHT')
    return doc,cases,original,source


class CorePreservingTests(unittest.TestCase):
    def test_original_core_geometry_rewards_gate_and_program_are_not_quantized(self):
        doc,cases,original,source=fixture();before=copy.deepcopy((doc,cases,original,source))
        fixed,new,receipt=bottom_pocket(doc,cases,original,source,'exit')
        self.assertEqual((doc,cases,original,source),before)
        self.assertEqual(new[0]['platforms'][:4],source[0]['platforms'])
        for key in ('spawn','goal','latches','reward_sites','control_plan'):
            self.assertEqual(new[0][key],source[0][key])
        self.assertEqual(receipt['normal'],[0,1]);self.assertTrue(receipt['originalCoreRectanglesExact'])
        self.assertEqual(fixed['generationContract']['validations'][0]['result'],'UNKNOWN')

    def test_boundary_program_waits_for_actual_original_goal(self):
        doc,cases,original,source=fixture();fixed,new,receipt=bottom_pocket(doc,cases,original,source,'exit')
        program=new[0]['migration_boundary_plans']['exit']['egress'];count=len(source[0]['control_plan'])
        self.assertEqual(program[:count],source[0]['control_plan'])
        self.assertEqual(program[count]['trigger']['migration_goal'],source[0]['goal'])
        ready=[c for c in program if c.get('trigger',{}).get('migration_drop_ready')]
        self.assertEqual(len(ready),1);self.assertEqual(ready[0]['trigger']['state'],'grounded')

    def test_thin_material_window_keeps_original_top_and_honest_geometry_receipt(self):
        doc,cases,original,source=fixture()
        fixed,new,receipt=bottom_pocket(doc,cases,original,source,'exit',window_depth=12,short_local_ingress=True)
        self.assertEqual(new[0]['platforms'][3][:3],source[0]['platforms'][3][:3])
        self.assertEqual(new[0]['platforms'][3][3],12)
        self.assertFalse(receipt['originalCoreRectanglesExact']);self.assertTrue(receipt['originalCoreTopSurfacesExact'])
        self.assertEqual(new[0]['migration_boundary_plans']['exit']['local_ingress'][2]['trigger']['after'],6)
        self.assertEqual(len(receipt['localMaterialWindow']['backing']),2)

    def test_side_repair_does_not_carve_an_intact_core_bank(self):
        doc,cases,original,source=fixture()
        with self.assertRaisesRegex(ValueError,'original_core_blocks_proposed_side_interface'):
            side_interfaces(doc,cases,original,source)

    def test_imported_shore_repair_keeps_source_frame_input_authority(self):
        doc,cases,original,source=fixture()
        frames=[dict(frame=0,axis=1,requested=[]),dict(frame=1,axis=0,requested=[dict(type='shoot_release',direction=[0,-1])])]
        cases[0]['recorded_frames']=copy.deepcopy(frames)
        fixed,new,receipt=restore_core_shores(doc,cases,original,source)
        self.assertEqual(new[0]['recorded_frames'],frames)
        self.assertEqual(new[0]['platforms'][:4],source[0]['platforms'])
        self.assertEqual(new[0]['control_plan'],cases[0]['control_plan'])
        self.assertTrue(new[0]['migration_core_replay_authority']['boundaryEgressPlanIsTailOnly'])
        self.assertTrue(receipt['originalCoreRectanglesExact'])

    def test_hazard_hosted_pocket_does_not_get_silently_replaced(self):
        doc,cases,original,source=fixture();original['objects'].append(dict(id='spike',type='spike',hostId='p3',x=240,y=706,w=40,h=12))
        with self.assertRaisesRegex(ValueError,'hazard_host'):
            bottom_pocket(doc,cases,original,source,'exit')


if __name__=='__main__':unittest.main()
