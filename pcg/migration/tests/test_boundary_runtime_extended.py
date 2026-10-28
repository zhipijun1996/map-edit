"""Real runner budget/data binding tests; these do not certify gameplay."""
import copy
import unittest
from pcg.migration import boundary_runtime_extended as extended,corner_batch_adapter_v4 as v4
from pcg.migration.tests.test_corner_batch_adapter import fixture
from pcg.prototype.factory.core.quality import digest


def waits(count):
    return [dict(op='wait',trigger=dict(after=i%2))for i in range(count)]


class NativeBoundaryBudgetTests(unittest.TestCase):
    def test_existing_foundry_ancestor_really_declares_384_not_python_128(self):
        _,cases=fixture('game-foundry-route-1521b6b7c3')
        maximum,proof=extended.native_plan_limit(cases[0])
        self.assertEqual(maximum,384);self.assertEqual(proof['maximumCommands'],384)
        self.assertTrue(proof['path'].endswith('foundry_feedback_runner_v5.gd'))

    def test_original_resource_wrapper_retains_native_foundry_budget(self):
        _,cases=fixture('game-plains-wind-spire')
        self.assertEqual(extended.native_plan_limit(cases[0])[0],384)

    def test_other_real_runner_does_not_get_an_expanded_budget(self):
        document,cases=fixture('b31-n06-fourport-two-low-ingress')
        self.assertEqual(extended.native_plan_limit(cases[0])[0],128)
        cases[0]['migration_boundary_plans']={'B':{'local_ingress':waits(129)}}
        with self.assertRaisesRegex(ValueError,'complete_original_DSL_program'):
            extended.bind(document,cases)

    def test_full_384_commands_are_retained_and_hashed_past_first_128(self):
        document,cases=fixture('game-foundry-route-1521b6b7c3')
        plan=waits(384);cases[0]['migration_boundary_plans']={'exit':{'egress':plan}}
        saved=copy.deepcopy(cases)
        doc,bound,records=extended.bind(document,cases)
        self.assertEqual(cases,saved)
        self.assertEqual(bound[0]['migration_boundary_plans']['exit']['egress'],plan)
        self.assertEqual(records[0]['fullPlansSha256'],digest(cases[0]['migration_boundary_plans']))
        self.assertEqual(records[0]['nativePlanBudget']['maximumCommands'],384)
        changed=copy.deepcopy(cases[0]['migration_boundary_plans']);changed['exit']['egress'][-1]['trigger']['after']=3
        self.assertNotEqual(records[0]['fullPlansSha256'],digest(changed))

    def test_original_384_command_limit_is_not_relaxed(self):
        document,cases=fixture('game-foundry-route-1521b6b7c3')
        cases[0]['migration_boundary_plans']={'exit':{'egress':waits(385)}}
        with self.assertRaisesRegex(ValueError,'complete_original_DSL_program'):
            extended.bind(document,cases)

    def test_long_plan_candidate_does_not_overwrite_v3_id(self):
        self.assertEqual(v4.configuration_id('exit','TOP_RIGHT'),'exit-top-right-open-v4')
        self.assertNotEqual(v4.configuration_id('exit','TOP_RIGHT'),'exit-top-right-open-v3')


if __name__=='__main__':unittest.main()
