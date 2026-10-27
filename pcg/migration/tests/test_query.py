"""Static selector adversaries; mocked validation is not Module certification.

Configuration fixtures below exercise selection and durable artifact plumbing.
They are explicit test doubles, not actual Godot certificates or library content.
"""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from pcg.migration import core, corners
from pcg.migration.query import find, _reasons, _physical_port_groups


class RetrievalGuards(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name); self.addCleanup(patch.stopall)
        self.active = self.root/'modules'; self.folder = self.active/'fixture'
        patch.multiple(core, REPO=self.root, ACTIVE=self.active, JOURNAL=self.root/'state/ledger.json').start()
        self.validation = patch.object(core, 'validate', return_value={
            'mapReady': False, 'certifiedClosureProfiles': [], 'certifiedMirror': False}).start()
        self.configuration_verifier = patch.object(corners, 'verified_receipts', return_value=[]).start()
        self.row = {'id': 'fixture', 'moduleId': 'fixture', 'file': './modules/fixture/module.mapnote.json',
            'contentVersion': 'sha256:'+'a'*64, 'mapReady': True, 'humanReview': 'UNKNOWN', 'unresolved': ['Map']}
        self.gc = {'contentVersion': self.row['contentVersion'], 'foundation': {'blockSize': 128},
            'space': {'bounds': {'x': 0, 'y': 0, 'w': 512, 'h': 256}},
            'ports': [dict(id='A', normal=[-1, 0], position=[0, 64], face='LEFT', surface='ROCK', permission='INOUT'),
                      dict(id='B', normal=[1, 0], position=[512, 64], face='RIGHT', surface='ROCK', permission='INOUT')],
            'routes': [{'id': 'main', 'from': 'A', 'to': 'B', 'requiredAbilities': ['move', 'jump', 'shot_recoil']}],
            'relations': [{'from': a, 'to': b, 'status': 'path' if (a, b) == ('A', 'B') else 'UNKNOWN',
                           'routeIds': ['main'] if (a, b) == ('A', 'B') else []} for a in ('A', 'B') for b in ('A', 'B')],
            'closures': [], 'mirror': {'status': 'verified'}}
        self.doc = {'id': 'fixture', 'generationContract': self.gc}
        core.write(self.folder/'physics-input-cases.json', dict(cases=[dict(id='TEST-ONLY-canonical',
            capabilities=self.gc['routes'][0]['requiredAbilities'][:], route_spec=dict(id='main'))]))
        self.save_base()
        self.spec = {'abilities': ['move', 'jump', 'shot_recoil'], 'relations': [{'from': 'A', 'to': 'B'}]}

    def save_base(self):
        core.write(self.folder/'module.mapnote.json', self.doc)
        self.row['contentSha256'] = core.sha(self.folder/'module.mapnote.json')
        core.write(self.active/'catalog.json', {'modules': [self.row]})

    def add_configuration(self, ident='left-up', port_id='A'):
        """Write a fake certified-whole-profile fixture for selector tests only."""
        doc = copy.deepcopy(self.doc); gc = doc['generationContract']
        gc['contentVersion'] = 'sha256:'+('b' if port_id == 'A' else 'c')*64
        port = next(p for p in gc['ports'] if p['id'] == port_id)
        port.update(normal=[0, -1], face='TOP', surface='ONE_WAY_PLATFORM',
                    position=[64 if port_id == 'A' else 448, 0])
        folder = self.folder/'port-configurations'/ident
        core.write(folder/'module.mapnote.json', doc)
        core.write(folder/'physics-input-cases.json', core.read(self.folder/'physics-input-cases.json'))
        receipt = dict(schema='TEST-DOUBLE-NOT-ACTUAL-CERTIFICATE', moduleId='fixture', configurationId=ident,
            baseContentVersion=self.row['contentVersion'], baseDocumentSha256=self.row['contentSha256'],
            relocations=[dict(portId=port_id, corner='TOP_LEFT' if port_id == 'A' else 'TOP_RIGHT')],
            configuration=dict(path=core.relative(folder/'module.mapnote.json'),
                sha256=core.sha(folder/'module.mapnote.json'), contentVersion=gc['contentVersion']))
        core.write(folder/'receipt.json', receipt)
        artifact = dict(path=core.relative(folder/'receipt.json'), sha256=core.sha(folder/'receipt.json'))
        self.configuration_verifier.return_value.append(artifact)
        return folder, doc, receipt

    def require_native_profile(self):
        profile = dict(id='air_chain', overrides={'max_jumps': 2, 'max_air_shots': 4},
            abilities=['jump', 'double_jump', 'shot_recoil', 'multi_air_shot'],
            effectiveTuning={'max_jumps': 2, 'max_air_shots': 4})
        self.gc['requiredNativeProfile'] = copy.deepcopy(profile)
        self.gc['generation'] = {'parameters': {'original_tuning_profile': copy.deepcopy(profile)}}
        self.gc['routes'][0]['requiredAbilities'].append('double_jump')
        self.spec['abilities'].extend(['double_jump', 'multi_air_shot'])
        core.write(self.folder/'physics-input-cases.json', dict(cases=[dict(id='TEST-ONLY-native-input',
            capabilities=self.gc['routes'][0]['requiredAbilities'][:], route_spec=dict(id='main'))]))
        self.save_base()
        return profile

    def require_oneway_initial_capabilities(self):
        caps = ['move', 'wall_climb']
        self.gc['ports'][0].update(permission='INPUT', face='TOP', normal=[0, -1],
            position=[64, 0], surface='ONE_WAY_PLATFORM',
            initialPermissionConditions=dict(availableAbilitiesExact=caps[:],
                requiresRevalidationWithAdditionalUpwardAbilities=True))
        self.gc['routes'][0]['requiredAbilities'] = caps[:]
        self.gc['validations'] = [dict(id='TEST-ONLY-physics-main', kind='physics', result='pass',
            contentVersion=self.gc['contentVersion'], routeId='main',
            capabilityConfiguration=dict(available=caps[:]),
            artifacts=[dict(path='TEST-ONLY-NOT-A-PHYSICS-CERTIFICATE', sha256='0'*64)])]
        core.write(self.folder/'physics-input-cases.json', dict(cases=[dict(id='TEST-ONLY-input',
            capabilities=caps[:], route_spec=dict(id='main'))]))
        self.spec['abilities'] = caps[:]
        self.save_base()
        return caps

    def test_catalog_boolean_cannot_claim_map_certification(self):
        self.assertEqual(find(self.spec)['status'], 'unsatisfied')

    def test_explicit_scoped_retrieval_can_match(self):
        result = find(self.spec, allow_scoped=True)
        self.assertEqual(result['status'], 'matched')
        match = result['matches'][0]
        self.assertEqual(match['portConfigurationId'], 'base')
        self.assertEqual(match['baseContentVersion'], self.row['contentVersion'])
        self.assertEqual(match['ports'], self.gc['ports'])

    def test_mirror_flag_cannot_substitute_for_measured_orientation(self):
        self.spec['mirror_x'] = True
        self.assertEqual(find(self.spec, allow_scoped=True)['status'], 'unsatisfied')

    def test_partial_connections_need_real_closure_coverage(self):
        self.spec['connected_ports'] = ['A']
        self.assertEqual(find(self.spec, allow_scoped=True)['status'], 'unsatisfied')

    def add_coincident_alias(self):
        alias = copy.deepcopy(self.gc['ports'][1]); alias['id'] = 'B_alias'
        self.gc['ports'].append(alias)
        self.save_base()

    def test_logical_aliases_cannot_inflate_physical_port_count(self):
        self.add_coincident_alias()
        self.spec['ports'] = {'count': 3}
        result = find(self.spec, allow_scoped=True)
        self.assertEqual(result['status'], 'unsatisfied')
        conflict = result['conflicts'][0]
        self.assertIn('requested_physical_port_count_mismatch:3!=2', conflict['reasons'])
        self.assertIn('coincident_logical_ports_need_alias_normalization:B,B_alias', conflict['reasons'])
        self.assertEqual(conflict['physicalPortCount'], 2)
        self.assertEqual(conflict['coincidentPortGroups'], [dict(position=[512, 64], face='RIGHT', logicalNames=['B', 'B_alias'])])

    def test_correct_physical_count_still_does_not_certify_joint_aliases(self):
        self.add_coincident_alias()
        self.spec['ports'] = {'count': 2}
        result = find(self.spec, allow_scoped=True)
        self.assertEqual(result['status'], 'unsatisfied')
        self.assertIn('coincident_logical_ports_need_alias_normalization:B,B_alias', result['conflicts'][0]['reasons'])
        self.assertFalse(any(r.startswith('requested_physical_port_count_mismatch:') for r in result['conflicts'][0]['reasons']))

    def test_selecting_one_alias_keeps_original_route_and_closure_guards(self):
        self.add_coincident_alias()
        self.spec.update(connected_ports=['A', 'B'], ports={'count': 2})
        result = find(self.spec, allow_scoped=True)
        self.assertEqual(result['status'], 'unsatisfied')
        self.assertNotIn('coincident_logical_ports_need_alias_normalization:B,B_alias', result['conflicts'][0]['reasons'])
        self.assertIn('requested_partial_connection_closure_not_certified', result['conflicts'][0]['reasons'])
        # A test-only already-verified closure permits the same existing route;
        # the selector itself never manufactures such a certificate.
        self.gc['closures'] = [dict(id='test-only-C-closed', closedPorts=['B_alias'], routeIds=['main'])]
        self.validation.return_value['certifiedClosureProfiles'] = ['test-only-C-closed']
        self.save_base()
        self.assertEqual(find(self.spec, allow_scoped=True)['status'], 'matched')

    def test_unknown_size_is_a_gap_not_a_silent_default(self):
        self.spec['space'] = {'max_width': 'UNKNOWN'}
        result = find(self.spec, allow_scoped=True)
        self.assertEqual(result['status'], 'unsatisfied')
        self.assertEqual(result['conflicts'][0]['field'], 'space.max_width')

    def test_normals_automatically_select_actual_certified_configuration(self):
        folder, doc, _ = self.add_configuration()
        self.spec['ports'] = {'required_normals': [[0, -1], [1, 0]]}
        result = find(self.spec, allow_scoped=True)
        self.assertEqual([m['portConfigurationId'] for m in result['matches']], ['left-up'])
        match = result['matches'][0]
        self.assertEqual(match['id'], 'fixture'); self.assertEqual(match['baseModuleId'], 'fixture')
        self.assertEqual(match['baseContentVersion'], self.row['contentVersion'])
        self.assertEqual(match['contentVersion'], doc['generationContract']['contentVersion'])
        self.assertEqual(match['ports'], doc['generationContract']['ports'])
        self.assertEqual(match['scene'], core.relative(folder/'module.tscn'))
        self.assertEqual(self.validation.call_count, 1, 'Validate the base once, not once per alternative')
        self.assertEqual(self.configuration_verifier.call_count, 1)

    def test_explicit_configuration_and_explicit_base_selection(self):
        self.add_configuration(); self.spec['port_configuration_id'] = 'left-up'
        result = find(self.spec, allow_scoped=True)
        self.assertEqual([m['portConfigurationId'] for m in result['matches']], ['left-up'])
        self.configuration_verifier.reset_mock(); self.spec['port_configuration_id'] = 'base'
        result = find(self.spec, allow_scoped=True)
        self.assertEqual([m['portConfigurationId'] for m in result['matches']], ['base'])
        self.configuration_verifier.assert_not_called()

    def test_default_expands_verified_whole_configurations_only(self):
        self.add_configuration()
        result = find(self.spec, allow_scoped=True)
        self.assertEqual([m['portConfigurationId'] for m in result['matches']], ['base', 'left-up'])
        self.assertEqual(result['searched']['currentTemplates'], 1)
        self.assertEqual(result['searched']['portConfigurations'], 2)
        self.assertEqual(self.validation.call_count, 1)

    def test_metadata_hold_is_honored_even_if_catalog_was_not_rebuilt(self):
        self.add_configuration(); core.write(self.folder/'migration.json', {'humanReview': 'design_hold'})
        self.assertEqual(find(self.spec, allow_scoped=True)['status'], 'unsatisfied')
        self.configuration_verifier.assert_not_called()

    def test_unknown_assessments_and_unverified_receipts_do_not_expand(self):
        self.add_configuration()
        # A JSON file and an input boolean cannot substitute for helper approval.
        self.configuration_verifier.return_value = []
        self.gc['ports'][0]['cornerRelocations'] = {'TOP_LEFT': {'allowed': 'UNKNOWN'}}
        self.save_base(); self.spec['ports'] = {'required_normals': [[0, -1], [1, 0]]}
        result = find(self.spec, allow_scoped=True)
        self.assertEqual(result['status'], 'unsatisfied'); self.assertEqual(result['searched']['certifiedAlternatives'], 0)
        self.spec['port_configuration_id'] = 'left-up'
        result = find(self.spec, allow_scoped=True)
        self.assertTrue(any('port_configuration_not_certified_or_unknown:left-up' in c['reasons'] for c in result['conflicts']))

    def test_two_individually_certified_changes_are_not_implicitly_combined(self):
        self.add_configuration('left-up', 'A'); self.add_configuration('right-up', 'B')
        self.spec['ports'] = {'required_normals': [[0, -1], [0, -1]]}
        result = find(self.spec, allow_scoped=True)
        self.assertEqual(result['status'], 'unsatisfied')
        self.assertEqual(result['searched']['certifiedAlternatives'], 2)
        self.assertEqual(len(result['conflicts']), 3, 'Only base and two frozen whole configurations were searched')

    def test_corner_configuration_keeps_map_mirror_and_closure_unknown(self):
        self.add_configuration(); self.spec['port_configuration_id'] = 'left-up'
        self.validation.return_value = {'mapReady': True, 'certifiedMirror': True, 'certifiedClosureProfiles': ['close-B']}
        self.assertEqual(find(self.spec)['status'], 'unsatisfied', 'Base Map certification does not certify an adapted configuration')
        self.spec['mirror_x'] = True
        self.assertEqual(find(self.spec, allow_scoped=True)['status'], 'unsatisfied')

    def test_human_hold_cannot_be_bypassed_with_configuration(self):
        self.add_configuration(); self.row['humanReview'] = 'design_hold'; self.save_base()
        self.spec['port_configuration_id'] = 'left-up'
        result = find(self.spec, allow_scoped=True)
        self.assertEqual(result['status'], 'unsatisfied')
        self.configuration_verifier.assert_not_called()

    def test_direction_unknown_and_missing_abilities_still_reject_configuration(self):
        self.add_configuration(); self.spec['port_configuration_id'] = 'left-up'
        self.spec['relations'] = [{'from': 'B', 'to': 'A'}]
        self.assertEqual(find(self.spec, allow_scoped=True)['status'], 'unsatisfied')
        self.spec['relations'] = [{'from': 'A', 'to': 'B'}]; self.spec['abilities'] = ['move']
        self.assertEqual(find(self.spec, allow_scoped=True)['status'], 'unsatisfied')

    def test_metadata_cannot_override_actual_initial_permissions_or_size(self):
        folder, doc, _ = self.add_configuration(); self.spec['port_configuration_id'] = 'left-up'
        doc['generationContract']['ports'][0]['permission'] = 'OUTPUT'
        core.write(folder/'module.mapnote.json', doc)
        # The verifier is mocked to approve this static fixture deliberately;
        # query must still respect its actual declared initial permissions.
        receipt = core.read(folder/'receipt.json')
        receipt['configuration']['sha256'] = core.sha(folder/'module.mapnote.json')
        core.write(folder/'receipt.json', receipt)
        self.configuration_verifier.return_value[0]['sha256'] = core.sha(folder/'receipt.json')
        result = find(self.spec, allow_scoped=True)
        self.assertEqual(result['status'], 'unsatisfied')
        self.assertTrue(any('requested_pair_violates_initial_port_permissions:A->B' in c['reasons'] for c in result['conflicts']))
        self.spec['relations'] = []; self.spec['space'] = {'max_width': 128}
        self.assertEqual(find(self.spec, allow_scoped=True)['status'], 'unsatisfied')

    def test_catalog_identity_and_configuration_receipt_tampering_reject(self):
        self.row['contentSha256'] = '0'*64
        core.write(self.active/'catalog.json', {'modules': [self.row]})
        with self.assertRaisesRegex(ValueError, 'catalog_module_identity'):
            find(self.spec, allow_scoped=True)
        self.save_base(); folder, _, _ = self.add_configuration()
        (folder/'receipt.json').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'missing_or_changed_evidence'):
            find(self.spec, allow_scoped=True)

    def test_invalid_configuration_selection_is_not_silent_default(self):
        for value in ('UNKNOWN', '', [], None):
            with self.subTest(value=value):
                self.spec['port_configuration_id'] = value
                result = find(self.spec, allow_scoped=True)
                self.assertEqual(result['status'], 'unsatisfied')
                self.assertEqual(result['conflicts'][0]['field'], 'port_configuration_id')

    def test_native_profile_is_required_even_with_identical_available_abilities(self):
        self.require_native_profile()
        result = find(self.spec, allow_scoped=True)
        self.assertEqual(result['status'], 'unsatisfied')
        self.assertIn('initial_profile_required:air_chain', result['conflicts'][0]['reasons'])
        # Both requests have the exact same ability vector. A two-jump profile
        # with another air-shot capacity cannot inherit the four-shot witness.
        self.spec['initial_profile'] = 'double_jump'
        result = find(self.spec, allow_scoped=True)
        self.assertEqual(result['status'], 'unsatisfied')
        self.assertIn('initial_profile_mismatch:double_jump!=air_chain', result['conflicts'][0]['reasons'])

    def test_correct_native_profile_returns_exact_selected_tuning_requirement(self):
        profile = self.require_native_profile(); self.spec['initial_profile'] = 'air_chain'
        result = find(self.spec, allow_scoped=True)
        self.assertEqual(result['status'], 'matched')
        self.assertEqual(result['matches'][0]['requiredNativeProfile'], profile)

    def test_unknown_or_partial_native_profile_is_not_an_identity_match(self):
        self.require_native_profile()
        for value in ('UNKNOWN', None, {}, {'id': 'air_chain', 'effectiveTuning': {'max_air_shots': 2}}, []):
            with self.subTest(value=value):
                self.spec['initial_profile'] = value
                result = find(self.spec, allow_scoped=True)
                self.assertEqual(result['status'], 'unsatisfied')
                self.assertEqual(result['conflicts'][0]['field'], 'initial_profile')

    def test_native_generation_binding_cannot_be_bypassed_by_missing_convenience_field(self):
        self.require_native_profile(); self.gc.pop('requiredNativeProfile'); self.save_base()
        self.assertEqual(find(self.spec, allow_scoped=True)['status'], 'unsatisfied')
        self.spec['initial_profile'] = 'air_chain'
        self.assertEqual(find(self.spec, allow_scoped=True)['status'], 'matched')

    def test_native_profile_declaration_mismatch_or_unknown_capacities_reject(self):
        self.require_native_profile(); self.spec['initial_profile'] = 'air_chain'
        self.gc['requiredNativeProfile']['effectiveTuning']['max_air_shots'] = 2; self.save_base()
        result = find(self.spec, allow_scoped=True)
        self.assertEqual(result['status'], 'unsatisfied')
        self.assertIn('native_profile_declaration_mismatch', result['conflicts'][0]['reasons'])
        profile = self.gc['requiredNativeProfile']
        profile['effectiveTuning']['max_air_shots'] = 'UNKNOWN'
        self.gc['generation']['parameters']['original_tuning_profile'] = copy.deepcopy(profile); self.save_base()
        result = find(self.spec, allow_scoped=True)
        self.assertEqual(result['status'], 'unsatisfied')
        self.assertIn('required_native_profile_effective_tuning_unknown', result['conflicts'][0]['reasons'])

    def test_corner_configuration_respects_its_own_native_profile_requirement(self):
        profile = self.require_native_profile(); self.add_configuration()
        self.spec['port_configuration_id'] = 'left-up'
        self.assertEqual(find(self.spec, allow_scoped=True)['status'], 'unsatisfied')
        self.spec['initial_profile'] = 'air_chain'
        result = find(self.spec, allow_scoped=True)
        self.assertEqual(result['status'], 'matched')
        self.assertEqual(result['matches'][0]['requiredNativeProfile'], profile)

    def test_ordinary_corner_query_needs_no_native_profile(self):
        self.add_configuration(); self.spec['ports'] = {'required_normals': [[0, -1], [1, 0]]}
        result = find(self.spec, allow_scoped=True)
        self.assertEqual([m['portConfigurationId'] for m in result['matches']], ['left-up'])
        self.assertIsNone(result['matches'][0]['requiredNativeProfile'])

    def test_oneway_port_accepts_exact_actual_initial_ability_set(self):
        caps = self.require_oneway_initial_capabilities()
        # Ability order and duplicate names do not change the available set.
        self.spec['abilities'] = ['wall_climb', 'move', 'move']
        result = find(self.spec, allow_scoped=True)
        self.assertEqual(result['status'], 'matched')
        match = result['matches'][0]
        self.assertEqual(match['testedInitialAbilityConfigurations'], [caps])
        self.assertEqual(match['ports'][0]['initialPermissionConditions'],
                         self.gc['ports'][0]['initialPermissionConditions'])

    def test_oneway_port_does_not_inherit_certificate_with_additional_abilities(self):
        self.require_oneway_initial_capabilities()
        for abilities in (['move'], ['move', 'wall_climb', 'jump'],
                          ['move', 'wall_climb', 'jump', 'shot_recoil']):
            with self.subTest(abilities=abilities):
                self.spec['abilities'] = abilities
                result = find(self.spec, allow_scoped=True)
                self.assertEqual(result['status'], 'unsatisfied')
                self.assertIn('initial_permission_ability_configuration_not_certified', result['conflicts'][0]['reasons'])

    def test_oneway_current_validation_must_have_current_version_and_real_scope(self):
        self.require_oneway_initial_capabilities()
        saved = copy.deepcopy(self.gc['validations'][0])
        for mutate in (lambda v: v.update(contentVersion='sha256:'+'f'*64),
                       lambda v: v.update(result='UNKNOWN'), lambda v: v.update(kind='static'),
                       lambda v: v.update(artifacts=[]), lambda v: v.update(routeId='another-route')):
            self.gc['validations'][0] = copy.deepcopy(saved); mutate(self.gc['validations'][0]); self.save_base()
            result = find(self.spec, allow_scoped=True)
            self.assertEqual(result['status'], 'unsatisfied')
            self.assertIn('initial_permission_ability_configuration_not_certified', result['conflicts'][0]['reasons'])

    def test_oneway_metadata_cannot_forge_a_higher_actual_input_capability_set(self):
        caps = self.require_oneway_initial_capabilities(); higher = caps+['jump']
        self.spec['abilities'] = higher
        self.gc['ports'][0]['initialPermissionConditions']['availableAbilitiesExact'] = higher
        self.gc['validations'][0]['capabilityConfiguration']['available'] = higher
        self.gc['ports'][0]['initialPermissionCertified'] = True
        # A forged replay declaration cannot override the separately bound
        # canonical physics inputs, whose actual set still excludes jump.
        core.write(self.folder/'cases.json', dict(cases=[dict(capabilities=higher, route_spec=dict(id='main'))]))
        self.save_base()
        result = find(self.spec, allow_scoped=True)
        self.assertEqual(result['status'], 'unsatisfied')
        self.assertIn('initial_permission_ability_configuration_not_certified', result['conflicts'][0]['reasons'])

    def test_oneway_port_condition_must_agree_with_request_and_actual_set(self):
        self.require_oneway_initial_capabilities()
        for value in ('UNKNOWN', ['move', 'wall_climb', 'jump'], []):
            self.gc['ports'][0]['initialPermissionConditions']['availableAbilitiesExact'] = value
            self.save_base()
            result = find(self.spec, allow_scoped=True)
            self.assertEqual(result['status'], 'unsatisfied')
            self.assertIn('initial_permission_ability_configuration_not_certified', result['conflicts'][0]['reasons'])

    def test_oneway_opposite_relation_remains_unavailable_for_exact_abilities(self):
        self.require_oneway_initial_capabilities(); self.spec['relations'] = [{'from': 'B', 'to': 'A'}]
        result = find(self.spec, allow_scoped=True)
        self.assertEqual(result['status'], 'unsatisfied')
        self.assertIn('requested_pair_violates_initial_port_permissions:B->A', result['conflicts'][0]['reasons'])

    def test_oneway_permission_needs_bound_input_even_if_metadata_says_pass(self):
        self.require_oneway_initial_capabilities()
        (self.folder/'physics-input-cases.json').unlink()
        self.save_base()
        result = find(self.spec, allow_scoped=True)
        self.assertEqual(result['status'], 'unsatisfied')
        self.assertIn('initial_permission_ability_configuration_not_certified', result['conflicts'][0]['reasons'])

    def test_route_minimum_and_validation_metadata_cannot_omit_actual_tested_ability(self):
        actual = self.spec['abilities']+['double_jump']
        core.write(self.folder/'physics-input-cases.json', dict(cases=[dict(id='TEST-ONLY-real-capabilities',
            capabilities=actual, route_spec=dict(id='main'))]))
        self.gc['validations'] = [dict(kind='physics', result='pass', routeId='main',
            contentVersion=self.gc['contentVersion'], capabilityConfiguration=dict(available=self.spec['abilities'][:]),
            artifacts=[dict(path='TEST-ONLY-NOT-AN-ACTUAL-CERTIFICATE', sha256='0'*64)])]
        self.save_base()
        result = find(self.spec, allow_scoped=True)
        self.assertEqual(result['status'], 'unsatisfied')
        self.assertIn('actual_tested_route_abilities_unavailable:main', result['conflicts'][0]['reasons'])
        self.spec['abilities'] = actual
        result = find(self.spec, allow_scoped=True)
        self.assertEqual(result['status'], 'matched')
        self.assertEqual(result['matches'][0]['requiredTestedAbilities'], sorted(actual))
        self.assertEqual(result['matches'][0]['testedInitialAbilityConfigurations'], [sorted(actual)],
                         'Output reports actual bound input capabilities, not the wrong display record')

    def test_native_profile_identity_does_not_supply_missing_actual_abilities(self):
        self.require_native_profile(); self.spec['initial_profile'] = 'air_chain'
        self.gc['routes'][0]['requiredAbilities'] = ['move', 'jump', 'shot_recoil']
        self.save_base(); self.spec['abilities'] = ['move', 'jump', 'shot_recoil']
        result = find(self.spec, allow_scoped=True)
        self.assertEqual(result['status'], 'unsatisfied')
        self.assertIn('initial_profile_abilities_unavailable:air_chain', result['conflicts'][0]['reasons'])
        self.assertIn('actual_tested_route_abilities_unavailable:main', result['conflicts'][0]['reasons'])
        self.spec['abilities'].append('double_jump')
        result = find(self.spec, allow_scoped=True)
        self.assertEqual(result['status'], 'unsatisfied', 'The native profile also requires multi_air_shot')
        self.assertIn('initial_profile_abilities_unavailable:air_chain', result['conflicts'][0]['reasons'])

    def test_missing_actual_route_configuration_is_a_gap(self):
        (self.folder/'physics-input-cases.json').unlink()
        result = find(self.spec, allow_scoped=True)
        self.assertEqual(result['status'], 'unsatisfied')
        self.assertIn('actual_route_ability_configuration_unknown:main', result['conflicts'][0]['reasons'])


