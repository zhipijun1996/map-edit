"""Exact new Cell fields must survive the existing canonical output adapter."""
import copy,json,tempfile,unittest
from pathlib import Path
from pcg.map_directed.director import REPO
from pcg.map_directed.direct_join.canonical import export_reload

class CatalogRoundtrip(unittest.TestCase):
    def test_native_cell_parameters_survive_roundtrip(self):
        fixture=json.loads((REPO/'pcg/map_directed/direct_join/guard-fixture.json').read_text())
        m=copy.deepcopy(fixture['modules'][0]);c=m['case'];m['spec']['id']='test-native-cell';m['spec']['node']={'id':m['id'],'role':'challenge'}
        m.setdefault('boundary_gates',[]);c.update(id='test-native-cell',spawn=[24,20],entry_port=[24,20],exit_port=[76,20],goal=[69,16,14,8],capabilities=['move','jump','shot_recoil'],family='test',control_plan=[],hooks=[],hazards=[],enemies=[],thorns=[],reward_sites=[],shop_sites=[],moving_platforms=[])
        c['latches']=[dict(id='native',bell=[50,10],gate=[60,0,4,30],open_seconds=.3,prompt='',occupancy={'rect':[20,10,8,8]},sequence_offset=[10,0],sequence_gate=[70,0,4,30])]
        c['saws']=[dict(source_id='saw',origin=[50,10],travel=[0,4],radius=3,period=2,initial_phase=0,damage=2,contact_interval=.7)]
        c['ports']=[dict(id='A',position=[24,20])]
        c.setdefault('one_way_platform_indices',[])
        for key,p in m['ports'].items():
            x,y=p['position'];p['id']=key;p['aperture']=[x-48,y-64,96,128];p['dock']={'support_indices':[0]};p['kind']='side'
        m['center_to_port']={};m['port_to_center']={}
        # A real producer path/hash is required by the existing exporter.
        with tempfile.TemporaryDirectory(dir=REPO/'pcg')as tmp:
            out=export_reload([m],Path(tmp),producer='pcg/map_directed/catalog_feed/adapt.py')[0]
        self.assertEqual(out['case']['latches'],c['latches']);self.assertEqual(out['case']['saws'],c['saws']);self.assertEqual(out['case']['ports'],c['ports'])
