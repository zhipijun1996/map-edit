"""Conservative identity tests; these fixtures make no physics claims."""
import copy
import tempfile
import unittest
from pathlib import Path
from pcg.migration import core
from pcg.migration.equivalence import fingerprint


class ExactEquivalenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.folder=Path(self.tmp.name)
        self.doc={'id':'sample','title':'label','objects':[{'id':'sample/bell','type':'bell','x':0,'y':0,'w':28,'h':34,'label':'bell','mechanics':{'openSeconds':1}}],
            'capabilityRequirements':{'allOf':['jump','shot_recoil']},'generationContract':{
                'kind':'module','generation':{'source':{'physicsSourceCommit':'a'*40,'sourceManifestSha256':'b'*64}},
                'space':{'actorBody':{'size':[24,36]},'bounds':{'x':0,'y':0,'w':256,'h':256}},
                'ports':[{'id':'A','permission':'INOUT'}],'relations':[],'routes':[]}}
        self.cases={'cases':[{'id':'recording','platforms':[[0,128,256,32]],'recorded_frames':[{'frame':0,'axis':1,'requested':[]}]}]}
        self.save(self.doc,self.cases)
        self.original=fingerprint(self.folder)

    def save(self,doc,cases):
        core.write(self.folder/'module.mapnote.json',doc);core.write(self.folder/'cases.json',cases)

    def test_title_and_label_do_not_manufacture_new_content(self):
        self.doc['title']='renamed';self.doc['objects'][0]['label']='renamed'
        self.save(self.doc,self.cases);self.assertEqual(fingerprint(self.folder),self.original)

    def test_mechanism_difference_prevents_merge(self):
        self.doc['objects'][0]['mechanics']['openSeconds']=2
        self.save(self.doc,self.cases);self.assertNotEqual(fingerprint(self.folder),self.original)

    def test_port_permission_difference_prevents_merge(self):
        self.doc['generationContract']['ports'][0]['permission']='INPUT'
        self.save(self.doc,self.cases);self.assertNotEqual(fingerprint(self.folder),self.original)

    def test_real_input_difference_prevents_merge(self):
        self.cases['cases'][0]['recorded_frames'][0]['requested']=[{'type':'jump'}]
        self.save(self.doc,self.cases);self.assertNotEqual(fingerprint(self.folder),self.original)

    def test_different_frozen_source_prevents_merge(self):
        self.doc['generationContract']['generation']['source']['sourceManifestSha256']='c'*64
        self.save(self.doc,self.cases);self.assertNotEqual(fingerprint(self.folder),self.original)


if __name__=='__main__':unittest.main()
