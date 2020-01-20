from src.game.ttt import TTT
import pickle
import numpy as np
from typing import Callable, Tuple

Move = int
Score = int

def minimax(state,mover:int,t:TTT)->[Score,Move]:

    next_mover = -1 if mover is 1 else 1
    possible_moves = t.get_available_positions(state)
    corresponding_scores = []
    best_score = 0
    best_move = None

    for index in possible_moves:
        next_state = state.copy()
        next_state[index] = mover
        if t.is_terminated(next_state):
            score = t.get_score(next_state)
            corresponding_scores.append(score)
        else:
            [score, _] = minimax(next_state,next_mover,t)
            corresponding_scores.append(score)

    if mover == 1:
        best_score = max(corresponding_scores)
        best_move_index = corresponding_scores.index(best_score)
        best_move = possible_moves[best_move_index]
    elif mover == -1:
        best_score = min(corresponding_scores)
        best_move_index = corresponding_scores.index(best_score)
        best_move = possible_moves[best_move_index]

    return [best_score, best_move]


def minimax_save(state,mover:int,t:TTT,table)->(Score,Move):

    encoded_state = encode_state(state)
    if encode_state in table:
        return table[encoded_state]

    next_mover = -1 if mover is 1 else 1
    possible_moves = t.get_available_positions(state)
    corresponding_scores = []
    best_score = 0
    best_move = None

    for index in possible_moves:
        next_state = state.copy()
        next_state[index] = mover
        if t.is_terminated(next_state):
            score = t.get_score(next_state)
            corresponding_scores.append(score)
        else:
            [score, _] = minimax_save(next_state,next_mover,t,table)
            corresponding_scores.append(score)

    if mover == 1:
        best_score = max(corresponding_scores)
        best_move_index = corresponding_scores.index(best_score)
        best_move = possible_moves[best_move_index]
    elif mover == -1:
        best_score = min(corresponding_scores)
        best_move_index = corresponding_scores.index(best_score)
        best_move = possible_moves[best_move_index]
    
    table[encoded_state] = (best_score,best_move)
    return (best_score, best_move)

def minimax_load(filepath:str)->Callable[[np.ndarray],Tuple[Score,Move]]:
    with open(filepath,'rb') as f:
        table = pickle.load(f)
        pass
    def minimax(state:np.ndarray)->(Score,Move):
        encoded = encode_state(state)
        return table[encoded]
    return minimax

def encode_state(state):
    encode = state.__str__()
    return encode