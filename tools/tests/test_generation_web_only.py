"""Web-only verification is explicit; default archive checks remain mandatory."""
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools import check_generation


class GenerationWebOnlyTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  self.context=patch.object(check_generation,'ROOT',self.root);self.context.start()
  video=self.root/'generation/videos/fixture';video.mkdir(parents=True)
  data=b'\x00\x00\x00\x10ftypfixture';(video/'combined.mp4').write_bytes(data)
  (video/'manifest.json').write_text(json.dumps(dict(playback_speed=1,physics_hz=60,approved_offline=0,clips=[],combined=dict(file='combined.mp4',bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))))
  summary=self.root/'pcg/results/guided-landing-v2/summary.json';summary.parent.mkdir(parents=True)
  summary.write_text(json.dumps(dict(arms={'fixture':{'parents':6}},approved_offline=0,human_video_feedback=0)))
  archive=self.root/'pcg/archives/fixture';archive.mkdir(parents=True)
  payload=b'fixture archive bytes';(archive/'part001').write_bytes(payload)
  self.manifest=archive/'manifest.json'
  self.record=dict(parts=[dict(file='part001',bytes=len(payload),sha256=hashlib.sha256(payload).hexdigest())],archive_bytes=len(payload),archive_sha256=hashlib.sha256(payload).hexdigest())
  self.manifest.write_text(json.dumps(self.record))
 def tearDown(self):self.context.stop();self.tmp.cleanup()
 def call(self,web_only=False):
  with redirect_stdout(io.StringIO()):return check_generation.run(web_only)
 def test_default_checks_archives_and_video(self):
  result=self.call();self.assertEqual(result['archive_parts_verified'],1);self.assertEqual(result['archive_validation'],'VERIFIED');self.assertEqual(result['videos_verified'],1)
 def test_default_rejects_corrupt_archive(self):
  self.record['parts'][0]['sha256']='0'*64;self.manifest.write_text(json.dumps(self.record))
  with self.assertRaises(AssertionError):self.call()
 def test_web_only_omission_is_explicit_even_with_bad_archive(self):
  self.record['parts'][0]['sha256']='0'*64;self.manifest.write_text(json.dumps(self.record))
  result=self.call(True);self.assertEqual(result['archive_parts_verified'],0);self.assertEqual(result['archive_validation'],'NOT_RUN_WEB_ONLY');self.assertEqual(result['videos_verified'],1)
 def test_web_only_still_rejects_corrupt_video(self):
  (self.root/'generation/videos/fixture/combined.mp4').write_bytes(b'wrong bytes')
  with self.assertRaises(AssertionError):self.call(True)


if __name__=='__main__':unittest.main()
