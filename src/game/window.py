import tkinter as tk
from src.game.ttt import TTT

class GameWindow(tk.Toplevel):

    def __init__(self,user_first:bool,size=3,*args,**kwargs):
        
        super().__init__(*args,**kwargs)
        
        self._user_first = user_first
        
        self._num_of_moves = 0
        self._state_history = [[0]*size*size]
        self._history_scale:tk.Scale

        self._t = TTT(size)
        
        self._buttons = []
        self._make_board(size)
        self._make_bottom_frame(size)
        return

    def _make_board(self,size):
        
        board = tk.Frame(self)
        buttons = self._buttons
        num_of_buttons = size*size
        for i in range(num_of_buttons):
            b = tk.Button(board,width=8,height=4,
                        command=lambda num=i:self._on_click(num))
            buttons.append(b)
            b.grid(column=i%size,row=int(i/size))
            pass
        
        board.pack()
        return

    def _on_click(self,position:int):

        # TODO
        # if last state, go on.
        # else, remove later history
        self._t.put(position)
        current_state = self._t.get_state()
        self._state_history.append(current_state)
        self._num_of_moves += 1
        self._history_scale.configure(to=self._num_of_moves)
        self._history_scale.set(self._num_of_moves)

        return

    def _modify_button(self,button_position:int,mover:0):

        button = self._buttons[button_position]
        
        if mover == 1 :
            text = '○'
            button_state = 'disabled'
        elif mover == -1 :
            text = '×'
            button_state = 'disabled'
        else:
            text = ' '
            button_state = 'normal'

        button.config(text=text,state=button_state)
        
        return

    def _make_bottom_frame(self,size):

        frame = tk.Frame(self)

        history_scale = tk.Scale(frame,command=self._on_scale_move
                                ,orient='horizontal',from_=0,to=0)
        history_scale.grid(row=0,columnspan=2)
        self._history_scale = history_scale

        restart_button = tk.Button(frame,text="Restart")
        exit_button = tk.Button(frame,text="Exit")
        restart_button.grid(row=1,column=0)
        exit_button.grid(row=1,column=1)

        frame.pack()

        return

    def _on_scale_move(self,state_num):
        print(state_num)
        state_num = int(state_num)
        to_state = self._state_history[state_num]
        for p in range(len(to_state)):
            move = int(to_state[p])
            self._modify_button(p,move)

        return

    def put(self,position:int):
        
        self._buttons[position].invoke()

    def get_result(self)->dict:

        return self._t.get_result()

if __name__ == '__main__':
    mother_window = tk.Tk()
    game_window = GameWindow(True)
    mother_window.mainloop()