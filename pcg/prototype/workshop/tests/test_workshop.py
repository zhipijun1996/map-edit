import copy,json,tempfile,unittest,shutil
from pathlib import Path
from pcg.prototype.workshop.rules import generate,specifications
from pcg.prototype.workshop.intake import ingest,propose
from pcg.prototype.workshop.library import WorkshopLibrary
from pcg.prototype.workshop.engine import ROOT
from pcg.map_directed.library import CandidateLibrary,verified_document

class WorkshopBoundaryTests(unittest.TestCase):
    def test_unsupported_idea_cannot_self_implement(self):
        s=copy.deepcopy(specifications()[0]);s.update(required_family='time-reversing-platform',implemented=True)
        r=generate(s);self.assertEqual(r['status'],'unsatisfied');self.assertTrue(r['conflicts']);self.assertNotIn('cases',r)
    def test_small_space_not_silently_widened(self):
        s=copy.deepcopy(specifications()[0]);s['space']['max_width']=120
        r=generate(s);self.assertEqual(r['status'],'unsatisfied');self.assertTrue(r['searched']);self.assertNotIn('cases',r)
    def test_missing_recoil_not_substituted(self):
        s=copy.deepcopy(specifications()[0]);s['capabilities']['allOf'].remove('shot_recoil')
        self.assertEqual(generate(s)['status'],'unsatisfied')
    def test_unverified_return_not_promised(self):
        s=copy.deepcopy(specifications()[0]);s['return_conditions']='all entering states bidirectional'
        self.assertEqual(generate(s)['status'],'unsatisfied')
    def test_coupled_interface_conflict_is_nonempty(self):
        ss=[s for s in specifications()if s['required_family']=='thorn-slot'];s=copy.deepcopy(ss[0]);s['rise']=ss[1]['rise']
        r=generate(s);self.assertEqual(r['status'],'unsatisfied');self.assertTrue(r['conflicts'])
    def test_original_idea_is_immutable_and_not_approval(self):
        with tempfile.TemporaryDirectory()as tmp:
            source=dict(id='human-test',source_type='human_idea',source_revision=1,original_text='保留原话\n  不归一化空白',human_approval=True)
            p=ingest(source,Path(tmp));r=json.loads(p.read_text());self.assertEqual(r['original_text'],source['original_text']);self.assertEqual(r['human_approval'],'UNKNOWN')
            source['original_text']='changed'
            with self.assertRaises(ValueError):ingest(source,Path(tmp))
    def test_failure_changes_proposal_selection(self):
        failure=dict(family='one-shot-two-routes',flag='unexpected_shortcut',next_revision='raise receiver')
        self.assertEqual(propose({'family':'one-shot-two-routes'},[failure])[0]['selection_weight'],0)
        failure['resolved_by']='actual new evidence';self.assertEqual(propose({'family':'one-shot-two-routes'},[failure])[0]['selection_weight'],1)
    def test_technical_status_does_not_promote(self):
        reasons=CandidateLibrary.promotion_reasons(dict(technical_status='passed_scoped',human_reviews=[]))
        self.assertIn('human_quality_review_missing',reasons);self.assertIn('canonical_assembly_interface_not_admitted',reasons)

class PersistedContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_run=ROOT/'results/workshop-five-holdout-v1'
        if not(cls.source_run/'multi-route-retrieval-v2.json').exists():raise unittest.SkipTest('restore content-workshop-v1 for real persisted evidence checks')
    def test_three_port_demands_do_not_cross_match(self):
        specs=[s for s in json.loads((self.source_run/'challenge-specifications.json').read_text())if s['ports']['count']==3]
        lib=WorkshopLibrary(self.source_run/'library');matches=[lib.find_multi(s)for s in specs]
        self.assertEqual([len(ms)for ms in matches],[1,1]);self.assertNotEqual(matches[0][0]['record']['contentVersion'],matches[1][0]['record']['contentVersion'])
        s=copy.deepcopy(specs[0]);s['objective']['upper'][1]-=1;self.assertEqual(lib.find_multi(s),[])
    def test_all_ordered_pairs_and_unknowns_preserved(self):
        item=next(m for m in json.loads((self.source_run/'modules/manifest.json').read_text())['modules']if m['portCount']==3)
        doc=verified_document(self.source_run/'modules'/item['file']);gc=doc['generationContract'];self.assertEqual(len(gc['relations']),6)
        reverse=next(r for r in gc['relations']if r['from']=='C'and r['to']=='A');self.assertEqual(reverse['status'],'UNKNOWN')
        self.assertTrue(all(r['transfer']['ensures']['grounded']=='UNKNOWN'for r in gc['routes']))
    def test_tampered_persistent_case_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'results')as tmp:
            target=Path(tmp)/'library';shutil.copytree(self.source_run/'library',target)
            p=next((target/'candidates').glob('*/cases.json'));p.write_text('{}')
            spec=json.loads((p.parent/'record.json').read_text())['specification']
            with self.assertRaises(ValueError):WorkshopLibrary(target).find_multi(spec)

class MapDemandTests(unittest.TestCase):
    def test_adapted_actual_map_demand_keeps_footprint(self):
        from pcg.prototype.workshop.map_demand import request,adapt
        from pcg.map_directed.library import fits
        original,spec=request();response=adapt(spec)
        self.assertEqual(response['status'],'requires_physics')
        self.assertTrue(fits(response['cases'][0],spec));self.assertEqual(spec['rise'],original['rise']);self.assertEqual(spec['space'],original['space'])
        spec['space']['max_width']=899
        self.assertEqual(adapt(spec)['status'],'unsatisfied')
    def test_adapted_candidate_can_be_reloaded_from_disk(self):
        root=ROOT/'results/workshop-map-demand-v4'
        if not(root/'summary.json').exists():self.skipTest('restore content-workshop-v1 for persisted Map demand')
        spec=json.loads((root/'effective-map-demand.json').read_text());spec['relations']=[dict(**r,**{'from':r['from_port'],'to':r['to_port']})for r in spec['relations']]
        matches=CandidateLibrary(root/'holdout/library').find(spec);self.assertEqual(len(matches),1)

if __name__=='__main__':unittest.main()
