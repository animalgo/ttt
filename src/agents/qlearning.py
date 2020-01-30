from src.game.ttt import TTT
from src.utils.path import Settings
import numpy as np
import random
import json
import pickle
import os
from typing import Callable
from tqdm import tqdm

class TabularQ:

    s = Settings()

    @staticmethod
    def load(id):
        results = TabularQ._get_results()
        info = results.get(str(id))
        if info is None:
            raise f"there's no stored data with id : {id}"
        else:
            size = info['size']
            parameters = info['parameters']
            q_file = info['q_file']
            q = TabularQ(size=size)
            q.set_params(**parameters)
            _Q = np.load(q_file)
            q._Q = _Q
            return q

    @staticmethod
    def _get_results()->dict:

        results_file = TabularQ.s.path('tabular_q')
        with open(results_file) as f:
            results = json.load(f)
        return results

    def __init__(self,size=3):
        self._size = size
        self._d = self._load_state_indices()
        self._Q = self._initialize_Q(size)
        self._parameters = {}
        self.set_params()
        self._is_first_mover = True
        pass

    def __eq__(self,other):
        s1 = self._size
        s2 = other._size
        if s1 != s2:
            return False
        p1 = self._parameters
        p2 = other._parameters
        if p1 != p2:
            return False
        check_Q = np.array_equal(self._Q,other._Q)
        return check_Q

    def set_params(self,alpha=1,gamma=1,ep_train=0.5,ep_infer=0.05,agent_for="both")->dict:
        
        assert agent_for == 'both' or agent_for == 'maximizer' or agent_for == 'minimizer'
        parameters = {
            "ep_train":ep_train,         # random sampling ratio
            "ep_infer":ep_infer,         # random inference ratio
            "gamma":gamma,               # discounted factor for each step. 1 for no penalty
            "alpha":alpha,               # new sample weight (learning rate)
            "agent_for":agent_for,       # 'both' or 'maximizer' or 'minimizer'
        }
        self._parameters = parameters

    def _load_state_indices(self):
        d = {}
        with open(TabularQ.s.path('state_index_3'),'rb') as f:
            d = pickle.load(f)
        return d

    def get_index(self,encoded_state:str)->int:
        return self._d.get(encoded_state)

    def get_state(self,state_index:int)->np.ndarray:
        
        d = self._d # {'[0 0 1 ...]' : 1283} {state(str):index} pair
        order = list(d.values()).index(state_index)
        encoded_state = list(d.keys())[order]
        state_raw = encoded_state[1:-1]
        state_raw = state_raw.split(' ')
        state_list = []
        for s in state_raw:
            if s != '':
                state_list.append(int(s))
        state = np.array(state_list,dtype='int')
        return state

    def _initialize_Q(self,size):
        num_states = len(self._d)
        num_actions = size*size
        Q = np.zeros((num_states,num_actions))
        return Q

    def update(self,encoded_state,move,encoded_next_state,reward):
        lr = self._parameters['alpha']
        Q = self._Q

        prev_state_index = self.get_index(encoded_state)

        sample_value = self._compute_sample_value(encoded_next_state,reward)

        Q[prev_state_index,move] = (lr * sample_value) + ( (1-lr) * Q[prev_state_index,move] )

        return None

    def _compute_sample_value(self,encoded_next_state,reward):
        Q = self._Q
        params = self._parameters
        gamma = params['gamma']
        next_state_index = self.get_index(encoded_next_state)
        if params['agent_for'] == 'both' :
            if self._is_first_mover :
                # next mover is minimizer :
                opt_func = np.min
            else :
                # next mover is maximizer :
                opt_func = np.max
        else :
            if self._is_first_mover :
                # always maximizer
                opt_func = np.max
            else :
                # always minimizer
                opt_func = np.min

        if next_state_index is None:
            # next_state is terminated state
            sample_value = reward
        else:
            sample_value = reward + ( gamma * opt_func(Q[next_state_index,:]) )
        
        # switch player :
        if params['agent_for'] == 'both':
            self._is_first_mover = not self._is_first_mover

        return sample_value

    def train(self, numOfGames=1000, opponent_agent=None):
        print(f'start to train {numOfGames} games')
        params = self._parameters
        if params['agent_for'] == 'both':
            assert opponent_agent is None
            self._train_both(numOfGames)
        else :
            # assert opponent_agent(np.ndarray) == move inferred :
            test_state = np.zeros(self._size * self._size,dtype=int)
            assert type(opponent_agent(test_state)) is int
            if params['agent_for'] == 'maximizer':
                self._is_first_mover = True
            elif params['agent_for'] == 'minimizer':
                self._is_first_mover = False
            else:
                raise NameError('invalid agent specified (for this instance)')
            self._train_against(opponent_agent,numOfGames)
            pass

        return

    def _train_both(self,numOfGames):
        for _ in tqdm(range(numOfGames)):
            game = TTT(self._size)
            self._is_first_mover = True

            # one complete game :
            while True:
                encoded_prev_state = game.get_encoded_state()

                possible_moves = game.get_available_positions()
                selected_move = self._epsilon_greedy_train(encoded_prev_state,possible_moves)
                game.put(selected_move)

                encoded_next_state =  game.get_encoded_state()
                result = game.get_result()
                self.update(encoded_prev_state,selected_move,encoded_next_state,result['score'])
                if result['terminated']:
                    break
                pass

            pass

    def _train_against(self,opponent_agent:Callable[[np.ndarray],int],numOfGames:int)->None:

        agent_q_turn = self._is_first_mover
        for _ in tqdm(range(numOfGames)):
            game = TTT(self._size)
            turn = True

            # one complete game :
            # prev state, action taken are from agent's turn
            # next state is from opponent's turn.
            # update in opponent's turn
            encoded_prev_state = None
            move_taken = None
            encoded_next_state = None
            while True:

                if turn is agent_q_turn:
                    # Q turn :
                    if game.is_terminated():
                        break
                    else:
                        possible_moves = game.get_available_positions()
                        encoded_prev_state = game.get_encoded_state()
                        move_taken = self._epsilon_greedy_train(encoded_prev_state,possible_moves)
                        game.put(move_taken)
                        pass
                    pass
                else:
                    # opponent's turn :
                    if not game.is_terminated():
                        state = game.get_state()
                        # move below is considered as random (sampling procedure) :
                        move = opponent_agent(state)
                        game.put(move)
                        pass
                    encoded_next_state = game.get_encoded_state()
                    score = game.get_score()
                    if encoded_prev_state is not None:
                        # : to avoid just after first move case ( in case of Q is second mover )
                        self.update(encoded_prev_state,move_taken,encoded_next_state,score)
                    
                    pass
                
                turn = not turn
            pass
        
        return None

    def _epsilon_greedy_train(self,encoded_state,possible_moves:list)->int:
        # trivial case :
        num_of_moves = len(possible_moves)
        if num_of_moves == 1 :
            return possible_moves[0]
        
        epsilon = self._parameters['ep_train']
        state_index = self.get_index(encoded_state)

        # impossible move might be chosen as the best move at some initial step :
        if self._is_first_mover:
            best_move_order = np.argmax(self._Q[state_index,possible_moves])
            best_move = possible_moves[best_move_order]
        else:
            best_move_order = np.argmin(self._Q[state_index,possible_moves])
            best_move = possible_moves[best_move_order]

        r = random.random()
        if r < epsilon:
            # random selection
            # to avoid best move :
            best_move_index = possible_moves.index(best_move)
            random_index = random.randint(0,num_of_moves-2)
            if random_index >= best_move_index:
                random_index += 1
            return possible_moves[random_index]
        else:
            # best choice
            return best_move

    def infer(self,encoded_state:str,possible_moves:list,mover:int)->int:
        
        # trivial case :
        num_of_moves = len(possible_moves)
        if num_of_moves == 1 :
            return possible_moves[0]
        
        agent = self._parameters['agent_for']
        state_index = self.get_index(encoded_state)
        if mover == 1:
            assert (agent == 'maximizer') or (agent == 'both')
            best_move_order = np.argmax(self._Q[state_index,possible_moves])
            best_move = possible_moves[best_move_order]
        elif mover == -1:
            assert (agent == 'minimizer') or (agent == 'both')
            best_move_order = np.argmin(self._Q[state_index,possible_moves])
            best_move = possible_moves[best_move_order]
        else:
            raise 'mover must be 1 (for maximizer) or -1 (for minimizer)'
        
        epsilon = self._parameters['ep_infer']
        r = random.random()
        if r > epsilon:
            return best_move
        else :
            # random inference
            best_move_index = possible_moves.index(best_move)
            random_index = random.randint(0,num_of_moves-2)
            if random_index >= best_move_index:
                random_index += 1
            return possible_moves[random_index]

    def save(self,comment='',id_forced=None):
        
        results = TabularQ._get_results()
        
        # forced_id to test :
        if id_forced is None:
            new_id = max(results.keys()) + 1
            while True:
                if str(new_id) in results:
                    new_id += 1
                else:
                    break
        else:
            new_id = id_forced

        # Save Q array :
        results_dir = TabularQ.s.path('results')
        new_q_file = 'tabular_q_trained_' + str(new_id) + '.npy'
        new_q_file = os.path.join(results_dir,new_q_file)
        np.save(new_q_file,self._Q)

        # update tabular_q.json :
        info = {
            "size":self._size,
            "parameters":self._parameters,
            "q_file":new_q_file,
            "comment":comment
        }
        results[str(new_id)] = info
        with open(TabularQ.s.path('tabular_q'),'w') as f:
            json.dump(results,f,sort_keys=True,indent=4)

        return


