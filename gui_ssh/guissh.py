from Tkinter import *
import load_cfg
import ssh_manager

class StatusBar(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.label = Label(self, bd=1, relief=SUNKEN, anchor=W)
        self.label.pack(fill=X)

    def set(self, format, *args):
        self.label.config(text=format % args)
        self.label.update_idletasks()

    def clear(self):
        self.label.config(text="")
        self.label.update_idletasks()

class App:
    def __init__(self, master):
        self.ssh_manager = ssh_manager.SSH()
        self.master = master
        self.frame = Frame(master)
        self.init_gui()
        self.servers = load_cfg.load_file()
        for server in self.servers:
            self.listbox.insert(END, server['ip'])


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
        self.listbox.bind("<Double-Button-1>", self.listbox_sel_changed)

        self.statusbar = StatusBar(self.master)
        self.statusbar.set("no server selected")

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
        self.statusbar.grid(row = 3, columnspan = 6, sticky = W+E+N+S)

    def listbox_sel_changed(self, event):
        sel = self.listbox.curselection()
        if sel:
            sel = int(sel[0])
            print("selection is: %d" % sel)
            self.statusbar.set("selected server: %s" % self.servers[sel]['ip'])
        else:
            print("the first!")

    def cmd_connect(self):
        # server = self.servers[int(self.listbox.curselection()[0])]
        # self.ssh_manager.connect(server['ip'], 'root', server['password'])
        self.text.insert(INSERT, '=insert text=')
        # print("connect button clicked, server: %s" % server)


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
