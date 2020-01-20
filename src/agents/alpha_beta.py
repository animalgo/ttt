from src.game.ttt import TTT
import random
import numpy as np

Score = int
Move = int

class ABPruning:

    def __init__(self,size=3):
        
        self._t = TTT(size)
        self._mode = 'optimal'
        self._penalty_prob = 0

        pass

    def set_penalty(self,penalty_prob=1):
        
        self._mode = 'modified'
        assert penalty_prob >= 0
        assert penalty_prob <= 1
        self._penalty_prob = penalty_prob

        return

    def get(self,state:np.ndarray,mover:int)->(Score,Move):

        if self._mode == 'optimal':
            return self._optimal(state,mover)
        elif self._mode == 'modified':
            return self._modified(state,mover)

    def _optimal(self,state,mover:int,alpha=-1000,beta=1000)->(Score,Move):
        
        t = self._t
        next_mover = -1 if mover is 1 else 1
        possible_moves = t.get_available_positions(state)
        best_move = None
        best_score = None

        # maximizer :
        if mover == 1:
            best_score = -1000
            for i in possible_moves:
                next_state = state.copy()
                next_state[i] = mover
                if t.is_terminated(next_state):
                    score = t.get_score(next_state)
                else:
                    [score,_] = self._optimal(next_state,next_mover,alpha,beta)
                
                if score > best_score:
                    best_score = score
                    best_move = i
                    
                    alpha = best_score
                    if alpha >= beta:
                        break
        
        # minimizer :
        elif mover == -1:
            best_score = 1000
            for i in possible_moves:
                next_state = state.copy()
                next_state[i] = mover
                if t.is_terminated(next_state):
                    score = t.get_score(next_state)
                else:
                    [score,_] = self._optimal(next_state,next_mover,alpha,beta)
                
                if score < best_score:
                    best_score = score
                    best_move = i

                    beta = best_score
                    if alpha >= beta:
                        break


        return (best_score, best_move)

    def _modified(self,state,mover:int,alpha=-1000,beta=1000)->(Score,Move):

        t = self._t
        next_mover = -1 if mover is 1 else 1
        possible_moves = self._get_reduced_moves(state)
        best_move = None
        best_score = None

        # maximizer :
        if mover == 1:
            best_score = -1000
            for i in possible_moves:
                next_state = state.copy()
                next_state[i] = mover
                if t.is_terminated(next_state):
                    score = t.get_score(next_state)
                else:
                    [score,_] = self._modified(next_state,next_mover,alpha,beta)
                
                if score > best_score:
                    best_score = score
                    best_move = i
                    
                    alpha = best_score
                    if alpha >= beta:
                        break
        
        # minimizer :
        elif mover == -1:
            best_score = 1000
            for i in possible_moves:
                next_state = state.copy()
                next_state[i] = mover
                if t.is_terminated(next_state):
                    score = t.get_score(next_state)
                else:
                    [score,_] = self._modified(next_state,next_mover,alpha,beta)
                
                if score < best_score:
                    best_score = score
                    best_move = i

                    beta = best_score
                    if alpha >= beta:
                        break


        return (best_score, best_move)

    def _get_reduced_moves(self,state)->tuple:

        all_moves = self._t.get_available_positions(state)
        if len(all_moves) == 0:
            return []
            
        p = 1 - self._penalty_prob
        num_of_moves = int(len(all_moves)*p)
        if num_of_moves == 0:
            num_of_moves = 1

        sample_moves = random.sample(all_moves,num_of_moves)

        return sample_moves