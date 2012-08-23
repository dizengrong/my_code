from Tkinter import *

class App:
    def __init__(self, master):
        self.master = master
        self.frame = Frame(master)
        self.init_gui()

    def init_gui(self):
        Label(self.master, text = 'Server List:').grid(row = 0, columnspan = 2)

        self.btn_connect     = Button(self.master, text = 'Connect', command = self.cmd_connect)
        self.btn_connect_all = Button(self.master, text = 'Connect all', command = self.cmd_connect_all)
        self.btn_start       = Button(self.master, text = 'Start', command = self.cmd_start)
        self.btn_start_all   = Button(self.master, text = 'Start all', command = self.cmd_start_all)
        self.btn_stop        = Button(self.master, text = 'Stop', command = self.cmd_stop)
        self.btn_stop_all    = Button(self.master, text = 'Stop all', command = self.cmd_stop_all)
        self.btn_status      = Button(self.master, text = 'Status', command = self.cmd_status)
        self.btn_status_all  = Button(self.master, text = 'Status all', command = self.cmd_status_all)

        self.text_scrollbar = Scrollbar(self.master)

        self.text    = Text(self.master, height = 25, width = 80, 
                            # xscrollcommand = self.scrollbar.set,
                            yscrollcommand = self.text_scrollbar.set)
        self.text_scrollbar.config(command=self.text.yview)

        self.list_scrollbar = Scrollbar(self.master)
        self.listbox = Listbox(self.master, selectmode = SINGLE, yscrollcommand = self.list_scrollbar.set)
        self.list_scrollbar.config(command=self.listbox.yview)
        self.listbox.insert(END, 'server1')
        self.listbox.insert(END, 'server2')

        self.btn_connect.grid(row = 0, column = 2, sticky = W+E+N+S)
        self.btn_connect_all.grid(row = 2, column = 2, sticky = W+E+N+S)
        self.btn_start.grid(row = 0, column = 3, sticky = W+E+N+S)
        self.btn_start_all.grid(row = 2, column = 3, sticky = W+E+N+S)
        self.btn_stop.grid(row = 0, column = 4, sticky = W+E+N+S)
        self.btn_stop_all.grid(row = 2, column = 4, sticky = W+E+N+S)
        self.btn_status.grid(row = 0, column = 5, sticky = W+E+N+S)
        self.btn_status_all.grid(row = 2, column = 5, sticky = W+E+N+S)
        self.listbox.grid(row = 1, column = 0, rowspan = 2, sticky = W+E+N+S)
        self.list_scrollbar.grid(row = 1, column = 1, rowspan = 2, sticky = W+E+N+S)
        self.text.grid(row = 1, column = 2, columnspan = 4, sticky = W+E+N+S)
        self.text_scrollbar.grid(row = 1, column = 6, sticky = W+E+N+S)

    def cmd_connect(self):
            pass

    def cmd_connect_all(self):
            pass    

    def cmd_start(self):
            pass    

    def cmd_start_all(self):
            pass    

    def cmd_stop(self):
            pass    

    def cmd_stop_all(self):
            pass    

    def cmd_status(self):
            pass    

    def cmd_status_all(self):
            pass            
        



if __name__ == '__main__':
    root = Tk()
    app = App(root)
    root.mainloop()
