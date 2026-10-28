import unittest
from pcg.migration import review_air_runtime,godot_package
class ReviewAirRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.doc={'objects':[{'type':'enemy','definition':'plains_diver'}]}
    def test_actual_air_cell_selects_additive_binding(self):
        self.assertTrue(review_air_runtime.required(self.doc,[{}]))
        self.assertFalse(review_air_runtime.required({'objects':[{'type':'enemy','definition':'plains_sentry'}]},[{}]))
    def test_native_profiles_are_not_silently_discarded(self):
        for field in ('original_pickups','original_tuning_profile','original_fixture_profile'):
            with self.subTest(field=field),self.assertRaisesRegex(godot_package.PackageError,'combination_not_implemented'):
                review_air_runtime.required(self.doc,[{field:{'id':'original-native-profile'}}])
