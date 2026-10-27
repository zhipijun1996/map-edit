"""Offline analyses retain original trials; these tests approve no gameplay."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pcg.migration import core, offline_reanalysis as analysis


class OfflineLineageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.patch = patch.object(core, 'REPO', self.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.run = self.root / 'results' / 'actual-experiment'
        self.run.mkdir(parents=True)
        self.source = self.run / 'migration-physics.json'
        self.original = dict(passed=False, actualAttempts=132,
            contentVersion='sha256:unchanged', routes=[dict(routeId='outbound',
            holdout=dict(path='actual-heldout.json', sha256='original'))],
            protocol=dict(path='original-protocol.json', sha256='original'),
            humanReview='UNKNOWN', productionAdmitted=False)
        core.write(self.source, self.original)
        code = []
        for name in ('physics.py', 'causal_observer.py', 'causal_observer_v2.py', 'offline_reanalysis.py'):
            source = self.run / 'offline-analysis' / 'frozen' / name
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text('# actual frozen checker source\n')
            code.append(dict(path=core.relative(source), sha256=core.sha(source)))
        self.report = copy.deepcopy(self.original)
        self.report.update(passed=True, offlineAnalysis=dict(schema=analysis.SCHEMA,
            newPhysicsAttempts=0, newIndependentHoldout=False,
            sourceReport=dict(path=core.relative(self.source), sha256=core.sha(self.source)), analysisCode=code))
        self.target = self.run / 'migration-physics-offline.json'

    def test_changed_verdict_reuses_exact_original_experiment(self):
        analysis.validate_lineage(self.report, self.target)
        self.assertEqual(core.read(self.source), self.original)

    def test_cannot_claim_new_attempts_or_new_holdout(self):
        for field, value in (('newPhysicsAttempts', 1), ('newIndependentHoldout', True)):
            with self.subTest(field=field):
                changed = copy.deepcopy(self.report)
                changed['offlineAnalysis'][field] = value
                with self.assertRaisesRegex(ValueError, 'must_not_claim'):
                    analysis.validate_lineage(changed, self.target)

    def test_attempts_routes_protocol_and_human_status_cannot_change(self):
        changes = {'actualAttempts': 133, 'routes': [], 'protocol': {},
            'humanReview': 'approved', 'productionAdmitted': True}
        for key, value in changes.items():
            with self.subTest(field=key):
                changed = copy.deepcopy(self.report)
                changed[key] = value
                with self.assertRaisesRegex(ValueError, 'changed_experimental'):
                    analysis.validate_lineage(changed, self.target)

    def test_must_keep_original_report_and_same_experiment_directory(self):
        with self.assertRaisesRegex(ValueError, 'reference_itself'):
            analysis.validate_lineage(self.report, self.source)
        with self.assertRaisesRegex(ValueError, 'original_experiment_directory'):
            analysis.validate_lineage(self.report, self.root / 'new-experiment' / self.target.name)
        self.source.write_text('{}')
        with self.assertRaises(ValueError):
            analysis.validate_lineage(self.report, self.target)

    def test_actual_checker_snapshots_are_required_and_hash_bound(self):
        changed = copy.deepcopy(self.report)
        changed['offlineAnalysis']['analysisCode'].pop()
        with self.assertRaisesRegex(ValueError, 'checker_source_missing'):
            analysis.validate_lineage(changed, self.target)
        path = core.resolve_artifact(self.report['offlineAnalysis']['analysisCode'][0]['path'])
        path.write_text('# altered checker\n')
        with self.assertRaises(ValueError):
            analysis.validate_lineage(self.report, self.target)

    def test_unactivated_global_observer_cannot_create_analysis_report(self):
        from pcg.migration import physics
        # DRAFT remains inert while actors use the frozen global verifier.
        if hasattr(physics, 'causal_observer_v2'):
            self.skipTest('Coordinated global observer is already activated')
        with self.assertRaisesRegex(ValueError, 'not_integrated'):
            analysis.reanalyse(self.root, self.source)
        self.assertFalse(self.target.exists())


if __name__ == '__main__':
    unittest.main()
