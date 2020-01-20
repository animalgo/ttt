import unittest
from src.agents.qlearning import TabularQ
from src.agents.minimax import minimax_load
from src.game.ttt import TTT
from src.utils.path import Settings
import numpy as np

class ImplementationTest(unittest.TestCase):

    def test_save_load(self):
        parameters = {
            "ep_train":0.5,
            "ep_infer":0,
            "gamma":1,
            "alpha":1,
            "agent_for":'both',
        }
        q1 = TabularQ(3)
        q1.set_params(**parameters)
        q1.train(numOfGames=100)
        q1.save(comment='validate save and load',id_forced='save_load_test')

        q2 = TabularQ.load(id='save_load_test')

        self.assertTrue(q1==q2)

    def test_encode_decode(self):
        
        q = TabularQ(3)
        for i in range(len(q._d)):
            state = q.get_state(i)
            index = q.get_index(state.__str__())
            self.assertTrue(i == index)

    def test_update(self):
        t = TTT(3)
        prev_state = [
            [ 1, 1, 0],
            [-1,-1, 0],
            [ 0, 0, 0]
        ]
        next_state = [
            [ 1, 1, 1],
            [-1,-1, 0],
            [ 0, 0, 0]
        ]
        prev_state = np.array(prev_state).reshape(-1)
        next_state = np.array(next_state).reshape(-1)
        result = t.get_result(next_state)
        self.assertEqual(result,{'terminated':True,'score':5})

        q = TabularQ(3)
        q.set_params(alpha=1,gamma=1)

        encoded_prev_state = t.get_encoded_state(prev_state)
        prev_state_index = q.get_index(encoded_prev_state)
        encoded_next_state = t.get_encoded_state(next_state)
        next_state_index = q.get_index(encoded_next_state)
        self.assertEqual(next_state_index,None)

        q.update(encoded_prev_state,2,encoded_next_state,5)
        updated_row = q._Q[prev_state_index,:]

        check_row = np.array_equal(updated_row, [0,0,5,0,0,0,0,0,0])
        self.assertTrue(check_row)

        # test correct inference :
        q._is_first_mover = True
        possible_moves = t.get_available_positions(prev_state)
        inferred = q.infer(encoded_prev_state,possible_moves,1)
        self.assertEqual(inferred,2)

        pass

    def test_deterministic_vs_minimax(self):
        # gamma, alpha == 1 guarantees that for endstates s and optimal move a,
        # Q(s,a) = R(s,a) if Q is not 0
        parameters = {
            "ep_train":0.5,
            "ep_infer":0,
            "gamma":1,
            "alpha":1,
            "agent_for":'both',
        }
        q = TabularQ(3)
        q.set_params(**parameters)
        q.train(numOfGames=500)

        s = Settings()
        minimax = minimax_load(s.path('minimax'))
        t = TTT(3)

        Q = q._Q
        to_check_state_indices = np.where(Q != [0,0,0,0,0,0,0,0,0])[0]
        to_check_state_indices = map(int, to_check_state_indices)

        for state_index in to_check_state_indices:

            self.assertFalse(np.array_equal(Q[state_index],np.array([0,0,0,0,0,0,0,0,0])))
            state = q.get_state(state_index)
            encoded_state = t.get_encoded_state(state)
            mover = t.get_mover(state=state)
            possible_moves = t.get_available_positions(state)

            if mover == 1:
                best_move_q = np.argmax(Q[state_index])
                if int(Q[state_index,best_move_q]) is not 0:
                    move_inferred = q.infer(encoded_state,possible_moves,mover)
                    q_value_1 = Q[state_index,best_move_q]
                    q_value_2 = Q[state_index,move_inferred]
                    self.assertEqual(q_value_1,q_value_2)
            elif mover == -1:
                best_move_q = np.argmin(Q[state_index])
                if int(Q[state_index,best_move_q]) is not 0:
                    move_inferred = q.infer(encoded_state,possible_moves,mover)
                    q_value_1 = Q[state_index,best_move_q]
                    q_value_2 = Q[state_index,move_inferred]
                    self.assertEqual(q_value_1,q_value_2)

            next_state = state.copy()
            next_state[best_move_q] = mover

            result = t.get_result(next_state)
            if result['terminated']:
                best_score, _ = minimax(state)
                q_value = Q[state_index,best_move_q]
                if best_score != q_value:
                    # not yet sampled (s,a)
                    # or withdraw case
                    self.assertEqual(q_value,0)
                else:
                    # sampled (s,a)
                    self.assertEqual( best_score, q_value )
            pass

