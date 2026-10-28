import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pcg.migration import corners, core


def document(width=3, height=2, origin=(-256, -128)):
    return dict(id='corner-fixture', generationContract=dict(contentVersion='sha256:'+'a'*64,
                foundation=dict(blockSize=128), space=dict(bounds=dict(x=origin[0], y=origin[1],
                w=128*width, h=128*height)), ports=[]))


class CornerTests(unittest.TestCase):
    def test_four_corner_pairs_both_directions_with_negative_origin(self):
        d = document()
        examples = [
            ('TOP_LEFT', 'LEFT', [-256, -64], 'TOP', [-192, -128]),
            ('TOP_RIGHT', 'RIGHT', [128, -64], 'TOP', [64, -128]),
            ('BOTTOM_LEFT', 'LEFT', [-256, 64], 'BOTTOM', [-192, 128]),
            ('BOTTOM_RIGHT', 'RIGHT', [128, 64], 'BOTTOM', [64, 128]),
        ]
        for corner, face, position, target, destination in examples:
            for source_face, source_position, target_face, target_position in (
                    (face, position, target, destination), (target, destination, face, position)):
                p = dict(id='p', face=source_face, position=source_position,
                         surface='ONE_WAY_PLATFORM', permission='INOUT')
                o = corners.options(d, p)[corner]
                self.assertTrue(o['applicable'])
                self.assertEqual(o['allowed'], 'UNKNOWN')
                self.assertEqual(o['targetFace'], target_face)
                self.assertEqual(o['targetPosition'], target_position)

    def test_single_block_has_two_distinct_nearest_options_for_one_port(self):
        d = document(1, 1)
        p = dict(face='LEFT', position=[-256, -64], surface='ROCK', permission='INPUT')
        o = corners.options(d, p)
        self.assertEqual([c for c, v in o.items() if v['applicable']], ['TOP_LEFT', 'BOTTOM_LEFT'])
        self.assertEqual(o['TOP_LEFT']['targetPosition'], [-192, -128])
        self.assertEqual(o['BOTTOM_LEFT']['targetPosition'], [-192, 0])
        self.assertEqual(o['BOTTOM_LEFT']['proposedSurface'], 'ONE_WAY_PLATFORM')

    def test_non_corner_and_internal_marker_are_not_candidates(self):
        d = document(3, 3)
        for face, position in [('LEFT', [-256, 64]), ('LEFT', [-244, -64]), ('TOP', [-64, -128])]:
            o = corners.options(d, dict(face=face, position=position, surface='ROCK', permission='INOUT'))
            self.assertTrue(all(v['allowed'] is False for v in o.values()))

    def test_rock_vertical_is_tooling_work_not_permission_by_marker(self):
        p = dict(face='LEFT', position=[-256, -64], surface='ROCK', permission='INOUT')
        row = corners.options(document(), p)['TOP_LEFT']
        self.assertEqual(row['proposedSurface'], 'ONE_WAY_PLATFORM')
        self.assertEqual(row['allowed'], 'UNKNOWN')
        self.assertIsNone(row['profileId'])

    def test_bottom_air_input_requires_actual_surface_adaptation(self):
        d = document()
        p = dict(face='LEFT', position=[-256, 64], surface='AIR', permission='INPUT')
        self.assertEqual(corners.options(d, p)['BOTTOM_LEFT']['proposedSurface'], 'ONE_WAY_PLATFORM')
        p['permission'] = 'OUTPUT'
        self.assertEqual(corners.options(d, p)['BOTTOM_LEFT']['proposedSurface'], 'AIR')

    def test_assessment_does_not_modify_frozen_document(self):
        d = document()
        d['generationContract']['ports'] = [dict(id='p', face='LEFT', position=[-256, -64],
                                               surface='ROCK', permission='INPUT')]
        before = copy.deepcopy(d)
        report = corners.assess_document(d)
        self.assertEqual(d, before)
        self.assertEqual(report['contentVersion'], d['generationContract']['contentVersion'])
        self.assertEqual(report['certifiedOptions'], 0)

    def test_annotation_resets_stale_certification_before_freeze(self):
        d = document()
        d['generationContract']['ports'] = [dict(id='p', face='LEFT', position=[-256, -64],
                                               surface='ROCK', permission='INPUT', cornerRelocations={'OLD': True})]
        d['generationContract']['portConfigurations'] = [{'id': 'stale'}]
        corners.annotate(d)
        self.assertEqual(d['generationContract']['portConfigurations'], [])
        self.assertEqual(d['generationContract']['ports'][0]['cornerRelocations']['TOP_LEFT']['allowed'], 'UNKNOWN')

    def test_external_receipt_cannot_rebind_changed_base_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);folder=root/'base';folder.mkdir()
            core.write(folder/'module.mapnote.json',document())
            with patch.object(core,'ACTIVE',root):
                with self.assertRaisesRegex(ValueError,'base_bytes_changed'):
                    corners.verified_receipts('base','0'*64,document()['generationContract']['contentVersion'])

    def test_stale_configuration_is_preserved_but_not_eligible(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);folder=root/'base';folder.mkdir()
            base=folder/'module.mapnote.json';core.write(base,document())
            core.write(folder/'port-configurations'/'old'/'receipt.json',dict(baseContentVersion='sha256:'+'b'*64,baseDocumentSha256=core.sha(base),allowed=True,technicalStatus='verified'))
            with patch.object(core,'ACTIVE',root):
                self.assertEqual(corners.verified_receipts('base',core.sha(base),document()['generationContract']['contentVersion']),[])

    def test_pass_fields_without_actual_configuration_artifact_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);folder=root/'base';folder.mkdir()
            base=folder/'module.mapnote.json';doc=document();core.write(base,doc)
            core.write(folder/'cases.json',dict(cases=[]))
            core.write(folder/'port-configurations'/'fake'/'receipt.json',dict(schema='pcg/corner-port-configuration/v1',
                       moduleId='base',baseContentVersion=doc['generationContract']['contentVersion'],baseDocumentSha256=core.sha(base),
                       basePhysicsInputSha256=core.sha(folder/'cases.json'),
                       allowed=True,technicalStatus='verified',configuration=dict(path='missing-test-artifact.json',sha256='0'*64)))
            with patch.object(core,'ACTIVE',root):
                with self.assertRaisesRegex(ValueError,'artifact_changed'):
                    corners.verified_receipts('base',core.sha(base),doc['generationContract']['contentVersion'])

    def test_unverified_preparation_cannot_write_into_current_or_recycle(self):
        from pcg.migration.corner_experiment import prepare
        for folder in (core.ACTIVE,core.RECYCLE):
            with self.assertRaisesRegex(ValueError,'outside_authoritative_archives'):
                prepare('missing-source-must-never-be-read',folder/'corner-negative-scope-fixture')

    def test_same_ability_names_cannot_hide_increased_native_air_capacity(self):
        with tempfile.TemporaryDirectory()as temporary:
            root=Path(temporary);folder=root/'base';folder.mkdir()
            base=folder/'module.mapnote.json';doc=document();doc['generationContract']['requiredNativeProfile']={'id':'air-one'};core.write(base,doc)
            inputs=folder/'cases.json';core.write(inputs,dict(cases=[]))
            target=folder/'port-configurations'/'bad-profile';target.mkdir(parents=True)
            changed=copy.deepcopy(doc);changed['generationContract']['requiredNativeProfile']={'id':'air-two'}
            core.write(target/'module.mapnote.json',changed);core.write(target/'godot-package.json',{})
            core.write(target/'receipt.json',dict(schema='pcg/corner-port-configuration/v1',moduleId='base',
                baseContentVersion=doc['generationContract']['contentVersion'],baseDocumentSha256=core.sha(base),basePhysicsInputSha256=core.sha(inputs),
                allowed=True,technicalStatus='verified',
                configuration=dict(path=str(target/'module.mapnote.json'),sha256=core.sha(target/'module.mapnote.json'),contentVersion=changed['generationContract']['contentVersion']),
                package=dict(path=str(target/'godot-package.json'),sha256=core.sha(target/'godot-package.json'))))
            with patch.object(core,'ACTIVE',root):
                with self.assertRaisesRegex(ValueError,'native_ability_resource_profile'):
                    corners.verified_receipts('base',core.sha(base),doc['generationContract']['contentVersion'])


if __name__ == '__main__':
    unittest.main()
