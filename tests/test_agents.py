from src.game.ttt import TTT
from src.agents.minimax import minimax, minimax_load
from src.agents.alpha_beta import ABPruning
import src.agents
import unittest
import numpy as np

class CompetingTest(unittest.TestCase):

    def test_minimax_vs_minimax(self):
        
        size = 3
        t = TTT(size)
        filepath = 'results/minimax.pk'
        minimax_loaded = minimax_load(filepath)
        moves = 0
        while True:
            [_,best_move] = minimax_loaded(t.get_state())
            t.put(best_move)
            moves += 1
            if t.is_terminated():
                break
            pass

        self.assertEqual(t.check_winner()['winner'],0)
        pass

    def test_alphabeta_vs_alphabeta(self):
        
        t = TTT(3)
        player = ABPruning(3)
        moves = 0
        print('Moves : 0 ', end='')
        while True:
            [_, best_move] = player.get(t.get_state(),t.get_mover())
            t.put(best_move)
            moves += 1
            print(f'{moves} ',end='')
            if t.is_terminated():
                break
            pass

        print('final state')
        print(t)
        self.assertEqual(t.check_winner()['winner'],0)

    def test_alphabeta_vs_minimax(self):
        
        t = TTT(3)
        minimax_player = minimax_load('results/minimax.pk')
        alphabeta_player = ABPruning(3)

        moves = 0
        print('Moves : 0 ', end='')
        while True:
            if t.get_mover() == 1:
                [_, best_move] = alphabeta_player.get(t.get_state(),t.get_mover())
            elif t.get_mover() == -1:
                [_, best_move] = minimax_player(t.get_state())
            t.put(best_move)
            moves += 1
            print(f'{moves} ',end='')
            if t.is_terminated():
                break
            pass

        print('final state')
        print(t)
        self.assertEqual(t.check_winner()['winner'],0)

    def test_penalty_vs_penalty(self):

        t = TTT(3)
        player1 = ABPruning(3)
        player1.set_penalty(0.7)
        player2 = ABPruning(3)
        player2.set_penalty(0.7)
        
        games_played = 1
        scores = set()
        case1 = {1,2,3,4}
        case2 = {-1,-2,-3}
        case3 = {0}
        
        while True:
            if t.is_terminated():
                score = t.get_score()
                scores.add(score)

                # check whether if win,draw,lose all happened
                wins = case1 & scores
                loses = case2 & scores
                draw = case3 & scores
                if len(wins) > 0:
                    if len(loses) > 0:
                        if len(draw) > 0:
                            break
                t = TTT(3)
                games_played += 1
                pass

            mover = t.get_mover()
            if mover == 1:
                [_,move] = player1.get(t.get_state(),mover)
                t.put(move)
            elif mover == -1:
                [_,move] = player2.get(t.get_state(),mover)
                t.put(move)

        self.assertTrue( len(scores) > 2 )

    def test_alphabeta_vs_penalty(self):

        t = TTT(3)
        player1 = ABPruning(3)
        player2 = ABPruning(3)
        player2.set_penalty(0.2)
        
        scores = {-4:0,-2:0,0:0,1:0,3:0,5:0}
        game_played = 0

        while game_played < 11:
            if t.is_terminated():
                score = t.get_score()
                scores[score] += 1
                game_played += 1
                t = TTT(3)
                pass

            mover = t.get_mover()
            if mover == 1:
                [_,move] = player1.get(t.get_state(),mover)
                t.put(move)
            elif mover == -1:
                [_,move] = player2.get(t.get_state(),mover)
                t.put(move)
            
            pass

        print(scores)
        wrong_cases = scores[-4]+scores[-2]
        self.assertTrue(wrong_cases==0)

class CorrectnessTest(unittest.TestCase):

    def test_minimax_1(self):
        t = TTT(3)
        state = [[1,-1,0],
                 [-1,1,0],
                 [0,0,0]]
        state = np.array(state,dtype='int')
        state = state.reshape(-1)
        t._state = state
        [score,move] = minimax(t.get_state(),1,t)
        self.assertListEqual(list(state),list(t.get_state()))
        self.assertEqual(8,move)
        self.assertEqual(5,score)

    def test_alpha_beta_1(self):
        t = TTT(3)
        player = ABPruning(3)
        state = [[1,-1,0],
                 [-1,1,0],
                 [0,0,0]]
        state = np.array(state,dtype='int')
        state = state.reshape(-1)
        t._state = state
        [score,move] = player.get(t.get_state(),1)
        self.assertListEqual(list(state),list(t.get_state()))
        self.assertEqual(8,move)
        self.assertEqual(5,score)

class LoadAgentsTest(unittest.TestCase):

    def run_game(self,agent1,agent2,size=3):

        t = TTT(size)
        for i in range(size*size):
            agent = agent1 if i%2 == 0 else agent2
            inferred = agent(t.get_state())
            t.put(inferred)
            if t.is_terminated():
                break
        
        return t.get_result()

    def test_load_random(self):

        agent = src.agents.load('random',size=3)
        result = self.run_game(agent,agent)
        self.assertEqual(result['terminated'],True)

    def test_load_minimax(self):

        agent = src.agents.load('minimax')
        result = self.run_game(agent,agent)
        self.assertEqual(result['terminated'],True)
        self.assertEqual(result['winner'],0)
        self.assertEqual(result['score'],0)

    def test_load_alpha_beta(self):

        agent = src.agents.load('alpha_beta',size=3,penalty_prob=0)
        result = self.run_game(agent,agent)
        self.assertEqual(result['terminated'],True)
        self.assertEqual(result['winner'],0)
        self.assertEqual(result['score'],0)

    def test_load_alpha_beta_penalty(self):
        
        kwargs = {
            'size':3,
            'penalty_prob':0.5
        }
        agent = src.agents.load('alpha_beta',**kwargs)
        result = self.run_game(agent,agent)
        self.assertEqual(result['terminated'],True)

    def test_load_tabular_q(self):

        agent = src.agents.load('tabular_q',id='save_load_test')
        result = self.run_game(agent,agent)
        self.assertEqual(result['terminated'],True)

if __name__ == '__main__':
    unittest.main()