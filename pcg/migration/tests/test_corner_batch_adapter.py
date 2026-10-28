"""Corner adaptation data checks; none of these tests certify real physics."""
import copy
import json
import unittest
from pathlib import Path
from pcg.migration import core, corners, corner_batch_adapter as adapter, godot_package

FIXTURES = (
    ('b31-n06-fourport-two-low-ingress','B','TOP_LEFT'),
    ('b31-n06-fourport-two-low-ingress','C','TOP_RIGHT'),
    ('game-forest-playful-module-variants-forked-bough-hh','basin','BOTTOM_RIGHT'),
    ('game-foundry-climb-change-height-base-v1-p0','entry','BOTTOM_LEFT'),
)


def fixture(module_id):
    path=core.resolve_artifact('modules/'+module_id+'/module.mapnote.json')
    cases=path.with_name('physics-input-cases.json')
    if not cases.exists():cases=path.with_name('cases.json')
    return core.read(path),core.read(cases)['cases']


def inside(point,rect):
    return rect[0] < point[0] < rect[0]+rect[2] and rect[1] < point[1] < rect[1]+rect[3]


class CornerBatchAdapterTests(unittest.TestCase):
    def test_all_four_actual_corner_directions_preserve_native_geometry_binding(self):
        for module_id,pid,corner in FIXTURES:
            with self.subTest(corner=corner):
                doc,cases=fixture(module_id)
                changed,new_cases,report=adapter.adapt_data(doc,cases,pid,corner)
                godot_package.audit_cases(changed,new_cases,require_replay=False)
                p=next(p for p in changed['generationContract']['ports']if p['id']==pid)
                expected=corners.options(doc,next(p for p in doc['generationContract']['ports']if p['id']==pid))[corner]
                self.assertEqual(p['position'],expected['targetPosition'])
                self.assertEqual(p['face'],expected['targetFace'])
                self.assertEqual(p['surface'],'ONE_WAY_PLATFORM')
                self.assertEqual(report['oldOpeningClosure'],None)
                self.assertEqual(report['retiredSidePolicy'],'preserve_geometry_no_extra_closure')

    def test_all_actual_assessed_options_preserve_original_actions_rewards_and_resources(self):
        inventory=core.read(core.STATE/'corner-port-inventory-v1.json');checked=0
        for row in inventory['rows']:
            if row['scope']!='current':continue
            document=core.read(core.resolve_artifact(row['source']))
            folder=core.resolve_artifact(row['source']).parent
            path=folder/'physics-input-cases.json'
            if not path.exists():path=folder/'cases.json'
            cases=core.read(path)['cases']
            for p in row['ports']:
                for corner,option in p['cornerRelocations'].items():
                    if not option.get('applicable')or option.get('allowed')!='UNKNOWN':continue
                    doc,new,report=adapter.adapt_data(document,cases,p['portId'],corner)
                    godot_package.audit_cases(doc,new,require_replay=False)
                    for before,after in zip(cases,new):
                        changed_fields={'platforms','ports','block_ports','one_way_platform_indices','wall_platform_indices','migration_boundary_plans','recorded_frames'}
                        self.assertEqual({k:v for k,v in before.items()if k not in changed_fields},
                                         {k:v for k,v in after.items()if k not in changed_fields})
                    self.assertEqual(doc['capabilityRequirements'],document['capabilityRequirements'])
                    self.assertEqual(doc['difficulty'],document['difficulty'])
                    self.assertEqual(doc['generationContract']['space']['bounds'],document['generationContract']['space']['bounds'])
                    self.assertEqual(doc['generationContract'].get('requiredNativeProfile'),document['generationContract'].get('requiredNativeProfile'))
                    self.assertEqual([r['requiredAbilities']for r in doc['generationContract']['routes']],
                                     [r['requiredAbilities']for r in document['generationContract']['routes']])
                    checked+=1
        self.assertGreater(checked,0)

    def test_no_new_solid_material_and_no_solid_loss_outside_corner_window(self):
        for module_id,pid,corner in FIXTURES:
            source,cases=fixture(module_id);doc,_,report=adapter.adapt_data(source,cases,pid,corner)
            before=[adapter._rect(o)for o in source['objects']if o['type']=='terrain'and not o.get('trackId')]
            after=[adapter._rect(o)for o in doc['objects']if o['type']=='terrain'and not o.get('trackId')]
            window=[report['conversionWindow'][k]for k in ('x','y','w','h')]
            xs=sorted({x for r in before+after+[window]for x in(r[0],r[0]+r[2])})
            ys=sorted({y for r in before+after+[window]for y in(r[1],r[1]+r[3])})
            for a,b in zip(xs,xs[1:]):
                for c,d in zip(ys,ys[1:]):
                    at=[(a+b)/2,(c+d)/2];had=any(inside(at,r)for r in before);has=any(inside(at,r)for r in after)
                    self.assertFalse(has and not had,'No new solid walls or islands may be added')
                    if not inside(at,window):self.assertEqual(had,has,'Original rock outside local window must remain')

    def test_input_is_immutable_and_only_selected_marker_moves(self):
        source,cases=fixture(FIXTURES[0][0]);saved=copy.deepcopy((source,cases))
        doc,new,report=adapter.adapt_data(source,cases,'B','TOP_LEFT')
        self.assertEqual((source,cases),saved)
        marker=next(p for p in source['generationContract']['ports']if p['id']=='B')['objectId']
        changed={o['id']:o for o in doc['objects']}
        for old in source['objects']:
            if old['type']!='terrain' and old['id']!=marker:self.assertEqual(old,changed[old['id']])
        for p in doc['generationContract']['ports']:
            if p['id']=='B':continue
            old=next(q for q in source['generationContract']['ports']if q['id']==p['id'])
            for key in ('position','normal','face','surface','permission'):
                self.assertEqual(p[key],old[key])

    def test_short_edge_dock_gets_only_local_full_body_one_way_extension(self):
        source,cases=fixture('game-challenge-ferry-ascent')
        doc,new,report=adapter.adapt_data(source,cases,'exit','TOP_RIGHT')
        port=next(p for p in doc['generationContract']['ports']if p['id']=='exit')
        dock=next(o for o in doc['objects']if o['id']==port['support']['objectId'])
        self.assertEqual(dock['w'],48)
        self.assertEqual(dock['x']+24,port['position'][0])
        self.assertEqual(dock['y'],report['originalSupport'][1])
        self.assertEqual(dock['type'],'platform')
        b=doc['generationContract']['space']['bounds']
        self.assertGreaterEqual(dock['x'],b['x']+b['w']-128)
        self.assertLessEqual(dock['x']+dock['w'],b['x']+b['w'])
        godot_package.audit_cases(doc,new,require_replay=False)

    def test_vertical_case_retires_only_selected_horizontal_controller_overrides(self):
        source,cases=fixture(FIXTURES[0][0]);case=cases[0]
        case['migration_boundary_plans']={'B':{'egress':[{'op':'wait','trigger':{'after':1}}]},'A':{'egress':[{'op':'wait','trigger':{'after':2}}]}}
        _,new,_=adapter.adapt_data(source,cases,'B','TOP_LEFT')
        self.assertNotIn('B',new[0]['migration_boundary_plans'])
        self.assertEqual(new[0]['migration_boundary_plans']['A'],case['migration_boundary_plans']['A'])

    def test_stable_configuration_ids_cannot_smuggle_paths(self):
        self.assertEqual(adapter.configuration_id('A','BOTTOM_LEFT'),'a-bottom-left-open-v2')
        self.assertNotIn('/',adapter.configuration_id('../A','BOTTOM_LEFT'))
        with self.assertRaisesRegex(adapter.AdaptationGap,'invalid_corner_selection'):
            adapter.configuration_id('A','NOT_A_CORNER')

    def test_noncorner_and_authoritative_output_rejected_before_mutation(self):
        source,cases=fixture(FIXTURES[0][0])
        with self.assertRaisesRegex(adapter.AdaptationGap,'not_on_requested_corner'):
            adapter.adapt_data(source,cases,'A','TOP_LEFT')
        for directory in (core.ACTIVE,core.RECYCLE):
            with self.assertRaisesRegex(ValueError,'outside_authoritative_archives'):
                adapter.prepare('missing-source',directory/'corner-test','A','BOTTOM_LEFT')


if __name__=='__main__':unittest.main()
