"""Fidelity checks for original input streams, profiles and reward consumers."""
import unittest
from pcg.migration import core,game_adapter,game_world_v4,foundry_replay_v4


class OriginalNativeV4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=game_adapter.source_entries()
        cls.resources={r['id']:r for r in cls.rows if r['kind']=='resource'}

    def test_all_fifty_four_source_recordings_preserve_inputs_not_poses(self):
        for source in self.rows:
            if source['kind']!='foundry':continue
            case=game_adapter.foundry_case(source,self.resources)
            value=foundry_replay_v4.replay_case(case,source)
            recording=core.read(core.REPO/value['original_replay_source']['path'])
            self.assertEqual(recording['manifest_hash'],source['data']['hash'])
            self.assertEqual(recording['basis'],source['data']['basis'])
            self.assertEqual(value['original_replay_frame_count'],len(recording['frames']))
            axes={a['frame']:a['value']for a in value['axes']}
            actions={}
            for action in value['actions']:
                actions.setdefault(action['frame'],[]).append(dict(type=action['type'],direction=action['direction']))
            axis=0
            for index,frame in enumerate(recording['frames']):
                axis=axes.get(index,axis)
                self.assertEqual(axis,frame['axis'],(source['id'],index))
                self.assertEqual(actions.get(index,[]),frame['actions'],(source['id'],index))
            self.assertNotIn('recorded_frames',value,'old recording is not a new Harness witness')
            self.assertNotIn('original_input_frames',value,'only axes/actions are executable input authority')
            self.assertFalse(value['original_replay_source']['posesUsedAsMovement'])

    def test_profile_capacity_uses_actual_config_not_stale_display_label(self):
        for profile,expected in [('base',(1,1)),('double_jump',(2,1)),('air_chain',(2,4))]:
            source=next(r for r in self.rows if r['kind']=='foundry'and r['data']['capability_profile']==profile)
            case=game_adapter.foundry_case(source,self.resources)
            native=game_world_v4.native_fields(case,source)['original_tuning_profile']
            self.assertEqual((native['effectiveTuning']['max_jumps'],native['effectiveTuning']['max_air_shots']),expected)

    def test_root_coin_keeps_original_amount_location_and_consumer_goal(self):
        source=next(r for r in self.rows if r['id']=='forest_exploration_modules__root_meadow')
        case=game_adapter.forest_case(source);value=game_world_v4.native_fields(case,source)
        self.assertEqual(value['original_pickups'],[dict(id='root_coin',kind='coin',amount=1,position=[432,-50])])
        self.assertEqual(value['required_original_pickups'],['root_coin'])
        self.assertNotIn('original_coin_note_pickup_consumer',value['decoder_pending_behavior'])
        fake=dict(ok=True,hp=5,returns=[],original_pickups=dict(consumer='DemoApp._commit_pickup',interaction_radius=46,resources_reset=False,pickups=[]))
        self.assertIn('original_world_pickup_not_actually_claimed',game_world_v4.purpose(value,fake)['reasons'])

    def test_branch_chest_is_not_silently_replaced_with_coin_pickup(self):
        source=next(r for r in self.rows if r['kind']=='forest'and r['data'].get('branch_reward_contract'))
        case=game_adapter.forest_case(source);value=game_world_v4.native_fields(case,source)
        self.assertEqual(value['original_pickups'],[])
        self.assertIn('original_branch_chest_consumer',value['decoder_pending_behavior'])


if __name__=='__main__':unittest.main()
