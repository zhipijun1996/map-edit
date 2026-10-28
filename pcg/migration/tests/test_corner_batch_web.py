from pathlib import Path
import os
import tempfile
import unittest
from unittest.mock import patch
from pcg.migration import core,corner_batch_web


class CornerReviewExportTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.active=self.root/'modules';self.state=self.root/'pcg/migration/foundation-v1'
        self.stack=[]
        for name,value in [('REPO',self.root),('ACTIVE',self.active),('STATE',self.state)]:
            handle=patch.object(core,name,value);handle.start();self.stack.append(handle)
        self.base=self.active/'demo';self.source=self.root/'.cache/migration/demo';self.batch=self.state/'corner-batches/test-batch'
        doc={'id':'demo-data','generationContract':{'mirror':{'status':'UNKNOWN'}}}
        core.write(self.base/'module.mapnote.json',doc)
        self.digest=core.sha(self.base/'module.mapnote.json')
        self.entry=dict(id='demo',moduleId='demo-data',contentVersion='sha256:'+'1'*64,
            contentSha256=self.digest,file='./modules/demo/module.mapnote.json',cornerConfigurationReceipts=[])
        core.write(self.active/'catalog.json',{'modules':[self.entry]})
        self.option=dict(key='demo-corner',moduleId='demo',portId='entry',corner='BOTTOM_LEFT',
            targetFace='BOTTOM',baseContentVersion=self.entry['contentVersion'],baseDocumentSha256=self.digest)
        core.write(self.batch/'plan.json',{'options':[self.option]})
        proposal={'id':'demo-data','generationContract':{'mirror':{'status':'UNKNOWN'}},'proposal':'frozen'}
        core.write(self.source/'module.mapnote.json',proposal)
        self.frozen=core.sha(self.source/'module.mapnote.json')
        self.prepared=dict(**self.option,status='prepared',prepared=core.relative(self.source),
            documentSha256=self.frozen,contentVersion='sha256:'+'2'*64)
        core.write(self.batch/'preparation.json',{'rows':[self.prepared]})

    def tearDown(self):
        for handle in reversed(self.stack):handle.stop()
        self.temp.cleanup()

    def test_preflight_is_uncertified_and_preview_keeps_frozen_bytes(self):
        core.write(self.batch/'preflight.json',{'rows':[dict(key='demo-corner',status='preflight_passed')],'actualAttempts':19})
        data=corner_batch_web.export('test-batch');row=data['rows'][0]
        self.assertEqual(row['status'],'preflight_passed');self.assertFalse(row['preview']['certified'])
        self.assertEqual(data['modules'][0]['certifiedConfigurations'],0)
        frozen=self.root/row['preview']['path'];self.assertEqual(core.sha(frozen),self.frozen)
        core.write(self.source/'module.mapnote.json',{'proposal':'later certification metadata'})
        again=corner_batch_web.export('test-batch')
        self.assertEqual(again['rows'][0]['preview']['sha256'],self.frozen)
        self.assertEqual(core.sha(frozen),self.frozen)

    def test_old_base_is_omitted_instead_of_reused(self):
        option={**self.option,'baseContentVersion':'sha256:'+'3'*64}
        core.write(self.batch/'plan.json',{'options':[option]})
        data=corner_batch_web.export('test-batch')
        self.assertEqual(data['rows'],[]);self.assertEqual(data['staleOptionsOmitted'],1)

    def test_verified_flag_without_receipt_cannot_appear_certified(self):
        core.write(self.batch/'qualification.json',{'rows':[dict(key='demo-corner',status='verified')]})
        data=corner_batch_web.export('test-batch')
        self.assertEqual(data['rows'][0]['status'],'verification_pending')
        self.assertEqual(data['modules'][0]['certifiedConfigurations'],0)

    def test_current_document_changed_is_rejected(self):
        core.write(self.base/'module.mapnote.json',{'changed':True})
        with self.assertRaisesRegex(ValueError,'current_review_document_changed'):
            corner_batch_web.export('test-batch')

    def test_newer_batch_overrides_success_with_failure_not_best_result(self):
        core.write(self.batch/'preflight.json',{'rows':[dict(key='demo-corner',status='preflight_passed')]})
        newer=self.state/'corner-batches/earlier-lexical-name'
        core.write(newer/'plan.json',{'options':[self.option]})
        core.write(newer/'preparation.json',{'rows':[self.prepared]})
        core.write(newer/'preflight.json',{'rows':[dict(key='demo-corner',status='preflight_failed')]})
        os.utime(self.batch/'plan.json',ns=(1_000_000_000,1_000_000_000))
        os.utime(newer/'plan.json',ns=(2_000_000_000,2_000_000_000))
        data=corner_batch_web.export_all();row=data['rows'][0]
        self.assertEqual(data['batchIds'],['test-batch','earlier-lexical-name'])
        self.assertEqual(row['status'],'preflight_failed')
        self.assertEqual(row['sourceBatchId'],'earlier-lexical-name')
        self.assertEqual([h['status']for h in row['history']],['preflight_passed','preflight_failed'])
        self.assertEqual(data['counts'],{'preflight_failed':1})

    def test_partial_new_batch_keeps_older_options_without_promoting_them(self):
        other={**self.option,'key':'demo-other','portId':'exit','corner':'TOP_RIGHT','targetFace':'TOP'}
        core.write(self.batch/'plan.json',{'options':[self.option,other]})
        core.write(self.batch/'preparation.json',{'rows':[self.prepared,{**self.prepared,**other}]})
        core.write(self.batch/'preflight.json',{'rows':[dict(key='demo-corner',status='preflight_passed'),dict(key='demo-other',status='preflight_failed')]})
        newer=self.state/'corner-batches/repair-batch'
        core.write(newer/'plan.json',{'options':[self.option]})
        core.write(newer/'preparation.json',{'rows':[self.prepared]})
        os.utime(self.batch/'plan.json',ns=(1_000_000_000,1_000_000_000))
        os.utime(newer/'plan.json',ns=(2_000_000_000,2_000_000_000))
        data=corner_batch_web.export_all();rows={r['key']:r for r in data['rows']}
        self.assertEqual(data['totalOptions'],2)
        self.assertEqual(rows['demo-corner']['status'],'prepared')
        self.assertEqual(rows['demo-other']['status'],'preflight_failed')
        self.assertEqual(rows['demo-other']['sourceBatchId'],'test-batch')
        self.assertEqual(data['modules'][0]['certifiedConfigurations'],0)
        self.assertEqual(set(data['sources']),{'test-batch','repair-batch'})

    def test_source_phase_snapshot_stays_exact_after_live_state_changes(self):
        core.write(self.batch/'preflight.json',{'rows':[dict(key='demo-corner',status='preflight_failed')]})
        data=corner_batch_web.export('test-batch');ref=data['sources']['preflight']
        snapshot=self.root/ref['path'];raw=snapshot.read_bytes()
        self.assertIn('/states/preflight-',ref['path'])
        self.assertEqual(core.sha(snapshot),ref['sha256'])
        core.write(self.batch/'preflight.json',{'rows':[dict(key='demo-corner',status='preflight_passed')]})
        self.assertEqual(snapshot.read_bytes(),raw)
        next_data=corner_batch_web.export('test-batch')
        self.assertNotEqual(next_data['sources']['preflight']['path'],ref['path'])
        self.assertEqual(core.sha(snapshot),ref['sha256'])


if __name__=='__main__':unittest.main()