class RealCurrentCoincidentAnchors(unittest.TestCase):
    """Read actual admitted content; rejection is not new physical approval."""
    def test_both_current_source_alias_contracts_are_not_extra_physical_forks(self):
        for name, expected_logical, expected_physical in (
            ('game-route-junction', 5, 4),
            ('game-forest-playful-module-variants-thorn-side-outlet', 4, 3),
        ):
            with self.subTest(module=name):
                folder = core.ACTIVE/name; path = folder/'module.mapnote.json'
                before = core.sha(path); doc = core.read(path); gc = doc['generationContract']
                names = [p['id'] for p in gc['ports']]
                self.assertEqual(len(names), expected_logical)
                groups = _physical_port_groups(gc['ports'], names)
                self.assertEqual(len(groups), expected_physical)
                caps = {a for c in core.read(folder/'physics-input-cases.json')['cases'] for a in c['capabilities']}
                variant = dict(folder=folder, document=doc,
                    verified=dict(mapReady=False, certifiedClosureProfiles=[], certifiedMirror=False))
                reasons, _ = _reasons(dict(abilities=sorted(caps), ports=dict(count=expected_logical)),
                    dict(humanReview='UNKNOWN'), variant, caps, [], True)
                self.assertIn(f'requested_physical_port_count_mismatch:{expected_logical}!={expected_physical}', reasons)
                for group in groups:
                    if len(group['logicalNames']) > 1:
                        self.assertIn('coincident_logical_ports_need_alias_normalization:'+','.join(group['logicalNames']), reasons)
                self.assertEqual(core.sha(path), before)


if __name__ == '__main__': unittest.main()
