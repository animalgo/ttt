from src.agents.alpha_beta import ABPruning
from src.agents.minimax import minimax_load
from src.agents.qlearning import TabularQ
from src.game.ttt import TTT
import numpy as np
from typing import Callable

def load(name:str,**kwargs)->Callable[[np.ndarray],int]:
    
    if name == 'minimax':

        from src.utils.path import Settings
        s = Settings()
        minimax = minimax_load(s.path('minimax'))
        def agent(state:np.ndarray)->int:
            move = minimax(state)[1]
            return int(move)
        return agent
    
    elif name == 'alpha_beta':

        assert 'size' in kwargs
        assert 'penalty_prob' in kwargs
        size = kwargs.get('size')
        penalty_prob = kwargs.get('penalty_prob')
        ab = ABPruning(size)
        ab.set_penalty(penalty_prob)
        t = TTT(size)
        def agent(state:np.ndarray)->int:
            mover = t.get_mover(state=state)
            inferred = ab.get(state=state,mover=mover)[1]
            return inferred
        return agent
    
    elif name == 'random':

        assert 'size' in kwargs
        import random
        size = kwargs.get('size')
        t = TTT(size)
        def agent(state:np.ndarray)->int:
            possible_moves = t.get_available_positions(state)
            nums = len(possible_moves)
            random_index = random.randint(0,nums-1)
            return int(possible_moves[random_index])
        return agent
    
    elif name == 'tabular_q':
        
        assert 'id' in kwargs
        id = kwargs.get('id')
        q = TabularQ.load(id)
        size = q._size
        t = TTT(size)
        def agent(state:np.ndarray)->int:
            possible_moves = t.get_available_positions(state)
            encoded_state = t.get_encoded_state(state)
            mover = t.get_mover(state=state)
            inferred = q.infer(encoded_state,possible_moves,mover)
            return inferred
        return agent
    
    else:
        raise NameError(f'{name} is not implemented')