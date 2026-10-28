"""Structural open-corner policy negatives. Test doubles grant no certification."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from pcg.migration import core, corners


def documents():
    port = dict(id='P', objectId='marker', position=[0,64], normal=[-1,0], face='LEFT',
                surface='ROCK', permission='INOUT', support=dict(objectId='host'))
    base = dict(id='TEST-ONLY', capabilityRequirements={}, difficulty={}, objects=[
        dict(id='host',type='terrain',x=0,y=96,w=256,h=24),
        dict(id='marker',type='entry',x=0,y=64,w=0,h=0),
        dict(id='bell',type='bell',x=200,y=32,w=24,h=24)],
        generationContract=dict(contentVersion='sha256:'+'a'*64,foundation=dict(blockSize=128),
            space=dict(bounds=dict(x=0,y=0,w=256,h=128)), ports=[port],
            generation=dict(parameters={}), routes=[dict(id='main',**{'from':'P','to':'P'},requiredAbilities=['jump'])]))
    target = copy.deepcopy(base);target['generationContract']['contentVersion']='sha256:'+'b'*64
    target['objects'][0]['w']=40
    target['objects'] += [dict(id='dock',type='platform',x=40,y=96,w=48,h=24),
                          dict(id='right-rock',type='terrain',x=88,y=96,w=168,h=24)]
    target['objects'][1].update(x=64,y=0)
    target['generationContract']['ports'][0].update(position=[64,0],normal=[0,-1],face='TOP',surface='ONE_WAY_PLATFORM',support=dict(objectId='dock'))
    relocation=dict(portId='P',corner='TOP_LEFT',targetFace='TOP',targetPosition=[64,0],surface='ONE_WAY_PLATFORM',permission='INOUT')
    return base,target,[relocation]


class OpenCornerGeometryTests(unittest.TestCase):
    def test_local_one_way_window_and_rock_fragments_preserve_union(self):
        a,b,r=documents();before=copy.deepcopy((a,b,r))
        result=corners.verify_open_geometry(a,b,r)
        self.assertTrue(result['passed']);self.assertEqual((a,b,r),before)

    def test_narrow_source_bank_permits_short_body_dock_extension(self):
        a,b,r=documents();a['objects'][0].update(x=64,w=64)
        b['objects']=[o for o in b['objects'] if o['id'] not in ('host','right-rock')]
        b['objects'].append(dict(id='host',type='terrain',x=88,y=96,w=40,h=24))
        self.assertTrue(corners.verify_open_geometry(a,b,r)['passed'])

    def test_new_solid_in_old_air_is_not_allowed_even_in_local_window(self):
        a,b,r=documents();b['objects'].append(dict(id='wall',type='terrain',x=60,y=120,w=8,h=8))
        with self.assertRaisesRegex(ValueError,'added_solid'):corners.verify_open_geometry(a,b,r)

    def test_tall_retired_side_wall_cannot_be_relabelled_open_policy(self):
        a,b,r=documents();b['objects'].append(dict(id='wall',type='terrain',x=0,y=0,w=8,h=96))
        with self.assertRaisesRegex(ValueError,'outside_local'):corners.verify_open_geometry(a,b,r)

    def test_one_way_conversion_cannot_spread_outside_target_dock(self):
        a,b,r=documents();b['objects'][0]['type']='platform'
        with self.assertRaisesRegex(ValueError,'outside_local'):corners.verify_open_geometry(a,b,r)

    def test_other_reward_or_mechanism_is_not_editable(self):
        a,b,r=documents();b['objects'][2]['x']+=1
        with self.assertRaisesRegex(ValueError,'nonterrain_object_changed'):corners.verify_open_geometry(a,b,r)

    def test_new_mechanism_is_not_an_interface_adaptation(self):
        a,b,r=documents();b['objects'].append(dict(id='extra-bell',type='bell',x=64,y=64,w=12,h=12))
        with self.assertRaisesRegex(ValueError,'nonterrain_object_set'):corners.verify_open_geometry(a,b,r)

    def test_marker_metadata_is_not_editable(self):
        a,b,r=documents();b['objects'][1]['type']='exit'
        with self.assertRaisesRegex(ValueError,'nonterrain_object_changed'):corners.verify_open_geometry(a,b,r)


class OpenCornerReceiptTests(unittest.TestCase):
    def fixture(self,root):
        a,b,relocations=documents();base=root/'base';base.mkdir();target=base/'port-configurations/open';target.mkdir(parents=True)
        core.write(base/'module.mapnote.json',a);core.write(base/'cases.json',dict(cases=[]))
        core.write(target/'module.mapnote.json',b);core.write(target/'godot-package.json',{})
        adaptation=dict(schema='pcg/corner-interface-adaptation/v2',retiredSidePolicy=corners.OPEN_RETIRED_SIDE_POLICY,
            baseDocumentSha256=core.sha(base/'module.mapnote.json'),targetDocumentSha256=core.sha(target/'module.mapnote.json'),selectedPortId='P',corner='TOP_LEFT')
        core.write(target/'corner-adaptation.json',adaptation)
        receipt=dict(schema=corners.OPEN_RECEIPT_SCHEMA,moduleId='base',configurationId='open',
            baseDocumentSha256=core.sha(base/'module.mapnote.json'),baseContentVersion=a['generationContract']['contentVersion'],
            basePhysicsInputSha256=core.sha(base/'cases.json'),retiredSidePolicy=corners.OPEN_RETIRED_SIDE_POLICY,
            allowed=True,technicalStatus='verified',relocations=relocations,
            configuration=dict(path=str(target/'module.mapnote.json'),sha256=core.sha(target/'module.mapnote.json'),contentVersion=b['generationContract']['contentVersion']),
            package=dict(path=str(target/'godot-package.json'),sha256=core.sha(target/'godot-package.json')),
            adaptation=dict(path=str(target/'corner-adaptation.json'),sha256=core.sha(target/'corner-adaptation.json')),
            physicsReport=dict(path='TEST-DOUBLE-NOT-ACTUAL-PHYSICS',sha256='0'*64))
        core.write(target/'receipt.json',receipt)
        return base,target,a,b,receipt

    def test_v2_dispatch_still_requires_physics_and_native_but_not_closed_report(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);base,target,a,b,receipt=self.fixture(root)
            with patch.object(core,'REPO',root),patch.object(core,'ACTIVE',root),patch.object(core,'contract',return_value=dict(versionMatches=True)),patch('pcg.migration.physics.verify_report') as physics,patch('pcg.migration.godot_package.verify_package') as native,patch('pcg.migration.corner_experiment.verify_closed') as closed:
                result=corners.verified_receipts('base',core.sha(base/'module.mapnote.json'),a['generationContract']['contentVersion'])
                self.assertEqual(len(result),1);physics.assert_called_once();native.assert_called_once_with(target,require_loaded=True);closed.assert_not_called()

    def test_v1_dispatch_keeps_legacy_closed_verifier(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);base,target,a,b,r=self.fixture(root);r['schema']='pcg/corner-port-configuration/v1';r['retiredOpeningReport']={'testOnly':True};core.write(target/'receipt.json',r)
            with patch.object(core,'REPO',root),patch.object(core,'ACTIVE',root),patch.object(core,'contract',return_value=dict(versionMatches=True)),patch('pcg.migration.physics.verify_report'),patch('pcg.migration.godot_package.verify_package'),patch('pcg.migration.corner_experiment.verify_closed') as closed:
                corners.verified_receipts('base',core.sha(base/'module.mapnote.json'),a['generationContract']['contentVersion'])
                closed.assert_called_once_with(target,r['retiredOpeningReport'])

    def test_v2_policy_or_relabelled_legacy_report_is_rejected(self):
        for field,value in [('retiredSidePolicy','closed'),('retiredOpeningReport',{})]:
            with self.subTest(field=field),tempfile.TemporaryDirectory() as d:
                root=Path(d);base,target,a,b,r=self.fixture(root);r[field]=value;core.write(target/'receipt.json',r)
                with patch.object(core,'REPO',root),patch.object(core,'ACTIVE',root),patch.object(core,'contract',return_value=dict(versionMatches=True)),patch('pcg.migration.physics.verify_report'),patch('pcg.migration.godot_package.verify_package'):
                    with self.assertRaisesRegex(ValueError,'retired_side_policy|relabel_legacy'):corners.verified_receipts('base',core.sha(base/'module.mapnote.json'),a['generationContract']['contentVersion'])

    def test_adaptation_hash_or_document_identity_cannot_be_forged(self):
        for broken in ('hash','target'):
            with self.subTest(broken=broken),tempfile.TemporaryDirectory() as d:
                root=Path(d);base,target,a,b,r=self.fixture(root)
                if broken=='hash':r['adaptation']['sha256']='0'*64
                else:
                    data=core.read(target/'corner-adaptation.json');data['targetDocumentSha256']='0'*64;core.write(target/'corner-adaptation.json',data);r['adaptation']['sha256']=core.sha(target/'corner-adaptation.json')
                core.write(target/'receipt.json',r)
                with patch.object(core,'REPO',root),patch.object(core,'ACTIVE',root),patch.object(core,'contract',return_value=dict(versionMatches=True)),patch('pcg.migration.physics.verify_report'),patch('pcg.migration.godot_package.verify_package'):
                    with self.assertRaisesRegex(ValueError,'missing_or_changed|not_bound'):corners.verified_receipts('base',core.sha(base/'module.mapnote.json'),a['generationContract']['contentVersion'])

    def test_physics_failure_never_grants_open_permission(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);base,target,a,b,r=self.fixture(root)
            with patch.object(core,'REPO',root),patch.object(core,'ACTIVE',root),patch.object(core,'contract',return_value=dict(versionMatches=True)),patch('pcg.migration.physics.verify_report',side_effect=ValueError('TEST physics failure')),patch('pcg.migration.godot_package.verify_package') as native:
                with self.assertRaisesRegex(ValueError,'physics failure'):corners.verified_receipts('base',core.sha(base/'module.mapnote.json'),a['generationContract']['contentVersion'])
                native.assert_not_called()


REAL_FORKED = core.ACTIVE/'game-forest-playful-module-variants-forked-bough-hh'


@unittest.skipUnless((REAL_FORKED/'module.mapnote.json').is_file(), 'Restore the actual migrated forked-bough Module')
class ActualForkedDockClearancePolicy(unittest.TestCase):
    """Actual source geometry, policy only; no physical success is inferred."""
    def fixture(self, drop=8):
        from pcg.migration.corner_batch_adapter import adapt_data
        base=core.read(REAL_FORKED/'module.mapnote.json')
        inputs=REAL_FORKED/'physics-input-cases.json'
        if not inputs.exists():inputs=REAL_FORKED/'cases.json'
        target,_,_=adapt_data(base,core.read(inputs)['cases'],'basin','BOTTOM_RIGHT')
        port=next(p for p in target['generationContract']['ports'] if p['id']=='basin')
        dock=next(o for o in target['objects'] if o['id']==port['support']['objectId'])
        dock['y']+=drop;dock['h']-=drop;port['stagingPosition'][1]+=drop
        return base,target,[dict(portId='basin',corner='BOTTOM_RIGHT')],dock

    def test_lowering_short_dock_by_eight_or_sixteen_does_not_require_roof_edit(self):
        for drop in (8,16):
            with self.subTest(drop=drop):
                base,target,relocations,dock=self.fixture(drop)
                self.assertTrue(corners.verify_open_geometry(base,target,relocations)['passed'])
                old_roof=next(o for o in base['objects'] if o.get('x')==880 and o.get('y')==220 and o.get('w')==80)
                new_roof=next(o for o in target['objects'] if o['id']==old_roof['id'])
                self.assertEqual(old_roof,new_roof)
                self.assertEqual(dock['y']-(old_roof['y']+old_roof['h']),30+drop)
                self.assertEqual(dock['y']+dock['h'],306)

    def test_roof_motion_is_rejected_even_when_dock_lowering_is_allowed(self):
        base,target,relocations,dock=self.fixture()
        roof=next(o for o in target['objects'] if o.get('x')==880 and o.get('y')==220 and o.get('w')==80)
        roof['y']-=8
        with self.assertRaisesRegex(ValueError,'outside_local'):corners.verify_open_geometry(base,target,relocations)

    def test_lowering_must_not_extend_collision_beyond_same_corner_block(self):
        base,target,relocations,dock=self.fixture();dock['h']+=8
        with self.assertRaisesRegex(ValueError,'outside_local'):corners.verify_open_geometry(base,target,relocations)

    def test_solid_side_wall_remains_forbidden_on_real_forked_geometry(self):
        base,target,relocations,dock=self.fixture()
        target['objects'].append(dict(id='TEST-FORBIDDEN-WALL',type='terrain',x=1016,y=242,w=8,h=40))
        with self.assertRaisesRegex(ValueError,'outside_local|added_solid'):corners.verify_open_geometry(base,target,relocations)


if __name__=='__main__':unittest.main()
