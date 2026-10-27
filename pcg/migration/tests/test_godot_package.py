import copy,json,shutil,tempfile,unittest
from pathlib import Path
from pcg.migration.godot_package import ROOT,PackageError,audit_cases,compile_package,sha,verify_package
from pcg.migration import core

class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=next((ROOT/'pcg/map_directed/library/candidates').glob('87731645f7be*'),None)
        if cls.source is None:
            original=next(path for path in core.ledger()['relocations'] if Path(path).name.startswith('87731645f7be'))
            cls.source=core.resolve_artifact(original+'/module.mapnote.json').parent
        cls.doc=json.loads((cls.source/'module.mapnote.json').read_text());raw=json.loads((cls.source/'cases.json').read_text());cls.cases=raw['cases']if isinstance(raw,dict)else raw
        cls.temp=tempfile.TemporaryDirectory();cls.base=Path(cls.temp.name)/'package';compile_package(cls.source/'module.mapnote.json',cls.source/'cases.json',cls.base,stable_id='test-n16')
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()
    def cloned(self):
        p=Path(self.temp.name)/self._testMethodName;shutil.copytree(self.base,p);return p
    def write(self,p,v):p.write_text(json.dumps(v,ensure_ascii=False))
    def test_exact_old_canonical_and_document_bytes_preserved(self):
        self.assertEqual((self.base/'module.mapnote.json').read_bytes(),(self.source/'module.mapnote.json').read_bytes());self.assertEqual((self.base/'cases.json').read_bytes(),(self.source/'cases.json').read_bytes());self.assertTrue(verify_package(self.base,require_loaded=False)['passed'])
    def test_one_pixel_geometry_change_rejected(self):
        doc=copy.deepcopy(self.doc);doc['objects'][0]['w']+=1
        with self.assertRaises(PackageError)as c:audit_cases(doc,self.cases)
        self.assertEqual(c.exception.code,'geometry_mismatch')
    def test_unbound_unsupported_cell_rejected(self):
        doc=copy.deepcopy(self.doc);doc['objects'].append(dict(id='new-enemy',type='enemy',x=0,y=0,w=30,h=30))
        with self.assertRaises(PackageError)as c:audit_cases(doc,self.cases)
        self.assertEqual(c.exception.code,'unsupported_cell')
    def test_no_online_rule_fallback_when_input_missing(self):
        cases=copy.deepcopy(self.cases);cases[0].pop('recorded_frames')
        with self.assertRaises(PackageError)as c:audit_cases(self.doc,cases)
        self.assertEqual(c.exception.code,'missing_frozen_replay')
    def test_fake_passed_boolean_is_not_load_evidence(self):
        p=self.cloned();m=json.loads((p/'godot-package.json').read_text());m['godotLoad']={'passed':True};self.write(p/'godot-package.json',m)
        with self.assertRaises(PackageError)as c:verify_package(p,require_loaded=True)
        self.assertEqual(c.exception.code,'missing_real_load_evidence')
    def test_rehashed_but_changed_compilation_rejected(self):
        p=self.cloned();data=json.loads((p/'compiled-content.json').read_text());data['platforms'][0][2]+=1;self.write(p/'compiled-content.json',data);m=json.loads((p/'godot-package.json').read_text());m['artifacts']['compiled-content.json']=sha(p/'compiled-content.json');self.write(p/'godot-package.json',m)
        with self.assertRaises(PackageError)as c:verify_package(p,require_loaded=False)
        self.assertEqual(c.exception.code,'geometry_mismatch')
    def test_retargeted_bell_rejected(self):
        doc=copy.deepcopy(self.doc);next(o for o in doc['objects']if o['type']=='bell')['targetId']='missing-gate'
        with self.assertRaises(PackageError)as c:audit_cases(doc,self.cases)
        self.assertEqual(c.exception.code,'unsupported_bell_target')
    def test_stripped_runtime_dependency_list_rejected(self):
        p=self.cloned();m=json.loads((p/'godot-package.json').read_text());m['runtimeDependencies']=m['runtimeDependencies'][:1];self.write(p/'godot-package.json',m)
        with self.assertRaises(PackageError)as c:verify_package(p,require_loaded=False)
        self.assertEqual(c.exception.code,'geometry_mismatch')
    def test_rehashed_compiled_port_change_rejected(self):
        p=self.cloned();data=json.loads((p/'compiled-content.json').read_text());data['ports'][0]['position'][0]+=1;self.write(p/'compiled-content.json',data);m=json.loads((p/'godot-package.json').read_text());m['artifacts']['compiled-content.json']=sha(p/'compiled-content.json');self.write(p/'godot-package.json',m)
        with self.assertRaises(PackageError)as c:verify_package(p,require_loaded=False)
        self.assertEqual(c.exception.code,'geometry_mismatch')
    def test_portable_bundle_is_exact_source_bytes_and_recursive_artifacts(self):
        manifest=json.loads((self.base/'godot-package.json').read_text())
        self.assertEqual(len(manifest['bundledRuntime']),9)
        for row in manifest['bundledRuntime']:
            self.assertEqual((self.base/row['packagePath']).read_bytes(),(ROOT/row['sourcePath']).read_bytes())
            self.assertIn(row['packagePath'],manifest['artifacts'])
        for name,script in [('module','module_loader.gd'),('demo','package_demo.gd')]:
            text=(self.base/(name+'.tscn')).read_text()
            self.assertIn('path="runtime/pcg/migration/runtime/'+script+'"',text)
            self.assertNotIn(str(ROOT),text)
    def test_rehashed_bundle_modification_still_rejected(self):
        p=self.cloned();m=json.loads((p/'godot-package.json').read_text());name=m['bundledRuntime'][0]['packagePath'];target=p/name;target.write_bytes(target.read_bytes()+b'\n# changed copy\n');m['artifacts'][name]=sha(target);self.write(p/'godot-package.json',m)
        with self.assertRaises(PackageError)as c:verify_package(p,require_loaded=False)
        self.assertEqual(c.exception.code,'changed_bundled_runtime')
    def test_historical_v1_absolute_scene_remains_supported(self):
        from pcg.migration.godot_package import RUNTIME,_scene_text,LEGACY_VERSION
        p=self.cloned();m=json.loads((p/'godot-package.json').read_text());m['compiler_version']=LEGACY_VERSION
        for key in ['bundledRuntime','portableLayout','compilerSource']:m.pop(key,None)
        shutil.rmtree(p/'runtime')
        m['artifacts']={key:value for key,value in m['artifacts'].items()if not key.startswith('runtime/')}
        for name,script in [('module','module_loader.gd'),('demo','package_demo.gd')]:
            file=p/(name+'.tscn');file.write_text(_scene_text(m['stable_id'],name,str(RUNTIME/script)));m['artifacts'][file.name]=sha(file)
        self.write(p/'godot-package.json',m)
        self.assertTrue(verify_package(p,require_loaded=False)['passed'])
    def test_package_cannot_be_silently_overwritten(self):
        with self.assertRaises(PackageError)as c:compile_package(self.source/'module.mapnote.json',self.source/'cases.json',self.base)
        self.assertEqual(c.exception.code,'output_exists')

if __name__=='__main__':unittest.main()
