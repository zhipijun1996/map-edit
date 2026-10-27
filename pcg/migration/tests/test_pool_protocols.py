"""DRAFT pool-protocol binding adversaries; no synthetic gameplay approvals."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from pcg.migration import core,physics,holdout_guard as guard,pool_protocols as pools
from pcg.prototype.factory.core.quality import digest


class PoolRuntimeBindings(unittest.TestCase):
    def setUp(self):
        originals=[core.read(physics.PROTOCOL),core.read(physics.FULL_PROTOCOL)]
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.addCleanup(patch.stopall)
        patch.object(core,'REPO',self.root).start()
        patch.object(guard,'LOCKS',self.root/'state/locks.json').start()
        patch.object(guard,'POOLS',self.root/'state/pools').start()
        legacy=self.root/'state/protocol.json';full=self.root/'state/protocol-full-v2.json'
        core.write(legacy,originals[0]);core.write(full,originals[1])
        patch.object(physics,'PROTOCOL',legacy).start();patch.object(physics,'FULL_PROTOCOL',full).start()
        self.folder=self.root/'candidate';self.folder.mkdir()
        core.write(self.folder/'migration.json',{'sourcePath':'original/source','sourceVersion':'sha256:'+'a'*64})
        core.write(self.folder/'module.mapnote.json',{'generationContract':{'contentVersion':'sha256:'+'b'*64}})
        core.write(self.folder/'cases.json',{'cases':[{'id':'candidate','platforms':[[0,64,256,32]],
            'spawn':[20,46],'goal':[200,40,20,10],'capabilities':['move','jump','shot_recoil'],
            'control_plan':[{'op':'settle','trigger':{'after':0},'target_x':210,'deadband':3}]}]})
        core.write(self.folder/'adaptation.json',{})
        self.protocol=copy.deepcopy(originals[1]);self.protocol.update(holdoutSeed=12345678,independentPoolId='frozen-pool')
        target=guard.POOLS/'frozen-pool';target.mkdir(parents=True)
        frozen=dict(contentVersion='sha256:'+'b'*64,documentSha256=core.sha(self.folder/'module.mapnote.json'),
            canonicalCasesSha256=core.sha(self.folder/'cases.json'),programSignature=guard._program_signature(core.read(self.folder/'cases.json')['cases']))
        self.declaration=dict(schema='pcg/independent-holdout-registration/v1',id='frozen-pool',source=guard._identity(self.folder),
            frozenCandidate=frozen,pool=guard._pool(self.protocol),allocationNonce='d'*64,candidateFrozenBeforeAllocation=True,
            baseProtocol={'path':core.relative(full),'sha256':core.sha(full)})
        core.write(target/'protocol.json',self.protocol);core.write(target/'registration.json',self.declaration)
        self.row=dict(id='frozen-pool',source=self.declaration['source'],frozenCandidate=frozen,
            pool=self.declaration['pool'],poolKey=digest(self.declaration['pool']),
            protocol={'path':core.relative(target/'protocol.json'),'sha256':core.sha(target/'protocol.json')},
            declaration={'path':core.relative(target/'registration.json'),'sha256':core.sha(target/'registration.json')})
        self.state=guard._state();self.state['independentPools']=[self.row];core.write(guard.LOCKS,self.state)
        self.path=target/'protocol.json'

    def bind(self):return pools.bind_registered_pool(self.folder,'frozen-pool')

    def test_historical_v1_v2_protocols_need_no_new_pool_registration(self):
        for path in (physics.PROTOCOL,physics.FULL_PROTOCOL):
            self.assertEqual(pools.evidence_protocol(self.root/'absent',core.read(path)),{'mode':'historical_v1_v2'})
        self.assertEqual(pools.runtime_protocol(self.folder),physics.FULL_PROTOCOL)

    def test_registered_protocol_is_selected_only_from_bound_candidate_metadata(self):
        with self.assertRaisesRegex(ValueError,'not_bound'):pools.runtime_protocol(self.folder,self.path)
        self.bind();self.assertEqual(pools.runtime_protocol(self.folder,new_run=True),self.path)
        self.assertEqual(pools.runtime_protocol(self.folder,self.path),self.path)
        with self.assertRaisesRegex(ValueError,'disagrees'):pools.runtime_protocol(self.folder,physics.FULL_PROTOCOL)

    def test_alias_file_with_same_bytes_cannot_override_registered_canonical_path(self):
        self.bind();alias=self.root/'renamed.json';alias.write_bytes(self.path.read_bytes())
        with self.assertRaisesRegex(ValueError,'disagrees'):pools.runtime_protocol(self.folder,alias)

    def test_new_seed_cannot_change_any_other_protocol_requirement(self):
        for field,value in [('thresholds',{'clean':.5,'mild':.5,'moderate':.4}),('trialsPerNoiseLevel',1),
                            ('bodySize',[1,1]),('maximumAttemptsPerModule',999999),
                            ('selection','pick best heldout'),('calibrationSeed',1)]:
            with self.subTest(field=field):
                protocol=copy.deepcopy(self.protocol);protocol[field]=value
                # Even consistently rehashed bookkeeping cannot make a lower
                # threshold/trial count/body envelope a legitimate new pool.
                row=copy.deepcopy(self.row);declaration=copy.deepcopy(self.declaration)
                declaration['pool']=guard._pool(protocol);row['pool']=declaration['pool'];row['poolKey']=digest(row['pool'])
                core.write(self.path,protocol);core.write(self.path.parent/'registration.json',declaration)
                row['protocol']['sha256']=core.sha(self.path);row['declaration']['sha256']=core.sha(self.path.parent/'registration.json')
                with self.assertRaisesRegex(ValueError,'quality_selection_noise_body_or_budget'):pools._validate(self.folder,row,protocol)
        core.write(self.path,self.protocol);core.write(self.path.parent/'registration.json',self.declaration)

    def test_source_content_and_program_bindings_are_all_required(self):
        self.bind();meta=core.read(self.folder/'migration.json');meta['sourceVersion']='sha256:'+'c'*64;core.write(self.folder/'migration.json',meta)
        with self.assertRaisesRegex(ValueError,'another_original_source'):pools.runtime_protocol(self.folder)
        meta['sourceVersion']='sha256:'+'a'*64;core.write(self.folder/'migration.json',meta)
        doc=core.read(self.folder/'module.mapnote.json');doc['generationContract']['contentVersion']='sha256:'+'c'*64;core.write(self.folder/'module.mapnote.json',doc)
        with self.assertRaisesRegex(ValueError,'another_content_version'):pools.runtime_protocol(self.folder)
        doc['generationContract']['contentVersion']='sha256:'+'b'*64;core.write(self.folder/'module.mapnote.json',doc)
        cases=core.read(self.folder/'cases.json');cases['cases'][0]['control_plan'][0]['target_x']=250;core.write(self.folder/'cases.json',cases)
        with self.assertRaisesRegex(ValueError,'another_frozen_program'):pools.runtime_protocol(self.folder)

    def test_certification_annotations_can_change_bytes_but_not_semantics_for_replay(self):
        self.bind();doc=core.read(self.folder/'module.mapnote.json');doc['generationContract']['validationNote']='actual evidence attached';core.write(self.folder/'module.mapnote.json',doc)
        self.assertEqual(pools.runtime_protocol(self.folder,new_run=False),self.path)
        with self.assertRaisesRegex(ValueError,'document_changed_after_pool_allocation'):pools.runtime_protocol(self.folder,new_run=True)

    def test_random_nonce_and_freeze_order_are_explicit(self):
        declaration=copy.deepcopy(self.declaration);declaration.pop('allocationNonce');core.write(self.path.parent/'registration.json',declaration)
        row=copy.deepcopy(self.row);row['declaration']['sha256']=core.sha(self.path.parent/'registration.json')
        with self.assertRaisesRegex(ValueError,'random_nonce'):pools._validate(self.folder,row,self.protocol)

    def test_one_holdout_execution_can_cover_routes_but_cannot_be_rerolled(self):
        self.bind();pools.assert_unstarted(self.folder,self.path)
        first=pools.reserve_holdout(self.folder,self.path,'actual-run')
        self.assertEqual(first,pools.reserve_holdout(self.folder,self.path,'actual-run'))
        with self.assertRaisesRegex(ValueError,'already_started'):pools.assert_unstarted(self.folder,self.path)
        with self.assertRaisesRegex(ValueError,'another_execution'):pools.reserve_holdout(self.folder,self.path,'new-name')

    def test_registered_report_requires_its_actual_reserved_execution(self):
        self.bind();report={'holdoutPool':pools.report_binding(self.folder,self.path,'actual-run')}
        with self.assertRaisesRegex(ValueError,'did_not_execute'):pools.evidence_protocol(self.folder,self.protocol,report=report)
        pools.reserve_holdout(self.folder,self.path,'actual-run');report['holdoutPool']=pools.report_binding(self.folder,self.path,'actual-run')
        result=pools.evidence_protocol(self.folder,self.protocol,report=report,report_path=self.root/'actual-run/migration-physics.json')
        self.assertEqual(result['mode'],'registered_independent_pool')
        with self.assertRaisesRegex(ValueError,'not_its_reserved_execution'):
            pools.evidence_protocol(self.folder,self.protocol,report=report,report_path=self.root/'renamed-run/migration-physics.json')

    def test_frozen_source_dependencies_and_cache_bind_the_declared_pool(self):
        self.bind();dependencies=pools.source_dependencies(self.folder,self.path)
        self.assertIn(self.path,dependencies);self.assertIn(self.path.parent/'registration.json',dependencies)
        before=pools.cache_identity(self.folder,self.protocol)
        pools.reserve_holdout(self.folder,self.path,'actual-run');after=pools.cache_identity(self.folder,self.protocol)
        self.assertNotEqual(before,after)

if __name__=='__main__':unittest.main()
