import unittest
from contracts import Registry,Grammar,ContractError
class Contracts(unittest.TestCase):
 def test_unknown_mechanic_never_falls_back_to_all(self):
  with self.assertRaisesRegex(ContractError,'unregistered_capability'):Registry().resolve(['move','teleport'])
 def test_double_jump_requires_usable_jump(self):
  with self.assertRaisesRegex(ContractError,'missing jump'):Registry().resolve(['double_jump'])
 def test_passive_hook_and_wall_do_not_refill_rounds(self):
  g=Grammar(['move','jump','shot_recoil','double_jump','grapple','wall_climb'])
  for w in [('ground_jump','recoil','hook_hang','anchor_jump','recoil'),('ground_jump','recoil','wall_contact','wall_jump','recoil')]:
   with self.assertRaisesRegex(ContractError,'unmet_action_precondition:recoil'):g.validate_word(w)
 def test_anchor_allows_extra_jump_without_inventing_ground_jump(self):
  g=Grammar(['move','jump','double_jump','grapple']);s,_=g.validate_word(['ground_jump','air_jump','hook_hang','anchor_jump','air_jump'])
  self.assertEqual(s.jumps,0)
  with self.assertRaises(ContractError):g.step(s,'air_jump')
 def test_wall_kick_works_when_normal_jump_is_disabled(self):
  s,_=Grammar(['move','wall_climb']).validate_word(['wall_contact','wall_jump']);self.assertEqual(s.mode,'air')
 def test_recoil_takeoff_does_not_invent_two_air_jumps(self):
  g=Grammar(['move','jump','double_jump','shot_recoil']);s,_=g.validate_word(['recoil','air_jump'])
  self.assertEqual(s.jumps,0)
  with self.assertRaises(ContractError):g.step(s,'air_jump')
 def test_seed_is_reproducible_across_hash_seeds(self):
  import subprocess,os,sys
  code="from contracts import *;print(Grammar(list(Registry().items)).derive(194,limit=12))"
  outputs=[subprocess.check_output([sys.executable,'-c',code],env=dict(os.environ,PYTHONHASHSEED=str(n)),cwd=__import__('pathlib').Path(__file__).parent) for n in (1,29)]
  self.assertEqual(*outputs)
 def test_composition_is_derived_from_available_operators(self):
  for caps in Registry().combinations():
   g=Grammar(caps)
   for word in g.derive(194,limit=12):
    s,_=g.validate_word(word);self.assertTrue((caps-{'move','jump'})<=s.used)
if __name__=='__main__':unittest.main()
