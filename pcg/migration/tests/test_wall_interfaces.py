import copy
import unittest
from pcg.migration.tests.test_adaptation import fixture as base_fixture
from pcg.migration.adaptation import adapt
from pcg.migration.wall_interfaces import guided_top_entry


def fixture():
    source,cases=base_fixture();c=cases[0]
    rectangles=[[90,18,50,60],[-180,318,200,30],[195,-80,32,1000],[40,-500,20,600]]
    source['objects']=source['objects'][:2]+source['objects'][2:]
    for i,r in enumerate(rectangles[:2]):
        o=source['objects'][i]
        for k,v in zip(('x','y','w','h'),r):o[k]=v
    for i,r in enumerate(rectangles[2:],2):
        source['objects'].append(dict(id='p'+str(i),type='terrain',x=r[0],y=r[1],w=r[2],h=r[3],rotation=0,sourceIndex=i,wallClimbable=True))
    c['platforms']=copy.deepcopy(rectangles);c['spawn']=[110,0];c['entry_port']=[110,0];c['exit_port']=[-90,300];c['goal']=[-99,295,18,10]
    c['capabilities']=['move','wall_climb'];c['wall_platform_indices']=[2,3]
    c['control_plan']=[dict(op='settle',trigger=dict(after=0),target_x=-90,deadband=3)]
    c['route_spec']=dict(id='main',from_port='A',to_port='B')
    source['generationContract']['ports'][0]['position']=[110,0]
    source['generationContract']['ports'][1]['position']=[-90,300]
    for p in source['generationContract']['ports']:
        marker=next(o for o in source['objects']if o['id']==p['objectId']);marker['x']=p['position'][0]-12;marker['y']=p['position'][1]-18
    source['generationContract']['space']['actionClearance']['regions']=[dict(x=98,y=-18,w=24,h=336)]
    source['generationContract']['generation']=dict(migration={});source['generationContract']['validations']=[]
    source['generationContract']['routes']=[dict(id='main',from_='A',to='B')]
    source['generationContract']['routes'][0]['from']=source['generationContract']['routes'][0].pop('from_')
    original=copy.deepcopy(source);original_cases=copy.deepcopy(cases)
    doc,cases,_=adapt(source,cases);b=doc['generationContract']['space']['bounds']
    doc['generationContract']['foundation']=dict(blockSize=128,widthBlocks=b['w']//128,heightBlocks=b['h']//128)
    return doc,cases,original,original_cases


class GuidedWallInterfaceTests(unittest.TestCase):
    def test_original_core_and_abilities_preserved_with_nonclimbable_entrance(self):
        doc,cases,original,source=fixture()
        fixed,new,receipt=guided_top_entry(doc,cases,original,source,entry_id='A',exit_id='B')
        self.assertEqual(new[0]['platforms'][:4],source[0]['platforms'])
        self.assertEqual(new[0]['capabilities'],source[0]['capabilities'])
        self.assertEqual(new[0]['control_plan'],source[0]['control_plan'])
        ports=fixed['generationContract']['ports']
        self.assertEqual((ports[0]['face'],ports[0]['permission']),('TOP','INPUT'))
        self.assertEqual(ports[1]['face'],'LEFT')
        self.assertTrue(all(w['platformIndex']not in new[0]['wall_platform_indices']for w in receipt['entry']['shaft']))
        self.assertTrue(all(w['rect'][1]+w['rect'][3]<-18 for w in receipt['entry']['shaft']))

    def test_top_input_is_not_claimed_for_extra_upward_capabilities(self):
        doc,cases,original,source=fixture();source[0]['capabilities'].append('jump')
        with self.assertRaisesRegex(ValueError,'upward_abilities'):
            guided_top_entry(doc,cases,original,source,entry_id='A',exit_id='B')

    def test_known_reverse_route_cannot_be_hidden_by_input_permission(self):
        doc,cases,original,source=fixture();doc['generationContract']['routes'].append(dict(id='back',from_='B',to='A'))
        doc['generationContract']['routes'][-1]['from']=doc['generationContract']['routes'][-1].pop('from_')
        with self.assertRaisesRegex(ValueError,'known_reverse_route'):
            guided_top_entry(doc,cases,original,source,entry_id='A',exit_id='B')


if __name__=='__main__':unittest.main()
