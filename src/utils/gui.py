import tkinter as tk
import tkinter.ttk as ttk
from typing import Callable

class MainWindow:

    def __init__(self):
        window = tk.Tk()
        window.title('Tic Tac Toe')
        window.geometry('640x400+200+200')
        window.resizable(False,False)
        mover_selected = tk.IntVar()
        # for easy access :
        self._widgets = {
            'main':window,
            'mover_selected':mover_selected,
        }
        self._make_notebook_layout()
        self._fill_play_frame()
        # to relate treeview item and agent functions :
        self._num_of_agents = 0
        self._iid_to_agent = {} # iid(of treeview):agent function
        self._iid_to_explanation = {}

    def show(self):
        self._widgets['radio1'].invoke() # select() doesn't trigger event
        self._widgets['main'].mainloop()

    def _make_notebook_layout(self):
        w = self._widgets
        notebook = ttk.Notebook(w['main'],width=640,height=400)
        notebook.pack()
        play_frame = tk.Frame(w['main'])
        notebook.add(play_frame,text='Play')
        w['play_frame'] = play_frame

    def _fill_play_frame(self):
        
        w = self._widgets
        f = w['play_frame']

        radio1 = tk.Radiobutton(f,text="Move First",value=1,
                                variable=w['mover_selected'],command=self._on_mover_changed)
        radio2 = tk.Radiobutton(f,text="Move Second",value=-1,
                                variable=w['mover_selected'],command=self._on_mover_changed)
        radio1.grid(column=0,row=0)
        radio2.grid(column=1,row=0)
        w['radio1'] = radio1

        agents_frame = tk.LabelFrame(f,text='Agents List')
        agents_frame.grid(column=0,row=1,columnspan=2)

        tree = ttk.Treeview(agents_frame,columns=["agent","comment",'agent_for'],displaycolumns=["agent","comment"])
        # "#0" for the first column always :
        tree.column("#0",width=40)
        tree.heading("#0",text="#")
        tree.column("agent",width=100)
        tree.heading("agent",text="agent")
        tree.column("comment",width=300)
        tree.heading("comment",text="comment")
        tree.bind("<<TreeviewSelect>>",self._on_tree_selected)
        tree.pack(side="left")
        tabular_q_items = tree.insert('','end',iid='tq',text='Q',open=True)
        self._widgets['tree'] = tree
        self._widgets['tq_items'] = tabular_q_items

        explanation = tk.Text(agents_frame,width=30,height=17)
        explanation.pack(side='left')
        self._widgets['explanation'] = explanation
        
        play_button = tk.Button(f,text="Play",command=self._on_play)
        exit_button = tk.Button(f,text="Exit",command=self._widgets['main'].destroy)
        play_button.grid(column=0,row=2)
        exit_button.grid(column=1,row=2)
        return

    def _on_tree_selected(self,_):
        tree = self._widgets['tree']
        selected = tree.selection() # tuple of selected rows iids

        iid = selected[0]
        d = self._iid_to_explanation
        explanation = d.get(iid)
        widget = self._widgets['explanation']
        widget.delete("1.0",tk.END) # args=*[from,to] positions 1.0 = y.x form
        if explanation:
            widget.insert("1.0",explanation)

    def _on_mover_changed(self):

        mover = self._widgets['mover_selected'].get()
        tree = self._widgets['tree']
        if mover == 1:
            tree.tag_configure('minimizer',foreground='black')
            tree.tag_configure('maximizer',foreground='red')
        elif mover == -1:
            tree.tag_configure('minimizer',foreground='red')
            tree.tag_configure('maximizer',foreground='black')

        return

    def _on_play(self):
        
        # validation start :
        validated = False
        tree = self._widgets['tree']
        iid = tree.selection()
        if len(iid) == 1:
            iid = iid[0]
            agent_functions = self._iid_to_agent
            agent_function = agent_functions.get(iid)
            row_dict = tree.set(iid)
            agent_for = row_dict.get('agent_for')
            if iid in agent_functions:
                mover_player = self._widgets['mover_selected'].get()
                if mover_player == 1:
                    validated = agent_for=='minimizer' or agent_for=='both'
                elif mover_player == -1:
                    validated = agent_for=='maximizer' or agent_for=='both'

        else:
            # no agent is selected
            pass
        
        # after validation :
        if validated:
            # TODO
            print(f'play mover : {mover_player}, agent:{agent_function}')
        else:
            text = self._widgets['explanation']
            text.delete("1.0",tk.END)
            text.insert("1.0","Please select your opponent's agent")

    def add_agent(self,agent:Callable,agent_name:str,comment:str,agent_for:str,explanation:str):
        assert (agent_for=='both') or (agent_for=='maximizer') or (agent_for=='minimizer')
        tree = self._widgets['tree']
        tq = self._widgets['tq_items']
        self._num_of_agents += 1
        iid = str(self._num_of_agents)
        self._iid_to_agent[iid] = agent
        self._iid_to_explanation[iid] = explanation
        parent = tq if agent_name is 'tabular_q' else ''
        tree.insert(parent,'end',text=iid,values=[agent_name,comment,agent_for],
                    iid=iid,tags=[agent_for,'agent'])
        pass

if __name__ == '__main__':
    # layout test
    w = MainWindow()
    w.add_agent(max,'agent_name','comment','both','explanation both')
    w.add_agent(max,'tabular_q','it is maximizer','maximizer','explanation maximizer')
    w.add_agent(max,'tabular_q','it is minimizer','minimizer','explanation minimizer')
    w.show()