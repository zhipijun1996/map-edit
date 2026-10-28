import copy,unittest
from pcg.migration.projection_rebind import projection_diff,unchanged_cases

class ProjectionRebindTests(unittest.TestCase):
    def setUp(self):
        self.old=dict(objects=[dict(id='saw',type='gear',x=1,y=2,w=36,h=36)],generationContract=dict(ports=[dict(position=[0,64])],routes=[],profile='base',control=['jump']))
        self.new=copy.deepcopy(self.old);self.new['objects'][0]['mechanics']=dict(runtimeParameters=dict(period=4,damage=1))
    def test_missing_parameters_allowed(self):self.assertEqual(len(projection_diff(self.old,self.new)),2)
    def test_position_tamper_rejected(self):
        self.new['objects'][0]['x']=2
        with self.assertRaisesRegex(ValueError,'geometry'):projection_diff(self.old,self.new)
    def test_existing_parameter_tamper_rejected(self):
        self.old['objects'][0]['mechanics']=dict(runtimeParameters=dict(period=3))
        with self.assertRaisesRegex(ValueError,'existing_parameter'):projection_diff(self.old,self.new)
    def test_ports_tamper_rejected(self):
        self.new['generationContract']['ports'][0]['position'][0]=128
        with self.assertRaisesRegex(ValueError,'ports'):projection_diff(self.old,self.new)
    def test_profile_and_control_tamper_rejected(self):
        for field,value in [('profile','air_chain'),('control',['walk'])]:
            new=copy.deepcopy(self.new);new['generationContract'][field]=value
            with self.assertRaises(ValueError):projection_diff(self.old,new)
    def test_case_bytes_tamper_rejected(self):
        with self.assertRaisesRegex(ValueError,'physical_case_bytes'):unchanged_cases(b'{"x":1}',b'{"x":2}')
    def test_unexpected_parameter_rejected(self):
        self.new['objects'][0]['mechanics']['runtimeParameters']['speed']=99
        with self.assertRaisesRegex(ValueError,'unsupported'):projection_diff(self.old,self.new)

if __name__=='__main__':unittest.main()
