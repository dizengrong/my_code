from Tkinter import *

class ShellText(Text):
    def __init__(self, master, prefix, height = 25, width = 80, yscrollcommand = None):
        Text.__init__(self, master)
        self.bind('<Key>', self.insert_char)
        self.bind('<Return>', self.insert_return)
        self.set_prefix(prefix)

    def get_cmd():
    	return 'ls'

    def set_prefix(self, prefix):
    	self.prefix = prefix
    	self.insert(END, prefix)

    def insert_char(self, event):
    	print('pressed char key code is: %s' % event.keycode)
    	if event.keycode == 37:
    		return 'break'

    def insert_return(self, event):
    	self.insert(END, '\n' + self.prefix)
    	return 'break'

