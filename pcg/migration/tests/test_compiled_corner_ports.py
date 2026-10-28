"""Consumer overlay regressions using the actual certified corner configuration."""
import copy,unittest
from unittest.mock import patch
from pcg.migration import core,corners

BASE=core.ACTIVE/'plains50-ports-brake-branch-0'
RECEIPT=BASE/'port-configurations/c-bottom-right-v1/receipt.json'
AVAILABLE=RECEIPT.is_file()

@unittest.skipUnless(AVAILABLE,'Restore actual certified corner configuration package')
class ActualCompiledPorts(unittest.TestCase):
    def fixture(self):
        doc=core.read(BASE/'module.mapnote.json')
        refs=corners.verified_receipts(BASE.name,core.sha(BASE/'module.mapnote.json'),doc['generationContract']['contentVersion'])
        refs=[ref for ref in refs if ref['path']==core.relative(RECEIPT)]
        self.assertEqual(len(refs),1)  # This regression binds the historical v1 sample.
        return doc,refs
    def test_real_whole_configuration_opens_only_its_certified_selection(self):
        doc,refs=self.fixture();before=copy.deepcopy(doc);ports=corners.compiled_ports(doc,refs)
        self.assertEqual(doc,before)
        allowed=[(p['id'],c,o)for p in ports for c,o in p['cornerRelocations'].items()if o['allowed']is True]
        self.assertEqual(len(allowed),1);pid,corner,option=allowed[0]
        self.assertEqual((pid,corner),('C','BOTTOM_RIGHT'))
        self.assertEqual(option['targetFace'],'BOTTOM');self.assertEqual(option['targetPosition'],[960,744])
        self.assertEqual(option['proposedSurface'],'ONE_WAY_PLATFORM')
        self.assertEqual(option['configurationIds'],['c-bottom-right-v1'])
        self.assertEqual(option['reason'],'actual_offline_certified_whole_configuration')
        for p in ports:
            for c,o in p['cornerRelocations'].items():
                if o['applicable']and(p['id'],c)!=('C','BOTTOM_RIGHT'):self.assertEqual(o['allowed'],'UNKNOWN')
    def test_source_booleans_without_verified_receipt_never_grant_permission(self):
        doc,_=self.fixture()
        for p in doc['generationContract']['ports']:
            p['cornerRelocations']={c:dict(applicable=True,allowed=True)for c in corners.CORNERS}
        ports=corners.compiled_ports(doc,[])
        self.assertFalse(any(o['allowed']is True for p in ports for o in p['cornerRelocations'].values()))
    def test_repeated_receipt_does_not_duplicate_configuration_identity(self):
        doc,refs=self.fixture();ports=corners.compiled_ports(doc,refs+refs)
        option=next(p for p in ports if p['id']=='C')['cornerRelocations']['BOTTOM_RIGHT']
        self.assertEqual(option['configurationIds'],['c-bottom-right-v1'])
    def test_changed_receipt_bytes_are_rejected(self):
        doc,refs=self.fixture();bad=copy.deepcopy(refs);bad[0]['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'missing_or_changed_evidence'):corners.compiled_ports(doc,bad)
    def test_receipt_target_must_still_match_nearest_same_corner_face(self):
        doc,refs=self.fixture();original=core.read
        def changed(path):
            value=original(path)
            if str(path)==str(RECEIPT):
                value=copy.deepcopy(value);value['relocations'][0]['targetPosition'][0]+=128
            return value
        with patch.object(core,'read',side_effect=changed):
            with self.assertRaisesRegex(ValueError,'no_longer_matches_base'):corners.compiled_ports(doc,refs)
    def test_initial_conditional_permissions_remain_exact_and_detached(self):
        doc,_=self.fixture();p=doc['generationContract']['ports'][0]
        p['initialPermissionConditions']=[dict(available=['jump'],permission='INPUT')]
        ports=corners.compiled_ports(doc,[])
        self.assertEqual(ports[0]['initialPermissionConditions'],p['initialPermissionConditions'])
        ports[0]['initialPermissionConditions'][0]['available'].append('dash')
        self.assertEqual(p['initialPermissionConditions'][0]['available'],['jump'])

if __name__=='__main__':unittest.main()
