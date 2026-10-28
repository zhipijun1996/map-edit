"""PR#1 compatibility and bounded larger-region contract, not physics tests."""
import json,unittest
from pathlib import Path
import region_network as network

class RegionalScale(unittest.TestCase):
 def test_existing_twenty_core_corpus_is_byte_equivalent(self):
  rows=json.loads((Path(__file__).parent/'results/region-network-v2/runs.json').read_text())['runs']
  for row in rows:
   self.assertEqual(network.construct(str(row['seed']),row['region']),row['exploration_graph'])
 def test_larger_core_still_has_no_mandatory_regional_bottleneck(self):
  g=network.construct('plains-region-next-0/attempt/0','plains',core_count=32)
  self.assertEqual(len(g['core_nodes']),32)
  self.assertEqual(network.validate_region_intent(g),[])
  self.assertGreater(len(g['nodes']),32)
 def test_unbounded_size_is_refused(self):
  with self.assertRaisesRegex(ValueError,'outside_12_48'):
   network.construct('oversized','plains',core_count=1000)
