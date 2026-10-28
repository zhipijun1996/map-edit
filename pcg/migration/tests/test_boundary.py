"""Adversarial checks of the measurement, not simulated gameplay successes."""
import unittest
from pcg.migration.physics import crossing


class BoundaryMeasurementTests(unittest.TestCase):
    def probe(self, height=14):
        case={'migration_probe':{'kind':'local_boundary','portId':'P','boundary':[0,0],'normal':[1,0],
              'direction':'egress','neighbor':{}},'block_ports':{'P':{'aperture':[-32,-32,64,64]}}}
        raw={'ok':True,'hp':5,'frames':[{'frame':i,'x':x,'y':height}for i,x in enumerate([-30,-10,10,30])],'returns':0}
        return case,raw

    def test_entire_body_through_declared_aperture(self):
        self.assertTrue(crossing(*self.probe())['passed'])

    def test_infinite_boundary_line_is_not_a_port(self):
        self.assertFalse(crossing(*self.probe(10000))['passed'])

    def test_center_inside_but_body_clips_lintel(self):
        self.assertFalse(crossing(*self.probe(-20))['passed'])

    def test_wrong_direction_is_not_ingress(self):
        case,raw=self.probe();case['migration_probe']['direction']='ingress'
        self.assertFalse(crossing(case,raw)['passed'])

    def test_teleport_or_reset_does_not_certify(self):
        case,raw=self.probe();raw['returns']=1
        self.assertFalse(crossing(case,raw)['passed'])

    def test_missing_aperture_fails_closed(self):
        case,raw=self.probe();case['block_ports']={}
        self.assertFalse(crossing(case,raw)['passed'])

    def test_continuous_exit_cannot_skip_required_reward(self):
        case,raw=self.probe();case['migration_probe']['kind']='continuous_exit'
        case['required_rewards']=['cache'];case['expected_reward']=8
        self.assertFalse(crossing(case,raw)['passed'])


if __name__=='__main__':unittest.main()
