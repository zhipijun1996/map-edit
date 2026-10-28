"""Source fidelity checks; native gameplay remains real Godot evidence."""
import hashlib,json,unittest
from pathlib import Path
from pcg.migration import core,game_adapter,foundry_feedback_v5 as feedback

class FoundryFeedbackTests(unittest.TestCase):
    def test_original_driver_git_blobs(self):
        receipt=core.read(core.STATE/'original-foundry-driver-v5.json')
        self.assertEqual(receipt['sourceCommit'],game_adapter.COMMIT)
        for item in receipt['files']:
            source=(core.REPO/item['frozenSnapshotPath']).read_bytes()
            self.assertEqual(hashlib.sha1(b'blob '+str(len(source)).encode()+b'\0'+source).hexdigest(),item['gitBlob'])
            self.assertEqual(hashlib.sha256(source).hexdigest(),item['sha256'])

    def test_feedback_translation_covers_all_registered_components(self):
        rows=game_adapter.source_entries();resources={r['id']:r for r in rows if r['kind']=='resource'}
        used={n['module_id']for r in rows if r['kind']=='foundry'for n in r['data']['nodes']}
        self.assertEqual(len(used),10)
        for identity in used:
            for variant in(0,1):
                plan=feedback.component_plan(resources[identity],[0,0],0,variant)
                self.assertTrue(plan)
                self.assertTrue(all(c['op']in('axis','jump','jump_release','shoot','wait','settle')for c in plan))
                self.assertTrue(all('position'not in c for c in plan))

    def test_registered_profiles_are_native_source_profiles(self):
        rows=[r for r in game_adapter.source_entries()if r['kind']=='foundry']
        self.assertEqual(len(rows),54)
        self.assertEqual({r['data']['capability_profile']for r in rows},{'base','double_jump','air_chain'})
        # Six phrase templates and registered composites are not54 newfamilies.
        self.assertEqual(len(feedback.REPRESENTATIVES),6)

if __name__=='__main__':unittest.main()
