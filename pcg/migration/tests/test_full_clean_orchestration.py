"""Real Harness refusal paths; no mocked physics success and no new Godot run."""
import contextlib
import io
import shutil
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch
from pcg.migration import core,full_clean


class FullCleanOrchestrationTests(unittest.TestCase):
    def setUp(self):
        (core.REPO/'.cache/migration').mkdir(parents=True,exist_ok=True)
        self.tmp=tempfile.TemporaryDirectory(prefix='orchestration-test-',dir=core.REPO/'.cache/migration')
        self.addCleanup(self.tmp.cleanup)
        self.work=Path(self.tmp.name);self.prepared=self.work/'prepared';self.prepared.mkdir()
        self.state=self.work/'state';self.state.mkdir()
        self.state_patch=patch.object(core,'STATE',self.state);self.state_patch.start();self.addCleanup(self.state_patch.stop)
        self.name='test-full-clean-'+uuid.uuid4().hex

    def candidate(self,identifier):
        source=core.ACTIVE/'game-micro-board';folder=self.prepared/identifier;folder.mkdir()
        for name in ('module.mapnote.json','cases.json'):
            shutil.copy2(source/name,folder/name)
        return folder

    def previous_run(self,folder,attempts):
        name=full_clean.run_name_for(self.name,folder);run=core.REPO/'pcg/results'/name
        run.mkdir();self.addCleanup(shutil.rmtree,run)
        core.write(run/'batches.json',[dict(batch='historical-only',cases=attempts)])
        (run/'unchanged.txt').write_text('Existing run must not be rewritten or counted as a new attempt.')
        return run,core._tree_files(run)

    def diagnose(self):
        with contextlib.redirect_stdout(io.StringIO()):
            return full_clean.run(self.prepared,self.name,workers=1)

    def test_sources_with_same_12_and_28_prefix_use_distinct_actual_run_paths(self):
        prefix='abcdef012345'+'x'*20
        first=self.candidate(prefix+'first');second=self.candidate(prefix+'second')
        self.assertEqual(first.name[:28],second.name[:28])
        names=[full_clean.run_name_for(self.name,p)for p in (first,second)]
        self.assertNotEqual(*names)
        runs=[self.previous_run(first,91),self.previous_run(second,113)]
        result=self.diagnose()
        self.assertEqual(result['counts'],dict(passed=0,needs_repair=0,error=2))
        self.assertEqual(result['actualAttempts'],0)
        self.assertEqual({r['source']for r in result['rows']},{first.name,second.name})
        for row in result['rows']:
            self.assertIn('Refuse existing factory run:',row['error'])
            self.assertIn(full_clean.run_name_for(self.name,self.prepared/row['source']),row['error'])
        for run,before in runs:self.assertEqual(core._tree_files(run),before)

    def test_actual_existing_run_refusal_does_not_count_its_old_batches(self):
        folder=self.candidate('existing-source');run,before=self.previous_run(folder,987)
        result=self.diagnose();row=result['rows'][0]
        self.assertEqual(row['status'],'error')
        self.assertIn('Refuse existing factory run:',row['error'])
        self.assertEqual(row['actualAttempts'],0)
        self.assertEqual(result['actualAttempts'],0)
        self.assertFalse(result['technicalAdmission'])
        self.assertEqual(core._tree_files(run),before)
        self.assertFalse((run/'source_binding.json').exists())
        self.assertFalse((run/'physics').exists())


if __name__=='__main__':unittest.main()
