import copy
import unittest
from pcg.migration.tests.test_wall_interfaces import fixture
from pcg.migration.bell_wall_interfaces import right_entry


class BellWallEntryTests(unittest.TestCase):
    def test_window_preserves_wall_faces_and_original_controller(self):
        doc,cases,original,source=fixture();before=copy.deepcopy((doc,cases,original,source))
        fixed,new,receipt=right_entry(doc,cases,original,source,entry_id='A',exit_id='B')
        self.assertEqual((doc,cases,original,source),before)
        self.assertEqual(new[0]['control_plan'],source[0]['control_plan'])
        self.assertEqual(new[0]['capabilities'],source[0]['capabilities'])
        self.assertEqual(new[0]['platforms'][0],source[0]['platforms'][0])
        self.assertEqual(receipt['wallWindow']['opening'][3],48)
        self.assertTrue(all(i in new[0]['wall_platform_indices']for i in receipt['wallWindow']['preservedWallClimbableIndices']))
        self.assertEqual(fixed['generationContract']['ports'][0]['face'],'RIGHT')
        self.assertEqual(fixed['generationContract']['ports'][1]['face'],'LEFT')

    def test_new_inner_bridge_stays_right_of_original_gun_and_bank(self):
        doc,cases,original,source=fixture()
        fixed,new,receipt=right_entry(doc,cases,original,source,entry_id='A',exit_id='B')
        self.assertGreater(receipt['newApproach'][0],source[0]['spawn'][0])
        self.assertEqual(receipt['newApproach'][0],source[0]['platforms'][0][0]+source[0]['platforms'][0][2])

    def test_hazard_host_wall_is_not_carved_for_port(self):
        doc,cases,original,source=fixture()
        original['objects'].append(dict(id='danger',type='wallSpike',hostId='p2',x=180,y=40,w=12,h=80))
        with self.assertRaisesRegex(ValueError,'hazard_host'):
            right_entry(doc,cases,original,source,entry_id='A',exit_id='B')


if __name__=='__main__':unittest.main()
