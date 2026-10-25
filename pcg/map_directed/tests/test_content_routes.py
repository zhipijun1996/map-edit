"""Checks for actual hazard corruption and unsupported content fallback."""
import copy,unittest
from pcg.map_directed.direct_join.assemble import assemble_modules
from pcg.prototype.plains.content_routes import adapt

class ContentContracts(unittest.TestCase):
    def module(self,key,x,normal):
        t=dict(position=[32,20],region=[24,16,16,8],support_indices=[0],grounded=True)
        return dict(id=key,spec=dict(placement=[x,0],node=dict(role='hub',reward=0)),content_version='sha256:'+key,
            case=dict(platforms=[[0,38,64,16],[8,90,48,16]],one_way_platform_indices=[],
                thorns=[dict(surface_id='pit',platform_index=1,face='top',start_offset=0,length=48,depth=8)],hazards=[[16,110,12,8]]),
            center=t,ports={'e':dict(position=[64 if normal[0]>0 else 0,20],normal=normal,dock=t)},
            center_to_port={'e':[]},port_to_center={'e':[]},core=None,boundary_gates=[])

    def test_hazard_hosts_use_global_platform_index_after_placement(self):
        a=self.module('a',0,[1,0]);b=self.module('b',64,[-1,0])
        g=dict(entry='a',goal='b',edges=[dict(id='e',**{'from':'a','to':'b'},bidirectional=True)])
        c=assemble_modules(g,[a,b],[dict(id='e',kind='side')])
        self.assertEqual(c['case']['thorns'][1]['platform_index'],3)
        self.assertEqual(c['case']['thorns'][1]['surface_id'],'b/pit')
        self.assertEqual(c['case']['hazards'][1],[80,110,12,8])
        self.assertEqual(b['case']['thorns'][0]['platform_index'],1)

    def test_unsupported_challenge_is_a_gap_not_generic_success(self):
        m=self.module('a',0,[1,0]);s=copy.deepcopy(m['spec'])
        s.update(space={'core_bounds':[0,0,1024,432]},floor_margin=96,design_contract={'challenge':{'family':'unimplemented_idea'}})
        with self.assertRaisesRegex(ValueError,'unsupported_challenge_family'):adapt(m,s)
