import tkinter as tk
from src.game.ttt import TTT

class GameWindow(tk.Toplevel):

    def __init__(self,user_first:bool,size=3,*args,**kwargs):
        
        super().__init__(*args,**kwargs)
        
        self._user_first = user_first

        self._t = TTT(size)

        self._num_of_moves = 0
        self._state_history = [self._t.get_state()]
        self._history_scale:tk.Scale
        
        self._buttons = []
        self._make_board(size)
        self._make_bottom_frame(size)
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

        return

    def _modify_button(self,button_position:int,mover:int,terminated=False,of_line=False):

        button = self._buttons[button_position]
        
        args = {'disabledforeground':'black'}
        if mover == 1 :
            args['text'] = '○'
            args['state'] = 'disabled'
        elif mover == -1 :
            args['text'] = '×'
            args['state'] = 'disabled'
        else:
            args['text'] = ' '
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
        self._rewind_to(state_num)
        return

    def _rewind_to(self,state_num:int):

        to_state = self._state_history[state_num]
        result = self._t.get_result(to_state)
        terminated = result['terminated']
        lines = result['lines']
        lines = sum(lines,[]) # flattening
        for p in range(len(to_state)):
            move = int(to_state[p])
            of_line = p in lines
            self._modify_button(p,move,terminated,of_line)
        return

    def _on_click_reset(self):

        self._num_of_moves = 0
        self._state_history = self._state_history[0:1]
        self._t.set_state(self._state_history[0])
        self._history_scale.configure(to=0)
        self._history_scale.set(0)
        self._rewind_to(0)

        return

    def put(self,position:int):
        
        self._buttons[position].invoke()

    def get_result(self)->dict:

        return self._t.get_result()

if __name__ == '__main__':
    game_window = GameWindow(True,3)
    tk.mainloop()