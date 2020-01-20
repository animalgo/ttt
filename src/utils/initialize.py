import os
import pickle
from src.game.ttt import TTT
from src.agents.minimax import minimax_save

def initialize_minimax(filepath:str,size=3):
    table = {}
    t = TTT(size)
    minimax_save(t.get_state(),t.get_mover(),t,table)
    with open(filepath,'wb') as f:
        pickle.dump(table, f)

    return

def initialize_state_indices(filepath:str,size=3):
    table = {'current':0} # store state:index pair
    t = TTT(size)
    
    def dfs(state,mover:int,table=table)->None:
        
        # store if the state is new one :
        encoded_state = t.get_encoded_state(state)
        if not encoded_state in table:
            table[encoded_state] = table['current']
            table['current'] += 1

        assert type(table[encoded_state]) is int

        next_mover = 1 if mover is -1 else -1
        available_moves = t.get_available_positions(state)
        for i in available_moves:
            next_state = state.copy()
            next_state[i] = mover
            if not t.is_terminated(next_state):
                dfs(next_state,next_mover)

        return

    # indexing start :
    initial_mover = t.get_mover()
    initial_state = t.get_state()
    print('indexing start :')
    dfs(initial_state,initial_mover)

    # simple validate :
    num_visited = table['current']
    del(table['current'])
    num_stored = len(table)
    print(f'visited states : {num_visited}')
    print(f'stored states : {num_stored}')
    assert num_stored == num_visited
    indices = set(table.values())
    assert len(indices) == len(table)
    sample_index = list(table.values())[1]
    assert type(sample_index) is int

    # save :
    print('saving... ',end='')
    with open(filepath,'wb') as f:
        pickle.dump(table, f)
    print('done')

    return