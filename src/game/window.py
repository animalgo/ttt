import tkinter as tk
import tkinter.ttk as ttk
import time
from src.game.ttt import TTT
from typing import Callable
import numpy as np

class GameWindow(tk.Toplevel):

    def __init__(self,user_first:bool,size=3,*args,**kwargs):
        
        super().__init__(*args,**kwargs)
        
        self._user_first = user_first

        self._t = TTT(size)
        self._agent:Callable[[np.ndarray],int]

        self._num_of_moves = 0
        self._state_history = [self._t.get_state()]
        self._history_scale:tk.Scale
        
        self._player_labels:{1:tk.Label,2:tk.Label}
        self._progress_bar:ttk.Progressbar
        self._buttons = []
        self._make_top_frame()
        self._make_board(size)
        self._make_bottom_frame(size)
        return

    def _make_top_frame(self):

        frame = tk.Frame(self)
        label1 = tk.Label(frame, text='player1')
        label2 = tk.Label(frame, text='player2')
        label1.pack()
        label2.pack()
        bar = ttk.Progressbar(frame,maximum=100,mode="indeterminate")
        self._progress_bar = bar
        bar.pack()
        frame.pack()
        return

    def _make_board(self,size):
        
        board = tk.Frame(self)
        buttons = self._buttons
        num_of_buttons = size*size
        for i in range(num_of_buttons):
            b = tk.Button(board,width=3,height=1,font=('Helvetica',30),
                        activebackground='white',
                        command=lambda num=i:self._on_click_board(num))
            buttons.append(b)
            b.grid(column=i%size,row=int(i/size))
            pass
        
        board.pack()
        return

    def _on_click_board(self,position:int):

        state_num = int(self._history_scale.get())
        is_rewinded = not (self._num_of_moves == state_num)
        if is_rewinded:
            # reset the game to the rewinded one :
            state_to_force = self._state_history[state_num]
            self._t.set_state(state_to_force)
            self._num_of_moves = self._t._num_moves
            self._state_history = self._state_history[0:(self._num_of_moves+1)]
            pass

        self._t.put(position)
        current_state = self._t.get_state()
        self._state_history.append(current_state)
        self._num_of_moves += 1
        self._history_scale.configure(to=self._num_of_moves)
        self._history_scale.set(self._num_of_moves)
        """
        [issue] If this procedure is called by button.invoke()
        then it doesn't invoke the scale's command _on_scale_move.
        So call it manually (and hence, called twice in user's turn) :
        """
        self._on_scale_move(self._num_of_moves)

        return

    def _modify_button(self,button_position:int,mover:int,move_allowed:bool,terminated=False,of_line=False):

        button = self._buttons[button_position]
        
        args = {'disabledforeground':'black','state':'disabled'}
        if mover == 1 :
            args['text'] = '○'
            args['state'] = 'disabled'
        elif mover == -1 :
            args['text'] = '×'
            args['state'] = 'disabled'
        else:
            args['text'] = ' '
            if move_allowed:
                args['state'] = 'normal'
            elif not hasattr(self,'_agent'):
                args['state'] = 'normal'

        if terminated:
            args['state'] = 'disabled'
            if of_line:
                if mover == 1:
                    args['disabledforeground'] = 'steelblue'
                elif mover == -1:
                    args['disabledforeground'] = 'tomato'

        button.config(**args)
        
        return

    def _make_bottom_frame(self,size):

        frame = tk.Frame(self)

        history_scale = tk.Scale(frame,command=self._on_scale_move
                                ,orient='horizontal',from_=0,to=0)
        history_scale.grid(row=0,columnspan=2)
        self._history_scale = history_scale

        restart_button = tk.Button(frame,text="Restart",command=self._on_click_reset)
        exit_button = tk.Button(frame,text="Exit",command=self.destroy)
        restart_button.grid(row=1,column=0)
        exit_button.grid(row=1,column=1)

        frame.pack()

        return

    def _on_scale_move(self,state_num):
        
        state_num = int(state_num)
        first_mover_turn = True if state_num%2 == 0 else False
        user_turn = first_mover_turn == self._user_first

        self._set_board(state_num,user_turn)
        
        if self.get_result()['terminated']:
            return

        if state_num == len(self._state_history)-1:
            if user_turn:
                pass
            else:
                if hasattr(self,'_agent'):
                    self._on_agent_turn(state_num)
                pass
        else:
            # : agent's turn but it's a previous state
            pass

        return

    def _set_board(self,state_num:int,user_turn:bool):

        to_state = self._state_history[state_num]
        result = self._t.get_result(to_state)
        terminated = result['terminated']
        lines = result['lines']
        lines = sum(lines,[]) # flattening
        for p in range(len(to_state)):
            move = int(to_state[p])
            of_line = p in lines
            self._modify_button(p,move,user_turn,terminated,of_line)
        return

    def _on_click_reset(self):

        self._num_of_moves = 0
        self._state_history = self._state_history[0:1]
        self._t.set_state(self._state_history[0])
        self._history_scale.configure(to=0)
        self._history_scale.set(0)
        self._set_board(0,self._user_first==True)

        return

    def set_agent(self,agent:Callable[[np.ndarray],int],name:str)->None:

        self._agent = agent


        return

    def _on_agent_turn(self,state_num:int):

        # TODO : async progress bar
        self._progress_bar.start(50)
        state = self._state_history[state_num]
        move = self._agent(state)
        button = self._buttons[move]
        button.configure(state='normal')
        button.invoke()
        self._progress_bar.stop()

        return

    def get_result(self)->dict:

        return self._t.get_result()

if __name__ == '__main__':
    game_window = GameWindow(True,3)
    
    import time
    def agent(state:np.ndarray):
        time.sleep(0.3)
        for i in range(len(state)):
            if state[i] == 0:
                return i
    # import src.agents
    # agent = src.agents.load('alpha_beta',size=3,penalty_prob=0.3)
    
    game_window.set_agent(agent,'agent')

    tk.mainloop()