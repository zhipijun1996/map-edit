"""Compatibility never drops causal checks or substitutes sparse ownership."""
import types
import unittest
from unittest.mock import patch
from pcg.migration import purpose_compat as compat


class CompatibilityTests(unittest.TestCase):
    def fixture(self):
        rectangle=dict(x=10,y=10,w=128,h=128)
        return dict(migration_compat=dict(schema='pcg/migration-purpose-compatibility/v1',originalAuthorSource='fixture',
            legacyOwnership='superseded_by_exact_foundation_rectangle',foundationRectangle=rectangle),
            migration_adaptation=dict(rectangle=rectangle))

    def author(self,check=True):
        return types.SimpleNamespace(purpose=lambda case,raw:dict(ok=check,reasons=[]if check else['original_causal_failure'],causal={}))

    def test_exact_body_bounds_do_not_inherit_coarse_cell_false_positive(self):
        case=self.fixture();raw=dict(frames=[dict(frame=0,x=20,y=60)])
        with patch.dict(compat._AUTHORS,{'fixture':self.author()}):
            result=compat.purpose(case,raw)
            self.assertFalse(result['ok'])
            self.assertIn('actual_body_outside_foundation_rectangle',result['reasons'])

    def test_original_causal_failure_is_preserved(self):
        case=self.fixture();raw=dict(frames=[dict(frame=0,x=64,y=64)])
        with patch.dict(compat._AUTHORS,{'fixture':self.author(False)}):
            result=compat.purpose(case,raw)
            self.assertFalse(result['ok']);self.assertEqual(result['reasons'],['original_causal_failure'])

    def test_new_rectangle_cannot_be_swapped_by_binding_only(self):
        case=self.fixture();case['migration_adaptation']['rectangle']=dict(x=0,y=0,w=256,h=256)
        with patch.dict(compat._AUTHORS,{'fixture':self.author()}):
            with self.assertRaisesRegex(ValueError,'rectangle_drift'):compat.original_view(case)

    def test_compatibility_grid_is_only_a_transient_view(self):
        case=self.fixture()
        with patch.dict(compat._AUTHORS,{'fixture':self.author()}):
            _,view=compat.original_view(case)
            self.assertIn('block_grid',view);self.assertNotIn('block_grid',case)

if __name__=='__main__':unittest.main()
