import src.agents.alpha_beta
import src.agents.minimax
import src.agents.qlearning
import numpy as np
from typing import Callable

def load(name:str,params={})->Callable[[np.ndarray],int]:
    if name == 'minimax':
        from src.utils.path import Settings
        s = Settings()
        minimax = src.agents.minimax.minimax_load(s.path('minimax'))
        def agent(state:np.ndarray)->int:
            move = minimax(state)[1]
            return move
        return agent
    else:
        raise NameError(f'{name} is not implemented')