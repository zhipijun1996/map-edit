import ast
import hashlib
import importlib
import importlib.abc
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import shutil
from unittest.mock import patch
import unittest
from pcg.module_library.paths import REPO, DEFAULT_LIBRARY, evidence_path
from pcg.module_library.library import CandidateLibrary
from pcg.prototype.workshop.library import WorkshopLibrary
from pcg.prototype.workshop.production_loop import compile_request


class IsolationTests(unittest.TestCase):
    def test_retired_map_is_absent_and_cannot_be_imported(self):
        self.assertFalse((REPO/'pcg/map_directed').exists())
        self.assertIsNone(importlib.util.find_spec('pcg.map_directed'))
        self.assertFalse(hasattr(CandidateLibrary,'find_payload'))
        self.assertFalse(hasattr(CandidateLibrary,'enroll_direct_instance'))
        self.assertFalse(hasattr(CandidateLibrary,'enroll_payloads'))

    def test_no_active_source_imports_or_loads_old_map(self):
        roots=['pcg/prototype','pcg/module_library','pcg/contract','pcg/tools','tools']
        for name in roots:
            for path in (REPO/name).rglob('*'):
                if not path.is_file()or path.suffix not in ('.py','.mjs','.js','.gd'):continue
                if path==Path(__file__).resolve():continue
                source=path.read_text()
                if path.suffix=='.py':
                    for node in ast.walk(ast.parse(source)):
                        names=[n.name for n in node.names]if isinstance(node,ast.Import)else[node.module or '']if isinstance(node,ast.ImportFrom)else[]
                        self.assertFalse(any('map_directed'in n or n=='region_network'for n in names),str(path))
                # No indirect old file loader or runtime path; source snapshots
                # and checks in the restore utility are historical data rules.
                if path.name!='restore_archive.py':self.assertNotIn('map_directed/',source,str(path))

    def test_candidate_files_preserved_byte_for_byte(self):
        manifest=json.loads((REPO/'archive/mapgen-failed/manifest.json').read_text())
        entries=[r for r in manifest['files']if r['action']=='module_record_relocated_byte_identical']
        self.assertEqual(len(entries),282)
        for row in entries:
            raw=(REPO/row['destination']).read_bytes()
            self.assertEqual(len(raw),row['bytes']);self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256'])
        self.assertGreaterEqual(len(list((DEFAULT_LIBRARY/'candidates').glob('*/record.json'))),94)

    def test_map_context_records_preserved_but_not_in_library(self):
        manifest=json.loads((REPO/'archive/mapgen-failed/manifest.json').read_text())
        rows=[r for r in manifest['files']if r['action']=='map_context_record_quarantined_byte_identical']
        self.assertEqual(len(rows),162)
        for row in rows:self.assertEqual(hashlib.sha256((REPO/row['destination']).read_bytes()).hexdigest(),row['sha256'])
        for root in [REPO/'archive/mapgen-failed/library',REPO/'pcg/map_directed/library']:
            with self.assertRaisesRegex(ValueError,'retired_map_store'):CandidateLibrary(root)

    def test_records_only_audit_still_checks_semantic_content_version(self):
        from pcg.module_library.audit import audit
        source=next((DEFAULT_LIBRARY/'candidates').glob('*/record.json')).parent
        with tempfile.TemporaryDirectory() as tmp:
            store=Path(tmp);folder=store/'candidates'/source.name;shutil.copytree(source,folder)
            document=folder/'module.mapnote.json';doc=json.loads(document.read_text())
            doc['objects'][0]['x']+=1;document.write_text(json.dumps(doc))
            record=folder/'record.json';r=json.loads(record.read_text());r['document_sha256']=hashlib.sha256(document.read_bytes()).hexdigest();record.write_text(json.dumps(r))
            with patch('pcg.module_library.audit.DEFAULT_LIBRARY',store):
                with self.assertRaisesRegex(ValueError,'candidate_document'):audit(records_only=True)

    def test_retired_recipe_cannot_be_self_enabled(self):
        for name in ['map-owned-supports/v1','map-state-boundary/v1','ordered-interface/v1','rigid-mirror/v1','map-budget-binding/v1','bellstrider-court/v1','branch-terraces/v1']:
            result=compile_request(dict(recipe=name,implemented=True))
            self.assertEqual(result['status'],'needs_design');self.assertEqual(result['cases'],[])

    def test_original_file_references_only_resolve_with_same_bytes(self):
        rows=json.loads((REPO/'pcg/module_library/relocations.json').read_text());old,row=next(iter(rows.items()))
        self.assertEqual(evidence_path(old,row['sha256']),REPO/row['destination'])
        with self.assertRaisesRegex(ValueError,'checksum_mismatch'):evidence_path(old,'0'*64)
        with self.assertRaises(FileNotFoundError):evidence_path('pcg/map_directed/not-a-record.py')

    def test_restore_cannot_reintroduce_retired_code_or_store(self):
        from pcg.tools.restore_archive import check_retired_destinations
        for name in ['map_directed/director.py','prototype/plains/compound_terraces.py']:
            with self.assertRaisesRegex(ValueError,'Retired Map'):check_retired_destinations({name:{}},'')
        check_retired_destinations({'results/old-run/source_snapshot/map_directed/director.py':{}},'results/')

    def test_fresh_process_library_queries_without_map_imports(self):
        code='''
import importlib.abc,json,sys
class NoMap(importlib.abc.MetaPathFinder):
 def find_spec(self,fullname,path=None,target=None):
  if 'map_directed' in fullname or fullname=='region_network':raise RuntimeError('retired dependency '+fullname)
sys.meta_path.insert(0,NoMap())
from pcg.module_library.paths import DEFAULT_LIBRARY
from pcg.prototype.workshop.library import WorkshopLibrary
single=multi=0
for path in sorted((DEFAULT_LIBRARY/'candidates').glob('*/record.json')):
 record=json.loads(path.read_text())
 if record['technical_status']=='passed_scoped'and not single:
  case=json.loads((path.parent/'case.json').read_text());hits=WorkshopLibrary().find_single_exact(case['map_specification']);assert any(x['record']['contentVersion']==record['contentVersion']for x in hits);single=1
 if record['technical_status']=='passed_scoped_multi_route'and not multi:
  hits=WorkshopLibrary().find_multi(record['specification']);assert any(x['record']['contentVersion']==record['contentVersion']for x in hits);multi=1
 if single and multi:break
assert single and multi
assert not any('map_directed'in k or k=='region_network'for k in sys.modules)
print('independent single and multi-route retrieval passed')
'''
        p=subprocess.run([sys.executable,'-B','-c',code],cwd=REPO,capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr)


if __name__=='__main__':unittest.main()
