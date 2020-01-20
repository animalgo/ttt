import numpy as np

class TTT:
    def __init__(self, size):
        self._size = size
        self._state = np.zeros(size * size, dtype='int')
        self._num_moves = 0
        self._order = True
        return

    def __str__(self):
        size = self._size
        state = self._state.reshape((size,size)).__str__()
        mover = self.get_mover()
        winner = self.check_winner()
        if winner == 0:
            state += f'\n mover : {mover}'
        else:
            state += f'\n winner : {winner}'
        return state

    def __repr__(self):
        return self.__str__()

    def get_mover(self,order=None,state=None):
        if order is None and state is None:
            order = self._order
            mover = 1 if order==True else -1
        elif type(state) is np.ndarray:
            sum = np.sum(state)
            if sum == 0:
                mover = 1
            elif sum == 1:
                mover = -1
            else:
                raise 'invalid state'
        return mover

    def get_state(self):
        return self._state.copy()

    def get_encoded_state(self,state=None):
        if state is None:
            state = self._state
        return state.__str__()

    def get_available_positions(self,state=None):
        if state is None:
            state = self._state
        indices = np.argwhere(state==0)
        indices =  indices.reshape(-1)
        return list(indices)

    def put(self, index:int)->None:
        
        assert int(self._state[index]) == 0
        # if int(self._state[index]) is not 0:
        #     return False
        mover = self.get_mover()
        self._state[index] = mover
        self._order = not self._order
        self._num_moves += 1
        return None

    def check_winner(self,state=None):
        size = self._size
        if state is None:
            state = self._state
        
        # check rows :
        for r in range(size):
            sum = np.sum(state[r*size:r*size+size])
            if sum == size:
                return 1
            elif sum == -size:
                return -1
        # check columns :
        for c in range(size):
            sum = 0
            for r in range(size):
                sum = sum + state[c + r*size]
                pass
            if sum == size:
                return 1
            elif sum == -size:
                return -1
        # check diagonal :
        sum1 = 0
        sum2 = 0
        for r in range(size):
            sum1 += state[r + r*size] # : / shape
            sum2 += state[size-1-r + r*size] # : \ shape
        if sum1 == size:
            return 1
        elif sum1 == -size:
            return -1
        if sum2 == size:
            return 1
        elif sum2 == -size:
            return -1
        # not yet finished :
        return 0

    def is_terminated(self,state=None):
        if state is None:
            state = self._state
            num_moves = self._num_moves
        else:
            num_moves = len(state[state!=0])
        
        # check cases :
        if num_moves == self._size*self._size:
            # full
            return True
        elif num_moves < self._size*2 - 1:
            # not enough moves
            return False
        elif self.check_winner(state) is not 0:
            return True
        else:
            return False

    def get_score(self,state=None):
        if state is not None:
            num_moves = len(state[state!=0])
        else:
            state = self._state
            num_moves = self._num_moves
        winner = self.check_winner(state)
        
        if winner == 0:
            return 0
        elif winner == 1:
            # score = #empty positions + 1
            # +1 for winning full game
            return ((self._size*self._size)*winner) - num_moves + 1
        elif winner == -1:
            return ((self._size*self._size)*winner) + num_moves - 1
        else:
            raise 'not allowed winner'

    def get_result(self,state=None)->dict:

        if state is not None:
            num_moves = len(state[state!=0])
        else:
            state = self._state
            num_moves = self._num_moves

        score = 0
        if num_moves < self._size*2 - 1:
            # not enough moves
            terminated = False
            pass
        elif num_moves == self._size * self._size :
            # board full
            terminated = True
            # score is 0 or 1 or -1, which is same as winner value :
            score = self.check_winner(state)
        else :
            score = self.get_score(state)
            if score == 0 :
                terminated = False
            else :
                terminated = True
            pass

        return {'terminated':terminated, 'score':score}
