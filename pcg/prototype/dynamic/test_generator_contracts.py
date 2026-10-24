"""Regressions for actual run inventory versus a proposal's used subset."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from generators import motion_proposals

class ActualInventory(unittest.TestCase):
 def test_extra_available_abilities_are_in_the_current_snapshot(self):
  caps=['move','jump','double_jump','wall_climb','grapple','shot_recoil']
  proposals=motion_proposals(742100,1,families=['thorn_wall'],available_capabilities=caps)
  self.assertTrue(proposals)
  for c in proposals:
   self.assertEqual(set(c['capability_contract']['ids']),set(c['capabilities']))
   self.assertEqual(set(c['capabilities']),set(caps))
   self.assertEqual(set(c['proposal_capability_contract']['ids']),{'move','jump','double_jump','wall_climb'})
 def test_missing_family_abilities_are_not_added(self):
  self.assertEqual(motion_proposals(742100,1,families=['thorn_wall'],available_capabilities=['move','jump','grapple']),[])

if __name__=='__main__':unittest.main()
