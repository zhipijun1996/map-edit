"""Evidence restoration only; these fixtures never qualify playable content."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from pcg.migration import core, snapshot_preparations as snapshot


class ScratchEvidence(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.scope=patch.object(core,'REPO',self.root);self.scope.start();self.addCleanup(self.scope.stop)
        self.source=self.root/'.cache/migration/example/module.mapnote.json'
        self.source.parent.mkdir(parents=True);self.source.write_text('{"revision":1}\n')
        self.out=self.root/'pcg/results/snapshots'
        self.relative='.cache/migration/example/module.mapnote.json'

    def test_observed_revisions_retained_and_exact_old_bytes_restored(self):
        first=core.sha(self.source);snapshot.capture(self.out)
        self.source.write_text('{"revision":2}\n');snapshot.capture(self.out)
        self.assertEqual(len(core.read(self.out/'index.json')['files'][self.relative]),2)
        self.source.unlink()
        self.assertEqual(snapshot.restore(self.relative,first,self.out)['status'],'restored')
        self.assertEqual(self.source.read_bytes(),b'{"revision":1}\n')

    def test_changed_existing_scratch_and_unknown_historical_images_preserved(self):
        checksum=core.sha(self.source);snapshot.capture(self.out)
        self.source.write_text('{"revision":2}\n')
        with self.assertRaisesRegex(ValueError,'existing_scratch_bytes_differ'):
            snapshot.restore(self.relative,checksum,self.out)
        with self.assertRaisesRegex(ValueError,'not_in_snapshot'):
            snapshot.restore(self.relative,'0'*64,self.out)
        self.assertEqual(self.source.read_text(),'{"revision":2}\n')

    def test_corrupt_archive_or_destination_outside_scratch_rejected(self):
        checksum=core.sha(self.source);snapshot.capture(self.out)
        row=core.read(self.out/'index.json')['files'][self.relative][0]
        (self.out/row['object']).write_text('corrupt')
        self.source.unlink()
        with self.assertRaisesRegex(ValueError,'integrity_or_path'):
            snapshot.restore(self.relative,checksum,self.out)
        with self.assertRaisesRegex(ValueError,'restore_only'):
            snapshot.restore('.cache/migration/../../../AGENTS.md',checksum,self.out)

    def test_bounded_prefix_keeps_unselected_history_out(self):
        other=self.source.parent.parent/'unselected'/'cases.json'
        other.parent.mkdir();other.write_text('{"large_history":true}\n')
        result=snapshot.capture(self.out,source_prefixes=['.cache/migration/example'],include_tool_sources=False)
        index=core.read(self.out/'index.json')
        self.assertEqual(set(index['files']),{self.relative})
        self.assertEqual(index['currentToolSources'],{})
        self.assertEqual(result['lastCapture']['sourcePrefixes'],['.cache/migration/example'])
        self.source.unlink();snapshot.restore(self.relative,index['files'][self.relative][0]['sha256'],self.out)
        self.assertEqual(self.source.read_bytes(),b'{"revision":1}\n')

    def test_bounded_prefix_rejects_escape_and_empty_selection(self):
        for prefixes in ([],['.cache/migration/../../../AGENTS.md']):
            with self.assertRaisesRegex(ValueError,'prefix_(selection_must_not_be_empty|outside_migration_scratch)'):
                snapshot.capture(self.out,source_prefixes=prefixes)
        self.assertFalse(self.out.exists())


if __name__=='__main__':unittest.main()
