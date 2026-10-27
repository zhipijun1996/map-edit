"""Exact forest semantics; fake validators in negative tests admit nothing."""
import copy
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from pcg.migration import core,deduplicate as dedup,forest_equivalence as forest


class ExactForestSemantics(unittest.TestCase):
    def setUp(self):
        self.primary=core.ACTIVE/'game-forest-hollow-trunk-geometry-cavity'
        # The real duplicate is archived by the existing deduplication WAL.
        # Follow its durable relocation instead of requiring a second current
        # version merely to exercise negative equivalence comparisons.
        self.duplicate=core.resolve_artifact('modules/game-forest-hollow-upper-candidate-build-cavity/module.mapnote.json').parent
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.changed=Path(self.tmp.name)/'changed';self.changed.mkdir()
        for name in ('module.mapnote.json','migration.json','compiled-content.json','physics-input-cases.json','godot-package.json'):
            shutil.copy2(self.duplicate/name,self.changed/name)

    def mutate(self,file,fn):
        path=self.changed/file;data=core.read(path);fn(data);core.write(path,data)

    def reject_comparison(self,reason):
        with patch.object(core,'validate',return_value={'testOnly':True}):
            with self.assertRaisesRegex(ValueError,reason):dedup._compare(self.changed,self.primary)

    def test_actual_whole_original_data_and_complete_current_payload_equal(self):
        a=forest.semantics(self.primary);b=forest.semantics(self.duplicate)
        self.assertEqual(a[0],b[0]);self.assertEqual(a[3]['originalDataSha256'],b[3]['originalDataSha256'])

    def test_control_ports_capabilities_hooks_and_unknown_program_fields_remain_semantic(self):
        for kind in ('control','port','capability','hook','extra'):
            with self.subTest(kind=kind):
                for name in ('module.mapnote.json','compiled-content.json','physics-input-cases.json'):
                    shutil.copy2(self.duplicate/name,self.changed/name)
                if kind=='control':self.mutate('physics-input-cases.json',lambda d:d['cases'][0]['control_plan'][0].update(deadband=8))
                if kind=='port':self.mutate('module.mapnote.json',lambda d:d['generationContract']['ports'][0]['position'].__setitem__(0,-640))
                if kind=='capability':self.mutate('module.mapnote.json',lambda d:d['capabilityRequirements']['allOf'].append('dash'))
                if kind=='hook':self.mutate('compiled-content.json',lambda d:d['hooks'][0].update(x=201))
                if kind=='extra':self.mutate('physics-input-cases.json',lambda d:d['cases'][0].update(unknown_gameplay_rule=True))
                self.reject_comparison('actual_semantics_differ')

    def test_original_dictionary_difference_is_never_normalized_away(self):
        self.mutate('module.mapnote.json',lambda d:d['source']['original'].update(native_verified=True))
        self.reject_comparison('whole_original_forest_data_differ')

    def test_original_actual_input_dictionary_binding_is_mandatory(self):
        self.mutate('physics-input-cases.json',lambda d:d['cases'][0]['source_identity'].update(originalDictionarySha256='0'*64))
        with self.assertRaisesRegex(ValueError,'not_bound_to_whole_original_dictionary'):forest.semantics(self.changed)

    def test_persistent_pickups_enemies_and_other_mechanisms_are_excluded(self):
        for key in ('original_pickups','original_region_chests','enemies','moving_platforms','latches'):
            with self.subTest(key=key):
                shutil.copy2(self.duplicate/'physics-input-cases.json',self.changed/'physics-input-cases.json')
                self.mutate('physics-input-cases.json',lambda d:d['cases'][0].update({key:[{'id':'stateful'}]}))
                with self.assertRaisesRegex(ValueError,'progression_or_other_dynamic'):forest.semantics(self.changed)

    def test_native_profile_or_persistent_namespace_requires_separate_proof(self):
        for key,value in [('original_tuning_profile',{'max_jumps':2}),('global_pickup_namespace','global-save')]:
            with self.subTest(key=key):
                shutil.copy2(self.duplicate/'physics-input-cases.json',self.changed/'physics-input-cases.json')
                self.mutate('physics-input-cases.json',lambda d:d['cases'][0].update({key:value}))
                with self.assertRaisesRegex(ValueError,'separate_equivalence|persistent_progression'):forest.semantics(self.changed)

    def test_runtime_difference_is_not_erased_by_exact_source_dictionary(self):
        self.mutate('godot-package.json',lambda d:d['runtimeDependencies'].append(dict(path='foreign.gd',sha256='0'*64)))
        self.reject_comparison('native_runtime_sources_differ')


if __name__=='__main__':unittest.main()
