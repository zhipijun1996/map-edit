"""Small real ZIP fixtures; no production raw scans or Godot execution."""
import contextlib
import hashlib
import io
import json
import random
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from pcg.tools import build_archive as builder, restore_archive as restorer


class StreamingArchiveTests(unittest.TestCase):
    name = 'module-foundation-migration-v2'

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.addCleanup(patch.stopall)
        patch.object(builder, 'ROOT', self.root).start()
        patch.object(restorer, 'ROOT', self.root).start()
        (self.root / 'archives').mkdir()
        self.source = self.root / 'fixture'
        self.source.mkdir()
        data = random.Random(1401).randbytes(4096)
        (self.source / 'a.bin').write_bytes(data)
        (self.source / 'alias.bin').write_bytes(data)
        (self.source / 'notes.txt').write_text('真实流式归档 fixture\n' * 13)
        self.expected = {str(p.relative_to(self.root)): p.read_bytes() for p in self.source.iterdir()}
        self.folder = self.root / 'archives' / self.name

    def build(self, *, stream=True, deduplicate=False):
        with contextlib.redirect_stdout(io.StringIO()):
            return builder.build(self.name, ['fixture'], deduplicate, stream, part_bytes=127)

    def verify(self, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()):
            return restorer.restore(self.name, **kwargs)

    def manifest(self):
        return json.loads((self.folder / 'manifest.json').read_text())

    def save_manifest(self, value):
        (self.folder / 'manifest.json').write_text(json.dumps(value))

    def rewrite_zip(self, change):
        """Re-hash outer transport to expose inner index validation failures."""
        manifest = self.manifest()
        data = b''.join((self.folder / p['file']).read_bytes() for p in manifest['parts'])
        with zipfile.ZipFile(io.BytesIO(data)) as source:
            entries = [(info.filename, source.read(info)) for info in source.infolist()]
        entries = change(entries)
        output = io.BytesIO()
        with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as target:
            for name, content in entries:
                target.writestr(name, content)
        data = output.getvalue()
        for part in manifest['parts']:
            (self.folder / part['file']).unlink()
        manifest['parts'] = []
        for offset in range(0, len(data), 127):
            block = data[offset:offset+127]
            path = self.folder / f'{self.name}.zip.part{len(manifest["parts"])+1:03}'
            path.write_bytes(block)
            manifest['parts'].append(dict(file=path.name, bytes=len(block), sha256=hashlib.sha256(block).hexdigest()))
        manifest.update(archive_bytes=len(data), archive_sha256=hashlib.sha256(data).hexdigest())
        self.save_manifest(manifest)

    def test_streaming_multipart_roundtrip_and_legacy_extract(self):
        manifest = self.build()
        self.assertGreater(len(manifest['parts']), 3)
        self.assertTrue(all(p['bytes'] == 127 for p in manifest['parts'][:-1]))
        self.assertFalse((self.root / 'archives/_work').exists())
        result = self.verify(verify_parts_only=True)
        self.assertEqual(result['verified_files'], 3)
        self.assertFalse(result['reassembled'])
        self.assertFalse((self.root / 'archives/_work').exists())
        for relative in self.expected:
            (self.root / relative).unlink()
        self.verify(extract=True)
        self.assertEqual({name: (self.root/name).read_bytes() for name in self.expected}, self.expected)

    def test_default_historical_build_and_verify_are_preserved(self):
        self.build(stream=False)
        archive = self.root / 'archives/_work' / (self.name + '.zip')
        self.assertTrue(archive.exists())
        self.assertEqual(self.verify()['verified_files'], 3)
        self.assertEqual(self.verify(verify_parts_only=True)['verified_files'], 3)

    def test_deduplicated_alias_entries_are_hash_verified(self):
        manifest = self.build(deduplicate=True)
        self.assertEqual(manifest['files'], 3)
        self.assertEqual(manifest['unique_entries'], 2)
        self.assertEqual(self.verify(verify_parts_only=True)['verified_files'], 3)

    def test_old_v1_manifest_without_dedup_fields_can_stream_verify(self):
        manifest = self.build(stream=False)
        manifest.pop('unique_entries'); manifest.pop('deduplicated')
        self.save_manifest(manifest)
        self.assertEqual(self.verify(verify_parts_only=True)['verified_files'], 3)

    def test_history_cannot_be_overwritten(self):
        self.build()
        before = (self.folder/'manifest.json').read_bytes()
        with self.assertRaises(FileExistsError):
            self.build()
        self.assertEqual((self.folder/'manifest.json').read_bytes(), before)

    def test_corrupt_part_bytes_are_rejected(self):
        manifest = self.build()
        part = self.folder / manifest['parts'][1]['file']
        value = bytearray(part.read_bytes()); value[13] ^= 0x80; part.write_bytes(value)
        with self.assertRaisesRegex(ValueError, 'Part checksum'):
            self.verify(verify_parts_only=True)

    def test_whole_zip_hash_is_not_replaced_by_valid_part_hashes(self):
        manifest = self.build()
        manifest['archive_sha256'] = '0'*64; self.save_manifest(manifest)
        with self.assertRaisesRegex(ValueError, 'Combined checksum'):
            self.verify(verify_parts_only=True)

    def test_missing_truncated_duplicate_and_unsafe_parts_are_rejected(self):
        manifest = self.build()
        original = json.loads(json.dumps(manifest))
        for kind in ('truncated', 'duplicate', 'unsafe', 'missing'):
            with self.subTest(kind=kind):
                changed = json.loads(json.dumps(original))
                if kind == 'truncated': changed['parts'][0]['bytes'] += 1
                if kind == 'duplicate': changed['parts'][1] = changed['parts'][0]
                if kind == 'unsafe': changed['parts'][0]['file'] = '../escape'
                if kind == 'missing': changed['parts'][0]['file'] = 'missing.part'
                self.save_manifest(changed)
                with self.assertRaises((ValueError, FileNotFoundError)):
                    self.verify(verify_parts_only=True)

    def test_bad_index_hash_rejected_even_with_valid_outer_zip(self):
        self.build()
        def change(entries):
            result = []
            for name, content in entries:
                if name == 'PCG-ARCHIVE-INDEX.json':
                    index = json.loads(content); index['fixture/a.bin']['sha256'] = '0'*64
                    content = json.dumps(index).encode()
                result.append((name, content))
            return result
        self.rewrite_zip(change)
        with self.assertRaisesRegex(ValueError, 'Entry checksum'):
            self.verify(verify_parts_only=True)

    def test_bad_index_count_and_undeclared_zip_entry_are_rejected(self):
        self.build()
        manifest = self.manifest(); manifest['files'] += 1; self.save_manifest(manifest)
        with self.assertRaisesRegex(ValueError, 'index count'):
            self.verify(verify_parts_only=True)
        manifest['files'] -= 1; self.save_manifest(manifest)
        self.rewrite_zip(lambda entries: entries + [('undeclared.txt', b'not indexed')])
        with self.assertRaisesRegex(ValueError, 'entry set'):
            self.verify(verify_parts_only=True)

    def test_virtual_seek_read_crosses_part_boundaries(self):
        manifest = self.build()
        expected = b''.join((self.folder/p['file']).read_bytes() for p in manifest['parts'])
        with restorer.JoinedParts(self.folder, manifest['parts']) as stream:
            stream.seek(120)
            self.assertEqual(stream.read(400), expected[120:520])
            stream.seek(-80, io.SEEK_END)
            self.assertEqual(stream.read(), expected[-80:])
            stream.seek(20); stream.seek(-5, io.SEEK_CUR)
            self.assertEqual(stream.read(30), expected[15:45])
            stream.seek(1000000); self.assertEqual(stream.read(), b'')
            with self.assertRaises(ValueError): stream.seek(-1)

    def test_no_reassembly_mode_cannot_extract_or_skip_entries(self):
        self.build()
        for kwargs in (dict(extract=True), dict(prefix='fixture/a')):
            with self.assertRaisesRegex(ValueError, 'requires no'):
                self.verify(verify_parts_only=True, **kwargs)


if __name__ == '__main__':
    unittest.main()
