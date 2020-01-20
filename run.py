from src.utils.path import Settings
import src.utils.initialize
import json
import os

def make_initial_results():

    s = Settings()

    todo = {'minimax':True,'state_index_3':True,'tabular_q':True}

    if os.path.isdir(s.path('results')):
        print('results directory is found')

        if os.path.exists(s.path('minimax')):
            todo['minimax'] = False
            print('minimax result is found')

        if os.path.exists(s.path('state_index_3')):
            todo['state_index_3'] = False
            print('3 by 3 state indexing file is found')

        if os.path.exists(s.path('tabular_q')):
            todo['tabular_q'] = False
            print('tabular Q info file is found')

    else:
        cwd = os.getcwd()
        abs_path = os.path.join(cwd,s.path('results'))
        print(f'make dir : {abs_path}')
        os.mkdir(s.path('results'))

    if todo['minimax']:
        src.utils.initialize.initialize_minimax(s.path('minimax'))
    if todo['state_index_3']:
        src.utils.initialize.initialize_state_indices(s.path('state_index_3'))
    if todo['tabular_q']:
        with open(s.path('tabular_q'),'w') as f:
            json.dump({},f)

    return

if __name__ == '__main__':

    make_initial_results()