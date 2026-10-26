"""Exact new Cell fields must survive the existing canonical output adapter."""
import copy,json,tempfile,unittest,subprocess
from pathlib import Path
from pcg.map_directed.director import REPO
from pcg.map_directed.direct_join.canonical import reload_catalog
from pcg.prototype.factory.core.engine import file_sha

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
        # This is an output-only synthetic contract fixture, not physics. The
        # lean CI intentionally has no imported Godot project. Exercise the
        # same JS exporter and strict reloader without reading runtime assets.
        with tempfile.TemporaryDirectory(dir=REPO/'pcg')as tmp:
            tmp=Path(tmp);source=tmp/'source.json';source.write_text(json.dumps({'modules':[m]}))
            origin=dict(path=str(Path(__file__).relative_to(REPO)),sha256=file_sha(__file__))
            definitions=dict(player=dict(size=[24,36],source=origin),bell=dict(size=[28,28],source=origin),enemies={})
            bundle=dict(modules=[m],sourcePath=str(source.relative_to(REPO)),sourceSha=file_sha(source),producer=origin['path'],generatorSha=origin['sha256'],sourceCommit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),geometryDefinitions=definitions)
            (tmp/'bundle.json').write_text(json.dumps(bundle))
            subprocess.run(['node',str(REPO/'pcg/map_directed/direct_join/export_modules.mjs'),str(tmp/'bundle.json'),str(tmp/'documents')],cwd=REPO,check=True,capture_output=True)
            out=reload_catalog(tmp)[0]
        self.assertEqual(out['case']['latches'],c['latches']);self.assertEqual(out['case']['saws'],c['saws']);self.assertEqual(out['case']['ports'],c['ports'])
