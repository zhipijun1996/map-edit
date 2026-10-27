import copy
import unittest
from pcg.migration.adaptation import adapt
from pcg.migration.side_docks import repair
from pcg.migration.tests.test_adaptation import fixture


def source():
    doc,cases=fixture();doc['objects'][1]['type']='platform';cases[0]['one_way_platform_indices']=[1]
    doc,cases,_=adapt(doc,cases);gc=doc['generationContract'];gc['validations']=[];gc['routes']=[]
    for p in gc['ports']:
        p['face']='LEFT'if p['normal'][0]<0 else'RIGHT'
        p['surface']='ONE_WAY_PLATFORM'if p['id']=='B'else'ROCK'
        p['stagingPosition']=p['grid']['stagingPosition']
    return doc,cases


class SideDockTests(unittest.TestCase):
    def test_real_solid_dock_is_declared_rock_and_keeps_original_oneway(self):
        doc,cases=source();before=copy.deepcopy((doc,cases));old_oneways=list(cases[0]['one_way_platform_indices'])
        fixed,new,receipt=repair(doc,cases,['B'])
        self.assertEqual((doc,cases),before)
        port=fixed['generationContract']['ports'][1];self.assertEqual(port['surface'],'ROCK')
        index=next(p['support_index']for p in new[0]['ports']if p['id']=='B')
        self.assertNotIn(index,new[0]['one_way_platform_indices'])
        self.assertEqual(new[0]['one_way_platform_indices'],old_oneways)
        body=next(o for o in fixed['objects']if o['id']==port['support']['objectId'])
        self.assertEqual(body['type'],'terrain');self.assertEqual(body['w'],64)
        self.assertEqual(receipt['validation'],'UNKNOWN')

    def test_does_not_change_arbitrary_rock_or_vertical_ports(self):
        doc,cases=source()
        with self.assertRaisesRegex(ValueError,'requires_side_one_way'):
            repair(doc,cases,['A'])
        doc['generationContract']['ports'][1]['face']='TOP'
        with self.assertRaisesRegex(ValueError,'requires_side_one_way'):
            repair(doc,cases,['B'])

    def test_pass_certificates_are_invalidated_after_real_geometry_change(self):
        doc,cases=source();doc['generationContract']['validations']=[dict(result='pass',artifacts=[dict(path='old')])]
        fixed,new,receipt=repair(doc,cases,['B'])
        self.assertEqual(fixed['generationContract']['validations'][0]['result'],'UNKNOWN')
        self.assertEqual(fixed['generationContract']['validations'][0]['artifacts'],[])


if __name__=='__main__':unittest.main()
